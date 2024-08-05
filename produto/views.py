from io import BytesIO
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy

from django.db.models import Q
from django.http import HttpResponse

import pandas as pd

from openpyxl.styles import Font, PatternFill, Border, Side, Alignment, NamedStyle
from openpyxl.utils.dataframe import dataframe_to_rows

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
@login_required
def gerar_insights(request):
    try:
        # Obter todos os produtos
        df = pd.DataFrame(list(Produto.objects.all().values()))

        # Processar dados
        produtos_abaixo_estoque_minimo = df[df["estoque"] < df["estoque_minimo"]]
        df["valor_venda_pot"] = df["estoque"] * df["preco_venda"]
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
                # Estilo para cabeçalhos
                header_font = Font(bold=True, color="FFFFFF")
                header_fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
                
                # Definir largura das colunas
                column_widths = [max(len(str(cell.value)) for cell in col) for col in worksheet.columns]
                for i, width in enumerate(column_widths):
                    worksheet.column_dimensions[chr(65 + i)].width = width + 6  # Adiciona padding extra

                for cell in worksheet[1]:  # Cabeçalhos
                    cell.font = header_font
                    cell.fill = header_fill
                    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                
                # Estilo para linhas
                border_style = Border(
                    left=Side(border_style="thin"),
                    right=Side(border_style="thin"),
                    top=Side(border_style="thin"),
                    bottom=Side(border_style="thin"),
                )
                fill_odd = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")
                fill_even = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
                
                for row in worksheet.iter_rows(min_row=2):
                    for cell in row:
                        cell.border = border_style
                        if cell.row % 2 == 0:
                            cell.fill = fill_even
                        else:
                            cell.fill = fill_odd
                        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

            # Adicionar abas com os dados
            produtos_abaixo_estoque_minimo.to_excel(
                writer, sheet_name="Abaixo Estoque", index=False
            )
            df[["produto", "valor_venda_pot"]].to_excel(
                writer, sheet_name="Venda Potencial", index=False
            )
            produtos_preco_zero.to_excel(
                writer, sheet_name="Preço Zerado", index=False
            )
            produtos_estoque_excedente.to_excel(
                writer, sheet_name="Estoque Excedente", index=False
            )
            df[["produto", "rotatividade"]].to_excel(
                writer, sheet_name="Rotatividade", index=False
            )
            produtos_alto_custo_estoque.to_excel(
                writer, sheet_name="Custo Alto Estoque", index=False
            )

            # Adicionar aba com o valor total das vendas
            total_vendas_df = pd.DataFrame({"Total Vendas": [valor_total_vendas]})
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

    except Exception as e:
        return HttpResponse(f"Erro ao gerar insights: {str(e)}", status=500)


def import_csv(request):
    template_name = "import_csv.html"
    return render(request, template_name)



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
