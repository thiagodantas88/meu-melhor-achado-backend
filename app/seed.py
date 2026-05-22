"""
Seed idempotente para os dados editoriais iniciais do site.

Pode rodar no startup ou manualmente com:
  python -m app.seed
"""

from datetime import datetime

from app.database import SessionLocal
from app.migrations import ensure_database_schema
from app.models import Article, Category, ContentSection, Product

CATEGORIES = [
    {
        "slug": "tecnologia",
        "name": "Tecnologia",
        "description": "Celulares, notebooks, acessórios e tudo que conecta você ao mundo.",
        "icon": "💻",
        "color": "#1E3A5F",
    },
    {
        "slug": "casa",
        "name": "Casa",
        "description": "Eletrodomésticos, decoração e produtos que fazem a diferença no seu lar.",
        "icon": "🏠",
        "color": "#1E3A5F",
    },
    {
        "slug": "carro",
        "name": "Carro",
        "description": "Pneus, acessórios e produtos automotivos com custo-benefício real.",
        "icon": "🚗",
        "color": "#1E3A5F",
    },
    {
        "slug": "home-office",
        "name": "Home Office",
        "description": "Cadeiras, mesas, iluminação e tudo para trabalhar bem de casa.",
        "icon": "🖥️",
        "color": "#D4A373",
    },
    {
        "slug": "bebidas",
        "name": "Bebidas",
        "description": "Seleções de bebidas de melhor qualidade para apreciar, presentear e escolher bem.",
        "icon": "🍷",
        "color": "#1E3A5F",
    },
    {
        "slug": "moda",
        "name": "Moda",
        "description": "Moda feminina com achados elegantes, versáteis e bom custo-benefício.",
        "icon": "👗",
        "color": "#D4A373",
    },
]

