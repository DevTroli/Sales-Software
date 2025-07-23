from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from . import forms, services
from .models import SessaoCaixa


@login_required
def dashboard_caixa(request):
    sessao_aberta = SessaoCaixa.objects.get_sessao_aberta()

    context = {
        "sessao_aberta": sessao_aberta,
        "abertura_form": forms.AberturaCaixaForm(),
        "movimentacao_form": forms.MovimentacaoForm(),
        "fechamento_form": forms.FechamentoCaixaForm(),
    }

    if sessao_aberta:
        # Saldo atual
        context["saldo_atual"] = sessao_aberta.calcular_saldo_atual()

        # Todas as movimentações, da mais recente pra mais antiga
        movimentacoes = sessao_aberta.movimentacoes.order_by("-data_movimentacao")
        context["movimentacoes"] = movimentacoes

        # A última movimentação (mais recente)
        context["ultima_movimentacao"] = movimentacoes.first() if movimentacoes.exists() else None

    return render(request, "caixa/dashboard_caixa.html", context)



@login_required
def abrir_caixa(request):
    if request.method == "POST":
        form = forms.AberturaCaixaForm(request.POST)
        if form.is_valid():
            try:
                services.abrir_nova_sessao(
                    usuario=request.user,
                    valor_abertura=form.cleaned_data["valor_abertura"],
                )
                messages.success(request, "Caixa aberto com sucesso!")
            except ValueError as e:
                messages.error(request, str(e))
    return redirect("caixa:dashboard")


@login_required
def registrar_movimentacao_view(request, tipo):
    if request.method == "POST":
        form = forms.MovimentacaoForm(request.POST)
        sessao = SessaoCaixa.objects.get_sessao_aberta()
        if form.is_valid() and sessao:
            try:
                services.registrar_movimentacao(
                    sessao=sessao,
                    usuario=request.user,
                    tipo=tipo.upper(),
                    valor=form.cleaned_data["valor"],
                    descricao=form.cleaned_data["descricao"],
                )
                messages.success(
                    request, f"{tipo.capitalize()} registrada com sucesso."
                )
            except ValueError as e:
                messages.error(request, str(e))
    return redirect("caixa:dashboard")


@login_required
def fechar_caixa(request):
    if request.method == "POST":
        form = forms.FechamentoCaixaForm(request.POST)
        sessao = SessaoCaixa.objects.get_sessao_aberta()
        if form.is_valid() and sessao:
            services.fechar_sessao_atual(
                sessao=sessao,
                usuario_fechamento=request.user,
                valor_informado=form.cleaned_data["valor_fechamento_informado"],
            )
            messages.success(request, "Caixa fechado com sucesso.")
    return redirect("caixa:dashboard")


@login_required
def relatorio_caixa(request):
    form = forms.RelatorioCaixaForm(request.GET or None)
    dados_relatorio = {}

    if form.is_valid():
        dados_relatorio = services.gerar_dados_relatorio(
            data_inicio=form.cleaned_data.get("data_inicio"),
            data_fim=form.cleaned_data.get("data_fim"),
        )

    context = {
        "form": form,
        "movimentacoes": dados_relatorio.get("movimentacoes"),
        "sumario": dados_relatorio.get("sumario"),
    }
    return render(request, "caixa/relatorio_caixa.html", context)


@login_required
def exportar_relatorio_caixa(request):
    form = forms.RelatorioCaixaForm(request.GET or None)
    if form.is_valid():
        buffer = services.exportar_relatorio_excel(
            data_inicio=form.cleaned_data.get("data_inicio"),
            data_fim=form.cleaned_data.get("data_fim"),
        )

        response = HttpResponse(
            buffer,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        filename = f'relatorio_caixa_{timezone.now().strftime("%Y-%m-%d")}.xlsx'
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    messages.error(request, "Filtros inválidos para exportação.")
    return redirect("caixa:relatorio")
