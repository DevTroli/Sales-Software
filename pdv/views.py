from datetime import timedelta, timezone
from decimal import Decimal
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from pdv.forms import CompraForm, ItemCompraForm
from pdv.models import Compra, ItemCompra
from produto.models import Produto


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
                itens = request.session.get("itens", [])

                preco_unitario = produto.preco_venda
                subtotal_item = preco_unitario * quantidade

                itens.insert(
                    0,
                    {
                        "produto_id": produto.id,
                        "nome": produto.produto,
                        "quantidade": quantidade,
                        "preco_unitario": str(preco_unitario),
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

            return redirect("pdv:pdv")

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
                    return redirect("pdv:pdv")

            # Limpa os dados da sessão para nova venda
            request.session["itens"] = []
            request.session["subtotal"] = "0"
            request.session["nova_venda"] = True

            messages.success(request, "Compra finalizada com sucesso.")
            return redirect("pdv:purchase_details", pk=compra.pk)

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
    return render(request, "pdv/pdv.html", context)


@login_required
def purchase_details(request, pk):
    compra = get_object_or_404(Compra, pk=pk)
    context = {"compra": compra, "itens": compra.itens.all()}
    return render(request, "pdv/purchase_details.html", context)


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

    return redirect("pdv:pdv")


@login_required
@require_POST
def clear_checkout(request):
    # Limpa todos os itens e o subtotal da sessão
    request.session.pop("itens", None)
    request.session.pop("subtotal", None)

    messages.success(request, "Todos os itens foram removidos do checkout.")
    return redirect("pdv:pdv")
