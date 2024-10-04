from datetime import timedelta
from io import BytesIO
import os
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from decimal import Decimal, InvalidOperation
from django.core.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse, reverse_lazy

from django.db.models import Q, F
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from django.db import IntegrityError
from datetime import timedelta

from openpyxl import load_workbook
import pandas as pd

from openpyxl.styles import Font, PatternFill, Border, Side, Alignment, NamedStyle
from openpyxl.utils.dataframe import dataframe_to_rows

# from satcfe import BibliotecaSAT, ClienteSATLocal

from produto.models import Categoria, Produto, Compra, ItemCompra, TabItem, Tab
from produto.forms import (
    ProdutoForm,
    UploadFileForm,
    CompraForm,
    ItemCompraForm,
    TabItemForm,
    AbrirComandaForm,
    EditTabForm,
)


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
                | Q(categoria__categoria__icontains=q)
            )
        objects = objects.filter(q_objects)

    # Ordenação explícita antes da paginação
    objects = objects.order_by("produto")  # Substitua 'produto' pelo campo que desejar

    # Paginação
    paginator = Paginator(objects, 50)  # Mostra 40 produtos por página
    page_number = request.GET.get("page")
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


class ProductCreate(LoginRequiredMixin, CreateView):
    model = Produto
    template_name = "product_form.html"
    form_class = ProdutoForm
    login_url = "/login"

    def form_valid(self, form):
        response = super().form_valid(form)
        if not self.object.codigoBarra:
            # Atualiza o código de barras com o ID do produto gerado após o primeiro salvamento
            self.object.codigoBarra = str(self.object.pk)
            self.object.save(update_fields=["codigoBarra"])
        return response


class ProdutoUpdate(LoginRequiredMixin, UpdateView):
    model = Produto
    template_name = "product_form.html"
    form_class = ProdutoForm
    login_url = "/login"

    def get_success_url(self):
        # Redireciona para a página de detalhes do produto após a atualização
        return reverse("produto:product_detail", kwargs={"pk": self.object.pk})


def import_xlsx(file_path):
    """
    Importa planilhas xlsx.
    """
    workbook = load_workbook(file_path)
    sheet = workbook.active

    categorias = set()
    for row in sheet.iter_rows(min_row=2, values_only=True):
        categoria = row[8]
        if categoria:
            categorias.add(categoria)

    for categoria in categorias:
        Categoria.objects.get_or_create(categoria=categoria)

    for row in sheet.iter_rows(min_row=2, values_only=True):
        nivel_estoque = row[0]
        produto_nome = row[1]

        try:
            preco_custo = (
                Decimal(str(row[2]).replace(",", "."))
                if row[2] not in (None, "")
                else Decimal("0.00")
            )
            preco_venda = (
                Decimal(str(row[3]).replace(",", "."))
                if row[3] not in (None, "")
                else Decimal("0.00")
            )
            margem_venda = (
                Decimal(str(row[4]).replace(",", "."))
                if row[4] not in (None, "")
                else Decimal("0.00")
            )
        except (ValueError, InvalidOperation):
            preco_custo = Decimal("0.00")
            preco_venda = Decimal("0.00")
            margem_venda = Decimal("0.00")

        try:
            estoque = (
                int(row[5]) if row[5] not in (None, "") and str(row[5]).isdigit() else 0
            )
            estoque_minimo = (
                int(row[6]) if row[6] not in (None, "") and str(row[6]).isdigit() else 0
            )
        except ValueError:
            estoque = 0
            estoque_minimo = 0

        codigoBarra = row[7] if row[7] not in (None, "") else ""
        categoria_nome = row[8] if row[8] not in (None, "") else ""

        categoria = Categoria.objects.filter(categoria=categoria_nome).first()

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

        Produto.objects.update_or_create(produto=produto_nome, defaults=produto_data)


