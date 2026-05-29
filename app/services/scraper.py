# -*- coding: utf-8 -*-
import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

"""
Robô diário do Meu Melhor Achado.

Busca ofertas na Amazon e no Magalu, salva deals ativos e gera comparativos
simples para a API. O scraper falha de forma silenciosa por loja/termo para
não derrubar o backend caso uma página mude markup ou bloqueie a requisição.
"""

import logging
import re
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import urljoin, urlparse
from zoneinfo import ZoneInfo

import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Article, Category, ContentSection, DailyComparison, Deal, PriceHistory, Product, ScraperLog
from app.services.affiliate_links import is_product_affiliate_url
from app.services.notifier import send_run_report

logger = logging.getLogger(__name__)
PROJECT_TZ = ZoneInfo("America/Fortaleza")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Upgrade-Insecure-Requests": "1",
}

SEARCH_TERMS = [
    ("tecnologia", "fone de ouvido bluetooth"),
    ("tecnologia", "carregador usb-c"),
    ("tecnologia", "cabo usb-c"),
    ("tecnologia", "power bank"),
    ("casa", "air fryer"),
    ("casa", "air fryer mondial"),
    ("casa", "air fryer electrolux"),
    ("casa", "aspirador de po"),
    ("home-office", "mouse sem fio"),
    ("home-office", "teclado mecanico"),
    ("carro", "suporte celular carro"),
    ("carro", "carregador veicular"),
    ("bebidas", "vinho"),
    ("bebidas", "whisky"),
    ("bebidas", "cafe gourmet"),
    ("bebidas", "capsulas tres coracoes"),
    ("bebidas", "capsula cafe tres coracoes"),
    ("moda", "vestido feminino"),
    ("moda", "vestido midi feminino"),
    ("moda", "bolsa feminina"),
    ("moda", "bolsa feminina transversal"),
    ("moda", "tenis feminino casual"),
    ("moda", "calca jeans feminina"),
    ("moda", "blusa feminina"),
]

CATEGORY_ORDER = [
    "tecnologia",
    "casa",
    "carro",
    "home-office",
    "bebidas",
    "moda",
]

MAGALU_CAPTCHA_TERMS: set[str] = set()

COMPARISON_TEMPLATES = [
    {
        "title": "{a} ou {b}: qual compra faz mais sentido hoje?",
        "summary": "Comparamos preço, proposta de uso e pontos de atenção para ajudar você a decidir sem olhar apenas o desconto.",
    },
    {
        "title": "{a} vs {b}: veja antes de escolher",
        "summary": "Uma oferta pode parecer melhor no primeiro olhar, mas categoria, preço final e uso real mudam a decisão.",
    },
    {
        "title": "Comparativo rápido: {a} contra {b}",
        "summary": "Resumo objetivo para entender qual produto combina mais com rotina, presente, reposição ou compra urgente.",
    },
]

CATEGORY_COMPARISON_CONTEXT = {
    "bebidas": {
        "criteria": "Para bebidas, vale olhar volume, perfil de sabor, ocasião de consumo e preço por litro.",
        "best_a": "Boa escolha para quem quer economizar sem sair da categoria pesquisada.",
        "best_b": "Alternativa interessante para comparar marca, volume e proposta antes de fechar.",
    },
    "casa": {
        "criteria": "Em casa, capacidade, potência, consumo e facilidade de limpeza pesam tanto quanto o desconto.",
        "best_a": "Faz sentido para quem prioriza preço e uso frequente na rotina.",
        "best_b": "Vale considerar se entregar mais capacidade, marca ou acabamento.",
    },
    "tecnologia": {
        "criteria": "Em tecnologia, compatibilidade, potência, garantia e avaliações devem vir antes do menor preço.",
        "best_a": "Boa opção para resolver a necessidade gastando menos.",
        "best_b": "Pode valer mais se tiver especificação superior ou marca mais confiável.",
    },
    "moda": {
        "criteria": "Na moda, material, conforto, tamanho e versatilidade importam mais do que foto bonita.",
        "best_a": "Boa opção para quem busca preço e uso casual.",
        "best_b": "Compare se o modelo combina melhor com sua rotina e guarda-roupa.",
    },
    "carro": {
        "criteria": "Para carro, compatibilidade, fixação, segurança e durabilidade são decisivos.",
        "best_a": "Indicado para quem quer resolver uma necessidade prática sem gastar muito.",
        "best_b": "Pode compensar se oferecer melhor construção ou ajuste.",
    },
    "home-office": {
        "criteria": "No home office, conforto, ergonomia e durabilidade precisam acompanhar o preço.",
        "best_a": "Boa escolha para melhorar a rotina com menor investimento.",
        "best_b": "Vale olhar se entrega mais conforto ou ajuste para uso prolongado.",
    },
}

