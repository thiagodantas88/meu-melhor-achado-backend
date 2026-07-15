# -*- coding: utf-8 -*-
import csv
import base64
import io
import json
import re
import zipfile
from concurrent.futures import ThreadPoolExecutor, TimeoutError, as_completed
from datetime import datetime
from html import escape
from typing import Optional
from urllib.parse import parse_qs, quote_plus, urljoin, urlparse, urlunparse

import httpx
from bs4 import BeautifulSoup

from app.config import settings

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9",
    "Cache-Control": "no-cache",
}

PARTNER_SOURCES = {"amazon", "magalu"}
REQUEST_TIMEOUT = httpx.Timeout(8.0, connect=4.0)
PRICE_RE = re.compile(r"R\$\s*\d{1,3}(?:\.\d{3})*(?:,\d{2})?", re.IGNORECASE)
KNOWN_RETAILERS = [
    ("amazon.com.br", "Amazon", True, "partner"),
    ("magazinevoce.com.br", "Magalu", True, "partner"),
    ("magazineluiza.com.br", "Magalu", True, "partner"),
    ("buscape.com.br", "Buscape", False, "aggregator"),
    ("mercadolivre.com.br", "Mercado Livre", False, "marketplace"),
    ("shopee.com.br", "Shopee", False, "marketplace"),
    ("madeiramadeira.com.br", "MadeiraMadeira", False, "retailer"),
    ("mobly.com.br", "Mobly", False, "retailer"),
    ("leroymerlin.com.br", "Leroy Merlin", False, "retailer"),
    ("casasbahia.com.br", "Casas Bahia", False, "retailer"),
    ("pontofrio.com.br", "Ponto Frio", False, "retailer"),
    ("tokstok.com.br", "Tok&Stok", False, "retailer"),
    ("casaevideo.com.br", "Casa & Video", False, "retailer"),
    ("meumoveldemadeira.com.br", "Meu Movel de Madeira", False, "retailer"),
    ("westwing.com.br", "Westwing", False, "retailer"),
]


def parse_price(text: Optional[str]) -> Optional[float]:
    if not text:
        return None
    cleaned = re.sub(r"[^\d,.]", "", text)
    if not cleaned:
        return None
    if "," in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None


def find_price(text: Optional[str]) -> Optional[float]:
    if not text:
        return None
    match = PRICE_RE.search(text)
    return parse_price(match.group(0)) if match else None


def normalize_image_url(candidate: Optional[str], base_url: str) -> Optional[str]:
    if not candidate:
        return None
    image_url = candidate.split()[0].strip()
    if not image_url or image_url.startswith("data:"):
        return None
    return urljoin(base_url, image_url)


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def build_query(product_name: str = "", product_model: str = "", product_type: str = "", description: str = "") -> str:
    parts = [product_name, product_model, product_type, description]
    query = " ".join(clean_text(part) for part in parts if clean_text(part))
    return clean_text(query)


def detect_coupon_note(text: str) -> tuple[Optional[str], Optional[str]]:
    normalized = clean_text(text)
    if not re.search(r"\b(cupom|coupon|pix|frete gratis|frete grátis|desconto)\b", normalized, re.IGNORECASE):
        return None, None

    code_match = re.search(r"\b[A-Z0-9]{4,16}\b", normalized)
    code = code_match.group(0) if code_match and re.search(r"\d", code_match.group(0)) else None
    note = "Possível promoção/cupom informado na página. Confirme no carrinho antes de comprar."
    return code, note


def detect_shipping_note(text: str, cep: str) -> Optional[str]:
    normalized = clean_text(text)
    if re.search(r"frete\s+gr[aá]tis", normalized, re.IGNORECASE):
        return f"Página informa frete grátis. Confirme disponibilidade para o CEP {cep}."
    if re.search(r"retirada|entrega", normalized, re.IGNORECASE):
        return f"Entrega/retirada mencionada na página. Calcule no checkout para o CEP {cep}."
    return f"Frete não informado na listagem. Calcule no checkout para o CEP {cep}."


def unwrap_duckduckgo_url(href: str) -> str:
    if not href:
        return ""
    absolute = urljoin("https://duckduckgo.com", href)
    parsed = urlparse(absolute)
    query = parse_qs(parsed.query)
    if query.get("uddg"):
        return query["uddg"][0]
    return absolute


