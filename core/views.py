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
        ("almoco-executivo", "🌟Almoços"),
        ("espetos-brasa", "🔥Espetões"),
        ("sobremesas", "🍰 Doces"),
    ]

    # 1. Cervejas Artesanais
    cervejas_artesanais = {
        "garrafa_600ml": [
            {"nome": "Skol",            "unit": "R$ 11,90", "balde": "R$ 44,00"},
            {"nome": "Petra",           "unit": "R$ 11,90", "balde": "R$ 44,00"},
            {"nome": "Original",        "unit": "R$ 14,90", "balde": "R$ 56,00"},
            {"nome": "Imperio",         "unit": "R$ 11,90", "balde": "R$ 44,00"},
            {"nome": "Imperio Lager",   "unit": "R$ 14,90", "balde": "R$ 56,00"},
            {"nome": "Duplo Malte",     "unit": "R$ 13,90", "balde": "R$ 52,00"},
            {"nome": "Budweiser",       "unit": "R$ 14,90", "balde": "R$ 56,00"},
            {"nome": "Eisenbahn",       "unit": "R$ 14,50", "balde": "R$ 54,00"},
            {"nome": "Therezopolis",    "unit": "R$ 14,50", "balde": "R$ 54,00"},
            {"nome": "Spaten/Stella",   "unit": "R$ 14,90", "balde": "R$ 56,00"},
            {"nome": "Heinken/Corona",  "unit": "R$ 17,90", "balde": "R$ 72,00"},
        ],
        "long_neck_330ml": [
            {"nome": "Amstel Ultra",    "unit": "R$ 9,90",  "balde": "R$ 54,00"},
            {"nome": "Budweiser",       "unit": "R$ 9,90",  "balde": "R$ 54,00"},
            {"nome": "Spaten",          "unit": "R$ 9,90", "balde": "R$ 54,00"},
            {"nome": "Stella",          "unit": "R$ 10,90", "balde": "R$ 60,00"},
            {"nome": "Stella Pure Gold", "unit": "R$ 11,90", "balde": "R$ 66,00"},
            {"nome": "Heineken",        "unit": "R$ 10,90", "balde": "R$ 60,00"},
            {"nome": "Heineken Zero",   "unit": "R$ 10,90",  "balde": "R$ 60,00"},
            {"nome": "Corona",        "unit": "R$ 11,90", "balde": "R$ 66,00"},
        ],
    }

    # 2. Bebidas Especiais
    caipirinhas = [
        {"base": "Cachaça VB",        "preco": "R$ 18,90"},
        {"base": "Cachaça Sagatiba",  "preco": "R$ 21,90"},
        {"base": "Vodka Nacional",    "preco": "R$ 22,90"},
        {"base": "Whisky Nacional",    "preco": "R$ 24,90"},
        {"base": "Whisky Importada",   "preco": "R$ 27,90"},
        {"base": "Vodka Importada",   "preco": "R$ 25,90"},
        {"base": "Saquê",             "preco": "R$ 21,90"},
    ]
    sabores_caipirinhas = [
        "Limão", "Morango", "Abacaxi", "Maracujá", "Tangerina",
        "Kiwi", "Morango c/ Manjericão", "3 Limões + Gengibre",
        "Uva Roxa + Hortelã", "Matte com Limão",
    ]
    extra_caip = "2 frutas: +R$ 3,00"

    gin_tonica = [
        {"tipo": "Nacional",  "preco": "R$ 23,00"},
        {"tipo": "Importado", "preco": "R$ 33,00"},
    ]
    combos_gin = [
        "Clássico (zimbro + alecrim)",
        "Pepino + Siciliano",
        "Frutas Vermelhas",
        "Maçã Verde + Canela Defumada",
        "Maracujá + Alecrim",
        "Melancia + Hortelã",
    ]

    # 3. Refrescos
    sucos_naturais = [
        "Laranja", "Abacaxi c/ Hortelã", "Limonada", "Maracujá",
        "Chá Matte da Casa",
    ]
    preco_suco = "R$ 12,90"
    extra_suco = "+2 frutas: R$ 2,00"

    refrigerantes = [
        {"nome": "Coca / Zero",       "preco": "R$ 6,50"},
        {"nome": "Fanta Laranja/Uva", "preco": "R$ 6,50"},
        {"nome": "Guaraná / Zero",    "preco": "R$ 6,50"},
    ]
    aguas = [
        {"nome": "Sem gás 500ml",  "preco": "R$ 3,00"},
        {"nome": "Com gás 500ml",  "preco": "R$ 4,00"},
        {"nome": "H2O Lemon 500ml","preco": "R$ 7,50"},
    ]

    # 4. Almoço Executivo
    almoco_executivo = [
        {"dia": "SEGUNDA", "prato": "Filé de Frango à Parmegiana",    "preco": "R$ 22,90"},
        {"dia": "TERÇA",   "prato": "Panqueca Carne/Frango c/ Queijo","preco": "R$ 22,90"},
        {"dia": "QUARTA",  "prato": "Strogonoff de Carne",            "preco": "R$ 22,90"},
        {"dia": "QUINTA",  "prato": "Costela com Mandioca Crocante",  "preco": "R$ 22,90"},
        {"dia": "SEXTA",   "prato": "Filé de Tilápia Grelhado",       "preco": "R$ 24,90"},
        {"dia": "SÁBADO",  "prato": "Feijoada Completa",              "preco": "R$ 49,90"},
        {"dia": "DOMINGO","prato": "Lasanha de Cupim ou Frango",     "preco": "R$ 29,90"},
    ]
    almoco_horario = "Seg a Sex 12h-15h | Sáb/Dom 12h-16h"
    almoco_acomp = "Todos acompanham arroz, feijão, salada e batata frita"

    # 5. Espetos na Brasa
    espetos = [
        {"nome": "Picanha",        "preco": "R$ 249,90"},
        {"nome": "Ancho",          "preco": "R$ 239,90"},
        {"nome": "Contrafilé",     "preco": "R$ 199,90"},
        {"nome": "Misto Carnes",   "preco": "R$ 189,90"},
        {"nome": "Diplomata",      "preco": "R$ 179,90"},
        {"nome": "Costela Suína",  "preco": "R$ 139,90"},
    ]
    espetos_acomp = "Acompanham arroz, farofa, batata e vinagrete"

    # 6. Sobremesas
    sobremesas = [
        {"nome": "Pudim Clássico",  "preco": "R$ 10,00"},
        {"nome": "Pudim Chantilly", "preco": "R$ 12,90"},
        {"nome": "Brigadeirão",     "preco": "R$ 10,00"},
        {"nome": "Petit Gateau",    "preco": "R$ 29,90"},
        {"nome": "Salada de Frutas","preco": "R$ 29,90"},
    ]
    sobremesas_obs = "Artesanais – peça 15 min antes"

    # Rodapé
    rodape = "CNPJ XX.XXX.XXX/0001‑XX • Proibida venda a menores • Área não‑fumante"

    context = {
        "sections": sections,
        "cervejas_artesanais": cervejas_artesanais,
        "caipirinhas": caipirinhas,
        "sabores_caipirinhas": sabores_caipirinhas,
        "extra_caip": extra_caip,
        "gin_tonica": gin_tonica,
        "combos_gin": combos_gin,
        "sucos_naturais": sucos_naturais,
        "preco_suco": preco_suco,
        "extra_suco": extra_suco,
        "refrigerantes": refrigerantes,
        "aguas": aguas,
        "almoco_executivo": almoco_executivo,
        "almoco_horario": almoco_horario,
        "almoco_acomp": almoco_acomp,
        "espetos": espetos,
        "espetos_acomp": espetos_acomp,
        "sobremesas": sobremesas,
        "sobremesas_obs": sobremesas_obs,
        "rodape": rodape,
    }
    return render(request, "core/menu.html", context)