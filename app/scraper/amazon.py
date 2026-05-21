import httpx
import random
import re
from bs4 import BeautifulSoup
from typing import List, Optional
from dataclasses import dataclass

HEADERS_POOL = [
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    },
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    },
]

AFFILIATE_TAG = "meumelhoracha-20"

@dataclass
class ScrapedProduct:
    name: str
    price: str
    original_price: Optional[str]
    discount_pct: Optional[float]
    url: str
    image_url: Optional[str]
    rating: Optional[float]
    asin: Optional[str]

def build_affiliate_url(url: str) -> str:
    if "tag=" in url:
        return url
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}tag={AFFILIATE_TAG}"

def parse_price(text: str) -> Optional[float]:
    if not text:
        return None
    cleaned = re.sub(r"[^\d,]", "", text).replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None

async def search_amazon(query: str, max_results: int = 3) -> List[ScrapedProduct]:
    """Busca produtos na Amazon Brasil e retorna os mais relevantes."""
    url = f"https://www.amazon.com.br/s?k={query.replace(' ', '+')}"
    headers = random.choice(HEADERS_POOL)

    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)

        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        items = soup.select("div[data-component-type='s-search-result']")

        for item in items[:max_results * 2]:
            try:
                # Nome
                name_el = item.select_one("h2 a span")
                if not name_el:
                    continue
                name = name_el.get_text(strip=True)

                # ASIN
                asin = item.get("data-asin", "")

                # URL
                link_el = item.select_one("h2 a")
                product_url = ""
                if link_el and link_el.get("href"):
                    href = link_el["href"]
                    if href.startswith("/"):
                        href = f"https://www.amazon.com.br{href}"
                    product_url = build_affiliate_url(href)

                # Preço atual
                price_el = item.select_one("span.a-price > span.a-offscreen")
                price_str = price_el.get_text(strip=True) if price_el else None

                # Preço original (riscado)
                orig_el = item.select_one("span.a-price.a-text-price > span.a-offscreen")
                orig_str = orig_el.get_text(strip=True) if orig_el else None

                # Calcular desconto
                discount = None
                if price_str and orig_str:
                    p = parse_price(price_str)
                    o = parse_price(orig_str)
                    if p and o and o > p:
                        discount = round((1 - p / o) * 100, 1)

                # Imagem
                img_el = item.select_one("img.s-image")
                image_url = img_el.get("src") if img_el else None

                # Rating
                rating_el = item.select_one("span.a-icon-alt")
                rating = None
                if rating_el:
                    m = re.search(r"([\d,]+) de 5", rating_el.get_text())
                    if m:
                        rating = float(m.group(1).replace(",", "."))

                if name and product_url:
                    results.append(ScrapedProduct(
                        name=name,
                        price=price_str or "Ver preço",
                        original_price=orig_str,
                        discount_pct=discount,
                        url=product_url,
                        image_url=image_url,
                        rating=rating,
                        asin=asin,
                    ))

                if len(results) >= max_results:
                    break

            except Exception:
                continue

        return results

    except Exception as e:
        print(f"[Amazon Scraper] Erro ao buscar '{query}': {e}")
        return []