def unwrap_bing_url(href: str) -> str:
    if not href:
        return ""
    absolute = urljoin("https://www.bing.com", href)
    parsed = urlparse(absolute)
    if "bing.com" not in parsed.netloc:
        return absolute
    query = parse_qs(parsed.query)
    encoded = query.get("u", [""])[0]
    if not encoded:
        return absolute
    if encoded.startswith("a1"):
        encoded = encoded[2:]
    try:
        padding = "=" * (-len(encoded) % 4)
        return base64.urlsafe_b64decode((encoded + padding).encode("utf-8")).decode("utf-8")
    except Exception:
        return absolute


def source_from_url(url: str) -> Optional[tuple[str, bool, str]]:
    host = urlparse(url).netloc.lower().removeprefix("www.")
    for domain, source, is_partner, source_type in KNOWN_RETAILERS:
        if host == domain or host.endswith(f".{domain}") or domain in host:
            return source, is_partner, source_type
    return None


def magalu_store_path() -> str:
    store = settings.MAGALU_STORE.strip("/")
    parsed = urlparse(store)
    return parsed.path.strip("/") if parsed.scheme else store


def with_partner_tracking(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    if "amazon.com.br" in host:
        if "tag=" in parsed.query:
            return url
        separator = "&" if parsed.query else "?"
        return f"{url}{separator}tag={settings.AMAZON_TAG}"
    if "magazinevoce.com.br" in host:
        path_parts = [part for part in parsed.path.split("/") if part]
        if path_parts:
            path_parts[0] = magalu_store_path()
        else:
            path_parts = [magalu_store_path()]
        return urlunparse(parsed._replace(path="/" + "/".join(path_parts)))
    if "magazineluiza.com.br" in host:
        return urlunparse(
            parsed._replace(
                scheme="https",
                netloc="www.magazinevoce.com.br",
                path=f"/{magalu_store_path()}{parsed.path}",
            )
        )
    return url


def read_jsonld_price(soup: BeautifulSoup) -> Optional[float]:
    def walk(value):
        if isinstance(value, dict):
            offers = value.get("offers")
            if isinstance(offers, dict):
                price = offers.get("price") or offers.get("lowPrice") or offers.get("highPrice")
                parsed = parse_price(str(price)) if price is not None else None
                if parsed:
                    return parsed
            for nested in value.values():
                parsed = walk(nested)
                if parsed:
                    return parsed
        if isinstance(value, list):
            for item in value:
                parsed = walk(item)
                if parsed:
                    return parsed
        return None

    for script in soup.select("script[type='application/ld+json']"):
        try:
            payload = json.loads(script.string or "{}")
        except Exception:
            continue
        parsed = walk(payload)
        if parsed:
            return parsed
    return None


def enrich_offer_from_page(offer: dict) -> dict:
    url = offer.get("url") or ""
    if not source_from_url(url):
        return offer
    try:
        with httpx.Client(headers=HEADERS, timeout=httpx.Timeout(4.0, connect=2.0), follow_redirects=True) as client:
            response = client.get(url)
        if response.status_code != 200 or "captcha" in response.text[:3000].lower():
            return offer
        soup = BeautifulSoup(response.text, "html.parser")
        if not offer.get("image_url"):
            image_meta = (
                soup.select_one("meta[property='og:image']")
                or soup.select_one("meta[name='twitter:image']")
                or soup.select_one("link[rel='image_src']")
            )
            image = image_meta.get("content") or image_meta.get("href") if image_meta else None
            offer["image_url"] = normalize_image_url(image, str(response.url))
        if offer.get("price") is None:
            price_meta = (
                soup.select_one("meta[property='product:price:amount']")
                or soup.select_one("meta[property='og:price:amount']")
                or soup.select_one("meta[itemprop='price']")
            )
            price = parse_price(price_meta.get("content") if price_meta else None) or read_jsonld_price(soup)
            offer["price"] = price
        return offer
    except Exception:
        return offer


def sort_offers(offers: list[dict]) -> list[dict]:
    seen: set[str] = set()
    unique = []
    for offer in offers:
        url = offer.get("url") or ""
        title = offer.get("title") or ""
        key = url or f"{offer.get('source')}:{title}:{offer.get('price')}"
        if key in seen or not title:
            continue
        seen.add(key)
        unique.append(offer)

    return sorted(
        unique,
        key=lambda item: (
            0 if item.get("is_partner") else 1,
            item.get("price") if item.get("price") is not None else 999999999,
        ),
    )


def search_amazon(query: str, cep: str, limit: int = 12) -> list[dict]:
    url = f"https://www.amazon.com.br/s?k={quote_plus(query)}&tag={settings.AMAZON_TAG}"
    offers: list[dict] = []
    try:
        with httpx.Client(headers=HEADERS, timeout=REQUEST_TIMEOUT, follow_redirects=True) as client:
            response = client.get(url)
        if response.status_code != 200:
            return offers

        soup = BeautifulSoup(response.text, "html.parser")
        for item in soup.select("div[data-component-type='s-search-result']")[:limit]:
            title_el = item.select_one("h2 span") or item.select_one("a.a-text-normal span")
            price_el = item.select_one("span.a-price > span.a-offscreen")
            old_el = item.select_one("span.a-price.a-text-price > span.a-offscreen")
            img_el = item.select_one("img.s-image")
            href_el = item.select_one("a.a-text-normal[href]") or item.select_one("h2 a[href]")
            asin = item.get("data-asin") or ""
            href = href_el.get("href", "") if href_el else ""
            match = re.search(r"/dp/([A-Z0-9]{10})", href)
            if not asin and match:
                asin = match.group(1)

            title = clean_text(title_el.get_text(" ", strip=True) if title_el else "")
            price = parse_price(price_el.get_text(" ", strip=True) if price_el else "")
            original_price = parse_price(old_el.get_text(" ", strip=True) if old_el else "")
            if not title or not price or not asin:
                continue

            discount_pct = None
            if original_price and original_price > price:
                discount_pct = int(((original_price - price) / original_price) * 100)

            item_text = item.get_text(" ", strip=True)
            coupon_code, coupon_note = detect_coupon_note(item_text)
            offers.append(
                {
                    "title": title[:500],
                    "price": price,
                    "original_price": original_price,
                    "discount_pct": discount_pct,
                    "source": "Amazon",
                    "source_type": "partner",
                    "url": f"https://www.amazon.com.br/dp/{asin}?tag={settings.AMAZON_TAG}",
                    "image_url": img_el.get("src", "") if img_el else None,
                    "coupon_code": coupon_code,
                    "coupon_note": coupon_note,
                    "shipping_note": detect_shipping_note(item_text, cep),
                    "is_partner": True,
                }
            )
    except Exception:
        return offers
    return offers


def search_magalu(query: str, cep: str, limit: int = 12) -> list[dict]:
    store = settings.MAGALU_STORE.strip("/")
    parsed_store = urlparse(store)
    store_path = parsed_store.path.strip("/") if parsed_store.scheme else store
    url = f"https://www.magazinevoce.com.br/{store_path}/busca/{quote_plus(query)}/"
    offers: list[dict] = []
    try:
        with httpx.Client(headers=HEADERS, timeout=REQUEST_TIMEOUT, follow_redirects=True) as client:
            response = client.get(url)
        if response.status_code != 200 or "Captcha Magalu" in response.text:
            return offers

        soup = BeautifulSoup(response.text, "html.parser")
        next_data = soup.find("script", id="__NEXT_DATA__")
        if next_data and next_data.string:
            import json

            payload = json.loads(next_data.string)
            products = (
                payload.get("props", {})
                .get("pageProps", {})
                .get("data", {})
                .get("search", {})
                .get("products", [])
            )
            for product in products[:limit]:
                title = clean_text(product.get("title") or "")
                price_data = product.get("price") or {}
                price = parse_price(str(price_data.get("bestPrice") or price_data.get("fullPrice") or price_data.get("price") or ""))
                original_price = parse_price(str(price_data.get("price") or price_data.get("fullPrice") or ""))
                path = product.get("url") or product.get("path") or ""
                if not title or not price or not path:
                    continue

                discount_pct = None
                if original_price and original_price > price:
                    discount_pct = int(((original_price - price) / original_price) * 100)

                image_url = (product.get("image") or "").replace("{w}x{h}", "600x600")
                offer_url = path if path.startswith("http") else f"https://www.magazinevoce.com.br{path}"
                raw_text = f"{title} {product}"
                coupon_code, coupon_note = detect_coupon_note(raw_text)
                offers.append(
                    {
                        "title": title[:500],
                        "price": price,
                        "original_price": original_price,
                        "discount_pct": discount_pct,
                        "source": "Magalu",
                        "source_type": "partner",
                        "url": offer_url,
                        "image_url": image_url or None,
                        "coupon_code": coupon_code,
                        "coupon_note": coupon_note,
                        "shipping_note": detect_shipping_note(raw_text, cep),
                        "is_partner": True,
                    }
                )
            return offers

        for item in soup.select("li[data-testid='product-card']")[:limit]:
            title_el = item.select_one("[data-testid='product-title']")
            price_el = item.select_one("[data-testid='price-value']")
            old_el = item.select_one("[data-testid='price-original']")
            link_el = item.select_one("a[href]")
            img_el = item.select_one("img")
            title = clean_text(title_el.get_text(" ", strip=True) if title_el else "")
            price = parse_price(price_el.get_text(" ", strip=True) if price_el else "")
            href = link_el.get("href", "") if link_el else ""
            if not title or not price or not href:
                continue
            original_price = parse_price(old_el.get_text(" ", strip=True) if old_el else "")
            offer_url = href if href.startswith("http") else f"https://www.magazinevoce.com.br{href}"
            raw_text = item.get_text(" ", strip=True)
            coupon_code, coupon_note = detect_coupon_note(raw_text)
            offers.append(
                {
                    "title": title[:500],
                    "price": price,
                    "original_price": original_price,
                    "discount_pct": int(((original_price - price) / original_price) * 100) if original_price and original_price > price else None,
                    "source": "Magalu",
                    "source_type": "partner",
                    "url": offer_url,
                    "image_url": normalize_image_url(img_el.get("src") if img_el else None, str(response.url)),
                    "coupon_code": coupon_code,
                    "coupon_note": coupon_note,
                    "shipping_note": detect_shipping_note(raw_text, cep),
                    "is_partner": True,
                }
            )
    except Exception:
        return offers
    return offers


def search_mercado_livre(query: str, cep: str, limit: int = 16) -> list[dict]:
    url = f"https://lista.mercadolivre.com.br/{quote_plus(query)}"
    offers: list[dict] = []
    try:
        with httpx.Client(headers=HEADERS, timeout=REQUEST_TIMEOUT, follow_redirects=True) as client:
            response = client.get(url)
        if response.status_code != 200:
            return offers

        soup = BeautifulSoup(response.text, "html.parser")
        selectors = [
            "li.ui-search-layout__item",
            "div.ui-search-result__wrapper",
            "div.poly-card",
        ]
        items = []
        for selector in selectors:
            items = soup.select(selector)
            if items:
                break

        for item in items[:limit]:
            title_el = (
                item.select_one("h2")
                or item.select_one(".ui-search-item__title")
                or item.select_one(".poly-component__title")
                or item.select_one("a[title]")
            )
            link_el = item.select_one("a[href]")
            price_fraction = item.select_one(".andes-money-amount__fraction")
            price_cents = item.select_one(".andes-money-amount__cents")
            img_el = item.select_one("img")

            title = clean_text(title_el.get("title") if title_el and title_el.get("title") else title_el.get_text(" ", strip=True) if title_el else "")
            price_text = price_fraction.get_text("", strip=True) if price_fraction else ""
            if price_cents:
                price_text = f"{price_text},{price_cents.get_text('', strip=True)}"
            price = parse_price(price_text)
            href = link_el.get("href", "") if link_el else ""
            if not title or not price or not href:
                continue

            raw_text = item.get_text(" ", strip=True)
            coupon_code, coupon_note = detect_coupon_note(raw_text)
            offers.append(
                {
                    "title": title[:500],
                    "price": price,
                    "original_price": None,
                    "discount_pct": None,
                    "source": "Mercado Livre",
                    "source_type": "marketplace",
                    "url": href,
                    "image_url": normalize_image_url(
                        img_el.get("data-src") or img_el.get("src") if img_el else None,
                        str(response.url),
                    ),
                    "coupon_code": coupon_code,
                    "coupon_note": coupon_note,
                    "shipping_note": detect_shipping_note(raw_text, cep),
                    "is_partner": False,
                }
            )
    except Exception:
        return offers
    return offers


def search_bing(query: str, cep: str, limit: int = 12) -> list[dict]:
    url = f"https://www.bing.com/search?q={quote_plus(query + ' comprar Brasil promoção cupom')}"
    offers: list[dict] = []
    try:
        with httpx.Client(headers=HEADERS, timeout=REQUEST_TIMEOUT, follow_redirects=True) as client:
            response = client.get(url)
        if response.status_code != 200:
            return offers

        soup = BeautifulSoup(response.text, "html.parser")
        for item in soup.select("li.b_algo")[:limit]:
            title_el = item.select_one("h2 a[href]")
            snippet_el = item.select_one(".b_caption p")
            if not title_el:
                continue
            offer_url = unwrap_bing_url(title_el.get("href", ""))
            source_info = source_from_url(offer_url)
            if not source_info:
                continue

            source, is_partner, source_type = source_info
            title = clean_text(title_el.get_text(" ", strip=True))
            snippet = clean_text(snippet_el.get_text(" ", strip=True) if snippet_el else "")
            raw_text = f"{title} {snippet}"
            coupon_code, coupon_note = detect_coupon_note(raw_text)
            offers.append(
                {
                    "title": title[:500],
                    "price": find_price(raw_text),
                    "original_price": None,
                    "discount_pct": None,
                    "source": source,
                    "source_type": source_type,
                    "url": with_partner_tracking(offer_url),
                    "image_url": None,
                    "coupon_code": coupon_code,
                    "coupon_note": coupon_note,
                    "shipping_note": detect_shipping_note(raw_text, cep),
                    "is_partner": is_partner,
                }
            )
    except Exception:
        return offers
    return offers


def search_duckduckgo(query: str, cep: str, limit: int = 14) -> list[dict]:
    url = f"https://duckduckgo.com/html/?q={quote_plus(query + ' comprar Brasil promoção cupom')}"
    offers: list[dict] = []
    try:
        with httpx.Client(headers=HEADERS, timeout=REQUEST_TIMEOUT, follow_redirects=True) as client:
            response = client.get(url)
        if response.status_code != 200 or "Unfortunately, bots use DuckDuckGo too" in response.text:
            return offers

        soup = BeautifulSoup(response.text, "html.parser")
        for item in soup.select(".result")[:limit]:
            title_el = item.select_one(".result__a")
            snippet_el = item.select_one(".result__snippet")
            if not title_el:
                continue
            offer_url = unwrap_duckduckgo_url(title_el.get("href", ""))
            source_info = source_from_url(offer_url)
            if not source_info:
                continue

            source, is_partner, source_type = source_info
            title = clean_text(title_el.get_text(" ", strip=True))
            snippet = clean_text(snippet_el.get_text(" ", strip=True) if snippet_el else "")
            raw_text = f"{title} {snippet}"
            coupon_code, coupon_note = detect_coupon_note(raw_text)
            offers.append(
                {
                    "title": title[:500],
                    "price": find_price(raw_text),
                    "original_price": None,
                    "discount_pct": None,
                    "source": source,
                    "source_type": source_type,
                    "url": with_partner_tracking(offer_url),
                    "image_url": None,
                    "coupon_code": coupon_code,
                    "coupon_note": coupon_note,
                    "shipping_note": detect_shipping_note(raw_text, cep),
                    "is_partner": is_partner,
                }
            )

        if offers:
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(enrich_offer_from_page, offer) for offer in offers[:8]]
                enriched = []
                for future in as_completed(futures, timeout=8):
                    try:
                        enriched.append(future.result(timeout=1))
                    except Exception:
                        continue
                offers = enriched + offers[8:]
    except Exception:
        return offers
    return offers