ARTICLES = [
    {
        "slug": "melhor-notebook-custo-beneficio-ate-3000",
        "title": "Melhor notebook custo-benefício até R$ 3.000",
        "summary": "Para quem precisa de um notebook confiável para trabalho, estudos e uso diário sem gastar além do necessário.",
        "category_slug": "tecnologia",
        "published_at": datetime(2026, 5, 21),
        "reading_time": 7,
        "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&q=80",
        "sections": [
            {
                "type": "intro",
                "text": "Escolher um notebook até R$ 3.000 exige atenção aos detalhes certos. Nessa faixa de preço, você já encontra máquinas com processador moderno, memória RAM suficiente e armazenamento em SSD, que faz toda a diferença na velocidade do dia a dia.",
                "order": 0,
            },
            {
                "type": "criteria",
                "title": "O que olhar antes de comprar",
                "items": [
                    "Processador: AMD Ryzen 5 ou Intel Core i5 de última geração",
                    "RAM: 8 GB funciona, 16 GB é o ideal",
                    "Armazenamento: SSD é obrigatório",
                    "Tela: 15,6 polegadas Full HD",
                    "Bateria: acima de 40Wh",
                ],
                "order": 1,
            },
            {
                "type": "text",
                "text": "Com base nesses critérios, avaliamos modelos disponíveis nas principais lojas brasileiras e chegamos a três indicações claras.",
                "order": 2,
            },
        ],
        "products": [
            {
                "name": "Acer Aspire 5 (A515-45)",
                "summary": "AMD Ryzen 5 5500U, 8 GB RAM, SSD 512 GB, tela 15,6 polegadas Full HD.",
                "pros": ["AMD Ryzen 5 eficiente", "SSD 512 GB", "Tela Full HD", "Custo-benefício forte"],
                "cons": ["Acabamento plástico", "Webcam mediana"],
                "affiliate_url": "https://www.amazon.com.br/s?k=Acer+Aspire+5+A515+Ryzen+5&tag=meumelhoracha-20",
                "price": "R$ 2.399",
                "badge": "Melhor Custo-Benefício",
                "source": "amazon",
            },
            {
                "name": "Lenovo IdeaPad 3i (Core i5)",
                "summary": "Intel Core i5-1235U, 8 GB RAM, SSD 256 GB, tela 15,6 polegadas Full HD.",
                "pros": ["Design slim e leve", "Processador Intel eficiente", "Boa bateria"],
                "cons": ["SSD de 256 GB", "Vídeo integrado"],
                "affiliate_url": "https://www.amazon.com.br/s?k=Lenovo+IdeaPad+3i+Core+i5&tag=meumelhoracha-20",
                "price": "R$ 2.699",
                "badge": "Melhor para Mobilidade",
                "source": "amazon",
            },
            {
                "name": "Samsung Galaxy Book4",
                "summary": "Intel Core i5-1335U, 8 GB RAM, SSD 256 GB, construção em alumínio.",
                "pros": ["Construção em alumínio", "Tela de boa qualidade", "Integração Samsung"],
                "cons": ["Mais caro", "SSD de 256 GB"],
                "affiliate_url": "https://www.amazon.com.br/s?k=Samsung+Galaxy+Book4&tag=meumelhoracha-20",
                "price": "R$ 2.899",
                "badge": "Mais Premium",
                "source": "amazon",
            },
        ],
    },
    {
        "slug": "melhor-fone-bluetooth-ate-300",
        "title": "Melhor fone de ouvido Bluetooth até R$ 300",
        "summary": "Qualidade de som real, cancelamento de ruído e bateria para um dia inteiro.",
        "category_slug": "tecnologia",
        "published_at": datetime(2026, 5, 21),
        "reading_time": 5,
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&q=80",
        "sections": [
            {
                "type": "intro",
                "text": "O mercado de fones Bluetooth evoluiu bastante e hoje é possível ter qualidade muito boa sem gastar fortunas.",
                "order": 0,
            },
            {
                "type": "criteria",
                "title": "O que importa nessa categoria",
                "items": [
                    "Tipo: over-ear isola melhor; in-ear é mais prático",
                    "Cancelamento de ruído ativo ajuda em home office e transporte",
                    "Bateria: mínimo de 20h para uso diário",
                    "Microfone: essencial para chamadas",
                ],
                "order": 1,
            },
        ],
        "products": [
            {
                "name": "JBL Tune 510BT",
                "summary": "Over-ear com 40h de bateria, som JBL Signature Sound, dobrável e leve.",
                "pros": ["40h de bateria", "Som equilibrado", "Dobrável"],
                "cons": ["Sem ANC", "Microfone mediano"],
                "affiliate_url": "https://www.amazon.com.br/s?k=JBL+Tune+510BT&tag=meumelhoracha-20",
                "price": "R$ 199",
                "badge": "Melhor Custo-Benefício",
                "source": "amazon",
            },
            {
                "name": "Anker Soundcore Q20i",
                "summary": "Over-ear com ANC, 40h de bateria e hi-res audio.",
                "pros": ["ANC funcional", "40h com ANC", "Hi-res Audio"],
                "cons": ["Marca menos conhecida", "ANC não é o mais potente"],
                "affiliate_url": "https://www.amazon.com.br/s?k=Anker+Soundcore+Q20i&tag=meumelhoracha-20",
                "price": "R$ 249",
                "badge": "Melhor com ANC",
                "source": "amazon",
            },
            {
                "name": "Xiaomi Redmi Buds 5 Pro",
                "summary": "In-ear com ANC de até 46dB e 38h de bateria com case.",
                "pros": ["ANC potente", "Som excelente", "38h total"],
                "cons": ["In-ear isola menos", "App melhor no Android"],
                "affiliate_url": "https://www.magazinevoce.com.br/magazinemeumelhorachado/busca/Xiaomi+Redmi+Buds+5+Pro/",
                "price": "R$ 279",
                "badge": "Melhor In-ear",
                "source": "magalu",
            },
        ],
    },
    {
        "slug": "melhor-power-bank-carregador-portatil",
        "title": "Melhor carregador portátil (power bank) para celular",
        "summary": "Um bom power bank resolve a bateria na hora errada e não precisa custar caro.",
        "category_slug": "tecnologia",
        "published_at": datetime(2026, 5, 21),
        "reading_time": 5,
        "image_url": "https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=800&q=80",
        "sections": [
            {
                "type": "intro",
                "text": "Power bank é daqueles produtos que você só valoriza quando precisa. A escolha certa é compacta, carrega rápido e dura anos.",
                "order": 0,
            },
            {
                "type": "criteria",
                "title": "Como escolher o seu",
                "items": [
                    "Capacidade: 10.000 mAh carrega um celular duas ou três vezes",
                    "Potência de saída: mínimo 18W para carga rápida",
                    "Peso: 10.000 mAh costuma ficar perto de 200g",
                ],
                "order": 1,
            },
        ],
        "products": [
            {
                "name": "Xiaomi Power Bank 3 - 10.000 mAh",
                "summary": "10.000 mAh, carga rápida 22,5W, saída USB-A e USB-C.",
                "pros": ["Compacto e leve", "Carga rápida", "Duas saídas"],
                "cons": ["Sem display de porcentagem", "Apenas 10.000 mAh"],
                "affiliate_url": "https://www.amazon.com.br/s?k=Xiaomi+Power+Bank+3+10000mAh&tag=meumelhoracha-20",
                "price": "R$ 129",
                "badge": "Melhor Custo-Benefício",
                "source": "amazon",
            },
            {
                "name": "Baseus Adaman 20.000 mAh",
                "summary": "20.000 mAh, 65W de saída, display digital.",
                "pros": ["65W carrega notebook", "Display digital", "20.000 mAh"],
                "cons": ["Mais pesado", "Preço mais alto"],
                "affiliate_url": "https://www.amazon.com.br/s?k=Baseus+Adaman+20000mAh+65W&tag=meumelhoracha-20",
                "price": "R$ 219",
                "badge": "Melhor para Viagem",
                "source": "amazon",
            },
            {
                "name": "Anker PowerCore Slim 10.000 mAh",
                "summary": "10.000 mAh, formato slim, 20W. Cabe no bolso.",
                "pros": ["Fino e leve", "Cabe no bolso", "Acabamento premium"],
                "cons": ["20W apenas", "Uma saída USB-C"],
                "affiliate_url": "https://www.amazon.com.br/s?k=Anker+PowerCore+Slim+10000&tag=meumelhoracha-20",
                "price": "R$ 169",
                "badge": "Mais Compacto",
                "source": "amazon",
            },
        ],
    },
]


