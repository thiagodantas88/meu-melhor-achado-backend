"""
Adiciona 10 artigos de cauda longa ao banco.

Pode rodar manualmente com:
  python3 add_articles_v2.py
"""

from datetime import datetime

from app.database import SessionLocal
from app.models import Article, Category, ContentSection, Product

AMAZON_TAG = "meumelhoracha-20"


def amazon_search(term: str) -> str:
    return f"https://www.amazon.com.br/s?k={term.replace(' ', '+')}&tag={AMAZON_TAG}"


NEW_ARTICLES_V2 = [
    {
        "slug": "melhor-air-fryer-para-casal",
        "title": "Melhor air fryer para casal: modelos compactos que valem a pena",
        "summary": "Air fryer para duas pessoas precisa ser prática, econômica e fácil de limpar. Veja modelos que entregam bom resultado sem ocupar a cozinha inteira.",
        "category_slug": "casa",
        "published_at": datetime(2026, 5, 24),
        "reading_time": 6,
        "image_url": "/articles/air-fryer-casal.svg",
        "sections": [
            {"type": "intro", "text": "Para casal, uma air fryer enorme nem sempre faz sentido. O ideal é equilibrar capacidade, potência e tamanho para preparar porções do dia a dia sem gastar energia à toa.", "order": 0},
            {"type": "criteria", "title": "O que observar", "items": ["Capacidade entre 3L e 4L atende bem duas pessoas", "Cesto antiaderente facilita a limpeza", "Potência acima de 1400W ajuda a dourar melhor", "Tamanho externo importa para cozinhas pequenas"], "order": 1},
            {"type": "text", "text": "Selecionamos opções para quem quer praticidade na rotina, sem abrir mão de batata crocante, frango bem assado e legumes rápidos.", "order": 2},
        ],
        "products": [
            {"name": "Air Fryer Mondial Family 4L", "summary": "Boa capacidade para casal que cozinha sobras ou porções maiores no fim de semana.", "pros": ["Capacidade versátil", "Preço competitivo", "Fácil de encontrar"], "cons": ["Ocupa mais espaço que modelos 3L"], "affiliate_url": amazon_search("Air Fryer Mondial Family 4L"), "price": "R$ 299", "badge": "Melhor Custo-Benefício", "source": "amazon"},
            {"name": "Air Fryer Philips Walita Série 3000", "summary": "Modelo mais refinado, com construção consistente e bom controle de temperatura.", "pros": ["Acabamento superior", "Boa distribuição de calor", "Marca confiável"], "cons": ["Preço mais alto"], "affiliate_url": amazon_search("Air Fryer Philips Walita Serie 3000"), "price": "R$ 529", "badge": "Mais Premium", "source": "amazon"},
            {"name": "Air Fryer Oster Compacta", "summary": "Boa escolha para cozinha pequena, com uso simples e visual discreto.", "pros": ["Compacta", "Design discreto", "Boa para uso diário"], "cons": ["Cesto menor"], "affiliate_url": amazon_search("Air Fryer Oster Compacta"), "price": "R$ 349", "badge": "Mais Compacta", "source": "amazon"},
        ],
    },
    {
        "slug": "melhor-jogo-de-panelas-antiaderente",
        "title": "Melhor jogo de panelas antiaderente para o dia a dia",
        "summary": "Um bom jogo de panelas precisa aquecer bem, limpar fácil e durar mais do que poucos meses. Veja o que vale observar antes de comprar.",
        "category_slug": "casa",
        "published_at": datetime(2026, 5, 24),
        "reading_time": 6,
        "image_url": "/articles/jogo-panelas-antiaderente.svg",
        "sections": [
            {"type": "intro", "text": "Panelas antiaderentes são ótimas para a rotina, mas variam muito em espessura, revestimento e durabilidade. Comprar só pela quantidade de peças pode sair caro.", "order": 0},
            {"type": "criteria", "title": "Critérios de escolha", "items": ["Fundo mais grosso distribui melhor o calor", "Cabos firmes aumentam segurança", "Tampas de vidro ajudam no controle do preparo", "Compatibilidade com fogão por indução pode ser decisiva"], "order": 1},
            {"type": "text", "text": "A melhor escolha depende do tamanho da família e da frequência de uso, mas alguns conjuntos entregam equilíbrio melhor para a maioria das cozinhas.", "order": 2},
        ],
        "products": [
            {"name": "Tramontina Turim Jogo de Panelas", "summary": "Conjunto popular, honesto e suficiente para montar uma cozinha básica.", "pros": ["Bom preço", "Marca conhecida", "Peças leves"], "cons": ["Revestimento exige cuidado"], "affiliate_url": amazon_search("Tramontina Turim jogo de panelas antiaderente"), "price": "R$ 239", "badge": "Melhor Básico", "source": "amazon"},
            {"name": "Brinox Ceramic Life", "summary": "Opção com visual bonito e revestimento cerâmico para quem quer algo mais caprichado.", "pros": ["Revestimento cerâmico", "Visual elegante", "Boa variedade de peças"], "cons": ["Mais caro"], "affiliate_url": amazon_search("Brinox Ceramic Life jogo de panelas"), "price": "R$ 399", "badge": "Mais Elegante", "source": "amazon"},
            {"name": "Panelux Magnific Grafite", "summary": "Alternativa intermediária para quem quer conjunto completo sem subir muito o orçamento.", "pros": ["Preço equilibrado", "Boa quantidade de peças", "Uso simples"], "cons": ["Acabamento básico"], "affiliate_url": amazon_search("Panelux Magnific jogo de panelas grafite"), "price": "R$ 289", "badge": "Intermediário", "source": "amazon"},
        ],
    },
    {
        "slug": "melhor-tenis-branco-feminino-confortavel",
        "title": "Melhor tênis branco feminino confortável para usar todo dia",
        "summary": "Tênis branco combina com quase tudo, mas precisa ser confortável de verdade. Veja opções para rotina, trabalho e looks casuais.",
        "category_slug": "moda",
        "published_at": datetime(2026, 5, 24),
        "reading_time": 5,
        "image_url": "/articles/tenis-branco-feminino.svg",
        "sections": [
            {"type": "intro", "text": "O tênis branco feminino virou peça coringa: vai com jeans, vestido, alfaiataria leve e looks de viagem. O segredo é escolher um modelo confortável e fácil de limpar.", "order": 0},
            {"type": "criteria", "title": "Antes de comprar", "items": ["Palmilha macia faz diferença no uso prolongado", "Solado antiderrapante ajuda na rotina", "Material sintético costuma limpar mais fácil", "Forma pode variar muito por marca"], "order": 1},
            {"type": "text", "text": "Para usar todo dia, vale priorizar conforto e versatilidade em vez de escolher apenas pelo visual.", "order": 2},
        ],
        "products": [
            {"name": "Tênis Branco Casual Vizzano", "summary": "Modelo casual, fácil de combinar e com preço acessível.", "pros": ["Visual versátil", "Bom preço", "Fácil de combinar"], "cons": ["Conforto depende da forma"], "affiliate_url": amazon_search("tenis branco feminino Vizzano casual"), "price": "R$ 149", "badge": "Mais Versátil", "source": "amazon"},
            {"name": "Tênis Branco Via Marte", "summary": "Boa alternativa para looks casuais arrumados e uso em passeio.", "pros": ["Acabamento bonito", "Boa presença no look", "Marca conhecida"], "cons": ["Pode exigir amaciamento"], "affiliate_url": amazon_search("tenis branco feminino Via Marte"), "price": "R$ 189", "badge": "Mais Arrumado", "source": "amazon"},
            {"name": "Tênis Branco Beira Rio Conforto", "summary": "Foco em conforto e rotina, ideal para quem passa mais tempo em pé.", "pros": ["Confortável", "Leve", "Bom para rotina"], "cons": ["Design mais simples"], "affiliate_url": amazon_search("tenis branco feminino Beira Rio conforto"), "price": "R$ 139", "badge": "Mais Confortável", "source": "amazon"},
        ],
    },
    {
        "slug": "melhor-bolsa-feminina-para-trabalho",
        "title": "Melhor bolsa feminina para o trabalho: prática e elegante",
        "summary": "Bolsa para trabalho precisa carregar o essencial sem perder elegância. Veja modelos úteis para notebook, documentos e rotina.",
        "category_slug": "moda",
        "published_at": datetime(2026, 5, 24),
        "reading_time": 5,
        "image_url": "/articles/bolsa-feminina-trabalho.svg",
        "sections": [
            {"type": "intro", "text": "A bolsa ideal para trabalho precisa caber na rotina: celular, carteira, nécessaire, documentos e, em alguns casos, notebook. Beleza sozinha não resolve.", "order": 0},
            {"type": "criteria", "title": "O que importa", "items": ["Alça reforçada aumenta durabilidade", "Divisórias ajudam na organização", "Cores neutras combinam com mais looks", "Tamanho precisa acompanhar sua rotina real"], "order": 1},
            {"type": "text", "text": "A melhor escolha é aquela que organiza bem sem parecer uma mala. Modelos estruturados costumam funcionar melhor para trabalho.", "order": 2},
        ],
        "products": [
            {"name": "Bolsa Tote Feminina Estruturada", "summary": "Boa opção para quem leva documentos e quer visual mais profissional.", "pros": ["Cabe bastante coisa", "Visual elegante", "Combina com trabalho"], "cons": ["Pode ficar pesada"], "affiliate_url": amazon_search("bolsa tote feminina estruturada trabalho"), "price": "R$ 169", "badge": "Melhor para Trabalho", "source": "amazon"},
            {"name": "Bolsa Feminina para Notebook", "summary": "Ideal para quem precisa carregar notebook com mais proteção.", "pros": ["Espaço para notebook", "Mais organizada", "Boa para escritório"], "cons": ["Menos casual"], "affiliate_url": amazon_search("bolsa feminina notebook trabalho"), "price": "R$ 219", "badge": "Para Notebook", "source": "amazon"},
            {"name": "Bolsa Transversal Feminina Média", "summary": "Mais leve e prática para quem não carrega notebook todos os dias.", "pros": ["Mãos livres", "Leve", "Boa para rotina"], "cons": ["Menor capacidade"], "affiliate_url": amazon_search("bolsa transversal feminina media trabalho"), "price": "R$ 119", "badge": "Mais Prática", "source": "amazon"},
        ],
    },
    {
        "slug": "melhor-cadeira-escritorio-para-dor-nas-costas",
        "title": "Melhor cadeira de escritório para dor nas costas",
        "summary": "Quem passa horas sentado precisa de apoio real. Veja o que observar em uma cadeira para trabalhar com mais conforto.",
        "category_slug": "home-office",
        "published_at": datetime(2026, 5, 24),
        "reading_time": 7,
        "image_url": "/articles/cadeira-escritorio-costas.svg",
        "sections": [
            {"type": "intro", "text": "Dor nas costas no home office costuma vir de postura ruim, cadeira sem apoio e muitas horas sem pausa. Uma boa cadeira não faz milagre, mas muda bastante a rotina.", "order": 0},
            {"type": "criteria", "title": "Pontos essenciais", "items": ["Apoio lombar ajustável é prioridade", "Altura regulável ajuda a alinhar braços e mesa", "Assento com boa espuma evita desconforto", "Encosto respirável ajuda em dias quentes"], "order": 1},
            {"type": "text", "text": "Para quem sente dor, vale evitar cadeiras gamer muito inclinadas e priorizar ergonomia de verdade.", "order": 2},
        ],
        "products": [
            {"name": "Cadeira Presidente Ergonômica", "summary": "Boa para quem quer encosto alto e apoio mais completo.", "pros": ["Encosto alto", "Apoio de braços", "Boa presença"], "cons": ["Ocupa mais espaço"], "affiliate_url": amazon_search("cadeira presidente ergonomica apoio lombar"), "price": "R$ 599", "badge": "Mais Completa", "source": "amazon"},
            {"name": "Cadeira Tela Mesh com Apoio Lombar", "summary": "Modelo respirável e prático para longas jornadas.", "pros": ["Encosto ventilado", "Apoio lombar", "Boa para calor"], "cons": ["Visual mais simples"], "affiliate_url": amazon_search("cadeira escritorio mesh apoio lombar"), "price": "R$ 429", "badge": "Melhor para Rotina", "source": "amazon"},
            {"name": "Cadeira Ergonômica Compacta", "summary": "Alternativa para espaços pequenos sem abrir mão de ajustes básicos.", "pros": ["Compacta", "Altura regulável", "Boa para apartamentos"], "cons": ["Menos recursos premium"], "affiliate_url": amazon_search("cadeira ergonomica compacta escritorio"), "price": "R$ 329", "badge": "Mais Compacta", "source": "amazon"},
        ],
    },
    {
        "slug": "melhor-suporte-para-notebook-home-office",
        "title": "Melhor suporte para notebook no home office",
        "summary": "Um suporte simples pode melhorar postura, ventilação e conforto. Veja modelos que fazem diferença na mesa de trabalho.",
        "category_slug": "home-office",
        "published_at": datetime(2026, 5, 24),
        "reading_time": 4,
        "image_url": "/articles/suporte-notebook-home-office.svg",
        "sections": [
            {"type": "intro", "text": "Notebook baixo força o pescoço e esquenta mais. Um suporte ajusta a altura da tela e deixa o setup mais confortável, principalmente com teclado e mouse externos.", "order": 0},
            {"type": "criteria", "title": "Como escolher", "items": ["Altura ajustável ajuda a alinhar a tela aos olhos", "Base vazada melhora ventilação", "Material em alumínio tende a ser mais firme", "Modelos dobráveis são melhores para viagem"], "order": 1},
            {"type": "text", "text": "É um dos upgrades mais baratos para quem trabalha em notebook todos os dias.", "order": 2},
        ],
        "products": [
            {"name": "Suporte de Notebook em Alumínio", "summary": "Firme, bonito e bom para deixar fixo na mesa.", "pros": ["Estável", "Boa ventilação", "Visual limpo"], "cons": ["Menos portátil"], "affiliate_url": amazon_search("suporte notebook aluminio mesa"), "price": "R$ 89", "badge": "Melhor para Mesa", "source": "amazon"},
            {"name": "Suporte Dobrável para Notebook", "summary": "Leve e fácil de levar para escritório, viagem ou coworking.", "pros": ["Portátil", "Ajustável", "Preço baixo"], "cons": ["Pode ser menos firme"], "affiliate_url": amazon_search("suporte notebook dobravel ajustavel"), "price": "R$ 49", "badge": "Mais Portátil", "source": "amazon"},
            {"name": "Base Refrigerada para Notebook", "summary": "Ajuda quem usa notebook em tarefas mais pesadas.", "pros": ["Ajuda na ventilação", "Boa para notebooks quentes", "Uso simples"], "cons": ["Precisa de USB"], "affiliate_url": amazon_search("base refrigerada notebook"), "price": "R$ 79", "badge": "Melhor Ventilação", "source": "amazon"},
        ],
    },
    {
        "slug": "melhor-webcam-para-reuniao-online",
        "title": "Melhor webcam para reunião online com boa imagem",
        "summary": "Imagem ruim em reunião passa impressão errada. Veja webcams para melhorar videochamadas sem gastar demais.",
        "category_slug": "tecnologia",
        "published_at": datetime(2026, 5, 24),
        "reading_time": 5,
        "image_url": "/articles/webcam-reuniao-online.svg",
        "sections": [
            {"type": "intro", "text": "A webcam do notebook nem sempre dá conta. Para reuniões, aulas e entrevistas, uma câmera externa pode melhorar nitidez, luz e enquadramento.", "order": 0},
            {"type": "criteria", "title": "O que observar", "items": ["Full HD já é suficiente para a maioria", "Microfone embutido quebra galho, mas headset ainda é melhor", "Correção de luz ajuda em ambientes escuros", "Tampa de privacidade é um extra útil"], "order": 1},
            {"type": "text", "text": "A escolha depende mais da iluminação do ambiente e da estabilidade do software do que de números exagerados.", "order": 2},
        ],
        "products": [
            {"name": "Logitech C920s", "summary": "Clássica, confiável e com ótima imagem Full HD.", "pros": ["Imagem consistente", "Marca referência", "Tampa de privacidade"], "cons": ["Preço mais alto"], "affiliate_url": amazon_search("Logitech C920s webcam"), "price": "R$ 399", "badge": "Melhor Geral", "source": "amazon"},
            {"name": "Redragon Fobos GW600", "summary": "Opção acessível para melhorar a webcam do notebook.", "pros": ["Preço competitivo", "Full HD", "Instalação simples"], "cons": ["Microfone básico"], "affiliate_url": amazon_search("Redragon Fobos GW600 webcam"), "price": "R$ 169", "badge": "Custo-Benefício", "source": "amazon"},
            {"name": "Intelbras CAM 720p/Full HD", "summary": "Alternativa simples e fácil de encontrar no Brasil.", "pros": ["Marca nacional", "Boa disponibilidade", "Uso simples"], "cons": ["Recursos limitados"], "affiliate_url": amazon_search("webcam Intelbras full hd"), "price": "R$ 149", "badge": "Mais Simples", "source": "amazon"},
        ],
    },
    {
        "slug": "melhor-mouse-sem-fio-para-trabalhar",
        "title": "Melhor mouse sem fio para trabalhar o dia todo",
        "summary": "Mouse bom para trabalho precisa ser confortável, preciso e confiável. Veja opções para home office e escritório.",
        "category_slug": "tecnologia",
        "published_at": datetime(2026, 5, 24),
        "reading_time": 5,
        "image_url": "/articles/mouse-sem-fio-trabalho.svg",
        "sections": [
            {"type": "intro", "text": "Um mouse ruim incomoda mais do que parece. Para trabalhar o dia todo, conforto e conexão estável importam mais do que luzes ou muitos botões.", "order": 0},
            {"type": "criteria", "title": "O que vale priorizar", "items": ["Formato confortável para sua mão", "Conexão Bluetooth ou receptor USB estável", "Boa autonomia de bateria", "Cliques silenciosos podem ajudar em ambientes compartilhados"], "order": 1},
            {"type": "text", "text": "Selecionamos opções equilibradas para quem quer produtividade sem gastar demais.", "order": 2},
        ],
        "products": [
            {"name": "Logitech M650", "summary": "Confortável, silencioso e ótimo para rotina de escritório.", "pros": ["Cliques silenciosos", "Boa ergonomia", "Conexão estável"], "cons": ["Preço acima do básico"], "affiliate_url": amazon_search("Logitech M650 mouse sem fio"), "price": "R$ 189", "badge": "Melhor Geral", "source": "amazon"},
            {"name": "Logitech M170", "summary": "Mouse simples, barato e confiável para tarefas básicas.", "pros": ["Preço baixo", "Funciona bem", "Leve"], "cons": ["Poucos recursos"], "affiliate_url": amazon_search("Logitech M170 mouse sem fio"), "price": "R$ 59", "badge": "Melhor Barato", "source": "amazon"},
            {"name": "Microsoft Bluetooth Mouse", "summary": "Boa opção para quem prefere Bluetooth e visual discreto.", "pros": ["Bluetooth", "Design limpo", "Boa portabilidade"], "cons": ["Pode ser pequeno para algumas mãos"], "affiliate_url": amazon_search("Microsoft Bluetooth Mouse"), "price": "R$ 149", "badge": "Mais Portátil", "source": "amazon"},
        ],
    },
    {
        "slug": "melhor-vinho-para-presente-ate-100",
        "title": "Melhor vinho para presente até R$ 100",
        "summary": "Presentear com vinho não precisa ser caro. Veja opções seguras, bonitas e fáceis de agradar.",
        "category_slug": "bebidas",
        "published_at": datetime(2026, 5, 24),
        "reading_time": 5,
        "image_url": "/articles/vinho-presente-ate-100.svg",
        "sections": [
            {"type": "intro", "text": "Vinho para presente precisa equilibrar apresentação, sabor fácil de agradar e preço honesto. Até R$ 100, dá para escolher bem sem parecer improviso.", "order": 0},
            {"type": "criteria", "title": "Como não errar", "items": ["Rótulos conhecidos reduzem risco", "Tintos suaves ou meio secos agradam mais gente", "Espumante é bom para celebrações", "Embalagem e conservação também contam"], "order": 1},
            {"type": "text", "text": "Quando você não conhece muito o gosto da pessoa, prefira opções versáteis e de boa apresentação.", "order": 2},
        ],
        "products": [
            {"name": "Casillero del Diablo Cabernet Sauvignon", "summary": "Rótulo conhecido, fácil de encontrar e seguro para presente.", "pros": ["Marca reconhecida", "Boa apresentação", "Agrada muita gente"], "cons": ["Não é tão diferente"], "affiliate_url": amazon_search("Casillero del Diablo Cabernet Sauvignon"), "price": "R$ 59", "badge": "Escolha Segura", "source": "amazon"},
            {"name": "Miolo Seleção Tinto", "summary": "Vinho brasileiro honesto para presente casual.", "pros": ["Bom preço", "Nacional", "Fácil de harmonizar"], "cons": ["Mais simples"], "affiliate_url": amazon_search("Miolo Seleção Tinto vinho"), "price": "R$ 45", "badge": "Bom e Barato", "source": "amazon"},
            {"name": "Espumante Salton Brut", "summary": "Boa alternativa para aniversários, visitas e celebrações.", "pros": ["Clima de comemoração", "Boa apresentação", "Versátil"], "cons": ["Nem todo mundo prefere espumante"], "affiliate_url": amazon_search("Espumante Salton Brut"), "price": "R$ 54", "badge": "Para Celebrar", "source": "amazon"},
        ],
    },
    {
        "slug": "melhor-suporte-celular-carro-que-nao-cai",
        "title": "Melhor suporte de celular para carro que não cai",
        "summary": "Suporte de celular precisa ficar firme no painel ou na saída de ar. Veja modelos para usar GPS com mais segurança.",
        "category_slug": "carro",
        "published_at": datetime(2026, 5, 24),
        "reading_time": 5,
        "image_url": "/articles/suporte-celular-carro-firme.svg",
        "sections": [
            {"type": "intro", "text": "Um suporte que cai no meio do trajeto atrapalha e pode ser perigoso. Para usar GPS, a fixação precisa ser firme e o celular deve ficar fácil de visualizar.", "order": 0},
            {"type": "criteria", "title": "O que faz diferença", "items": ["Ventosa forte funciona bem no para-brisa e painel liso", "Fixação na saída de ar é prática, mas depende do carro", "Ímã precisa ser forte e bem posicionado", "Braço ajustável melhora o ângulo de visão"], "order": 1},
            {"type": "text", "text": "Antes de comprar, pense onde você prefere prender o suporte e se a superfície do carro ajuda ou atrapalha.", "order": 2},
        ],
        "products": [
            {"name": "Suporte Veicular com Ventosa", "summary": "Boa escolha para quem quer fixação firme no para-brisa ou painel.", "pros": ["Fixação forte", "Ajuste de ângulo", "Boa visibilidade"], "cons": ["Depende da superfície"], "affiliate_url": amazon_search("suporte celular carro ventosa forte"), "price": "R$ 49", "badge": "Mais Firme", "source": "amazon"},
            {"name": "Suporte Magnético para Saída de Ar", "summary": "Compacto e discreto para quem quer instalação rápida.", "pros": ["Discreto", "Fácil de instalar", "Ocupa pouco espaço"], "cons": ["Depende da grade de ar"], "affiliate_url": amazon_search("suporte magnetico celular carro saida de ar"), "price": "R$ 39", "badge": "Mais Discreto", "source": "amazon"},
            {"name": "Suporte Articulado para Painel", "summary": "Ajuda a posicionar o celular no ângulo certo para GPS.", "pros": ["Braço ajustável", "Bom para GPS", "Versátil"], "cons": ["Pode vibrar em ruas ruins"], "affiliate_url": amazon_search("suporte celular carro articulado painel"), "price": "R$ 59", "badge": "Mais Ajustável", "source": "amazon"},
        ],
    },
]


