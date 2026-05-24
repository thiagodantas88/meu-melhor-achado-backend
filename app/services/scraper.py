"""
Robo diario do Meu Melhor Achado.

Busca ofertas na Amazon e no Magalu, salva deals ativos e gera comparativos
simples para a API. O scraper falha de forma silenciosa por loja/termo para
nao derrubar o backend caso uma pagina mude markup ou bloqueie a requisicao.
"""

import logging
import re
from datetime import date, datetime
from typing import Optional
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.config import settings
from app.models import DailyComparison, Deal, PriceHistory, Product, ScraperLog
from app.services.notifier import send_run_report

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9",
}

SEARCH_TERMS = [
    ("tecnologia", "fone de ouvido bluetooth"),
    ("tecnologia", "carregador usb-c"),
    ("tecnologia", "cabo usb-c"),
    ("tecnologia", "power bank"),
    ("casa", "air fryer"),
    ("casa", "aspirador de po"),
    ("home-office", "mouse sem fio"),
    ("home-office", "teclado mecanico"),
    ("carro", "suporte celular carro"),
    ("carro", "carregador veicular"),
    ("bebidas", "vinho"),
    ("bebidas", "cafe gourmet"),
    ("moda", "vestido feminino"),
    ("moda", "bolsa feminina"),
]

COMPARISON_TEMPLATES = [
    {
        "title": "To em duvida entre o {a} e o {b}: qual levo?",
        "summary": "Dois produtos parecidos, precos diferentes. Olhamos de perto e contamos o que cada um entrega de verdade.",
    },
    {
        "title": "{a} ou {b}? Veja qual faz mais sentido para voce",
        "summary": "Nao e so o preco que conta: conforto, durabilidade e uso no dia a dia pesam tanto quanto o valor.",
    },
    {
        "title": "{a} vs {b}: qual da mais valor ao seu dinheiro?",
        "summary": "Olhamos os dois com cuidado: onde um vai melhor que o outro e para qual perfil cada um faz mais sentido.",
    },
]


def parse_price(text: str) -> Optional[float]:
    try:
        cleaned = re.sub(r"[^\d,]", "", text).replace(",", ".")
        return float(cleaned)
    except Exception:
        return None


def normalize_image_url(candidate: Optional[str], base_url: str) -> Optional[str]:
    if not candidate:
        return None

    image_url = candidate.split()[0].strip()
    if not image_url or image_url.startswith("data:"):
        return None

    return urljoin(base_url, image_url)


def extract_image_from_affiliate_link(url: Optional[str]) -> Optional[str]:
    if not url:
        return None

    parsed = urlparse(url)
    if parsed.netloc.endswith("amazon.com.br") and parsed.path.startswith("/s"):
        return None
    if "magazinevoce.com.br" in parsed.netloc and "/busca/" in parsed.path:
        return None

    try:
        with httpx.Client(headers=HEADERS, timeout=12, follow_redirects=True) as client:
            response = client.get(url)
    except Exception as exc:
        logger.debug("Nao foi possivel buscar imagem do link %s: %s", url, exc)
        return None

    if response.status_code != 200:
        logger.debug("Link %s retornou status %s ao buscar imagem", url, response.status_code)
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    for selector in [
        "meta[property='og:image']",
        "meta[name='twitter:image']",
        "img#landingImage",
        "img.s-image",
        "img[data-testid='product-image']",
        "img[data-testid='image']",
        "img[src]",
    ]:
        element = soup.select_one(selector)
        if not element:
            continue

        candidate = (
            element.get("content")
            or element.get("data-old-hires")
            or element.get("data-src")
            or element.get("src")
            or element.get("srcset")
        )
        image_url = normalize_image_url(candidate, str(response.url))
        if image_url and not image_url.endswith(".gif"):
            return image_url

    return None


def build_fallback_deals_from_products(db: Session) -> list[dict]:
    products = db.query(Product).filter(Product.affiliate_url.isnot(None)).limit(60).all()
    fallback_deals = []

    for product in products:
        deal_price = parse_price(product.price or "")
        if not deal_price:
            continue

        category = "tecnologia"
        if product.article and product.article.category:
            category = product.article.category.slug

        image_url = product.image_url or extract_image_from_affiliate_link(product.affiliate_url)
        if image_url and product.image_url != image_url:
            product.image_url = image_url

        fallback_deals.append(
            {
                "product_name": product.name[:290],
                "original_price": deal_price,
                "deal_price": deal_price,
                "discount_pct": 0,
                "affiliate_url": product.affiliate_url,
                "source": product.source or product.store or "amazon",
                "category": category,
                "image_url": image_url,
            }
        )

    logger.info("%s ofertas fallback geradas a partir dos produtos indicados", len(fallback_deals))
    return fallback_deals


