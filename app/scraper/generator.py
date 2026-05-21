import re
import random
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import Article, Product, Category
from app.scraper.amazon import search_amazon, ScrapedProduct
from app.scraper.magalu import search_magalu, MagaluProduct

# ── Tópicos rotativos por categoria ─────────────────────────────────────────
DAILY_TOPICS = {
    "tecnologia": [
        ("Fone de ouvido Bluetooth", "melhor-fone-bluetooth", 5),
        ("Carregador portátil power bank", "melhor-power-bank", 4),
        ("Mouse sem fio", "melhor-mouse-sem-fio", 4),
        ("Teclado sem fio", "melhor-teclado-sem-fio", 4),
        ("Webcam para home office", "melhor-webcam-home-office", 5),
        ("SSD externo portátil", "melhor-ssd-externo", 5),
        ("Hub USB-C", "melhor-hub-usb-c", 4),
        ("Suporte para notebook", "melhor-suporte-notebook", 4),
        ("Cabo USB-C resistente", "melhor-cabo-usb-c", 3),
        ("Carregador USB-C GaN", "melhor-carregador-gan", 5),
    ],
    "casa": [
        ("Air fryer elétrica", "melhor-air-fryer", 6),
        ("Aspirador de pó robô", "melhor-aspirador-robo", 7),
        ("Chaleira elétrica", "melhor-chaleira-eletrica", 4),
        ("Fritadeira sem óleo", "melhor-fritadeira-sem-oleo", 6),
        ("Liquidificador potente", "melhor-liquidificador", 5),
        ("Cafeteira elétrica", "melhor-cafeteira", 5),
        ("Ventilador de torre", "melhor-ventilador-torre", 5),
        ("Umidificador de ar", "melhor-umidificador", 5),
    ],
    "home-office": [
        ("Cadeira ergonômica", "melhor-cadeira-ergonomica", 6),
        ("Mesa para computador", "melhor-mesa-computador", 5),
        ("Luminária de mesa LED", "melhor-luminaria-led", 4),
        ("Suporte monitor tela", "melhor-suporte-monitor", 4),
        ("Headset para reunião", "melhor-headset-reuniao", 5),
        ("Webcam Full HD", "melhor-webcam-fullhd", 5),
    ],
    "carro": [
        ("Suporte celular carro", "melhor-suporte-celular-carro", 3),
        ("Carregador veicular USB", "melhor-carregador-veicular", 3),
        ("Câmera ré carro", "melhor-camera-re", 5),
        ("Aspirador carro portátil", "melhor-aspirador-carro", 4),
    ],
}

