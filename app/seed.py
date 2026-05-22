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
    {
        "slug": "melhor-air-fryer-custo-beneficio",
        "title": "Melhor air fryer custo-benefício para casa",
        "summary": "Modelos práticos para preparar refeições rápidas, com boa capacidade e limpeza simples.",
        "category_slug": "casa",
        "published_at": datetime(2026, 5, 22),
        "reading_time": 6,
        "image_url": "https://images.unsplash.com/photo-1585515320310-259814833e62?w=800&q=80",
        "sections": [
            {
                "type": "intro",
                "text": "Uma boa air fryer precisa equilibrar capacidade, potência, facilidade de limpeza e tamanho adequado para a rotina da casa. O melhor modelo nem sempre é o maior: para muita gente, um cesto médio e bem distribuído entrega resultado melhor no dia a dia.",
                "order": 0,
            },
            {
                "type": "criteria",
                "title": "O que observar antes de comprar",
                "items": [
                    "Capacidade: 4L a 5L atende bem uma família pequena",
                    "Potência: modelos acima de 1400W tendem a preparar mais rápido",
                    "Cesto removível facilita limpeza e manutenção",
                    "Controle de temperatura e timer simples evitam desperdício",
                ],
                "order": 1,
            },
            {
                "type": "text",
                "text": "Selecionamos opções populares e fáceis de encontrar, priorizando marcas conhecidas, boa reputação e uso prático no cotidiano.",
                "order": 2,
            },
        ],
        "products": [
            {
                "name": "Mondial Air Fryer Family 4L",
                "summary": "Boa capacidade para o dia a dia, controles simples e cesta antiaderente removível.",
                "pros": ["Preço competitivo", "Capacidade familiar", "Fácil de usar"],
                "cons": ["Acabamento simples", "Pode ocupar espaço na bancada"],
                "affiliate_url": "https://www.amazon.com.br/s?k=Mondial+Air+Fryer+Family+4L&tag=meumelhoracha-20",
                "price": "R$ 329",
                "badge": "Melhor Custo-Benefício",
                "source": "amazon",
            },
            {
                "name": "Philco Air Fryer Oven 12L",
                "summary": "Modelo tipo forno, indicado para quem quer mais espaço e versatilidade.",
                "pros": ["Alta capacidade", "Mais versátil", "Boa para famílias maiores"],
                "cons": ["Mais cara", "Ocupa mais espaço"],
                "affiliate_url": "https://www.amazon.com.br/s?k=Philco+Air+Fryer+Oven+12L&tag=meumelhoracha-20",
                "price": "R$ 599",
                "badge": "Mais Versátil",
                "source": "amazon",
            },
            {
                "name": "Midea Air Fryer 4L",
                "summary": "Opção equilibrada para quem busca construção sólida e preparo uniforme.",
                "pros": ["Boa construção", "Aquecimento consistente", "Design discreto"],
                "cons": ["Preço varia bastante", "Capacidade média"],
                "affiliate_url": "https://www.amazon.com.br/s?k=Midea+Air+Fryer+4L&tag=meumelhoracha-20",
                "price": "R$ 399",
                "badge": "Mais Equilibrada",
                "source": "amazon",
            },
        ],
    },
    {
        "slug": "melhor-suporte-celular-carro",
        "title": "Melhor suporte de celular para carro",
        "summary": "Suportes firmes e práticos para usar GPS com mais segurança no dia a dia.",
        "category_slug": "carro",
        "published_at": datetime(2026, 5, 22),
        "reading_time": 5,
        "image_url": "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=800&q=80",
        "sections": [
            {
                "type": "intro",
                "text": "Um suporte de celular para carro parece simples, mas faz diferença na segurança. O ideal é manter o aparelho estável, visível e sem atrapalhar a direção ou os comandos do painel.",
                "order": 0,
            },
            {
                "type": "criteria",
                "title": "Como escolher",
                "items": [
                    "Fixação: saída de ar, painel ou para-brisa mudam bastante a experiência",
                    "Compatibilidade: confira se aceita celulares maiores e capas grossas",
                    "Estabilidade: o suporte não pode vibrar demais em ruas irregulares",
                    "Uso com uma mão: ajuda muito na rotina",
                ],
                "order": 1,
            },
        ],
        "products": [
            {
                "name": "Baseus Suporte Veicular Magnético",
                "summary": "Suporte compacto com fixação magnética, bom para quem quer visual discreto.",
                "pros": ["Compacto", "Fácil de encaixar", "Visual discreto"],
                "cons": ["Pode exigir placa metálica", "Depende da capa usada"],
                "affiliate_url": "https://www.amazon.com.br/s?k=Baseus+suporte+veicular+magnetico&tag=meumelhoracha-20",
                "price": "R$ 59",
                "badge": "Mais Discreto",
                "source": "amazon",
            },
            {
                "name": "i2GO Suporte Veicular Universal",
                "summary": "Modelo universal com garras laterais, fácil de ajustar para diferentes aparelhos.",
                "pros": ["Compatível com vários celulares", "Instalação simples", "Bom preço"],
                "cons": ["Visual mais comum", "Pode vibrar em alguns painéis"],
                "affiliate_url": "https://www.amazon.com.br/s?k=i2GO+suporte+veicular+universal&tag=meumelhoracha-20",
                "price": "R$ 49",
                "badge": "Melhor Preço",
                "source": "amazon",
            },
            {
                "name": "Geonav Suporte Veicular com Ventosa",
                "summary": "Fixação por ventosa para quem prefere posicionar o celular no vidro ou painel.",
                "pros": ["Boa flexibilidade de posição", "Braço ajustável", "Fácil de remover"],
                "cons": ["Ventosa exige superfície limpa", "Pode chamar mais atenção"],
                "affiliate_url": "https://www.amazon.com.br/s?k=Geonav+suporte+veicular+ventosa&tag=meumelhoracha-20",
                "price": "R$ 69",
                "badge": "Mais Ajustável",
                "source": "amazon",
            },
        ],
    },
    {
        "slug": "melhor-cadeira-home-office-custo-beneficio",
        "title": "Melhor cadeira home office custo-benefício",
        "summary": "Cadeiras para trabalhar melhor em casa, com foco em conforto, ajustes e boa durabilidade.",
        "category_slug": "home-office",
        "published_at": datetime(2026, 5, 22),
        "reading_time": 6,
        "image_url": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800&q=80",
        "sections": [
            {
                "type": "intro",
                "text": "Para quem passa horas sentado, cadeira boa não é luxo. O ideal é procurar ajustes úteis, apoio lombar coerente e uma estrutura que aguente uso diário sem virar dor de cabeça em poucos meses.",
                "order": 0,
            },
            {
                "type": "criteria",
                "title": "Pontos que realmente importam",
                "items": [
                    "Ajuste de altura para alinhar braços e mesa",
                    "Apoio lombar ajuda em jornadas longas",
                    "Encosto em tela costuma ventilar melhor",
                    "Braços reguláveis são úteis, mas não obrigatórios",
                ],
                "order": 1,
            },
        ],
        "products": [
            {
                "name": "Flexform Uni",
                "summary": "Cadeira de escritório com bom equilíbrio entre ergonomia, construção e preço.",
                "pros": ["Boa ergonomia", "Marca reconhecida", "Design discreto"],
                "cons": ["Preço acima das básicas", "Ajustes variam por versão"],
                "affiliate_url": "https://www.amazon.com.br/s?k=Flexform+Uni+cadeira&tag=meumelhoracha-20",
                "price": "R$ 899",
                "badge": "Melhor Equilíbrio",
                "source": "amazon",
            },
            {
                "name": "Elements Astra",
                "summary": "Opção com visual moderno, encosto em tela e proposta ergonômica para home office.",
                "pros": ["Encosto ventilado", "Visual moderno", "Boa para uso prolongado"],
                "cons": ["Preço pode variar", "Exige montagem cuidadosa"],
                "affiliate_url": "https://www.amazon.com.br/s?k=Elements+Astra+cadeira&tag=meumelhoracha-20",
                "price": "R$ 749",
                "badge": "Mais Completa",
                "source": "amazon",
            },
            {
                "name": "Cadeira Presidente Tela Mesh",
                "summary": "Alternativa acessível com encosto em tela para quem quer melhorar o setup sem gastar tanto.",
                "pros": ["Preço acessível", "Encosto ventilado", "Visual profissional"],
                "cons": ["Menos ajustes", "Durabilidade depende do modelo"],
                "affiliate_url": "https://www.amazon.com.br/s?k=cadeira+presidente+tela+mesh&tag=meumelhoracha-20",
                "price": "R$ 399",
                "badge": "Mais Acessível",
                "source": "amazon",
            },
        ],
    },
    {
        "slug": "melhores-vinhos-custo-beneficio",
        "title": "Melhores vinhos custo-benefício para comprar online",
        "summary": "Rótulos versáteis para presentear, servir em casa ou começar uma pequena adega sem gastar demais.",
        "category_slug": "bebidas",
        "published_at": datetime(2026, 5, 22),
        "reading_time": 6,
        "image_url": "https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=800&q=80",
        "sections": [
            {
                "type": "intro",
                "text": "Comprar vinho online fica mais fácil quando você sabe o perfil que procura. Para custo-benefício, vale priorizar rótulos versáteis, fáceis de harmonizar e com boa reputação entre consumidores.",
                "order": 0,
            },
            {
                "type": "criteria",
                "title": "Como escolher sem complicar",
                "items": [
                    "Tintos leves e médios são mais fáceis de agradar",
                    "Espumantes brut funcionam bem para presente e celebrações",
                    "Rótulos conhecidos ajudam quem está começando",
                    "Confira sempre safra, volume e avaliações da loja",
                ],
                "order": 1,
            },
        ],
        "products": [
            {
                "name": "Casillero del Diablo Cabernet Sauvignon",
                "summary": "Tinto chileno conhecido, fácil de encontrar e versátil para carnes e massas.",
                "pros": ["Rótulo conhecido", "Boa versatilidade", "Fácil de presentear"],
                "cons": ["Perfil mais tradicional", "Preço varia por safra"],
                "affiliate_url": "https://www.amazon.com.br/s?k=Casillero+del+Diablo+Cabernet+Sauvignon&tag=meumelhoracha-20",
                "price": "R$ 59",
                "badge": "Mais Versátil",
                "source": "amazon",
            },
            {
                "name": "Miolo Seleção Merlot Cabernet",
                "summary": "Vinho brasileiro fácil de beber, com preço amigável para o dia a dia.",
                "pros": ["Bom para começar", "Preço acessível", "Produção nacional"],
                "cons": ["Menos complexo", "Pode variar conforme lote"],
                "affiliate_url": "https://www.amazon.com.br/s?k=Miolo+Selecao+Merlot+Cabernet&tag=meumelhoracha-20",
                "price": "R$ 39",
                "badge": "Melhor Nacional",
                "source": "amazon",
            },
            {
                "name": "Chandon Brut",
                "summary": "Espumante brut para ocasiões especiais, com boa aceitação e presença de marca.",
                "pros": ["Ótimo para presente", "Marca forte", "Boa para celebrações"],
                "cons": ["Mais caro", "Não é para consumo casual diário"],
                "affiliate_url": "https://www.amazon.com.br/s?k=Chandon+Brut&tag=meumelhoracha-20",
                "price": "R$ 89",
                "badge": "Melhor Presente",
                "source": "amazon",
            },
        ],
    },
    {
        "slug": "moda-feminina-pecas-coringa",
        "title": "Moda feminina: peças coringa para comprar melhor",
        "summary": "Achados de moda feminina para montar looks versáteis, elegantes e fáceis de combinar.",
        "category_slug": "moda",
        "published_at": datetime(2026, 5, 22),
        "reading_time": 6,
        "image_url": "https://images.unsplash.com/photo-1483985988355-763728e1935b?w=800&q=80",
        "sections": [
            {
                "type": "intro",
                "text": "Comprar moda feminina com bom custo-benefício é menos sobre seguir tendência e mais sobre escolher peças que combinam entre si. Bons tecidos, modelagem confortável e cores fáceis de usar fazem a peça render mais no guarda-roupa.",
                "order": 0,
            },
            {
                "type": "criteria",
                "title": "Critérios para escolher melhor",
                "items": [
                    "Prefira peças versáteis que combinam com diferentes ocasiões",
                    "Confira composição do tecido e avaliações sobre caimento",
                    "Cores neutras ajudam a multiplicar looks",
                    "Bolsa e calçado bons elevam produções simples",
                ],
                "order": 1,
            },
        ],
        "products": [
            {
                "name": "Vestido Midi Feminino",
                "summary": "Peça única versátil para trabalho, almoço, viagem ou ocasiões casuais arrumadas.",
                "pros": ["Fácil de combinar", "Funciona em várias ocasiões", "Boa peça coringa"],
                "cons": ["Caimento depende do tecido", "Atenção à tabela de medidas"],
                "affiliate_url": "https://www.amazon.com.br/s?k=vestido+midi+feminino&tag=meumelhoracha-20",
                "price": "R$ 129",
                "badge": "Peça Coringa",
                "source": "amazon",
            },
            {
                "name": "Bolsa Feminina Transversal",
                "summary": "Bolsa prática para rotina, com tamanho médio e visual fácil de combinar.",
                "pros": ["Prática para o dia a dia", "Mãos livres", "Combina com looks casuais"],
                "cons": ["Espaço limitado", "Material varia bastante"],
                "affiliate_url": "https://www.amazon.com.br/s?k=bolsa+feminina+transversal&tag=meumelhoracha-20",
                "price": "R$ 119",
                "badge": "Mais Prática",
                "source": "amazon",
            },
            {
                "name": "Tênis Casual Feminino Branco",
                "summary": "Tênis branco casual para usar com jeans, vestido, alfaiataria leve e looks de viagem.",
                "pros": ["Muito versátil", "Confortável para rotina", "Combina com várias peças"],
                "cons": ["Suja com facilidade", "Conforto varia por marca"],
                "affiliate_url": "https://www.amazon.com.br/s?k=tenis+casual+feminino+branco&tag=meumelhoracha-20",
                "price": "R$ 149",
                "badge": "Mais Versátil",
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