ARTICLE_CATEGORY_CONTEXT = {
    "tecnologia": {
        "headline": "Achados de tecnologia de hoje: acessórios úteis para comprar com mais critério",
        "summary": "Selecionamos ofertas de tecnologia com foco em utilidade real, compatibilidade e preço atual.",
        "intro": "Tecnologia boa não é só a que aparece com maior desconto. O ideal é olhar compatibilidade, potência, avaliações e se o produto resolve uma necessidade clara da rotina.",
        "criteria_title": "O que observar antes de comprar",
        "criteria": [
            "Confirme se o acessório é compatível com seus aparelhos.",
            "Compare potência, conexão e garantia antes de decidir.",
            "Dê preferência a produtos com imagem e link direto de produto.",
            "Preço baixo ajuda, mas especificação errada costuma sair caro.",
        ],
        "closing": "Para comprar melhor, escolha primeiro o uso principal e depois compare preço, marca e avaliação.",
    },
    "casa": {
        "headline": "Achados para casa de hoje: itens práticos que merecem comparação",
        "summary": "Ofertas para casa escolhidas pensando em uso frequente, praticidade e custo-benefício.",
        "intro": "Produto para casa precisa funcionar bem no dia a dia. Antes de olhar só o desconto, vale comparar capacidade, facilidade de limpeza, consumo e espaço disponível.",
        "criteria_title": "Antes de levar para casa",
        "criteria": [
            "Veja se a capacidade combina com o tamanho da família.",
            "Confira potência, consumo e facilidade de limpeza.",
            "Compare o preço atual com o benefício prático do produto.",
            "Avalie se o item resolve um problema real da rotina.",
        ],
        "closing": "A melhor compra costuma ser a que reduz trabalho sem virar mais um objeto parado em casa.",
    },
    "carro": {
        "headline": "Achados para carro de hoje: acessórios para uma rotina mais prática",
        "summary": "Opções automotivas selecionadas por compatibilidade, utilidade e preço atual.",
        "intro": "No carro, segurança e compatibilidade vêm antes do impulso. Um suporte, carregador ou acessório precisa ficar firme, encaixar bem e aguentar uso constante.",
        "criteria_title": "Pontos que fazem diferença",
        "criteria": [
            "Confirme compatibilidade com o modelo do veículo e do celular.",
            "Observe fixação, material e facilidade de instalação.",
            "Evite escolher apenas pelo menor preço.",
            "Prefira produtos úteis para trajetos frequentes.",
        ],
        "closing": "Acessório automotivo bom é aquele que ajuda sem atrapalhar a direção nem a organização do carro.",
    },
    "home-office": {
        "headline": "Achados de home office de hoje: produtos para trabalhar melhor",
        "summary": "Itens para home office avaliados por conforto, produtividade e valor atual.",
        "intro": "No home office, pequenos itens podem mudar a rotina. Mouse, teclado, suporte e iluminação precisam combinar conforto, durabilidade e facilidade de uso.",
        "criteria_title": "Como escolher melhor",
        "criteria": [
            "Priorize ergonomia se o uso for diário.",
            "Veja dimensões, conexão e compatibilidade.",
            "Compare preço com durabilidade esperada.",
            "Escolha produtos que reduzam atrito no trabalho.",
        ],
        "closing": "Uma boa compra de home office deve deixar o trabalho mais fluido, não só a mesa mais bonita.",
    },
    "bebidas": {
        "headline": "Achados de bebidas de hoje: opções para escolher com mais confiança",
        "summary": "Bebidas selecionadas com atenção a marca, volume, ocasião de consumo e preço atual.",
        "intro": "Em bebidas, o valor não está apenas no preço. Volume, marca, ocasião e perfil de sabor ajudam a entender se a oferta faz sentido para presente, reposição ou consumo casual.",
        "criteria_title": "O que comparar em bebidas",
        "criteria": [
            "Confira volume e preço por litro quando possível.",
            "Pense na ocasião: presente, reunião ou consumo cotidiano.",
            "Compare marca, tipo e proposta antes do clique.",
            "Lembre que preço e disponibilidade podem mudar rápido.",
        ],
        "closing": "A melhor escolha é a que combina preço atual com a ocasião certa de consumo.",
    },
    "moda": {
        "headline": "Achados de moda feminina de hoje: peças para comparar antes de comprar",
        "summary": "Seleção de moda feminina com foco em versatilidade, conforto e preço atual.",
        "intro": "Moda feminina com bom custo-benefício precisa ir além da foto. Material, modelagem, conforto e facilidade de combinar são pontos que aumentam a chance de usar a peça muitas vezes.",
        "criteria_title": "Antes de escolher a peça",
        "criteria": [
            "Confira material, modelagem e tabela de medidas.",
            "Pense se a peça combina com o que você já tem.",
            "Observe conforto e versatilidade para mais de uma ocasião.",
            "Compare o preço atual com a frequência de uso esperada.",
        ],
        "closing": "Peça boa é aquela que entra fácil na rotina, combina com vários looks e não fica esquecida no guarda-roupa.",
    },
}


