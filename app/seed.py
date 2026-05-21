"""
Popula o banco com categorias e artigos iniciais (migração do mock-data).
Execute uma única vez após criar o banco:
  python -m app.seed
"""
from app.database import SessionLocal, engine, Base
from app.models import Category, Article, Product
from datetime import datetime

Base.metadata.create_all(bind=engine)

INITIAL_CATEGORIES = [
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

def sync_categories(db):
    for item in INITIAL_CATEGORIES:
        category = db.query(Category).filter(Category.slug == item["slug"]).first()
        if category:
            category.name = item["name"]
            category.description = item["description"]
            category.icon = item["icon"]
            category.color = item["color"]
        else:
            db.add(Category(**item))
    db.commit()

def seed():
    db = SessionLocal()
    try:
        if db.query(Category).count() > 0:
            sync_categories(db)
            print("Banco já populado. Categorias sincronizadas.")
            return

        # ── Categorias ────────────────────────────────────────────────────
        cats = [Category(**item) for item in INITIAL_CATEGORIES]
        for c in cats:
            db.add(c)
        db.flush()

        tech = next(c for c in cats if c.slug == "tecnologia")

        # ── Artigo 1 — Notebooks ─────────────────────────────────────────
        a1 = Article(
            slug="melhor-notebook-custo-beneficio-ate-3000",
            title="Melhor notebook custo-benefício até R$ 3.000",
            summary="Para quem precisa de um notebook confiável para trabalho, estudos e uso diário sem gastar além do necessário.",
            category_id=tech.id,
            published_at=datetime(2026, 5, 21),
            reading_time=7,
            image_url="https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&q=80",
            content_sections=[
                {"type": "intro", "text": "Escolher um notebook até R$ 3.000 exige atenção aos detalhes certos. Nessa faixa de preço, você já encontra máquinas com processador moderno, memória RAM suficiente e armazenamento em SSD — que faz toda a diferença na velocidade do dia a dia."},
                {"type": "criteria", "title": "O que olhar antes de comprar", "items": [
                    "Processador: AMD Ryzen 5 ou Intel Core i5 de última geração",
                    "RAM: 8 GB funciona, 16 GB é o ideal",
                    "Armazenamento: SSD é obrigatório",
                    "Tela: 15,6\" Full HD sem negociação",
                    "Bateria: acima de 40Wh",
                ]},
            ],
            is_auto=False, is_featured=False, is_offer=False, active=True,
        )
        db.add(a1)
        db.flush()
        db.add_all([
            Product(article_id=a1.id, name="Acer Aspire 5 (A515-45)",
                    summary="AMD Ryzen 5 5500U, 8 GB RAM, SSD 512 GB, tela 15,6\" Full HD.",
                    pros=["AMD Ryzen 5 eficiente", "SSD 512 GB", "Full HD", "Custo-benefício imbatível"],
                    cons=["Acabamento plástico", "Webcam mediana"],
                    affiliate_url="https://www.amazon.com.br/s?k=Acer+Aspire+5+A515+Ryzen+5&tag=meumelhoracha-20",
                    price="R$ 2.399", badge="Melhor Custo-Benefício", store="amazon"),
            Product(article_id=a1.id, name="Lenovo IdeaPad 3i (Core i5)",
                    summary="Intel Core i5-1235U, 8 GB RAM, SSD 256 GB, tela 15,6\" Full HD.",
                    pros=["Design slim e leve", "Teclado retroiluminado", "Boa bateria"],
                    cons=["SSD de 256 GB", "Placa de vídeo integrada"],
                    affiliate_url="https://www.amazon.com.br/s?k=Lenovo+IdeaPad+3i+Core+i5&tag=meumelhoracha-20",
                    price="R$ 2.699", badge="Melhor para Mobilidade", store="amazon"),
            Product(article_id=a1.id, name="Samsung Galaxy Book4",
                    summary="Intel Core i5-1335U, 8 GB RAM, SSD 256 GB, construção em alumínio.",
                    pros=["Alumínio resistente", "Tela excelente", "Integração Samsung"],
                    cons=["O mais caro dos três", "SSD 256 GB"],
                    affiliate_url="https://www.amazon.com.br/s?k=Samsung+Galaxy+Book4&tag=meumelhoracha-20",
                    price="R$ 2.899", badge="Mais Premium", store="amazon"),
        ])

        # ── Artigo 2 — Fone Bluetooth ────────────────────────────────────
        a2 = Article(
            slug="melhor-fone-bluetooth-ate-300",
            title="Melhor fone de ouvido Bluetooth até R$ 300",
            summary="Nessa faixa de preço você já consegue qualidade de som real, cancelamento de ruído e bateria para um dia inteiro.",
            category_id=tech.id,
            published_at=datetime(2026, 5, 21),
            reading_time=5,
            image_url="https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&q=80",
            content_sections=[
                {"type": "intro", "text": "O mercado de fones Bluetooth explodiu nos últimos anos e hoje é possível ter qualidade muito boa sem gastar fortunas."},
                {"type": "criteria", "title": "O que importa nessa categoria", "items": [
                    "Tipo: over-ear tem melhor isolamento; in-ear é mais prático",
                    "Cancelamento de ruído ativo (ANC): útil para home office",
                    "Bateria: mínimo de 20h para uso diário",
                    "Microfone: essencial para chamadas de trabalho",
                ]},
            ],
            is_auto=False, is_featured=False, is_offer=False, active=True,
        )
        db.add(a2)
        db.flush()
        db.add_all([
            Product(article_id=a2.id, name="JBL Tune 510BT",
                    summary="Over-ear com 40h de bateria, som JBL Signature Sound, dobrável e leve.",
                    pros=["40h de bateria", "Som equilibrado", "Dobrável"],
                    cons=["Sem ANC", "Microfone mediano"],
                    affiliate_url="https://www.amazon.com.br/s?k=JBL+Tune+510BT&tag=meumelhoracha-20",
                    price="R$ 199", badge="Melhor Custo-Benefício", store="amazon"),
            Product(article_id=a2.id, name="Anker Soundcore Q20i",
                    summary="Over-ear com ANC, 40h de bateria e hi-res audio.",
                    pros=["ANC funcional", "40h com ANC", "Hi-res Audio"],
                    cons=["Marca menos conhecida", "ANC não é o mais potente"],
                    affiliate_url="https://www.amazon.com.br/s?k=Anker+Soundcore+Q20i&tag=meumelhoracha-20",
                    price="R$ 249", badge="Melhor com ANC", store="amazon"),
            Product(article_id=a2.id, name="Xiaomi Redmi Buds 5 Pro",
                    summary="In-ear com ANC de até 46dB e 38h de bateria com case.",
                    pros=["ANC potente (46dB)", "Som excelente", "38h total"],
                    cons=["In-ear menos isolante", "App só Android"],
                    affiliate_url="https://www.amazon.com.br/s?k=Xiaomi+Redmi+Buds+5+Pro&tag=meumelhoracha-20",
                    price="R$ 279", badge="Melhor In-ear", store="amazon"),
        ])

        # ── Artigo 3 — Power Bank ─────────────────────────────────────────
        a3 = Article(
            slug="melhor-power-bank-carregador-portatil",
            title="Melhor carregador portátil (power bank) para celular",
            summary="Um bom power bank resolve a bateria na hora errada — e não precisa custar caro.",
            category_id=tech.id,
            published_at=datetime(2026, 5, 21),
            reading_time=5,
            image_url="https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=800&q=80",
            content_sections=[
                {"type": "intro", "text": "Power bank é daqueles produtos que você só valoriza quando precisa. A escolha certa é compacta, carrega rápido e dura anos."},
                {"type": "criteria", "title": "Como escolher o seu", "items": [
                    "Capacidade: 10.000 mAh carrega um celular 2-3 vezes",
                    "Potência de saída: mínimo 18W para carga rápida",
                    "Peso: 10.000 mAh fica em torno de 200g",
                ]},
            ],
            is_auto=False, is_featured=False, is_offer=False, active=True,
        )
        db.add(a3)
        db.flush()
        db.add_all([
            Product(article_id=a3.id, name="Xiaomi Power Bank 3 — 10.000 mAh",
                    summary="10.000 mAh, carga rápida 22,5W, saída USB-A e USB-C, 220g.",
                    pros=["Compacto e leve", "Carga rápida 22,5W", "Duas saídas"],
                    cons=["Sem display de porcentagem", "Apenas 10.000 mAh"],
                    affiliate_url="https://www.amazon.com.br/s?k=Xiaomi+Power+Bank+3+10000mAh&tag=meumelhoracha-20",
                    price="R$ 129", badge="Melhor Custo-Benefício", store="amazon"),
            Product(article_id=a3.id, name="Baseus Adaman 20.000 mAh",
                    summary="20.000 mAh, 65W de saída, display digital, 440g.",
                    pros=["65W carrega notebook", "Display digital", "20.000 mAh"],
                    cons=["Mais pesado (440g)", "Preço mais alto"],
                    affiliate_url="https://www.amazon.com.br/s?k=Baseus+Adaman+20000mAh+65W&tag=meumelhoracha-20",
                    price="R$ 219", badge="Melhor para Viagem", store="amazon"),
            Product(article_id=a3.id, name="Anker PowerCore Slim 10.000 mAh",
                    summary="10.000 mAh, formato slim, 20W, 180g. Cabe no bolso.",
                    pros=["O mais fino (180g)", "Cabe no bolso", "Acabamento premium"],
                    cons=["20W apenas", "Uma saída USB-C"],
                    affiliate_url="https://www.amazon.com.br/s?k=Anker+PowerCore+Slim+10000&tag=meumelhoracha-20",
                    price="R$ 169", badge="Mais Compacto", store="amazon"),
        ])

        db.commit()
        print("✅ Banco populado com sucesso!")

    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao popular banco: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed()
