from decimal import Decimal
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.http import require_POST


from comandas.forms import AbrirComandaForm, EditTabForm, TabItemForm
from comandas.models import Tab, TabItem
from pdv.models import Compra, ItemCompra


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
            return redirect("comandas:detalhes_tab", pk=tab_existente.pk)

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
            return redirect("comandas:detalhes_tab", pk=tab_nova.pk)
        except IntegrityError:
            messages.error(
                request,
                "Erro ao tentar abrir a comanda. Por favor, verifique os dados e tente novamente.",
            )

    context = {"form": form}
    return render(request, "comandas/abrir_comanda.html", context)


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
    return render(request, "comandas/listar_tabs.html", context)


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
        return redirect("comandas:detalhes_tab", pk=comanda.pk)

    try:
        comanda.delete()
        messages.success(request, "Comanda excluída com sucesso.")
    except Exception as e:
        messages.error(request, f"Erro ao excluir comanda: {e}")

    return redirect("comandas:listar_tabs")


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

            return redirect("comandas:detalhes_tab", pk=tab.pk)

        if edit_form.is_valid():
            edit_form.save()
            messages.success(request, "Comanda atualizada com sucesso.")
            return redirect("comandas:detalhes_tab", pk=tab.pk)

    # Ordena os itens da Tab pelo campo de criação (exibindo os mais recentes primeiro)
    itens_ordenados = tab.itens.order_by("-id")

    context = {
        "tab": tab,
        "itens": itens_ordenados,
        "item_form": item_form,
        "edit_form": edit_form,
    }
    return render(request, "comandas/detalhes_tab.html", context)


@login_required
def fechar_tab(request, pk):
    tab = get_object_or_404(Tab, pk=pk)

    # Atualiza o estoque e remove itens da comanda
    for item in tab.itens.all():
        # Ajusta o estoque do produto conforme a quantidade na comanda
        item.produto.estoque -= item.quantidade
        item.produto.save()

    # Remove todos os itens da comanda
    tab.itens.all().delete()

    # Zera o subtotal da comanda
    tab.subtotal = Decimal("0.00")
    tab.aberta = True
    tab.save()

    messages.success(
        request,
        f"Comanda de {tab.nome_cliente} fechada com sucesso. Estoque ajustado e itens removidos.",
    )
    return redirect("comandas:listar_tabs")


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

    return redirect("comandas:detalhes_tab", pk=item.tab.pk)


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
        return redirect("comandas:detalhes_tab", pk=item.tab.pk)

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

    return redirect("comandas:detalhes_tab", pk=tab.pk)