def compact_product_name(name: str, max_chars: int = 46) -> str:
    normalized = re.sub(r"\s+", " ", name).strip()
    normalized = re.sub(r"\s[-–—]\s.*$", "", normalized)
    if len(normalized) > max_chars:
        prefix = re.split(r"\s(?:com|compatível|para)\s", normalized, maxsplit=1, flags=re.IGNORECASE)[0]
        if len(prefix) >= 18:
            normalized = prefix
    if len(normalized) <= max_chars:
        return normalized

    words = []
    current = 0
    for word in normalized.split():
        next_size = current + len(word) + (1 if words else 0)
        if next_size > max_chars:
            break
        words.append(word)
        current = next_size

    return " ".join(words) or normalized[:max_chars].rstrip()


def parse_price(text: str) -> Optional[float]:
    try:
        cleaned = re.sub(r"[^\d,.]", "", str(text or "").strip())
        if not cleaned:
            return None

        if "," in cleaned:
            cleaned = cleaned.replace(".", "").replace(",", ".")

        return float(cleaned)
    except Exception:
        return None


def format_price(value: float) -> str:
    """Formata float para padrão brasileiro: R$ 1.299,90."""
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


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
            return name[:290]

    return None


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
        if not is_product_affiliate_url(product.affiliate_url):
            continue

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
            logger.warning("Amazon [%s] retornou status %s em %s", term, response.status_code, url)
            return results

        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.select("div[data-component-type='s-search-result']")

        for item in items[:8]:
            price_el = item.select_one("span.a-price > span.a-offscreen")
            old_el = item.select_one("span.a-price.a-text-price > span.a-offscreen")
            link_el = item.select_one("a.a-text-normal[href]") or item.select_one("h2 a")
            img_el = item.select_one("img.s-image")
            product_name = extract_amazon_product_name(item)

            if not (product_name and price_el):
                continue

            new_price = parse_price(price_el.get_text())
            old_price = parse_price(old_el.get_text()) if old_el else None
            href = link_el.get("href", "") if link_el else ""
            asin = item.get("data-asin") or ""
            asin_match = re.search(r"/dp/([A-Z0-9]{10})", href) if href else None

            if not asin and asin_match:
                asin = asin_match.group(1)
            if not new_price or not asin:
                continue

            discount_pct = 0
            if old_price and old_price > new_price:
                discount_pct = int(((old_price - new_price) / old_price) * 100)

            if discount_pct >= 15 or (discount_pct == 0 and new_price < 300):
                results.append(
                    {
                        "product_name": product_name,
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
            logger.warning("Magalu [%s] retornou status %s em %s", term, response.status_code, url)
            return results

        if "Captcha Magalu" in response.text:
            MAGALU_CAPTCHA_TERMS.add(term)
            logger.warning("Magalu [%s] retornou captcha; fonte ignorada nesta rodada", term)
            return results

        soup = BeautifulSoup(response.text, "html.parser")
        next_data = soup.find("script", id="__NEXT_DATA__")
        if next_data and next_data.string:
            payload = json.loads(next_data.string)
            products = (
                payload.get("props", {})
                .get("pageProps", {})
                .get("data", {})
                .get("search", {})
                .get("products", [])
            )

            for product in products[:12]:
                name = (product.get("title") or "").strip()
                price = product.get("price") or {}
                deal_price = parse_price(str(price.get("bestPrice") or price.get("fullPrice") or price.get("price") or ""))
                original_price = parse_price(str(price.get("price") or price.get("fullPrice") or ""))
                path = product.get("url") or product.get("path") or ""

                if not (is_descriptive_product_name(name) and deal_price and path):
                    continue

                discount_pct = 0
                seller_tags = product.get("seller", {}).get("tags") or []
                for tag in seller_tags:
                    if tag.get("type") == "base_price" and tag.get("discountValue"):
                        discount_pct = int(float(tag["discountValue"]))
                        break

                if not discount_pct and original_price and original_price > deal_price:
                    discount_pct = int(((original_price - deal_price) / original_price) * 100)

                if discount_pct < 15 and deal_price >= 300:
                    continue

                image_url = product.get("image") or ""
                image_url = image_url.replace("{w}x{h}", "600x600")
                affiliate_url = path if path.startswith("http") else f"https://www.magazinevoce.com.br{path}"

                results.append(
                    {
                        "product_name": name[:290],
                        "original_price": original_price or deal_price,
                        "deal_price": deal_price,
                        "discount_pct": discount_pct,
                        "affiliate_url": affiliate_url,
                        "source": "magalu",
                        "category": category,
                        "image_url": image_url,
                    }
                )

            if not results:
                logger.info("Magalu [%s] sem ofertas validas nos dados estruturados", term)

            return results

        logger.info("Magalu [%s] sem __NEXT_DATA__; usando fallback HTML", term)
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
        context = CATEGORY_COMPARISON_CONTEXT.get(
            category,
            {
                "criteria": "Compare preço, marca, proposta de uso e confiabilidade antes de decidir.",
                "best_a": "Boa opção para quem quer aproveitar o preço atual.",
                "best_b": "Alternativa útil para validar se existe melhor encaixe para sua rotina.",
            },
        )
        price_gap = abs((product_a.get("deal_price") or 0) - (product_b.get("deal_price") or 0))
        cheaper = product_a if (product_a.get("deal_price") or 0) <= (product_b.get("deal_price") or 0) else product_b
        verdict = (
            f"Se a prioridade for pagar menos agora, {cheaper['product_name'][:80]} leva vantagem. "
            f"A diferença entre eles é de aproximadamente {format_price(price_gap)}, então vale conferir detalhes como marca, tamanho e avaliação antes do clique."
        )
        product_a_pros = (
            [context["best_a"], context["criteria"]]
            if product_a.get("discount_pct", 0) == 0
            else [
                f"Economia de {product_a['discount_pct']}% em relação ao preço cheio",
                context["best_a"],
            ]
        )
        product_b_pros = (
            [context["best_b"], context["criteria"]]
            if product_b.get("discount_pct", 0) == 0
            else [
                f"Economia de {product_b['discount_pct']}% em relação ao preço cheio",
                context["best_b"],
            ]
        )
        comparisons.append(
            {
                "title": template["title"].format(
                    a=compact_product_name(product_a["product_name"]),
                    b=compact_product_name(product_b["product_name"]),
                    month=month,
                ),
                "summary": template["summary"],
                "verdict": verdict,
                "criteria": context["criteria"],
                "category": category,
                "product_a": {
                    "name": product_a["product_name"],
                    "price": format_price(product_a["deal_price"]),
                    "affiliate_url": product_a["affiliate_url"],
                    "pros": product_a_pros,
                    "best_for": context["best_a"],
                },
                "product_b": {
                    "name": product_b["product_name"],
                    "price": format_price(product_b["deal_price"]),
                    "affiliate_url": product_b["affiliate_url"],
                    "pros": product_b_pros,
                    "best_for": context["best_b"],
                },
            }
        )

    return comparisons


def select_balanced_deals(deals: list[dict], max_deals: int) -> list[dict]:
    if max_deals <= 0 or len(deals) <= max_deals:
        return deals

    by_category: dict[str, list[dict]] = {}
    seen_urls = set()
    for deal in deals:
        affiliate_url = deal.get("affiliate_url")
        if affiliate_url in seen_urls:
            continue
        seen_urls.add(affiliate_url)
        by_category.setdefault(deal["category"], []).append(deal)

    for items in by_category.values():
        items.sort(
            key=lambda item: (
                item.get("discount_pct") or 0,
                -(item.get("deal_price") or 0),
            ),
            reverse=True,
        )

    categories = [category for category in CATEGORY_ORDER if by_category.get(category)]
    categories.extend(
        category
        for category in by_category
        if category not in categories
    )

    selected = []
    while len(selected) < max_deals and categories:
        next_categories = []
        for category in categories:
            items = by_category.get(category) or []
            if not items:
                continue

            selected.append(items.pop(0))
            if items:
                next_categories.append(category)
            if len(selected) >= max_deals:
                break

        categories = next_categories

    return selected


def slugify(value: str) -> str:
    accents = str.maketrans(
        "áàãâäéèêëíìîïóòõôöúùûüçñÁÀÃÂÄÉÈÊËÍÌÎÏÓÒÕÔÖÚÙÛÜÇÑ",
        "aaaaaeeeeiiiiooooouuuucnAAAAAEEEEIIIIOOOOOUUUUCN",
    )
    normalized = value.translate(accents).lower()
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    return normalized.strip("-") or "artigo"


def build_article_products(deals: list[dict]) -> list[Product]:
    products = []
    for index, deal in enumerate(deals[:3]):
        discount = int(deal.get("discount_pct") or 0)
        pros = [
            f"Preço atual: {format_price(deal['deal_price'])}",
            f"Link direto validado na {deal.get('source', 'loja').title()}",
        ]
        if discount > 0:
            pros.insert(1, f"Desconto informado de {discount}% em relação ao preço cheio")

        products.append(
            Product(
                name=deal["product_name"][:290],
                summary=(
                    "Boa alternativa para comparar dentro da categoria antes de decidir. "
                    "Confira medidas, avaliações e disponibilidade na página da loja."
                ),
                pros=pros,
                cons=[
                    "Preço e estoque podem mudar sem aviso.",
                    "Vale conferir avaliações recentes antes da compra.",
                ],
                affiliate_url=deal["affiliate_url"],
                image_url=deal.get("image_url"),
                price=format_price(deal["deal_price"]),
                original_price=format_price(deal.get("original_price") or deal["deal_price"]),
                discount_pct=discount,
                badge=["Maior desconto", "Mais barato", "Alternativa"][min(index, 2)],
                source=deal.get("source") or "amazon",
                store=deal.get("source") or "amazon",
                in_stock=True,
            )
        )
    return products


def build_editorial_sections(category: str, deals: list[dict]) -> list[ContentSection]:
    context = ARTICLE_CATEGORY_CONTEXT.get(category, ARTICLE_CATEGORY_CONTEXT["tecnologia"])
    product_lines = [
        f"{deal['product_name']} aparece por {format_price(deal['deal_price'])}"
        + (f" com {int(deal.get('discount_pct') or 0)}% de desconto." if deal.get("discount_pct") else ".")
        for deal in deals[:3]
    ]

    return [
        ContentSection(
            type="text",
            text=context["intro"],
            order=1,
        ),
        ContentSection(
            type="text",
            text=(
                "A seleção abaixo foi gerada a partir das ofertas ativas mais recentes do site. "
                "A ideia é trazer opções com preço atual, imagem de produto e link direto, evitando páginas genéricas de busca."
            ),
            order=2,
        ),
        ContentSection(
            type="criteria",
            title=context["criteria_title"],
            items=context["criteria"],
            order=3,
        ),
        ContentSection(
            type="criteria",
            title="Destaques encontrados agora",
            items=product_lines,
            order=4,
        ),
        ContentSection(
            type="text",
            text=context["closing"],
            order=5,
        ),
    ]


def should_refresh_editorial_articles(db: Session) -> bool:
    latest = (
        db.query(Article)
        .filter(Article.is_auto == True, Article.is_featured == True, Article.is_offer == False)
        .order_by(Article.published_at.desc())
        .first()
    )
    if not latest or not latest.published_at:
        return True

    return latest.published_at <= datetime.utcnow() - timedelta(days=2)


def generate_editorial_articles(db: Session, deals: list[dict], run_id: str, force: bool = False) -> int:
    if not force and not should_refresh_editorial_articles(db):
        return 0

    valid_deals = [
        deal
        for deal in deals
        if deal.get("image_url")
        and deal.get("affiliate_url")
        and deal.get("deal_price")
        and is_descriptive_product_name(deal.get("product_name") or "")
        and is_product_affiliate_url(deal.get("affiliate_url"))
    ]
    if not valid_deals:
        return 0

    categories = {category.slug: category for category in db.query(Category).all()}
    by_category: dict[str, list[dict]] = {}
    seen_urls = set()
    for deal in valid_deals:
        url = deal["affiliate_url"]
        if url in seen_urls:
            continue
        seen_urls.add(url)
        by_category.setdefault(deal["category"], []).append(deal)

    for items in by_category.values():
        items.sort(
            key=lambda item: (
                item.get("discount_pct") or 0,
                -(item.get("deal_price") or 0),
            ),
            reverse=True,
        )

    selected_categories = [
        category
        for category in CATEGORY_ORDER
        if category in categories and len(by_category.get(category, [])) >= 2
    ][:3]
    if not selected_categories:
        return 0

    db.query(Article).filter(
        Article.is_auto == True,
        Article.is_featured == True,
        Article.is_offer == False,
    ).update({"is_featured": False}, synchronize_session=False)

    created = 0
    published_at = datetime.utcnow()
    slug_suffix = published_at.strftime("%Y%m%d%H%M%S")
    for category in selected_categories:
        category_deals = by_category[category][:3]
        context = ARTICLE_CATEGORY_CONTEXT.get(category, ARTICLE_CATEGORY_CONTEXT["tecnologia"])
        slug = f"{slugify(context['headline'])}-{slug_suffix}-{created + 1}"

        article = Article(
            slug=slug[:200],
            title=context["headline"],
            summary=context["summary"],
            category_id=categories[category].id,
            published_at=published_at,
            reading_time=6,
            image_url=category_deals[0].get("image_url"),
            is_active=True,
            active=True,
            is_auto=True,
            is_offer=False,
            is_featured=True,
            sections=build_editorial_sections(category, category_deals),
            products=build_article_products(category_deals),
        )
        db.add(article)
        created += 1

    db.commit()
    logger.info("%s artigos editoriais gerados (run: %s)", created, run_id)
    return created


def save_deals(db: Session, deals: list[dict], run_id: str) -> int:
    saved = 0
    for deal_data in deals:
        existing = (
            db.query(Deal)
            .filter(Deal.affiliate_url == deal_data["affiliate_url"])
            .first()
        )
        if existing:
            for key, value in deal_data.items():
                setattr(existing, key, value)
            existing.is_active = True
        else:
            db.add(Deal(**deal_data, is_active=True))

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
        saved += 1

    db.commit()
    return saved


def run_category_terms(db: Session, category: str, terms: list[str]) -> dict:
    run_id = datetime.now(PROJECT_TZ).strftime("%Y-%m-%d_%H:%M")
    all_deals = []
    amazon_total = 0
    magalu_total = 0
    MAGALU_CAPTCHA_TERMS.clear()

    for term in terms:
        amazon_deals = fetch_amazon_deals(term, category)
        magalu_deals = fetch_magalu_deals(term, category)
        amazon_total += len(amazon_deals)
        magalu_total += len(magalu_deals)
        all_deals.extend(amazon_deals)
        all_deals.extend(magalu_deals)
        logger.info("Pontual %s/%s: %s Amazon + %s Magalu", category, term, len(amazon_deals), len(magalu_deals))

    saved = save_deals(db, all_deals, run_id)
    return {
        "runId": run_id,
        "category": category,
        "terms": terms,
        "amazonFound": amazon_total,
        "magaluFound": magalu_total,
        "dealsPublished": saved,
    }


def run_daily_job(db: Session):
    logger.info("Iniciando robo diario do Meu Melhor Achado")
    today = datetime.now(PROJECT_TZ).strftime("%Y-%m-%d")
    run_id = datetime.now(PROJECT_TZ).strftime("%Y-%m-%d_%H:%M")
    scraper_log = None
    MAGALU_CAPTCHA_TERMS.clear()

    if settings.LOG_SCRAPER_RUNS:
        scraper_log = ScraperLog(run_id=run_id, status="running")
        db.add(scraper_log)
        db.commit()

    amazon_total = 0
    magalu_total = 0
    fallback_count = 0
    error_count = 0
    article_count = 0

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
            all_deals = select_balanced_deals(all_deals, settings.SCRAPER_MAX_DEALS_PER_RUN)
            if fallback_count:
                fallback_count = min(fallback_count, len(all_deals))

        save_deals(db, all_deals, run_id)
        logger.info("%s ofertas salvas", len(all_deals))
        logger.info("%s precos registrados no historico (run: %s)", len(all_deals), run_id)

        article_count = generate_editorial_articles(db, all_deals, run_id)

        comparisons = generate_comparisons(all_deals)
        for comparison in comparisons:
            db.add(
                DailyComparison(
                    date=today,
                    title=comparison["title"],
                    summary=comparison["summary"],
                    verdict=comparison.get("verdict"),
                    criteria=comparison.get("criteria"),
                    category=comparison["category"],
                    product_a=comparison["product_a"],
                    product_b=comparison["product_b"],
                )
            )
        db.commit()
        logger.info("%s comparativos gerados para %s", len(comparisons), today)

        if scraper_log:
            notes = None
            if MAGALU_CAPTCHA_TERMS:
                notes = f"Magalu retornou captcha em {len(MAGALU_CAPTCHA_TERMS)} termos; fonte ignorada nesta rodada."
            if article_count:
                article_note = f"Artigos editoriais gerados: {article_count}."
                notes = f"{notes} {article_note}" if notes else article_note

            scraper_log.deals_found = len(all_deals)
            scraper_log.deals_published = len(all_deals)
            scraper_log.deals_fallback = fallback_count
            scraper_log.amazon_found = amazon_total
            scraper_log.magalu_found = magalu_total
            scraper_log.errors = error_count
            scraper_log.notes = notes
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