def add_articles() -> None:
    db = SessionLocal()
    try:
        added = 0
        updated = 0
        skipped = 0
        for article_data in NEW_ARTICLES_V2:
            existing = db.query(Article).filter(Article.slug == article_data["slug"]).first()
            if existing:
                if existing.image_url != article_data["image_url"]:
                    existing.image_url = article_data["image_url"]
                    print(f"Imagem atualizada: {article_data['slug']}")
                    updated += 1
                else:
                    print(f"Ja existe: {article_data['slug']}")
                    skipped += 1
                continue

            category = db.query(Category).filter(Category.slug == article_data["category_slug"]).first()
            if not category:
                print(f"Categoria nao encontrada: {article_data['category_slug']}")
                continue

            data = article_data.copy()
            sections = data.pop("sections")
            products = data.pop("products")
            data.pop("category_slug")

            article = Article(**data, category_id=category.id)
            db.add(article)
            db.flush()

            for section_data in sections:
                db.add(ContentSection(**section_data, article_id=article.id))

            for product_data in products:
                source = product_data.get("source", "amazon")
                db.add(Product(**product_data, store=source, article_id=article.id))

            print(f"Adicionado: {article.title}")
            added += 1

        db.commit()
        print(f"Concluido: {added} adicionados, {updated} atualizados, {skipped} ignorados")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    add_articles()
