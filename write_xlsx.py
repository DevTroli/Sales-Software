import openpyxl

def create_products_xlsx():
    # Criando um novo arquivo Excel
    workbook = openpyxl.Workbook()
    sheet = workbook.active  # Selecionando a primeira planilha

    # Escrevendo os cabeçalhos
    sheet.append([
        "produto",
        "preco_custo",
        "preco_venda",
        "margem_venda",
        "estoque",
        "estoque_minimo",
        "codigo_de_barra",
        "categoria"
    ])

    # Escrevendo os dados dos produtos
    for row in [
        ["GATORADE BLUE BERRY", 5.19, 6.5, 25.24, 14, 5, 7892840822019, "Energeticos"],
        ["GATORADE UVA", 5.19, 6.5, 25.24, 15, 6, 7892840808051, "Energeticos"],
        ["GATORADE LARANJA", 5.19, 6.5, 25.24, 16, 6, 7892840808020, "Energeticos"],
        ["GATORADE MORANGO & MARACUJÁ", 5.19, 6.5, 25.24, 17, 6, 7892840808174, "Energeticos"],
        ["GATORADE LIMÃO", 5.19, 6.5, 25.24, 18, 6, 7892840808037, "Energeticos"],
    ]:
        sheet.append(row)

    # Salvando o arquivo
    workbook.save("docs/test.xlsx")

create_products_xlsx()