def search_store_shortcuts(query: str, cep: str) -> list[dict]:
    encoded = quote_plus(query)
    shortcuts = [
        ("Amazon", "partner", True, f"https://www.amazon.com.br/s?k={encoded}&tag={settings.AMAZON_TAG}"),
        ("Magalu", "partner", True, f"https://www.magazinevoce.com.br/{magalu_store_path()}/busca/{encoded}/"),
        ("MadeiraMadeira", "retailer", False, f"https://www.madeiramadeira.com.br/busca?q={encoded}"),
        ("Mobly", "retailer", False, f"https://www.mobly.com.br/catalogsearch/result/?q={encoded}"),
        ("Mercado Livre", "marketplace", False, f"https://lista.mercadolivre.com.br/{encoded}"),
        ("Leroy Merlin", "retailer", False, f"https://www.leroymerlin.com.br/search?term={encoded}"),
        ("Casas Bahia", "retailer", False, f"https://www.casasbahia.com.br/{encoded}/b"),
        ("Tok&Stok", "retailer", False, f"https://www.tokstok.com.br/busca?q={encoded}"),
    ]
    return [
        {
            "title": f'Pesquisar "{query}" na {source}',
            "price": None,
            "original_price": None,
            "discount_pct": None,
            "source": source,
            "source_type": source_type,
            "url": url,
            "image_url": None,
            "coupon_code": None,
            "coupon_note": "Preço não disponível na listagem automática. Abra a loja para confirmar ofertas e cupons.",
            "shipping_note": f"Calcule o frete no checkout para o CEP {cep}.",
            "is_partner": is_partner,
        }
        for source, source_type, is_partner, url in shortcuts
    ]


