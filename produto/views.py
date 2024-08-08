from decimal import Decimal
from io import BytesIO
import os
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse, reverse_lazy

from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.contrib import messages

from openpyxl import load_workbook
import pandas as pd

from openpyxl.styles import Font, PatternFill, Border, Side, Alignment, NamedStyle
from openpyxl.utils.dataframe import dataframe_to_rows
import xlrd

from produto.models import Categoria, Produto
from produto.forms import ProdutoForm, UploadFileForm


@login_required
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

    # Paginação
    paginator = Paginator(objects, 40)  # Mostra 10 produtos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {"page_obj": page_obj}
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

def import_xlsx(filename):
    '''
    Importa planilhas xlsx.
    '''
    workbook = load_workbook(filename)
    sheet = workbook.active

    categorias = []
    for row in sheet.iter_rows(min_row=2, values_only=True):
        categoria = row[8]  # Corrigido para refletir a coluna correta
        if categoria:
            categorias.append(categoria)

    for categoria in set(categorias):
        Categoria.objects.get_or_create(categoria=categoria)

    for row in sheet.iter_rows(min_row=2, values_only=True):
        nivel_estoque = row[0]
        produto_nome = row[1]
        preco_custo = Decimal(row[2])
        preco_venda = Decimal(row[3])
        margem_venda = Decimal(row[4])
        estoque = int(row[5])
        estoque_minimo = int(row[6])
        codigoBarra = row[7]
        categoria_nome = row[8]

        try:
            categoria = Categoria.objects.get(categoria=categoria_nome)
        except Categoria.DoesNotExist:
            categoria = None

        produto_data = {
            "nivel_estoque": nivel_estoque,
            "preco_custo": preco_custo,
            "preco_venda": preco_venda,
            "margem_vendas": margem_venda,
            "estoque": estoque,
            "estoque_minimo": estoque_minimo,
            "codigoBarra": codigoBarra,
            "categoria": categoria,
        }

        Produto.objects.update_or_create(
            produto=produto_nome,
            defaults=produto_data
        )


@login_required
@require_POST
def import_data(request):
    form = UploadFileForm(request.POST, request.FILES)
    if form.is_valid():
        file = request.FILES['file']
        # Salvar o arquivo no sistema de arquivos temporariamente
        file_path = f'/tmp/{file.name}'
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        try:
            import_xlsx(file_path)
            messages.success(request, "Dados importados com sucesso.")
        except Exception as e:
            messages.error(request, f"Erro ao importar dados: {str(e)}")
        # Remover o arquivo após o processamento
        os.remove(file_path)
        return redirect('produto:index')
    else:
        messages.error(request, "Erro ao fazer upload do arquivo.")
    return redirect('produto:upload')


@login_required
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            
            # Verifique o tipo de arquivo e manipule-o
            if file.name.endswith('.xlsx'):
                # Processar arquivo Excel (exemplo básico)
                df = pd.read_excel(file)
                # Aqui você pode fazer o que precisa com o DataFrame
                # Exemplo: salvar dados no banco de dados
                return HttpResponse("Arquivo Excel processado com sucesso!")
            else:
                return HttpResponse("O arquivo enviado não é um arquivo Excel válido.")
    else:
        form = UploadFileForm()

    return render(request, 'upload.html', {'form': form})

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