@login_required
@require_POST
def import_data(request):
    form = UploadFileForm(request.POST, request.FILES)
    if form.is_valid():
        file = request.FILES["file"]
        file_path = f"/tmp/{file.name}"
        with open(file_path, "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        try:
            import_xlsx(file_path)
            messages.success(request, "Dados importados com sucesso.")
        except Exception as e:
            messages.error(request, f"Erro ao importar dados: {str(e)}")
        os.remove(file_path)
        return redirect("produto:index")
    else:
        messages.error(request, "Erro ao fazer upload do arquivo.")
    return redirect("produto:upload")


@login_required
def upload_file(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            if file.name.endswith(".xlsx"):
                return redirect("produto:import_data")
            else:
                messages.error(
                    request, "O arquivo enviado não é um arquivo Excel válido."
                )
    else:
        form = UploadFileForm()
    return render(request, "upload.html", {"form": form})


@login_required
def gerar_insights(request):
    try:
        # Importar datetime no topo do arquivo, se ainda não estiver importado
        from datetime import datetime

        # Obter a data atual
        data_atual = datetime.now().strftime("%d-%m-%Y")

        # Obter todos os produtos
        df_produtos = pd.DataFrame(list(Produto.objects.all().values()))

        # Filtrar produtos onde preço de venda e estoque mínimo não estão zerados ou nulos
        df_produtos = df_produtos[
            (df_produtos["preco_venda"] > 0) & (df_produtos["estoque_minimo"] > 0)
        ]

        # Processar dados
        produtos_abaixo_estoque_minimo = df_produtos[
            df_produtos["estoque"] < df_produtos["estoque_minimo"]
        ]
        df_produtos["valor_venda_pot"] = (
            df_produtos["estoque"] * df_produtos["preco_venda"]
        )
        produtos_preco_zero = df_produtos[df_produtos["preco_venda"] == 0]
        produtos_estoque_excedente = df_produtos[
            df_produtos["estoque"] > df_produtos["estoque_minimo"] * 2
        ]
        df_produtos["rotatividade"] = (
            df_produtos["estoque"] / df_produtos["estoque_minimo"]
        )
        df_produtos["custo_estoque"] = (
            df_produtos["estoque"] * df_produtos["preco_custo"]
        )
        produtos_alto_custo_estoque = df_produtos[df_produtos["custo_estoque"] > 1000]

        # Obter todas as categorias e seus produtos
        categorias = Categoria.objects.all().prefetch_related('produto_set')

        # Calcular o valor total das vendas
        valor_total_vendas = (df_produtos["estoque"] * df_produtos["preco_venda"]).sum()

        # Obter todos os detalhes de pagamento
        df_compras = pd.DataFrame(
            list(Compra.objects.all().values("id", "data", "metodo_pagamento", "total"))
        )
        df_itens_compra = pd.DataFrame(
            list(
                ItemCompra.objects.all().values(
                    "compra_id", "produto_id", "quantidade", "preco_unitario"
                )
            )
        )

        # Obter o nome dos produtos
        df_itens_compra = df_itens_compra.merge(
            df_produtos[["id", "produto"]],
            left_on="produto_id",
            right_on="id",
            how="left",
        )

        # Converta datetimes para timezone naive e formate para o padrão brasileiro
        if not df_compras.empty:
            df_compras["data"] = pd.to_datetime(df_compras["data"]).dt.tz_localize(None)
            df_compras["data"] = df_compras["data"].dt.strftime("%d/%m/%Y %H:%M")

        # Adicionar detalhes de itens de compra
        df_compras_details = df_compras.merge(
            df_itens_compra, left_on="id", right_on="compra_id", how="left"
        )

        # Adicionar coluna de semana
        df_compras_details["semana"] = (
            df_compras_details["data"]
            .apply(lambda x: pd.to_datetime(x, format="%d/%m/%Y %H:%M"))
            .dt.to_period("W")
            .apply(lambda r: r.start_time.strftime("%d/%m/%Y %H:%M"))
        )

        # Agrupar por semana e somar os preços unitários
        df_totais_semanais = (
            df_compras_details.groupby("semana")["preco_unitario"].sum().reset_index()
        )
        df_totais_semanais.columns = ["Semana", "Total Preço Unitário"]

        # Criar um buffer para o arquivo Excel
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:

            def style_worksheet(worksheet):
                # Estilo para cabeçalhos
                header_font = Font(bold=True, color="FFFFFF")
                header_fill = PatternFill(
                    start_color="4F81BD", end_color="4F81BD", fill_type="solid"
                )

                # Definir largura das colunas
                column_widths = [
                    max(len(str(cell.value)) for cell in col)
                    for col in worksheet.columns
                ]
                for i, width in enumerate(column_widths):
                    worksheet.column_dimensions[chr(65 + i)].width = (
                        width + 6
                    )  # Adiciona padding extra

                for cell in worksheet[1]:  # Cabeçalhos
                    cell.font = header_font
                    cell.fill = header_fill
                    cell.alignment = Alignment(
                        horizontal="center", vertical="center", wrap_text=True
                    )

                # Estilo para linhas
                border_style = Border(
                    left=Side(border_style="thin"),
                    right=Side(border_style="thin"),
                    top=Side(border_style="thin"),
                    bottom=Side(border_style="thin"),
                )
                fill_odd = PatternFill(
                    start_color="F2F2F2", end_color="F2F2F2", fill_type="solid"
                )
                fill_even = PatternFill(
                    start_color="FFFFFF", end_color="FFFFFF", fill_type="solid"
                )

                for row in worksheet.iter_rows(min_row=2):
                    for cell in row:
                        cell.border = border_style
                        if cell.row % 2 == 0:
                            cell.fill = fill_even
                        else:
                            cell.fill = fill_odd
                        cell.alignment = Alignment(
                            horizontal="center", vertical="center", wrap_text=True
                        )

            # Adicionar abas com os dados
            produtos_abaixo_estoque_minimo.to_excel(
                writer, sheet_name="Abaixo Estoque", index=False
            )
            df_produtos[["produto", "valor_venda_pot"]].to_excel(
                writer, sheet_name="Venda Potencial", index=False
            )
            produtos_preco_zero.to_excel(writer, sheet_name="Preço Zerado", index=False)
            produtos_estoque_excedente.to_excel(
                writer, sheet_name="Estoque Excedente", index=False
            )
            df_produtos[["produto", "rotatividade"]].to_excel(
                writer, sheet_name="Rotatividade", index=False
            )
            produtos_alto_custo_estoque.to_excel(
                writer, sheet_name="Custo Alto Estoque", index=False
            )

            # Adicionar aba com o valor total das vendas
            total_vendas_df = pd.DataFrame({"Total Vendas": [valor_total_vendas]})
            total_vendas_df.to_excel(writer, sheet_name="Total Vendas", index=False)

            # Adicionar aba com os detalhes dos pagamentos
            df_compras_details[
                [
                    "data",
                    "metodo_pagamento",
                    "total",
                    "produto",
                    "quantidade",
                    "preco_unitario",
                ]
            ].to_excel(writer, sheet_name="Detalhes Pagamentos", index=False)

            # Adicionar aba com os totais semanais
            df_totais_semanais.to_excel(
                writer, sheet_name="Totais Semanais", index=False
            )

            # Nova aba: Produtos por Categoria (com validação)
            produtos_por_categoria = []
            for categoria in categorias:
                produtos = categoria.produto_set.filter(preco_venda__gt=0, estoque__gt=0)
                for produto in produtos:
                    produtos_por_categoria.append({
                        'Categoria': categoria.categoria,
                        'Produto': produto.produto,
                        'Preço de Custo': produto.preco_custo,
                        'Preço de Venda': produto.preco_venda,
                        'Margem de Venda': produto.margem_vendas,
                        'Estoque': produto.estoque,
                        'Estoque Mínimo': produto.estoque_minimo,
                        'Código de Barras': produto.codigoBarra,
                        'Nível de Estoque': produto.nivel_estoque
                    })
            
            df_produtos_por_categoria = pd.DataFrame(produtos_por_categoria)
            if not df_produtos_por_categoria.empty:
                df_produtos_por_categoria.to_excel(writer, sheet_name="Produtos por Categoria", index=False)
            else:
                # Se não houver produtos que atendam aos critérios, crie uma planilha vazia com uma mensagem
                pd.DataFrame({'Mensagem': ['Nenhum produto atende aos critérios de preço de venda > 0 e estoque > 0']}).to_excel(
                    writer, sheet_name="Produtos por Categoria", index=False)

            # Aplicar formatação
            for sheet_name in writer.sheets:
                sheet = writer.sheets[sheet_name]
                style_worksheet(sheet)

                # Adicionar rodapé com totais (se necessário)
                if sheet_name == "Detalhes Pagamentos":
                    # Adicionar uma linha de rodapé
                    last_row = sheet.max_row + 1
                    sheet[f"A{last_row}"] = "Total por Semana"
                    for col in range(2, sheet.max_column + 1):
                        sheet.cell(row=last_row, column=col).value = (
                            "=SUM({}:{})".format(
                                sheet.cell(row=2, column=col).coordinate,
                                sheet.cell(row=sheet.max_row, column=col).coordinate,
                            )
                        )

        buffer.seek(0)

        # Criar a resposta para o download
        response = HttpResponse(
            buffer,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = (
            f'attachment; filename="RELATORIO-GZH_{data_atual}.xlsx"'
        )

        return response

    except Exception as e:
        return HttpResponse(f"Erro ao gerar insights: {str(e)}", status=500)


@login_required
def pdv(request):
    if "nova_venda" not in request.session or request.session["nova_venda"]:
        request.session["itens"] = []
        request.session["subtotal"] = "0"
        request.session["nova_venda"] = False

    if request.method == "POST":
        item_form = ItemCompraForm(request.POST)
        compra_form = CompraForm(request.POST)

        if item_form.is_valid() and "add_item" in request.POST:
            produto = item_form.get_produto()
            quantidade = item_form.cleaned_data["quantidade"]

            if produto:
                if "itens" not in request.session:
                    request.session["itens"] = []
                itens = request.session["itens"]

                preco_unitario = produto.preco_venda
                subtotal_item = preco_unitario * quantidade

                itens.insert(
                    0,
                    {
                        "produto_id": produto.id,
                        "nome": produto.produto,
                        "quantidade": quantidade,
                        "preco_unitario": str(produto.preco_venda),
                        "subtotal_item": str(subtotal_item),
                    },
                )

                request.session["itens"] = itens

                subtotal = sum(
                    Decimal(item["preco_unitario"]) * item["quantidade"]
                    for item in itens
                )
                request.session["subtotal"] = str(subtotal)

                messages.success(
                    request, f"Produto {produto.produto} adicionado com sucesso."
                )
            else:
                messages.error(request, "Produto não encontrado.")

            return redirect("produto:pdv")

        elif compra_form.is_valid() and "finalizar_compra" in request.POST:
            metodo_pagamento = compra_form.cleaned_data["metodo_pagamento"]
            itens = request.session.get("itens", [])
            subtotal = request.session.get("subtotal", "0")

            compra = Compra.objects.create(
                metodo_pagamento=metodo_pagamento, total=subtotal
            )

            for item in itens:
                produto = Produto.objects.get(pk=item["produto_id"])
                if produto.estoque >= item["quantidade"]:
                    ItemCompra.objects.create(
                        compra=compra,
                        produto=produto,
                        quantidade=item["quantidade"],
                        preco_unitario=item["preco_unitario"],
                    )

                    produto.estoque -= item["quantidade"]
                    produto.save()
                else:
                    messages.error(
                        request,
                        f"Estoque insuficiente para o produto {produto.produto}.",
                    )
                    return redirect("produto:pdv")

            request.session["itens"] = []
            request.session["subtotal"] = "0"
            request.session["nova_venda"] = True

            messages.success(request, "Compra finalizada com sucesso.")
            return redirect("produto:purchase_details", pk=compra.pk)

    else:
        item_form = ItemCompraForm()
        compra_form = CompraForm()

    itens = request.session.get("itens", [])
    subtotal = Decimal(request.session.get("subtotal", "0.00"))

    context = {
        "item_form": item_form,
        "compra_form": compra_form,
        "itens": itens,
        "subtotal": subtotal,
    }
    return render(request, "pdv.html", context)


@login_required
def purchase_details(request, pk):
    compra = get_object_or_404(Compra, pk=pk)
    context = {"compra": compra, "itens": compra.itens.all()}
    return render(request, "purchase_details.html", context)


@login_required
@require_POST
def remove_item(request):
    produto_id = request.POST.get("produto_id")

    # Remover o item da sessão
    if "itens" in request.session:
        itens = request.session["itens"]
        request.session["itens"] = [
            item for item in itens if item["produto_id"] != int(produto_id)
        ]

        # Atualizar subtotal
        subtotal = sum(
            Decimal(item["preco_unitario"]) * item["quantidade"]
            for item in request.session["itens"]
        )
        request.session["subtotal"] = str(subtotal)

    return redirect("produto:pdv")


@login_required
@require_POST
def clear_checkout(request):
    # Limpa todos os itens e o subtotal da sessão
    request.session.pop("itens", None)
    request.session.pop("subtotal", None)

    messages.success(request, "Todos os itens foram removidos do checkout.")
    return redirect("produto:pdv")


@login_required
def detalhes_pagamentos(request):
    # Obter o momento atual
    now = timezone.now()

    # Calcular o início das últimas 24 horas
    start_of_day = now - timedelta(days=1)

    # Filtrar as compras das últimas 24 horas
    compras = Compra.objects.filter(data__range=[start_of_day, now]).prefetch_related(
        "itens__produto"
    )

    # Paginação, mostra 10 compras por página
    paginator = Paginator(compras, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"page_obj": page_obj}
    return render(request, "detalhes_pagamentos.html", context)


@login_required
def abrir_comanda(request):
    form = AbrirComandaForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        nome_cliente = form.cleaned_data.get("nome_cliente")
        telefone_cliente = form.cleaned_data.get("telefone_cliente")

        tab_existente = None

        # Verifica se existe uma comanda aberta para o telefone ou nome do cliente
        if nome_cliente:
            tab_existente = Tab.objects.filter(
                nome_cliente=nome_cliente, aberta=True
            ).first()

        if not tab_existente and telefone_cliente:
            tab_existente = Tab.objects.filter(
                telefone_cliente=telefone_cliente, aberta=True
            ).first()

        if tab_existente:
            messages.warning(
                request,
                f"Já existe uma comanda aberta para o cliente {tab_existente.nome_cliente}.",
            )
            return redirect("produto:detalhes_tab", pk=tab_existente.pk)

        # Criação de nova comanda
        try:
            tab_nova = Tab.objects.create(
                telefone_cliente=telefone_cliente,
                nome_cliente=nome_cliente,
                aberta=True,
            )
            messages.success(
                request, f"Nova comanda aberta para {tab_nova.nome_cliente}."
            )
            return redirect("produto:detalhes_tab", pk=tab_nova.pk)
        except IntegrityError:
            messages.error(
                request,
                "Erro ao tentar abrir a comanda. Por favor, verifique os dados e tente novamente.",
            )

    context = {"form": form}
    return render(request, "abrir_comanda.html", context)


@login_required
def listar_tabs(request):
    query = request.GET.get("q", "")
    if query:
        tabs = (
            Tab.objects.filter(
                Q(nome_cliente__icontains=query) | Q(telefone_cliente__icontains=query)
            )
            .filter(aberta=True)
            .order_by("-data_criacao")
        )
    else:
        tabs = Tab.objects.filter(aberta=True).order_by("-data_criacao")

    context = {"tabs": tabs, "query": query}
    return render(request, "listar_tabs.html", context)


@require_POST
def excluir_comanda(request, pk):
    comanda = get_object_or_404(Tab, pk=pk)

    # Verifica se o usuário é superusuário
    if not request.user.is_superuser:
        # Exibe a mensagem de erro para usuários que não são superusuários
        messages.error(
            request,
            "Você não pode remover a comanda. Apenas ADMs podem realizar esta ação.",
        )
        return redirect("produto:detalhes_tab", pk=comanda.pk)

    try:
        comanda.delete()
        messages.success(request, "Comanda excluída com sucesso.")
    except Exception as e:
        messages.error(request, f"Erro ao excluir comanda: {e}")

    return redirect("produto:listar_tabs")


@login_required
def detalhes_tab(request, pk):
    tab = get_object_or_404(Tab, pk=pk)
    item_form = TabItemForm(request.POST or None)
    edit_form = EditTabForm(request.POST or None, instance=tab)

    if request.method == "POST":
        if item_form.is_valid():
            produto = item_form.get_produto()
            quantidade = item_form.cleaned_data["quantidade"]

            if produto:
                TabItem.objects.create(
                    tab=tab,
                    produto=produto,
                    quantidade=quantidade,
                    preco_unitario=produto.preco_venda,
                    adicionado_por=request.user,
                )

                tab.subtotal += quantidade * produto.preco_venda
                tab.save()

                if "itens" not in request.session:
                    request.session["itens"] = []

                itens = request.session["itens"]

                # Insere o novo item no topo da lista
                itens.insert(
                    0,
                    {
                        "produto_id": produto.id,
                        "nome": produto.produto,
                        "quantidade": quantidade,
                        "preco_unitario": str(produto.preco_venda),
                    },
                )
                request.session["itens"] = itens

                messages.success(
                    request,
                    f"{quantidade}x {produto.produto} adicionados à tab de {tab.nome_cliente}.",
                )
            else:
                messages.error(request, "Produto não encontrado.")

            return redirect("produto:detalhes_tab", pk=tab.pk)

        if edit_form.is_valid():
            edit_form.save()
            messages.success(request, "Comanda atualizada com sucesso.")
            return redirect("produto:detalhes_tab", pk=tab.pk)

    # Ordena os itens da Tab pelo campo de criação (exibindo os mais recentes primeiro)
    itens_ordenados = tab.itens.order_by("-id")

    context = {
        "tab": tab,
        "itens": itens_ordenados,
        "item_form": item_form,
        "edit_form": edit_form,
    }
    return render(request, "detalhes_tab.html", context)


@login_required
def fechar_tab(request, pk):
    tab = get_object_or_404(Tab, pk=pk)
    compra = Compra.objects.create(metodo_pagamento="DINHEIRO")  # Inicializa uma compra

    # Transferindo os itens da comanda para o checkout (PDV)
    for item in tab.itens.all():
        ItemCompra.objects.create(
            compra=compra,
            produto=item.produto,
            quantidade=item.quantidade,
            preco_unitario=item.preco_unitario,
        )
        # Atualiza o subtotal da compra
        compra.total += item.subtotal()
        # Opcional: ajustar o estoque do produto aqui, se necessário
        item.produto.estoque -= item.quantidade
        item.produto.save()

    compra.save()  # Salva a compra com o total atualizado

    # Remove todos os itens da comanda
    tab.itens.all().delete()

    # Zera o subtotal da comanda
    tab.subtotal = Decimal("0.00")
    tab.save()

    messages.success(
        request,
        f"Produtos da comanda de {tab.nome_cliente} transferidos para o checkout. Comanda ainda aberta.",
    )
    return redirect("produto:pdv")


@login_required
@require_POST
def atualizar_quantidade_item(request, pk):
    item = get_object_or_404(TabItem, pk=pk)
    nova_quantidade = request.POST.get("nova_quantidade")

    try:
        nova_quantidade = int(nova_quantidade)
        if nova_quantidade < 1:
            raise ValueError("Quantidade deve ser maior que zero.")

        item.quantidade = nova_quantidade
        item.save()

        tab = item.tab
        tab.subtotal = sum(
            item.quantidade * item.produto.preco_venda for item in tab.itens.all()
        )
        tab.save()

        messages.success(request, "Quantidade atualizada com sucesso.")
    except ValueError as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, f"Erro ao atualizar quantidade: {e}")

    return redirect("produto:detalhes_tab", pk=item.tab.pk)


@login_required
@require_POST
def remover_item_comanda(request, pk):
    item = get_object_or_404(TabItem, pk=pk)

    if not request.user.is_superuser:
        # Exibe a mensagem de erro para usuários que não são superusuários
        messages.error(
            request,
            "Você não pode remover itens da comanda. Apenas ADMs podem realizar esta ação.",
        )
        return redirect("produto:detalhes_tab", pk=item.tab.pk)

    try:
        tab = item.tab
        item.delete()

        # Recalcula o subtotal da tab após a remoção do item
        tab.subtotal = sum(
            item.quantidade * item.produto.preco_venda for item in tab.itens.all()
        )
        tab.save()

        messages.success(request, "Item removido com sucesso.")
    except Exception as e:
        messages.error(request, f"Erro ao remover item: {e}")

    return redirect("produto:detalhes_tab", pk=tab.pk)


# @login_required
# def configurar_cliente_sat():
#     # Configurar o caminho da DLL
#     biblioteca = BibliotecaSAT(settings.SAT_DLL_PATH)

#     # Código de ativação fornecido pelo fabricante
#     codigo_ativacao = '12345678'  # Substitua pelo código real

#     # Criar o cliente SAT
#     cliente = ClienteSATLocal(biblioteca, codigo_ativacao=codigo_ativacao)
#     return cliente

# def emitir_nota_fiscal(request):
#     try:
#         # Configurar o cliente SAT
#         cliente = configurar_cliente_sat()

#         # Consultar o SAT
#         resposta = cliente.consultar_sat()
#         if resposta.codigo == 0:  # Verifica se o código de resposta indica sucesso
#             messages.success(request, 'SAT está em operação: ' + resposta.mensagem)
#         else:
#             messages.error(request, f"Falha ao consultar o SAT: {resposta.mensagem}")

#     except FileNotFoundError as e:
#         messages.error(request, str(e))
#     except Exception as e:
#         messages.error(request, f"Erro inesperado: {str(e)}")

#     return render(request, 'purchase_details.html')