def search_mobilia_offers(query: str, cep: str = "59091-130") -> list[dict]:
    offers = []
    searchers = [search_amazon, search_magalu, search_mercado_livre, search_bing, search_duckduckgo]
    with ThreadPoolExecutor(max_workers=len(searchers)) as executor:
        futures = [executor.submit(searcher, query, cep) for searcher in searchers]
        try:
            for future in as_completed(futures, timeout=15):
                try:
                    offers.extend(future.result(timeout=1))
                except Exception:
                    continue
        except TimeoutError:
            for future in futures:
                future.cancel()
    sorted_offers = sort_offers(offers)
    return sorted_offers or search_store_shortcuts(query, cep)


def offers_to_csv(rows: list[dict]) -> bytes:
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "data",
            "busca",
            "titulo",
            "preco",
            "preco_original",
            "desconto_pct",
            "loja",
            "parceiro",
            "cupom",
            "observacao_cupom",
            "frete",
            "url",
            "imagem",
        ],
    )
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return output.getvalue().encode("utf-8-sig")


def column_letter(index: int) -> str:
    letters = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters


def sheet_xml(rows: list[list[str]]) -> str:
    sheet_rows = []
    for row_index, row in enumerate(rows, start=1):
        cells = []
        for col_index, value in enumerate(row, start=1):
            ref = f"{column_letter(col_index)}{row_index}"
            cells.append(f'<c r="{ref}" t="inlineStr"><is><t>{escape(str(value or ""))}</t></is></c>')
        sheet_rows.append(f'<row r="{row_index}">{"".join(cells)}</row>')
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<sheetData>{"".join(sheet_rows)}</sheetData>'
        '</worksheet>'
    )


