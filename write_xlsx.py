import openpyxl

def create_products_xlsx():
    # Criando um novo arquivo Excel
    workbook = openpyxl.Workbook()
    sheet = workbook.active  # Selecionando a primeira planilha

    # Escrevendo os cabeçalhos
    sheet.append([
        "nivel_estoque",
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
        [True, "RED BULL MELANCIA 250ML", 7,29, 11,90, 63,24, 16, 12, "7892840822019", "Energeticos"],
        [True, "GRED BULL TROPICAL 250ML", 7,29, 11,90, 63,24, 24, 12, "7892840808051", "Energeticos"],
        [True, "RED BULL MORANGO & PÊSSEGO 250ML", 7,29, 11,90, 63,24, 21, 12, "7892840808020", "Energeticos"],
        [True, "RED BULL PITAYA 250ML", 7,29, 11,90, 63,24, 16, 12, "7892840808174", "Energeticos"],
        [False, "RED BULL SUGAR FREE 250ML", 7,29, 11,90, 63,24, 8, 8, "7892840808037", "Energeticos"],
        [False, "RED BULL TRADICIONAL 250ML", 6,89, 10,00, 45,14, 16, 24, "7892840808037", "Energeticos"],
    ]:
        sheet.append(row)

    # Salvando o arquivo
    workbook.save("docs/produtostest.xlsx")

create_products_xlsx()
