import httpx
import re
from bs4 import BeautifulSoup
from typing import List, Optional
from dataclasses import dataclass

MAGALU_STORE = "https://www.magazinevoce.com.br/magazinemeumelhorachado"

@dataclass
class MagaluProduct:
    name: str
    price: str
    original_price: Optional[str]
    discount_pct: Optional[float]
    url: str
    image_url: Optional[str]

def parse_price(text: str) -> Optional[float]:
    if not text:
        return None
    cleaned = re.sub(r"[^\d,]", "", text).replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None

def build_magalu_affiliate_url(product_path: str) -> str:
    """Converte URL do produto para URL da loja parceira."""
    if product_path.startswith("http"):
        return product_path
    return f"{MAGALU_STORE}{product_path}"

async def search_magalu(query: str, max_results: int = 3) -> List[MagaluProduct]:
    """Busca produtos no Magazine Luiza."""
    url = f"https://www.magazineluiza.com.br/busca/{query.replace(' ', '%20')}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9",
    }

    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)

        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        items = soup.select("li[data-testid='product-card']")

        for item in items[:max_results * 2]:
            try:
                name_el = item.select_one("h2[data-testid='product-title']")
                if not name_el:
                    continue
                name = name_el.get_text(strip=True)

                link_el = item.select_one("a")
                product_url = ""
                if link_el and link_el.get("href"):
                    href = link_el["href"]
                    product_url = build_magalu_affiliate_url(href)

                price_el = item.select_one("p[data-testid='price-value']")
                price_str = price_el.get_text(strip=True) if price_el else None

                orig_el = item.select_one("p[data-testid='price-original']")
                orig_str = orig_el.get_text(strip=True) if orig_el else None

                discount = None
                if price_str and orig_str:
                    p = parse_price(price_str)
                    o = parse_price(orig_str)
                    if p and o and o > p:
                        discount = round((1 - p / o) * 100, 1)

                img_el = item.select_one("img")
                image_url = img_el.get("src") if img_el else None

                if name and product_url:
                    results.append(MagaluProduct(
                        name=name,
                        price=price_str or "Ver preço",
                        original_price=orig_str,
                        discount_pct=discount,
                        url=product_url,
                        image_url=image_url,
                    ))

                if len(results) >= max_results:
                    break

            except Exception:
                continue

        return results

    except Exception as e:
        print(f"[Magalu Scraper] Erro ao buscar '{query}': {e}")
        return []