def offers_to_xlsx(rows: list[dict]) -> bytes:
    headers = [
        "Data",
        "Busca",
        "Titulo",
        "Preco",
        "Preco original",
        "Desconto %",
        "Loja",
        "Parceiro",
        "Cupom",
        "Observacao cupom",
        "Frete",
        "URL",
        "Imagem",
    ]
    data_rows = [headers]
    for row in rows:
        data_rows.append(
            [
                row["data"],
                row["busca"],
                row["titulo"],
                row["preco"],
                row["preco_original"],
                row["desconto_pct"],
                row["loja"],
                row["parceiro"],
                row["cupom"],
                row["observacao_cupom"],
                row["frete"],
                row["url"],
                row["imagem"],
            ]
        )

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as xlsx:
        xlsx.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
            '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            "</Types>",
        )
        xlsx.writestr(
            "_rels/.rels",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
            "</Relationships>",
        )
        xlsx.writestr(
            "xl/workbook.xml",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            '<sheets><sheet name="Ofertas" sheetId="1" r:id="rId1"/></sheets></workbook>',
        )
        xlsx.writestr(
            "xl/_rels/workbook.xml.rels",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
            "</Relationships>",
        )
        xlsx.writestr("xl/worksheets/sheet1.xml", sheet_xml(data_rows))
    return buffer.getvalue()


def now_filename_suffix() -> str:
    return datetime.utcnow().strftime("%Y%m%d%H%M%S")
