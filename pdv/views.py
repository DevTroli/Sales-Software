from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from caixa.decorators import caixa_aberto_required
from caixa.services import registrar_venda_caixa

from produto.models import Produto

# Forms e Models do próprio app
from .forms import CompraForm, ItemCompraForm
from .models import Compra, ItemCompra


# ✅ A VIEW `pdv` agora é protegida pelo decorator. Nenhuma venda ocorre se o caixa estiver fechado.
@login_required
@caixa_aberto_required
def pdv(request):
    # A lógica de iniciar uma nova venda na sessão permanece a mesma
    if "nova_venda" not in request.session or request.session["nova_venda"]:
        request.session["pdv_itens"] = []
        request.session["pdv_subtotal"] = "0"
        request.session["nova_venda"] = False

    if request.method == "POST":
        item_form = ItemCompraForm(request.POST)
        compra_form = CompraForm(request.POST)

        # A lógica de adicionar item na sessão não muda
        if item_form.is_valid() and "add_item" in request.POST:
            produto = item_form.get_produto()
            quantidade = item_form.cleaned_data["quantidade"]

            if produto:
                itens = request.session.get("pdv_itens", [])
                itens.insert(
                    0,
                    {
                        "produto_id": produto.id,
                        "nome": produto.produto,
                        "quantidade": quantidade,
                        "preco_unitario": str(produto.preco_venda),
                        "subtotal_item": str(produto.preco_venda * quantidade),
                    },
                )
                request.session["pdv_itens"] = itens

                subtotal = sum(
                    Decimal(item["preco_unitario"]) * item["quantidade"]
                    for item in itens
                )
                request.session["pdv_subtotal"] = str(subtotal)
                messages.success(request, f"Produto {produto.produto} adicionado.")
            else:
                messages.error(request, "Produto não encontrado.")
            return redirect("pdv:pdv")

        # ✅ A lógica de finalizar a compra agora é mais limpa e integrada
        elif compra_form.is_valid() and "finalizar_compra" in request.POST:
            metodo_pagamento = compra_form.cleaned_data["metodo_pagamento"]
            itens = request.session.get("pdv_itens", [])
            subtotal = request.session.get("pdv_subtotal", "0")

            if not itens:
                messages.error(request, "Adicione itens antes de finalizar a venda.")
                return redirect("pdv:pdv")

            compra = Compra.objects.create(
                metodo_pagamento=metodo_pagamento, total=subtotal
            )

            for item_data in itens:
                produto = Produto.objects.get(pk=item_data["produto_id"])
                if produto.estoque >= item_data["quantidade"]:
                    ItemCompra.objects.create(
                        compra=compra,
                        produto=produto,
                        quantidade=item_data["quantidade"],
                        preco_unitario=item_data["preco_unitario"],
                    )
                    produto.estoque -= item_data["quantidade"]
                    produto.save()
                else:
                    messages.error(
                        request, f"Estoque insuficiente para {produto.produto}."
                    )
                    compra.delete()  # Reverte a compra se um item falhar
                    return redirect("pdv:pdv")

            # ✅ DX MELHORADO: Chamada única para o service de caixa.
            # A lógica complexa (verificar se é dinheiro, encontrar sessão, criar movimentação)
            # está encapsulada no service, deixando a view limpa.
            try:
                registrar_venda_caixa(usuario=request.user, compra=compra)
            except Exception as e:
                # A venda foi um sucesso, mas o registro no caixa falhou.
                # Informamos o usuário sem bloquear o fluxo principal.
                messages.warning(
                    request,
                    f"Atenção: A venda foi concluída, mas houve um erro ao registrá-la no caixa: {e}",
                )

            # Limpa a sessão para a próxima venda
            request.session["nova_venda"] = True
            messages.success(request, "Venda finalizada com sucesso.")
            return redirect("pdv:purchase_details", pk=compra.pk)
    else:
        item_form = ItemCompraForm()
        compra_form = CompraForm()

    itens = request.session.get("pdv_itens", [])
    subtotal = Decimal(request.session.get("pdv_subtotal", "0.00"))

    context = {
        "item_form": item_form,
        "compra_form": compra_form,
        "itens": itens,
        "subtotal": subtotal,
    }
    return render(request, "pdv/pdv.html", context)


# As views abaixo não precisam de alteração
@login_required
def purchase_details(request, pk):
    compra = get_object_or_404(Compra, pk=pk)
    context = {"compra": compra, "itens": compra.itens.all()}
    return render(request, "pdv/purchase_details.html", context)


@login_required
@require_POST
def remove_item(request):
    produto_id = request.POST.get("produto_id")
    if "pdv_itens" in request.session:
        itens = request.session["pdv_itens"]
        request.session["pdv_itens"] = [
            item for item in itens if item["produto_id"] != int(produto_id)
        ]
        subtotal = sum(
            Decimal(item["preco_unitario"]) * item["quantidade"]
            for item in request.session["pdv_itens"]
        )
        request.session["pdv_subtotal"] = str(subtotal)
    return redirect("pdv:pdv")


@login_required
@require_POST
def clear_checkout(request):
    request.session.pop("pdv_itens", None)
    request.session.pop("pdv_subtotal", None)
    messages.info(request, "Itens removidos do checkout.")
    return redirect("pdv:pdv")