def fetch_amazon_deals(term: str, category: str) -> list[dict]:
    url = f"https://www.amazon.com.br/s?k={term.replace(' ', '+')}&tag={settings.AMAZON_TAG}"
    results = []
    try:
        with httpx.Client(headers=HEADERS, timeout=15, follow_redirects=True) as client:
            response = client.get(url)
        if response.status_code != 200:
            return results

        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.select("div[data-component-type='s-search-result']")

        for item in items[:8]:
            name_el = item.select_one("h2 span")
            price_el = item.select_one("span.a-price > span.a-offscreen")
            old_el = item.select_one("span.a-price.a-text-price > span.a-offscreen")
            link_el = item.select_one("h2 a")
            img_el = item.select_one("img.s-image")

            if not (name_el and price_el and link_el):
                continue

            new_price = parse_price(price_el.get_text())
            old_price = parse_price(old_el.get_text()) if old_el else None
            href = link_el.get("href", "")
            asin_match = re.search(r"/dp/([A-Z0-9]{10})", href)

            if not new_price or not asin_match:
                continue

            discount_pct = 0
            if old_price and old_price > new_price:
                discount_pct = int(((old_price - new_price) / old_price) * 100)

            if discount_pct >= 15 or (discount_pct == 0 and new_price < 300):
                asin = asin_match.group(1)
                results.append(
                    {
                        "product_name": name_el.get_text(strip=True)[:290],
                        "original_price": old_price or new_price,
                        "deal_price": new_price,
                        "discount_pct": discount_pct,
                        "affiliate_url": f"https://www.amazon.com.br/dp/{asin}?tag={settings.AMAZON_TAG}",
                        "source": "amazon",
                        "category": category,
                        "image_url": img_el.get("src", "") if img_el else "",
                    }
                )
    except Exception as exc:
        logger.error("Erro ao buscar Amazon [%s]: %s", term, exc)

    return results


def fetch_magalu_deals(term: str, category: str) -> list[dict]:
    configured_store = settings.MAGALU_STORE.strip("/")
    parsed_store = urlparse(configured_store)
    store = parsed_store.path.strip("/") if parsed_store.scheme else configured_store
    url = f"https://www.magazinevoce.com.br/{store}/busca/{term.replace(' ', '+')}/"
    results = []
    try:
        with httpx.Client(headers=HEADERS, timeout=15, follow_redirects=True) as client:
            response = client.get(url)
        if response.status_code != 200:
            return results

        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.select("li[data-testid='product-card']")

        for item in items[:6]:
            name_el = item.select_one("[data-testid='product-title']")
            price_el = item.select_one("[data-testid='price-value']")
            old_el = item.select_one("[data-testid='price-original']")
            link_el = item.select_one("a")
            img_el = item.select_one("img")

            if not (name_el and price_el and link_el):
                continue

            new_price = parse_price(price_el.get_text())
            old_price = parse_price(old_el.get_text()) if old_el else None
            if not new_price:
                continue

            href = link_el.get("href", "")
            affiliate_url = href if href.startswith("http") else f"https://www.magazinevoce.com.br{href}"

            discount_pct = 0
            if old_price and old_price > new_price:
                discount_pct = int(((old_price - new_price) / old_price) * 100)

            if discount_pct >= 15:
                results.append(
                    {
                        "product_name": name_el.get_text(strip=True)[:290],
                        "original_price": old_price or new_price,
                        "deal_price": new_price,
                        "discount_pct": discount_pct,
                        "affiliate_url": affiliate_url,
                        "source": "magalu",
                        "category": category,
                        "image_url": img_el.get("src", "") if img_el else "",
                    }
                )
    except Exception as exc:
        logger.error("Erro ao buscar Magalu [%s]: %s", term, exc)

    return results


