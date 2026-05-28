import logging
import re
from typing import Optional
from urllib.parse import parse_qs, quote_plus, unquote_plus, urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.models import Product

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9",
}

COMMON_WORDS = {
    "para",
    "com",
    "sem",
    "uma",
    "um",
    "de",
    "do",
    "da",
    "dos",
    "das",
    "por",
    "mais",
    "melhor",
    "feminino",
    "masculino",
}


def parse_price(text: Optional[str]) -> Optional[str]:
    if not text:
        return None
    cleaned = text.strip()
    return cleaned if cleaned.startswith("R$") else None


def is_search_affiliate_url(url: Optional[str]) -> bool:
    if not url:
        return False

    parsed = urlparse(url)
    host = parsed.netloc.lower()
    path = parsed.path.lower()

    if host.endswith("amazon.com.br") and path.startswith("/s"):
        return True
    if "magazinevoce.com.br" in host and "/busca/" in path:
        return True
    return False


def is_product_affiliate_url(url: Optional[str]) -> bool:
    if not url or is_search_affiliate_url(url):
        return False

    parsed = urlparse(url)
    host = parsed.netloc.lower()
    path = parsed.path.lower()

    if host.endswith("amazon.com.br"):
        return "/dp/" in path or "/gp/product/" in path
    if "magazinevoce.com.br" in host:
        return "/p/" in path or "/produto/" in path
    return True


def safe_affiliate_url(url: Optional[str]) -> Optional[str]:
    return url if is_product_affiliate_url(url) else None


def extract_query_from_url(url: str, fallback: str) -> str:
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    if params.get("k"):
        return unquote_plus(params["k"][0])

    path_parts = [part for part in parsed.path.split("/") if part]
    if "busca" in path_parts:
        index = path_parts.index("busca")
        if len(path_parts) > index + 1:
            return unquote_plus(path_parts[index + 1].replace("+", " "))

    return fallback


def significant_tokens(text: str) -> set[str]:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return {token for token in tokens if len(token) >= 4 and token not in COMMON_WORDS}


def looks_relevant(query: str, title: str) -> bool:
    query_tokens = significant_tokens(query)
    title_tokens = significant_tokens(title)
    if not query_tokens:
        return True

    model_tokens = {token for token in query_tokens if any(char.isdigit() for char in token)}
    if model_tokens and not (model_tokens & title_tokens):
        return False

    matches = query_tokens & title_tokens
    required = 1 if len(query_tokens) <= 2 else 2
    return len(matches) >= required


def normalize_image_url(candidate: Optional[str], base_url: str) -> Optional[str]:
    if not candidate:
        return None
    image_url = candidate.split()[0].strip()
    if not image_url or image_url.startswith("data:"):
        return None
    return urljoin(base_url, image_url)


def is_descriptive_product_name(name: str) -> bool:
    normalized = re.sub(r"\s+", " ", name).strip().lower()
    if normalized in {"genérico", "generico", "hbd"}:
        return False
    if len(normalized) < 12:
        return False
    return len(re.findall(r"[a-z0-9]+", normalized)) >= 2


def extract_amazon_product_name(item) -> Optional[str]:
    for selector in [
        "a.a-text-normal h2 span",
        "a.a-text-normal span",
        "h2.a-text-normal span",
        "h2 span",
    ]:
        element = item.select_one(selector)
        if not element:
            continue

        name = element.get_text(" ", strip=True)
        if is_descriptive_product_name(name):
            return name

    return None


def resolve_amazon_product(query: str) -> Optional[dict]:
    from app.config import settings

    search_url = f"https://www.amazon.com.br/s?k={quote_plus(query)}"
    try:
        with httpx.Client(headers=HEADERS, timeout=15, follow_redirects=True) as client:
            response = client.get(search_url)
    except Exception as exc:
        logger.warning("Nao foi possivel resolver link Amazon para '%s': %s", query, exc)
        return None

    if response.status_code != 200:
        logger.warning("Busca Amazon '%s' retornou status %s", query, response.status_code)
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.select("div[data-component-type='s-search-result']")

    for item in items[:10]:
        title = extract_amazon_product_name(item)
        link_el = item.select_one("a.a-text-normal[href]") or item.select_one("h2 a")
        if not title:
            continue

        asin = item.get("data-asin") or ""
        href = link_el.get("href", "") if link_el else ""
        asin_match = re.search(r"/(?:dp|gp/product)/([A-Z0-9]{10})", href) if href else None
        if not asin and asin_match:
            asin = asin_match.group(1)
        if not asin or not looks_relevant(query, title):
            continue

        image_el = item.select_one("img.s-image")
        price_el = item.select_one("span.a-price > span.a-offscreen")

        return {
            "title": title,
            "affiliate_url": f"https://www.amazon.com.br/dp/{asin}?tag={settings.AMAZON_TAG}",
            "image_url": normalize_image_url(image_el.get("src") if image_el else None, str(response.url)),
            "price": parse_price(price_el.get_text(strip=True) if price_el else None),
        }

    logger.warning("Nenhum produto Amazon confiavel encontrado para '%s'", query)
    return None


def resolve_product_search_links(db: Session, limit: int = 80) -> int:
    products = (
        db.query(Product)
        .filter(Product.affiliate_url.isnot(None))
        .filter(
            (Product.affiliate_url.like("%amazon.com.br/s?%"))
            | (Product.affiliate_url.like("%/busca/%"))
        )
        .limit(limit)
        .all()
    )
    updated = 0

    for product in products:
        if not is_search_affiliate_url(product.affiliate_url):
            continue

        query = extract_query_from_url(product.affiliate_url, product.name)
        resolved = resolve_amazon_product(query)
        if not resolved:
            continue

        product.affiliate_url = resolved["affiliate_url"]
        product.source = "amazon"
        product.store = "amazon"
        if resolved.get("image_url"):
            product.image_url = resolved["image_url"]
        if resolved.get("price"):
            product.price = resolved["price"]
        updated += 1

    if updated:
        db.commit()
    logger.info("%s links de afiliado resolvidos para produto real", updated)
    return updated