def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[àáâãäå]", "a", text)
    text = re.sub(r"[èéêë]", "e", text)
    text = re.sub(r"[ìíîï]", "i", text)
    text = re.sub(r"[òóôõö]", "o", text)
    text = re.sub(r"[ùúûü]", "u", text)
    text = re.sub(r"[ç]", "c", text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")

def make_unique_slug(base_slug: str, db: Session) -> str:
    date_str = datetime.utcnow().strftime("%Y%m%d")
    slug = f"{base_slug}-{date_str}"
    count = db.query(Article).filter(Article.slug.like(f"{slug}%")).count()
    if count > 0:
        slug = f"{slug}-{count}"
    return slug

def extract_pros_cons(name: str, store: str) -> tuple:
    """Gera prós e contras genéricos baseados no produto."""
    pros = [
        f"Disponível com entrega rápida na {store.capitalize()}",
        "Boa avaliação dos compradores",
        "Custo-benefício competitivo",
    ]
    cons = [
        "Verifique disponibilidade de estoque",
        "Compare com outras ofertas antes de comprar",
    ]
    return pros, cons

async def generate_daily_comparatives(db: Session):
    """
    Roda todo dia às 6h.
    - Escolhe 3 tópicos aleatórios das categorias
    - Busca produtos na Amazon e Magalu
    - Salva como artigos featured no banco
    - Salva mais 2 artigos recentes
    - Salva produtos com desconto como ofertas
    """
    print(f"[Robô] Iniciando geração diária — {datetime.utcnow().isoformat()}")

    # Desativa os artigos automáticos do dia anterior
    db.query(Article).filter(
        Article.is_auto == True,
        Article.is_featured == True
    ).update({"is_featured": False, "active": False})
    db.commit()

    categories = db.query(Category).all()
    cat_map = {c.slug: c for c in categories}

    generated = 0

    # Seleciona tópicos aleatórios — 3 featured + 2 recentes
    all_topics = []
    for cat_slug, topics in DAILY_TOPICS.items():
        for topic in topics:
            all_topics.append((cat_slug, topic))

    random.shuffle(all_topics)
    selected = all_topics[:5]

    for i, (cat_slug, (query, base_slug, reading_time)) in enumerate(selected):
        is_featured = i < 3  # primeiros 3 vão para barra principal

        category = cat_map.get(cat_slug)
        if not category:
            continue

        # Busca na Amazon (primária) e Magalu (alternativa)
        amazon_products = await search_amazon(query, max_results=2)
        magalu_products = await search_magalu(query, max_results=1)

        if not amazon_products and not magalu_products:
            print(f"[Robô] Sem resultados para '{query}', pulando.")
            continue

        # Gera slug único para hoje
        slug = make_unique_slug(base_slug, db)

        # Título do artigo
        title = f"Melhor {query} — comparativo de hoje"

        # Resumo
        summary = (
            f"Comparamos as melhores opções de {query.lower()} disponíveis hoje "
            f"nas principais lojas do Brasil. Confira preços, prós e contras antes de comprar."
        )

        # Seções de conteúdo
        content_sections = [
            {
                "type": "intro",
                "text": (
                    f"Pesquisamos as melhores opções de {query.lower()} disponíveis agora "
                    f"na Amazon e no Magazine Luiza. Reunimos abaixo as indicações com melhor "
                    f"custo-benefício para você decidir sem perder tempo."
                ),
            }
        ]

        # Cria o artigo
        article = Article(
            slug=slug,
            title=title,
            summary=summary,
            category_id=category.id,
            published_at=datetime.utcnow(),
            reading_time=reading_time,
            content_sections=content_sections,
            is_auto=True,
            is_featured=is_featured,
            is_offer=False,
            active=True,
        )
        db.add(article)
        db.flush()

        # Adiciona produtos da Amazon
        for j, p in enumerate(amazon_products):
            pros, cons = extract_pros_cons(p.name, "amazon")
            badge = "Mais Vendido" if j == 0 else ("Melhor Custo-Benefício" if j == 1 else None)
            product = Product(
                article_id=article.id,
                name=p.name,
                summary=f"Disponível na Amazon com entrega rápida. {p.name}.",
                pros=pros,
                cons=cons,
                affiliate_url=p.url,
                image_url=p.image_url,
                price=p.price,
                original_price=p.original_price,
                discount_pct=p.discount_pct,
                badge=badge,
                store="amazon",
                in_stock=True,
            )
            db.add(product)

        # Adiciona produtos do Magalu
        for p in magalu_products:
            pros, cons = extract_pros_cons(p.name, "magalu")
            product = Product(
                article_id=article.id,
                name=p.name,
                summary=f"Disponível no Magazine Luiza. {p.name}.",
                pros=pros,
                cons=cons,
                affiliate_url=p.url,
                image_url=p.image_url,
                price=p.price,
                original_price=p.original_price,
                discount_pct=p.discount_pct,
                badge="Opção Magalu",
                store="magalu",
                in_stock=True,
            )
            db.add(product)

        db.commit()
        generated += 1
        print(f"[Robô] Artigo gerado: '{title}' (featured={is_featured})")

    # ── Gera ofertas do dia ──────────────────────────────────────────────
    await generate_daily_offers(db, cat_map)

    print(f"[Robô] Concluído. {generated} artigos gerados.")

async def generate_daily_offers(db: Session, cat_map: dict):
    """Busca produtos em promoção e salva na página /ofertas."""

    # Desativa ofertas do dia anterior
    db.query(Article).filter(
        Article.is_auto == True,
        Article.is_offer == True
    ).update({"active": False})
    db.commit()

    offer_queries = [
        ("notebook promoção", "tecnologia"),
        ("fone bluetooth oferta", "tecnologia"),
        ("air fryer promoção", "casa"),
        ("cadeira escritório desconto", "home-office"),
        ("carregador celular promoção", "tecnologia"),
    ]

    random.shuffle(offer_queries)

    for query, cat_slug in offer_queries[:4]:
        category = cat_map.get(cat_slug)
        if not category:
            continue

        products = await search_amazon(query, max_results=3)
        # Filtra apenas os que têm desconto real
        with_discount = [p for p in products if p.discount_pct and p.discount_pct >= 5]

        if not with_discount:
            continue

        slug = make_unique_slug(f"oferta-{slugify(query)}", db)

        article = Article(
            slug=slug,
            title=f"Oferta do dia: {query}",
            summary=f"Promoção encontrada agora. Desconto de até {max(p.discount_pct for p in with_discount):.0f}% — válido enquanto durar o estoque.",
            category_id=category.id,
            published_at=datetime.utcnow(),
            reading_time=2,
            content_sections=[],
            is_auto=True,
            is_featured=False,
            is_offer=True,
            active=True,
        )
        db.add(article)
        db.flush()

        for p in with_discount:
            pros, cons = extract_pros_cons(p.name, "amazon")
            db.add(Product(
                article_id=article.id,
                name=p.name,
                summary=f"Desconto de {p.discount_pct:.0f}% — de {p.original_price} por {p.price}.",
                pros=pros,
                cons=cons,
                affiliate_url=p.url,
                image_url=p.image_url,
                price=p.price,
                original_price=p.original_price,
                discount_pct=p.discount_pct,
                badge=f"{p.discount_pct:.0f}% OFF",
                store="amazon",
                in_stock=True,
            ))

        db.commit()
        print(f"[Robô] Oferta gerada: '{article.title}'")
