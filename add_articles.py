"""
Script para adicionar novos artigos ao banco — Fim de semana 23-24/05/2026
Execute: python3 add_articles.py
Categorias: Casa, Carro, Home Office
"""

from app.database import SessionLocal
from app.models import Article, Category, ContentSection, Product

NEW_ARTICLES = [

    # ── CASA 1 ──────────────────────────────────────────────────────────
    {
        "slug": "melhor-aspirador-de-po-apartamento",
        "title": "Melhor aspirador de pó para apartamento até R$ 600",
        "summary": "Apartamento menor não perdoa sujeira — mas também não precisa de um equipamento gigante. Veja qual aspirador limpa bem, faz pouco barulho e não ocupa espaço.",
        "category_slug": "casa",
        "reading_time": 6,
        "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80",
        "sections": [
            {
                "type": "intro",
                "text": "Quem mora em apartamento sabe: poeira aparece rápido, especialmente em piso claro. O problema é que muitos aspiradores são grandes, barulhentos e um pesadelo para guardar. Nessa faixa até R$ 600, existem opções que limpam muito bem, cabem num armário e não perturbam os vizinhos.",
                "order": 0
            },
            {
                "type": "criteria",
                "title": "O que olhar antes de comprar",
                "items": [
                    "Tipo: sem fio (cordless) é mais prático para apartamento — sem cabo para arrastar",
                    "Sucção: acima de 15.000 Pa para pegar sujeira fina do piso e pelos de pet",
                    "Ruído: abaixo de 75 dB é o ideal para não incomodar quem está em casa",
                    "Autonomia: mínimo 30 minutos por carga para limpar o apartamento inteiro",
                    "Filtro HEPA: essencial para quem tem alergia — retém partículas finas no ar"
                ],
                "order": 1
            },
            {
                "type": "text",
                "text": "Testamos os modelos mais procurados nessa faixa e chegamos a três indicações honestas — uma para cada perfil de uso.",
                "order": 2
            }
        ],
        "products": [
            {
                "name": "Xiaomi Mi Vacuum Cleaner G10",
                "summary": "Sem fio, 150W de sucção, filtro HEPA, 60 min de autonomia e apenas 1,5 kg. O melhor equilíbrio entre preço e desempenho para apartamentos até 80m².",
                "pros": ["Sem fio — zero cabo para arrastar", "60 minutos de autonomia", "Filtro HEPA para alérgicos", "Leve e fácil de guardar"],
                "cons": ["Reservatório pequeno (0,5L)", "Carregamento demorado (~4h)"],
                "affiliate_url": "https://www.amazon.com.br/s?k=Xiaomi+Mi+Vacuum+Cleaner+G10&tag=meumelhoracha-20",
                "price": "R$ 489",
                "badge": "Melhor Geral",
                "source": "amazon"
            },
            {
                "name": "Mondial Aspirador Ciclônico Sem Fio AP-35",
                "summary": "Nacional, com fio retrátil, 1.600W e sucção potente para tapetes. O mais potente da lista, ideal para quem tem tapetes grossos ou muito pelo de pet.",
                "pros": ["1.600W de potência — limpa tapete fundo", "Cabo retrátil prático", "Marca com assistência no Brasil", "Preço acessível"],
                "cons": ["Com fio — menos prático", "Mais barulhento que os sem fio"],
                "affiliate_url": "https://www.amazon.com.br/s?k=Mondial+Aspirador+AP-35&tag=meumelhoracha-20",
                "price": "R$ 329",
                "badge": "Melhor Custo-Benefício",
                "source": "amazon"
            },
            {
                "name": "Electrolux Ergoclean BGS21",
                "summary": "Sem fio, leve, silencioso e com encaixe de parede para guardar. Pensado para quem quer praticidade máxima no dia a dia.",
                "pros": ["Silencioso (68 dB)", "Suporte de parede incluso", "Design compacto", "Marca confiável"],
                "cons": ["Autonomia de apenas 30 min", "Sucção moderada em tapetes grossos"],
                "affiliate_url": "https://www.amazon.com.br/s?k=Electrolux+Ergoclean+BGS21&tag=meumelhoracha-20",
                "price": "R$ 549",
                "badge": "Mais Silencioso",
                "source": "amazon"
            }
        ]
    },

    # ── CASA 2 ──────────────────────────────────────────────────────────
    {
        "slug": "melhor-panela-pressao-eletrica",
        "title": "Melhor panela de pressão elétrica para o dia a dia",
        "summary": "Feijão em 30 minutos, frango desfiado sem esforço, arroz cremoso sem queimar. A panela de pressão elétrica mudou a cozinha de muita gente — mas qual vale a pena comprar?",
        "category_slug": "casa",
        "reading_time": 6,
        "image_url": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=800&q=80",
        "sections": [
            {
                "type": "intro",
                "text": "A panela de pressão elétrica é um daqueles produtos que, depois que você experimenta, não consegue mais imaginar a cozinha sem ela. Feijão que antes levava uma hora fica pronto em 30 minutos. O frango para desfiar sai macio sem precisar ficar na cozinha vigiando. E o melhor: sem risco do fogão — ela desliga sozinha.",
                "order": 0
            },
            {
                "type": "criteria",
                "title": "O que importa na hora de escolher",
                "items": [
                    "Capacidade: 3L para até 3 pessoas, 5L para famílias maiores ou quem cozinha em grande quantidade",
                    "Funções: pressão, refogar e manter aquecido são as mais usadas no dia a dia",
                    "Pressão de trabalho: acima de 70 kPa garante cozimento mais rápido",
                    "Segurança: válvula de segurança e tampa com trava são obrigatórias",
                    "Facilidade de limpeza: panelas com cuba antiaderente e peças removíveis são muito mais práticas"
                ],
                "order": 1
            },
            {
                "type": "text",
                "text": "Levamos em conta o que realmente importa para quem cozinha no dia a dia — não só as especificações técnicas, mas facilidade de uso e durabilidade real.",
                "order": 2
            }
        ],
        "products": [
            {
                "name": "Panela de Pressão Elétrica Philips Walita RI3104",
                "summary": "5L, 14 funções, pressão de 80 kPa, design compacto e interface simples. A mais vendida no Brasil por um bom motivo: faz tudo bem feito e dura anos.",
                "pros": ["14 funções em uma só panela", "Pressão de 80 kPa — cozinha rápido", "Fácil de usar e limpar", "Assistência Philips em todo Brasil"],
                "cons": ["Preço um pouco acima das concorrentes", "Não tem função de fritar"],
                "affiliate_url": "https://www.amazon.com.br/s?k=Philips+Walita+RI3104+panela+pressao&tag=meumelhoracha-20",
                "price": "R$ 449",
                "badge": "Mais Vendida",
                "source": "amazon"
            },
            {
                "name": "Mondial Pratic Cook PE-40",
                "summary": "5L, 12 funções, 900W. A opção nacional com melhor custo-benefício — faz tudo que a maioria precisa a um preço muito mais acessível.",
                "pros": ["Preço acessível", "12 funções completas", "Marca com assistência no Brasil", "Tampa com trava de segurança"],
                "cons": ["Interface menos intuitiva", "Pressão um pouco menor (70 kPa)"],
                "affiliate_url": "https://www.amazon.com.br/s?k=Mondial+Pratic+Cook+PE-40&tag=meumelhoracha-20",
                "price": "R$ 279",
                "badge": "Melhor Custo-Benefício",
                "source": "amazon"
            },
            {
                "name": "Instant Pot Duo 5,7L",
                "summary": "A queridinha dos cozinheiros mais exigentes. 7 funções em 1, pressão de 80 kPa e qualidade premium. Para quem quer o melhor sem pensar em trocar.",
                "pros": ["Qualidade premium reconhecida mundialmente", "7 funções incluindo iogurte e pasteurização", "Comunidade enorme com receitas", "Durabilidade excepcional"],
                "cons": ["A mais cara das três", "Tamanho maior ocupa mais espaço"],
                "affiliate_url": "https://www.amazon.com.br/s?k=Instant+Pot+Duo+5.7L&tag=meumelhoracha-20",
                "price": "R$ 589",
                "badge": "Premium",
                "source": "amazon"
            }
        ]
    },

    # ── CARRO 1 ──────────────────────────────────────────────────────────
    {
        "slug": "melhor-camera-re-carro",
        "title": "Melhor câmera de ré para carro com tela",
        "summary": "Estacionar em vaga apertada fica muito mais fácil com uma câmera de ré boa. Veja quais realmente valem o investimento — com imagem nítida e instalação simples.",
        "category_slug": "carro",
        "reading_time": 5,
        "image_url": "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=800&q=80",
        "sections": [
            {
                "type": "intro",
                "text": "Câmera de ré deixou de ser luxo. Hoje é segurança básica — especialmente em cidade grande, onde as vagas estão cada vez mais disputadas e os carros cada vez mais próximos. O problema é que o mercado está cheio de opções baratas que prometem muito e entregam pouco. Câmeras que embaçam com chuva, telas que escurecem ao sol, instalação que complica mais do que ajuda.",
                "order": 0
            },
            {
                "type": "criteria",
                "title": "O que realmente importa",
                "items": [
                    "Resolução: mínimo 720p para imagem útil — abaixo disso você vê mas não confia",
                    "Ângulo de visão: 120° a 170° para enxergar bem as laterais da vaga",
                    "Visão noturna: LEDs infravermelhos fazem a diferença à noite",
                    "Tela: displays de 4,3\" ou 5\" são confortáveis de usar no painel",
                    "Linha de guia: linhas dinâmicas que se movem com a direção são muito mais úteis que as estáticas"
                ],
                "order": 1
            }
        ],
        "products": [
            {
                "name": "Kit Câmera de Ré Multilaser AU011",
                "summary": "Câmera 120° com visão noturna + tela LCD 4,3\". O kit mais completo para instalar sem complicação. Plugue e use.",
                "pros": ["Kit completo — câmera + tela na caixa", "Visão noturna com LED infravermelho", "Ângulo de 120° com linhas de guia", "Instalação simples"],
                "cons": ["Resolução padrão (não HD)", "Tela de 4,3\" pode parecer pequena para alguns"],
                "affiliate_url": "https://www.amazon.com.br/s?k=Multilaser+AU011+camera+re&tag=meumelhoracha-20",
                "price": "R$ 189",
                "badge": "Melhor Kit Completo",
                "source": "amazon"
            },
            {
                "name": "Câmera de Ré Universal Automotiva Full HD",
                "summary": "Full HD 1080p, ângulo de 170°, IP67 (à prova d'água) e visão noturna potente. Para quem quer qualidade de imagem de verdade.",
                "pros": ["Full HD 1080p — imagem nítida mesmo à noite", "Ângulo de 170° — vê quase tudo atrás", "IP67 — resistente a chuva e poeira", "Linhas de guia dinâmicas"],
                "cons": ["Tela não inclusa — precisa comprar separado", "Instalação mais técnica"],
                "affiliate_url": "https://www.amazon.com.br/s?k=camera+re+full+hd+170+graus+automotiva&tag=meumelhoracha-20",
                "price": "R$ 149",
                "badge": "Melhor Imagem",
                "source": "amazon"
            },
            {
                "name": "Tela Monitor 7\" + Câmera de Ré HD",
                "summary": "Tela grande de 7\", câmera HD, suporte para 2 câmeras e entrada para DVD/GPS. Para quem quer conforto visual máximo no painel.",
                "pros": ["Tela de 7\" — fácil de ver", "Suporta 2 câmeras simultaneamente", "Entrada AV para GPS ou DVD", "Imagem colorida diurna e noturna"],
                "cons": ["Ocupa mais espaço no painel", "Instalação mais complexa"],
                "affiliate_url": "https://www.amazon.com.br/s?k=tela+monitor+7+polegadas+camera+re+kit&tag=meumelhoracha-20",
                "price": "R$ 279",
                "badge": "Maior Conforto Visual",
                "source": "amazon"
            }
        ]
    },

    # ── CARRO 2 ──────────────────────────────────────────────────────────
    {
        "slug": "melhor-tapete-automotivo-personalizado",
        "title": "Melhor tapete automotivo: como escolher e quais comprar",
        "summary": "Tapete bom protege o carpete do carro, não escorrega no freio e não solta cheiro ruim. Veja o que diferencia um tapete de qualidade de um que vai direto para o lixo.",
        "category_slug": "carro",
        "reading_time": 5,
        "image_url": "https://images.unsplash.com/photo-1503736334956-4c8f8e92946d?w=800&q=80",
        "sections": [
            {
                "type": "intro",
                "text": "Tapete de carro é um desses acessórios que a gente ignora até precisar. Mas quando o carpete original está manchado e difícil de limpar, bater o pé no tapete errado ao frear ou sentir aquele cheiro de borracha barata no interior, a escolha começa a fazer sentido. Um tapete bom protege, não escorrega e dura anos.",
                "order": 0
            },
            {
                "type": "criteria",
                "title": "O que separar um tapete bom de um ruim",
                "items": [
                    "Material: borracha termoplástica é o melhor — lava com água, não resseca e não escorrega",
                    "Trava de segurança: tapete de motorista precisa de gancho de fixação — tapete solto pode prender no pedal",
                    "Bordas altas: retém água e barro em dias de chuva, protegendo o carpete original",
                    "Personalizado por modelo: tapetes universais não encaixam bem — sobram bordas ou ficam pequenos",
                    "Certificação: verifique se o fabricante certifica para o modelo exato do seu carro"
                ],
                "order": 1
            }
        ],
        "products": [
            {
                "name": "Tapete Automotivo Beretto Borracha Termoplástica",
                "summary": "Borracha de alta densidade, bordas elevadas de 2cm, trava de segurança e molde específico por modelo de carro. O mais recomendado por quem não quer comprar duas vezes.",
                "pros": ["Borda de 2cm retém água e barro", "Trava de segurança no tapete do motorista", "Lava com água e sabão facilmente", "Sem cheiro — material atóxico"],
                "cons": ["Preço mais alto que tapetes universais", "Precisa escolher o modelo certo do carro"],
                "affiliate_url": "https://www.amazon.com.br/s?k=tapete+automotivo+Beretto+borracha&tag=meumelhoracha-20",
                "price": "R$ 189",
                "badge": "Melhor Qualidade",
                "source": "amazon"
            },
            {
                "name": "Tapete PVC Dupla Face Universal",
                "summary": "Universal, antiderrapante dos dois lados, resistente à água e fácil de cortar para ajustar ao tamanho da sua necessidade.",
                "pros": ["Universal — serve para qualquer carro", "Preço acessível", "Antiderrapante dos dois lados", "Fácil de cortar e personalizar"],
                "cons": ["Pode não encaixar perfeitamente em todos os modelos", "Sem trava de segurança"],
                "affiliate_url": "https://www.amazon.com.br/s?k=tapete+automotivo+PVC+antiderrapante+universal&tag=meumelhoracha-20",
                "price": "R$ 89",
                "badge": "Melhor Custo-Benefício",
                "source": "amazon"
            },
            {
                "name": "Tapete Carpet Luxo Personalizado por Modelo",
                "summary": "Acabamento premium em carpet, visual elegante, fácil instalação e personalizado para cada modelo de veículo. Para quem quer o interior do carro impecável.",
                "pros": ["Visual sofisticado no interior", "Personalizado por modelo — encaixe perfeito", "Material macio e confortável", "Disponível em várias cores"],
                "cons": ["Absorve sujeira — limpeza mais trabalhosa", "Não é ideal para dias de chuva frequentes"],
                "affiliate_url": "https://www.amazon.com.br/s?k=tapete+automotivo+carpet+personalizado&tag=meumelhoracha-20",
                "price": "R$ 149",
                "badge": "Visual Premium",
                "source": "amazon"
            }
        ]
    },

    # ── HOME OFFICE 1 ──────────────────────────────────────────────────
    {
        "slug": "melhor-luminaria-mesa-home-office",
        "title": "Melhor luminária de mesa para home office: sem cansar os olhos",
        "summary": "Trabalhar com luz ruim é receita para dor de cabeça e olhos cansados no fim do dia. Uma boa luminária de mesa resolve isso — e ainda melhora a aparência nas videochamadas.",
        "category_slug": "home-office",
        "reading_time": 5,
        "image_url": "https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=800&q=80",
        "sections": [
            {
                "type": "intro",
                "text": "Quem trabalha home office sabe: a iluminação do ambiente faz uma diferença enorme — não só para os olhos, mas para a energia ao longo do dia. Luz fria demais cansa, luz quente demais dá sono, e luz insuficiente força os olhos sem você perceber. Uma luminária de mesa boa resolve esse problema e ainda melhora muito a sua aparência nas videochamadas.",
                "order": 0
            },
            {
                "type": "criteria",
                "title": "O que observar antes de comprar",
                "items": [
                    "Temperatura de cor: 4.000K a 5.000K é o ideal para trabalho — nem fria demais, nem quente demais",
                    "Regulagem de intensidade: dimmer para ajustar conforme a luz do ambiente",
                    "IRC (Índice de Reprodução de Cor): acima de 80 para cores naturais e confortáveis",
                    "Articulação: braço flexível permite direcionar a luz exatamente onde precisa",
                    "Porta USB: luminárias modernas têm USB para carregar o celular junto"
                ],
                "order": 1
            },
            {
                "type": "text",
                "text": "Selecionamos três opções para perfis diferentes — quem quer o básico bem feito, quem quer mais controle e quem não abre mão do premium.",
                "order": 2
            }
        ],
        "products": [
            {
                "name": "Luminária de Mesa LED Multilaser LT-006",
                "summary": "LED 10W, 3 temperaturas de cor, 10 níveis de intensidade, carregador USB integrado e braço articulado. A melhor relação qualidade/preço para home office.",
                "pros": ["3 temperaturas de cor ajustáveis", "10 níveis de intensidade", "Porta USB para carregar celular", "Braço articulado flexível"],
                "cons": ["Sem memória de configuração ao desligar", "Plástico no braço (menos premium)"],
                "affiliate_url": "https://www.amazon.com.br/s?k=Luminaria+Mesa+LED+Multilaser+LT006&tag=meumelhoracha-20",
                "price": "R$ 149",
                "badge": "Melhor Custo-Benefício",
                "source": "amazon"
            },
            {
                "name": "Luminária BenQ ScreenBar",
                "summary": "Desenvolvida especialmente para monitores — se apoia na tela sem ocupar espaço na mesa, ilumina o teclado sem reflexo na tela e tem sensor automático de luz ambiente.",
                "pros": ["Sem reflexo na tela — sem cansaço visual", "Não ocupa espaço na mesa", "Sensor automático de brilho", "Design premium e discreto"],
                "cons": ["A mais cara das três", "Só funciona em monitores — não serve para leitura lateral"],
                "affiliate_url": "https://www.amazon.com.br/s?k=BenQ+ScreenBar+luminaria+monitor&tag=meumelhoracha-20",
                "price": "R$ 489",
                "badge": "Melhor para Monitor",
                "source": "amazon"
            },
            {
                "name": "Luminária LED Ring Light de Mesa 10\"",
                "summary": "Aro de LED 10\", 3 cores, 10 níveis, suporte para celular e braço flexível. Ilumina o rosto nas videochamadas e o ambiente ao mesmo tempo — duas funções em uma.",
                "pros": ["Ilumina o rosto nas videochamadas", "Suporte para celular incluso", "3 cores e 10 intensidades", "Ideal para quem faz reuniões online"],
                "cons": ["Ocupa mais espaço na mesa", "Não é ideal para iluminar apenas o teclado"],
                "affiliate_url": "https://www.amazon.com.br/s?k=ring+light+mesa+10+polegadas+suporte+celular&tag=meumelhoracha-20",
                "price": "R$ 199",
                "badge": "Melhor para Videochamadas",
                "source": "amazon"
            }
        ]
    }
]


