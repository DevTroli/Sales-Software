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

    ]:
        sheet.append(row)

    # Salvando o arquivo
    workbook.save("docs/produtostest.xlsx")

create_products_xlsx()
