from io import BytesIO
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy

from django.db.models import Q
from django.http import HttpResponse

import pandas as pd

from produto.models import Produto
from produto.forms import ProdutoForm


@login_required
def index(request):
    template_name = "index.html"

    query = request.GET.get("q")
    objects = Produto.objects.all()

    if query:
        queries = query.split()
        q_objects = Q()
        for q in queries:
            q_objects |= (
                Q(produto__icontains=q)
                | Q(codigoBarra__icontains=q)
                | Q(preco_venda__icontains=q)
            )
        objects = objects.filter(q_objects)

    context = {"object_list": objects}
    return render(request, template_name, context)


def product_detail(request, pk):
    template_name = "product_detail.html"
    obj = get_object_or_404(Produto, pk=pk)
    context = {"object": obj}
    return render(request, template_name, context)


@login_required
def product_add(request):
    template_name = "product_form.html"
    return render(request, template_name)


@login_required
def gerar_insights(request):
    # Obter todos os produtos
    df = pd.DataFrame(list(Produto.objects.all().values()))

    # Processar dados
    produtos_abaixo_estoque_minimo = df[df["estoque"] < df["estoque_minimo"]]
    df["valor_venda_potencial"] = df["estoque"] * df["preco_venda"]
    produtos_preco_zero = df[df["preco_venda"] == 0]
    produtos_estoque_excedente = df[df["estoque"] > df["estoque_minimo"] * 2]
    df["rotatividade"] = df["estoque"] / df["estoque_minimo"]
    df["custo_estoque"] = df["estoque"] * df["preco_custo"]
    produtos_alto_custo_estoque = df[df["custo_estoque"] > 1000]

    # Calcular o valor total das vendas
    valor_total_vendas = (df["estoque"] * df["preco_venda"]).sum()

    # Criar um buffer para o arquivo Excel
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:

        def style_worksheet(worksheet):
            for row in worksheet.iter_rows(
                min_row=2, max_col=worksheet.max_column, max_row=worksheet.max_row
            ):
                for cell in row:
                    if cell.row % 2 == 0:
                        cell.fill = PatternFill(
                            start_color="D9EAD3", end_color="D9EAD3", fill_type="solid"
                        )
                    else:
                        cell.fill = PatternFill(
                            start_color="FFFFFF", end_color="FFFFFF", fill_type="solid"
                        )
                    cell.border = Border(
                        left=Side(border_style="thin"),
                        right=Side(border_style="thin"),
                        top=Side(border_style="thin"),
                        bottom=Side(border_style="thin"),
                    )
                    cell.alignment = Alignment(horizontal="center", vertical="center")

        produtos_abaixo_estoque_minimo.to_excel(
            writer, sheet_name="Produtos Abaixo do Estoque Mínimo", index=False
        )
        df[["produto", "valor_venda_potencial"]].to_excel(
            writer, sheet_name="Valor Venda Potencial", index=False
        )
        produtos_preco_zero.to_excel(
            writer, sheet_name="Produtos Preço Zero", index=False
        )
        produtos_estoque_excedente.to_excel(
            writer, sheet_name="Produtos Estoque Excedente", index=False
        )
        df[["produto", "rotatividade"]].to_excel(
            writer, sheet_name="Rotatividade Estoque", index=False
        )
        produtos_alto_custo_estoque.to_excel(
            writer, sheet_name="Produtos Alto Custo Estoque", index=False
        )

        # Adicionar aba com o valor total das vendas
        total_vendas_df = pd.DataFrame({"Valor Total Vendas": [valor_total_vendas]})
        total_vendas_df.to_excel(writer, sheet_name="Total Vendas", index=False)

        # Aplicar formatação
        for sheet_name in writer.sheets:
            sheet = writer.sheets[sheet_name]
            style_worksheet(sheet)

    buffer.seek(0)

    # Criar a resposta para o download
    response = HttpResponse(
        buffer,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = 'attachment; filename="insights_estoque.xlsx"'

    return response


def import_csv(request):
    template_name = "import_csv.html"
    return render(request, template_name)


def dashboard(request):
    # Coleta de dados para o gráfico
    produtos = Produto.objects.all()
    vendas = [produto.valor_venda_potencial for produto in produtos]  # Exemplo de dados

    # Criação do gráfico
    fig, ax = plt.subplots()
    ax.plot(vendas, label="Vendas Potenciais")
    ax.set_title("Gráfico de Vendas Potenciais")
    ax.set_xlabel("Produto")
    ax.set_ylabel("Valor")

    # Convertendo o gráfico para imagem PNG
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    image_data = base64.b64encode(buf.getvalue()).decode("utf-8")
    buf.close()

    return render(request, "dashboard.html", {"graph": image_data})


class ProductCreate(LoginRequiredMixin, CreateView):
    model = Produto
    template_name = "product_form.html"
    form_class = ProdutoForm
    login_url = "/login"


class ProdutoUpdate(LoginRequiredMixin, UpdateView):
    model = Produto
    template_name = "product_form.html"
    form_class = ProdutoForm
    success_url = reverse_lazy("produto:index")
    login_url = "/login"
