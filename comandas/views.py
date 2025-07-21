from django.shortcuts import get_object_or_404, redirect, render
from decimal import Decimal 
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.http import require_POST
from .forms import AbrirComandaForm, EditTabForm, TabItemForm, CommentForm
from .models import Tab, TabItem, Comment

@login_required
def abrir_comanda(request):
    if request.method == "POST":
        form = AbrirComandaForm(request.POST)
        if form.is_valid():
            try:
                nova_comanda = form.save()
                messages.success(request, f"Nova comanda aberta para {nova_comanda.nome_cliente}.")
                return redirect("comandas:detalhes_tab", pk=nova_comanda.pk)
            except ValidationError as e:
                # Captura o erro de validação do modelo e exibe
                messages.error(request, ', '.join(e.messages))
        else:
             messages.error(request, "Ocorreu um erro. Verifique os dados.")
    else:
        form = AbrirComandaForm()
        
    context = {"form": form}
    return render(request, "comandas/abrir_comanda.html", context)

# MODIFICAÇÃO: A antiga 'listar_tabs' agora é o dashboard principal.
@login_required
def dashboard_comandas(request):
    """
    Exibe o dashboard com as comandas separadas por status:
    Ativas, Vazias (Disponíveis) e Fechadas (Histórico).
    """
    query = request.GET.get("q", "")
    
    # Base de consulta para busca
    base_query = Q()
    if query:
        base_query = Q(nome_cliente__icontains=query)

    # Filtra por status usando a base de consulta
    tabs_ativas = Tab.objects.filter(base_query, status='ATIVA').order_by("nome_cliente")
    tabs_vazias = Tab.objects.filter(base_query, status='VAZIA').order_by("nome_cliente")
    tabs_fechadas = Tab.objects.filter(base_query, status='FECHADA').order_by("-data_fechamento")[:50] # Limita o histórico

    context = {
        "tabs_ativas": tabs_ativas,
        "tabs_vazias": tabs_vazias,
        "tabs_fechadas": tabs_fechadas,
        "query": query,
        'titulo_pagina': 'Dashboard de Comandas'
    }
    return render(request, "comandas/dashboard_comandas.html", context)


@login_required
def detalhes_tab(request, pk):
    tab = get_object_or_404(Tab, pk=pk)
    
    # Instancia todos os formulários
    item_form = TabItemForm()
    edit_form = EditTabForm(instance=tab)
    comment_form = CommentForm()

    if request.method == "POST":
        # Verifica qual botão de submit foi pressionado
        if 'adicionar_item' in request.POST:
            item_form = TabItemForm(request.POST)
            if item_form.is_valid():
                produto = item_form.get_produto()
                quantidade = item_form.cleaned_data["quantidade"]
                
                TabItem.objects.create(
                    tab=tab,
                    produto=produto,
                    quantidade=quantidade,
                    preco_unitario=produto.preco_venda,
                    adicionado_por=request.user,
                )
                messages.success(request, f"{quantidade}x {produto.produto} adicionados.")
            else:
                messages.error(request, "Erro ao adicionar item: " + item_form.errors.as_text())
            return redirect("comandas:detalhes_tab", pk=tab.pk)

        elif 'atualizar_comanda' in request.POST:
            edit_form = EditTabForm(request.POST, instance=tab)
            if edit_form.is_valid():
                edit_form.save()
                messages.success(request, "Informações da comanda atualizadas.")
            return redirect("comandas:detalhes_tab", pk=tab.pk)

        elif 'adicionar_comentario' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                novo_comentario = comment_form.save(commit=False)
                novo_comentario.tab = tab
                novo_comentario.author = request.user
                novo_comentario.save()
                messages.success(request, "Anotação adicionada.")
            else:
                messages.error(request, "Erro ao adicionar anotação.")
            return redirect("comandas:detalhes_tab", pk=tab.pk)

    # Coleta de dados para o GET request
    itens_ordenados = tab.itens.order_by("-id")
    comentarios_ordenados = tab.comments.order_by("-created_at")

    context = {
        "tab": tab,
        "itens": itens_ordenados,
        "comentarios": comentarios_ordenados,
        "item_form": item_form,
        "edit_form": edit_form,
        "comment_form": comment_form,
    }
    return render(request, "comandas/detalhes_tab.html", context)
    