def generate_comparisons(deals: list[dict]) -> list[dict]:
    by_category: dict[str, list[dict]] = {}
    for deal in deals:
        by_category.setdefault(deal["category"], []).append(deal)

    comparisons = []
    month = datetime.now().strftime("%m/%Y")

    for index, (category, items) in enumerate(by_category.items()):
        if len(items) < 2 or len(comparisons) >= 3:
            break

        product_a, product_b = items[0], items[1]
        template = COMPARISON_TEMPLATES[index % len(COMPARISON_TEMPLATES)]
        product_a_pros = (
            ["Boa opcao nessa faixa de preco", "Produto bem avaliado pelos compradores"]
            if product_a.get("discount_pct", 0) == 0
            else ["Melhor preco do dia", f"Economia de {product_a['discount_pct']}% em relacao ao preco cheio"]
        )
        comparisons.append(
            {
                "title": template["title"].format(
                    a=product_a["product_name"][:40],
                    b=product_b["product_name"][:40],
                    month=month,
                ),
                "summary": template["summary"],
                "category": category,
                "product_a": {
                    "name": product_a["product_name"],
                    "price": f"R$ {product_a['deal_price']:.2f}".replace(".", ","),
                    "affiliate_url": product_a["affiliate_url"],
                    "pros": product_a_pros,
                },
                "product_b": {
                    "name": product_b["product_name"],
                    "price": f"R$ {product_b['deal_price']:.2f}".replace(".", ","),
                    "affiliate_url": product_b["affiliate_url"],
                    "pros": ["Muito bem avaliado por quem ja comprou", "Boa alternativa para comparar antes de decidir"],
                },
            }
        )

    return comparisons


def run_daily_job(db: Session):
    logger.info("Iniciando robo diario do Meu Melhor Achado")
    today = date.today().strftime("%Y-%m-%d")
    run_id = datetime.now().strftime("%Y-%m-%d_%H:%M")
    scraper_log = None

    if settings.LOG_SCRAPER_RUNS:
        scraper_log = ScraperLog(run_id=run_id, status="running")
        db.add(scraper_log)
        db.commit()

    amazon_total = 0
    magalu_total = 0
    fallback_count = 0
    error_count = 0

    try:
        db.query(Deal).update({"is_active": False})
        db.commit()

        all_deals = []
        for category, term in SEARCH_TERMS:
            amazon_deals = fetch_amazon_deals(term, category)
            magalu_deals = fetch_magalu_deals(term, category)
            amazon_total += len(amazon_deals)
            magalu_total += len(magalu_deals)
            all_deals.extend(amazon_deals)
            all_deals.extend(magalu_deals)
            logger.info("%s: %s Amazon + %s Magalu", term, len(amazon_deals), len(magalu_deals))

        if not all_deals and settings.SCRAPER_FALLBACK_ENABLED:
            logger.info("Nenhuma oferta externa encontrada; usando fallback de produtos indicados")
            all_deals = build_fallback_deals_from_products(db)
            fallback_count = len(all_deals)

        if settings.SCRAPER_MAX_DEALS_PER_RUN > 0:
            all_deals = all_deals[: settings.SCRAPER_MAX_DEALS_PER_RUN]
            if fallback_count:
                fallback_count = min(fallback_count, len(all_deals))

        for deal_data in all_deals:
            db.add(Deal(**deal_data, is_active=True))
        db.commit()
        logger.info("%s ofertas salvas", len(all_deals))

        for deal_data in all_deals:
            db.add(
                PriceHistory(
                    product_name=deal_data["product_name"],
                    price=deal_data["deal_price"],
                    source=deal_data["source"],
                    category=deal_data["category"],
                    affiliate_url=deal_data["affiliate_url"],
                    scraper_run=run_id,
                )
            )
        db.commit()
        logger.info("%s precos registrados no historico (run: %s)", len(all_deals), run_id)

        comparisons = generate_comparisons(all_deals)
        for comparison in comparisons:
            db.add(
                DailyComparison(
                    date=today,
                    title=comparison["title"],
                    summary=comparison["summary"],
                    category=comparison["category"],
                    product_a=comparison["product_a"],
                    product_b=comparison["product_b"],
                )
            )
        db.commit()
        logger.info("%s comparativos gerados para %s", len(comparisons), today)

        if scraper_log:
            scraper_log.deals_found = len(all_deals)
            scraper_log.deals_published = len(all_deals)
            scraper_log.deals_fallback = fallback_count
            scraper_log.amazon_found = amazon_total
            scraper_log.magalu_found = magalu_total
            scraper_log.errors = error_count
            scraper_log.finished_at = datetime.now()
            scraper_log.status = "ok"
            db.commit()

        send_run_report(
            run_id=run_id,
            deals=all_deals,
            comparisons=comparisons,
            errors=error_count,
            fallback_count=fallback_count,
        )
    except Exception as exc:
        db.rollback()
        error_count = 1
        if scraper_log:
            scraper_log.finished_at = datetime.now()
            scraper_log.errors = error_count
            scraper_log.status = "error"
            scraper_log.notes = str(exc)[:1000]
            db.commit()
        raise