def _upsert_category(db, data):
    category = db.query(Category).filter(Category.slug == data["slug"]).first()
    if not category:
        category = Category(**data)
        db.add(category)
    else:
        for key, value in data.items():
            setattr(category, key, value)
    db.flush()
    return category


def _upsert_article(db, data, category_id):
    article_data = {
        key: value
        for key, value in data.items()
        if key not in {"category_slug", "sections", "products"}
    }
    article_data.update(
        {
            "category_id": category_id,
            "content_sections": data["sections"],
            "is_active": True,
            "active": True,
            "is_auto": False,
            "is_featured": False,
            "is_offer": False,
        }
    )

    article = db.query(Article).filter(Article.slug == article_data["slug"]).first()
    if not article:
        article = Article(**article_data)
        db.add(article)
    else:
        for key, value in article_data.items():
            setattr(article, key, value)
    db.flush()
    return article


def seed():
    ensure_database_schema()
    db = SessionLocal()
    try:
        category_ids = {}
        for category_data in CATEGORIES:
            category = _upsert_category(db, category_data)
            category_ids[category.slug] = category.id

        for article_data in ARTICLES:
            article = _upsert_article(db, article_data, category_ids[article_data["category_slug"]])

            db.query(ContentSection).filter(ContentSection.article_id == article.id).delete()
            for section_data in article_data["sections"]:
                db.add(ContentSection(**section_data, article_id=article.id))

            db.query(Product).filter(Product.article_id == article.id).delete()
            for product_data in article_data["products"]:
                source = product_data.get("source", "amazon")
                db.add(Product(**product_data, store=source, article_id=article.id))

        db.commit()
        print(f"Seed concluido: {len(CATEGORIES)} categorias, {len(ARTICLES)} artigos")
    except Exception as exc:
        db.rollback()
        print(f"Erro no seed: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
