import csv
import random


# Função para gerar código de barra aleatório
def generate_barcode():
    return random.randint(10000000, 99999999)


with open("docs/produtosAdega.csv", "w") as f:
    csv_writer = csv.writer(f)
    csv_writer.writerow(
        [
            "produto",
            "preco_custo",
            "preco_venda",
            "margem_venda",
            "estoque",
            "estoque_minimo",
            "codigo_de_barra",
        ]
    )

    rows = [
        ["VODKA CIROC 750ML", 129.00, 215.00, 66.10, 50, 1, 88076161863]
        # Seguir exemplos acima para escrever documento csv
    ]

    csv_writer.writerows(rows)
