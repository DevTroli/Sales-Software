from django.shortcuts import render

def index(request):
    return render(request, "core/index.html")

def novidades(request):
    return render(request, "core/novidades.html")

def menu(request):
    # Navegação
    sections = [
        ("cervejas", "🍻Cerveja"),
        ("bebidas-especiais", "🍹Drinks"),
        ("refrescos", "🥤Refrescos"),
        ("porcoes", "🍟Porções"),
        ("almoco-executivo", "🌟Almoços"),
        ("espetos-brasa", "🔥Espetões"),
        ("sobremesas", "🍰 Doces"),
    ]
    
    # 1. Cervejas Artesanais
    cervejas_artesanais = {
        "garrafa_600ml": [
            {"nome": "Skol",            "unit": "R$ 11,90", "balde": "R$ 44,00"},
            {"nome": "Petra",           "unit": "R$ 11,90", "balde": "R$ 44,00"},
            {"nome": "Original",        "unit": "R$ 14,90", "balde": "R$ 56,00"},
            {"nome": "Imperio",         "unit": "R$ 11,90", "balde": "R$ 44,00"},
            {"nome": "Imperio Lager",   "unit": "R$ 14,90", "balde": "R$ 56,00"},
            {"nome": "Duplo Malte",     "unit": "R$ 13,90", "balde": "R$ 52,00"},
            {"nome": "Budweiser",       "unit": "R$ 14,90", "balde": "R$ 56,00"},
            {"nome": "Eisenbahn",       "unit": "R$ 14,50", "balde": "R$ 54,00"},
            {"nome": "Therezopolis",    "unit": "R$ 14,50", "balde": "R$ 54,00"},
            {"nome": "Spaten/Stella",   "unit": "R$ 14,90", "balde": "R$ 56,00"},
            {"nome": "Spaten/Stella",   "unit": "R$ 15,90", "balde": "R$ 60,00"},
            {"nome": "Heinken/Corona",  "unit": "R$ 17,90", "balde": "R$ 72,00"},
        ],
        "long_neck_330ml": [
            {"nome": "Amstel Ultra",    "unit": "R$ 9,90",  "balde": "R$ 54,00"},
            {"nome": "Budweiser",       "unit": "R$ 9,90",  "balde": "R$ 54,00"},
            {"nome": "Spaten",          "unit": "R$ 9,90", "balde": "R$ 54,00"},
            {"nome": "Stella",          "unit": "R$ 10,90", "balde": "R$ 60,00"},
            {"nome": "Stella Pure Gold", "unit": "R$ 11,90", "balde": "R$ 66,00"},
            {"nome": "Heineken",        "unit": "R$ 10,90", "balde": "R$ 60,00"},
            {"nome": "Heineken Zero",   "unit": "R$ 10,90",  "balde": "R$ 60,00"},
            {"nome": "Corona",        "unit": "R$ 11,90", "balde": "R$ 66,00"},
        ],
    }
    
    # 2. Bebidas Especiais
    caipirinhas = [
        {"base": "Cachaça Velho Barrero",        "preco": "R$ 18,90"},
        {"base": "Cachaça Sagatiba",  "preco": "R$ 21,90"},
        {"base": "Vodka Nacional",    "preco": "R$ 22,90"},
        {"base": "Whisky Nacional",    "preco": "R$ 24,90"},
        {"base": "Whisky Importada",   "preco": "R$ 27,90"},
        {"base": "Vodka Importada",   "preco": "R$ 25,90"},
        {"base": "Saquê",             "preco": "R$ 21,90"},
    ]
    
    sabores_caipirinhas = [
        "Limão", "Morango", "Abacaxi", "Maracujá", "Tangerina",
        "Kiwi", "Morango c/ Manjericão", "3 Limões + Gengibre",
        "Uva Roxa + Hortelã", "Matte com Limão",
    ]
    
    extra_caip = "2 frutas: +R$ 3,00"
    
    gin_tonica = [
        {"tipo": "Nacional",  "preco": "R$ 23,00"},
        {"tipo": "Importado", "preco": "R$ 33,00"},
    ]
    
    combos_gin = [
        "Clássico (zimbro + alecrim)",
        "Pepino + Siciliano",
        "Frutas Vermelhas",
        "Maçã Verde + Canela Defumada",
        "Maracujá + Alecrim",
        "Melancia + Hortelã",
    ]
    
    long_neck = [
        {"nome": "Smirnoff Ice", "preco": "R$ 12,00"},
        {"nome": "Cabaré Ice: Sabores", "preco": "R$ 12,00"},
        {"nome": "Skol Beats", "preco": "R$ 13,00"},
        {"nome": "Skol Beats: Gin Tônica", "preco": "R$ 13,00"},
        {"nome": "Skol Beats: Fruit Mix", "preco": "R$ 13,00"},
        {"nome": "Skol Beats: Caipirinha", "preco": "R$ 13,00"},
        {"nome": "Skol Beats: Tropical", "preco": "R$ 13,00"},
    ]
    
    # 3. Refrescos
    sucos_naturais = [
        "Laranja", "Abacaxi c/ Hortelã", "Limonada", "Maracujá", "Morango",
        "Chá Matte da Casa",
    ]
    
    preco_suco = "R$ 12,90"
    extra_suco = "+2 frutas: R$ 2,00"
    
    refrigerantes = [
        {"nome": "Coca /Zero",       "preco": "R$ 6,50"},
        {"nome": "Coca KS vidro",       "preco": "R$ 6,50"},
        {"nome": "Sprite /Zero",       "preco": "R$ 6,50"},
        {"nome": "Schweppes",       "preco": "R$ 6,50"},
        {"nome": "Pepsi", "preco": "R$ 6,50"},
        {"nome": "Guaraná Antaátrica / Zero",    "preco": "R$ 6,50"},
        {"nome": "H2O Lemon 500ml","preco": "R$ 7,50"},
    ]
    
    aguas = [
        {"nome": "Sem gás 500ml",  "preco": "R$ 4,00"},
        {"nome": "Com gás 500ml",  "preco": "R$ 4,50"},
        {"nome": "Tônica 500ml",  "preco": "R$ 6,50"},
    ]
    
    # 4. Porções
    porcoes = [
        {"nome": "Batata frita", "preco": "R$ 34,90"},
        {"nome": "Batata frita c/ Chedar", "preco": "R$ 45,00"},
        {"nome": "Calabresa", "preco": "R$ 49,90"},
        {"nome": "Frango Aperitivo", "preco": "R$ 69,90"},
        {"nome": "Isca de tilápia", "preco": "R$ 89,00"},
        {"nome": "Camarão", "preco": "R$ 99,00"},
        {"nome": "Fraldinha", "preco": "R$ 79,90"},
        {"nome": "Contra filé", "preco": "R$ 89,90"},
        {"nome": "Picanha Maturata", "preco": "R$ 99,90"},
    ]
    
    # 5. Almoço Executivo
    almoco_executivo = [
        {"dia": "SEGUNDA", "prato": "Filé de Frango à Parmegiana",    "preco": "R$ 22,90"},
        {"dia": "TERÇA",   "prato": "Panqueca Carne ou Frango c/ Queijo","preco": "R$ 22,90"},
        {"dia": "QUARTA",  "prato": "Strogonoff de Carne",            "preco": "R$ 22,90"},
        {"dia": "QUINTA",  "prato": "Costela com Mandioca Crocante",  "preco": "R$ 22,90"},
        {"dia": "SEXTA",   "prato": "Filé de Tilápia Grelhado",       "preco": "R$ 24,90"},
        {"dia": "SÁBADO",  "prato": "Feijoada Individual",            "preco": "R$ 39,90"},
        {"dia": "SÁBADO",  "prato": "Feijoada",            "preco": "R$ 69,90"},
        {"dia": "SÁBADO",  "prato": "Feijoada Gorda",            "preco": "R$ 119,90"},
        {"dia": "DOMINGO","prato": "Lasanha com Cupim ou Frango",     "preco": "R$ 29,90"},
    ]
    
    almoco_horario = "Seg a Sex 12h-16h | Sáb/Dom 12h-21h"
    almoco_acomp = "Todos acompanham arroz, feijão, salada e batata frita"
    pratos_fixos = "Todos os dias servimos Contrafilé, Filé de frango parmegiana ou Calabresa Acebolada"
    
    # 6. Espetos na Brasa
    espetos = [
        {"nome": "Picanha Maturatta", "preco": "R$ 249,90"},
        {"nome": "Bife Ancho",          "preco": "R$ 239,90"},
        {"nome": "Contrafilé",     "preco": "R$ 199,90"},
        {"nome": "Misto Carnes",   "preco": "R$ 189,90"},
        {"nome": "Frango Diplomata",      "preco": "R$ 179,90"},
        {"nome": "Costela Suína",  "preco": "R$ 139,90"},
    ]
    
    espetos_acomp = "Acompanham arroz, farofa, batata e vinagrete"
    
    # 7. Sobremesas
    sobremesas = [
        {"nome": "Pudim",  "preco": "R$ 10,00"},
        {"nome": "Pudim c/ Chantilly", "preco": "R$ 12,90"},
        {"nome": "Brigadeirão",     "preco": "R$ 10,00"},
        {"nome": "Petit Gateau",    "preco": "R$ 29,90"},
        {"nome": "Salada de Frutas","preco": "R$ 29,90"},
    ]
    
    sobremesas_obs = "Artesanais – peça 15 min antes"
    
    # Rodapé
    rodape = "CNPJ XX.XXX.XXX/0001‑XX • Proibida venda a menores • Área não‑fumante"
    
    context = {
        "sections": sections,
        "cervejas_artesanais": cervejas_artesanais,
        "caipirinhas": caipirinhas,
        "long_neck": long_neck,
        "sabores_caipirinhas": sabores_caipirinhas,
        "extra_caip": extra_caip,
        "gin_tonica": gin_tonica,
        "combos_gin": combos_gin,
        "sucos_naturais": sucos_naturais,
        "preco_suco": preco_suco,
        "extra_suco": extra_suco,
        "refrigerantes": refrigerantes,
        "aguas": aguas,
        "porcoes": porcoes,
        "almoco_executivo": almoco_executivo,
        "almoco_horario": almoco_horario,
        "almoco_acomp": almoco_acomp,
        "pratos_fixos": pratos_fixos,
        "espetos": espetos,
        "espetos_acomp": espetos_acomp,
        "sobremesas": sobremesas,
        "sobremesas_obs": sobremesas_obs,
        "rodape": rodape,
    }
    
    return render(request, "core/menu.html", context)