def add_articles():
    db = SessionLocal()
    try:
        added = 0
        skipped = 0

        for article_data in NEW_ARTICLES:
            # Verifica se já existe
            existing = db.query(Article).filter(Article.slug == article_data["slug"]).first()
            if existing:
                print(f"  ⚠ Já existe: {article_data['slug']}")
                skipped += 1
                continue

            # Busca categoria
            cat = db.query(Category).filter(Category.slug == article_data["category_slug"]).first()
            if not cat:
                print(f"  ❌ Categoria não encontrada: {article_data['category_slug']}")
                continue

            a = article_data.copy()
            sections  = a.pop("sections")
            products  = a.pop("products")
            a.pop("category_slug")

            article = Article(**a, category_id=cat.id)
            db.add(article)
            db.flush()

            for s in sections:
                sec = ContentSection(**s, article_id=article.id)
                db.add(sec)

            for p in products:
                prod = Product(**p, article_id=article.id)
                db.add(prod)

            print(f"  ✅ Adicionado: {article.title}")
            added += 1

        db.commit()
        print(f"\nConcluído: {added} adicionados, {skipped} ignorados (já existiam)")

    except Exception as e:
        db.rollback()
        print(f"❌ Erro: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Adicionando novos artigos ao banco...\n")
    add_articles()