@login_required
@require_POST
def excluir_comentario(request, pk):
    comment = get_object_or_404(Comment, pk=pk)

    # Verifica se o autor do comentário é o usuário atual ou se é um superusuário
    if request.user == comment.author or request.user.is_superuser:
        comment.delete()
        messages.success(request, "Comentário excluído com sucesso.")
    else:
        messages.error(request, "Você não tem permissão para excluir este comentário.")

    return redirect("comandas:detalhes_tab", pk=comment.tab.pk)


@login_required
@require_POST
def atualizar_comentario(request, pk):
    comment = get_object_or_404(Comment, pk=pk)

    if request.user == comment.author or request.user.is_superuser:
        novo_conteudo = request.POST.get("content")

        if novo_conteudo:
            comment.content = novo_conteudo
            comment.save()
            messages.success(request, "Comentário atualizado com sucesso.")
        else:
            messages.error(request, "O conteúdo do comentário não pode ser vazio.")
    else:
        messages.error(
            request, "Você não tem permissão para atualizar este comentário."
        )

    return redirect("comandas:detalhes_tab", pk=comment.tab.pk)



@login_required
@require_POST
def fechar_tab(request, pk):
    tab = get_object_or_404(Tab, pk=pk)

    if tab.status == 'ATIVA':
        # 1️⃣ Primeira “fechada”: limpa a comanda (ATIVA → VAZIA)

        # Ajusta o estoque
        for item in tab.itens.all():
            prod = item.produto
            prod.estoque -= item.quantidade
            prod.save()

        # Remove itens e zera subtotal
        tab.itens.all().delete()
        tab.subtotal = Decimal('0.00')
        tab.status = 'VAZIA'
        tab.aberta = True
        tab.data_fechamento = None
        tab.save(update_fields=['subtotal','status','aberta','data_fechamento'])

        messages.success(request, f"Comanda “{tab.nome_cliente}” esvaziada e liberada (VAZIA).")
    
    elif tab.status == 'VAZIA':
        # 2️⃣ Segunda “fechada”: manda para histórico (VAZIA → FECHADA)
        tab.fechar()  # usa seu método de modelo, que seta status='FECHADA' e data_fechamento
        messages.success(request, f"Comanda “{tab.nome_cliente}” movida para o histórico (FECHADA).")

    else:
        messages.warning(request, "Esta comanda já está fechada.")
    
    return redirect('comandas:dashboard')


# MODIFICAÇÃO: Nova view para reabrir uma comanda
@login_required
@require_POST
def reabrir_tab(request, pk):
    tab = get_object_or_404(Tab, pk=pk, status='FECHADA')
    tab.reabrir()
    messages.success(request, f"Comanda de {tab.nome_cliente} foi reaberta.")
    return redirect("comandas:detalhes_tab", pk=pk)

# MODIFICAÇÃO: Simplificação das views de atualização/remoção de item
@login_required
@require_POST
def atualizar_quantidade_item(request, pk):
    item = get_object_or_404(TabItem, pk=pk)
    # ... (lógica de validação da quantidade) ...
    item.quantidade = nova_quantidade
    item.save()
    # A atualização do subtotal da tab é automática via signal.
    messages.success(request, "Quantidade atualizada.")
    return redirect("comandas:detalhes_tab", pk=item.tab.pk)

@login_required
@require_POST
def remover_item_comanda(request, pk):
    item = get_object_or_404(TabItem, pk=pk)
    # ... (lógica de permissão) ...
    tab_pk = item.tab.pk
    item.delete()
    # A atualização do subtotal da tab é automática via signal.
    messages.success(request, "Item removido.")
    return redirect("comandas:detalhes_tab", pk=tab_pk)
