from datetime import datetime, time
from django.db.models import Sum, Count
from decimal import Decimal
from io import BytesIO

import pandas as pd
from django.utils import timezone
from openpyxl.styles import Alignment, Font, PatternFill

from django.db import models
from .models import MovimentacaoCaixa, SessaoCaixa


def abrir_nova_sessao(usuario, valor_abertura):
    """Cria uma nova sessão de caixa e a movimentação de abertura."""
    if SessaoCaixa.objects.get_sessao_aberta():
        raise ValueError("Já existe um caixa aberto.")

    sessao = SessaoCaixa.objects.create(
        usuario_abertura=usuario, valor_abertura=valor_abertura
    )
    MovimentacaoCaixa.objects.create(
        sessao=sessao,
        usuario=usuario,
        tipo="ABERTURA",
        valor=valor_abertura,
        descricao="Abertura de caixa inicial",
    )
    return sessao


def registrar_movimentacao(sessao, usuario, tipo, valor, descricao=""):
    """Registra uma nova movimentação (Sangria ou Suprimento)."""
    if tipo == "SANGRIA":
        saldo_atual = sessao.calcular_saldo_atual()
        if valor > saldo_atual:
            raise ValueError(
                f"Valor da sangria (R$ {valor}) excede o saldo em caixa (R$ {saldo_atual})."
            )

    return MovimentacaoCaixa.objects.create(
        sessao=sessao, usuario=usuario, tipo=tipo, valor=valor, descricao=descricao
    )


def registrar_venda_caixa(usuario, compra):
    """Registra uma venda em dinheiro no caixa aberto."""
    sessao_aberta = SessaoCaixa.objects.get_sessao_aberta()
    if sessao_aberta and compra.metodo_pagamento == "DINHEIRO":
        MovimentacaoCaixa.objects.create(
            sessao=sessao_aberta,
            usuario=usuario,
            tipo="VENDA",
            valor=compra.total,
            descricao=f"Venda PDV #{compra.id}",
        )


def fechar_sessao_atual(sessao, usuario_fechamento, valor_informado):
    """Fecha a sessão de caixa, calcula totais e salva a diferença."""
    valor_calculado = sessao.calcular_saldo_atual()
    diferenca = valor_informado - valor_calculado

    sessao.usuario_fechamento = usuario_fechamento
    sessao.valor_fechamento_calculado = valor_calculado
    sessao.valor_fechamento_informado = valor_informado
    sessao.diferenca = diferenca
    sessao.status = "FECHADO"
    sessao.data_fechamento = timezone.now()
    sessao.save()
    return sessao


def gerar_dados_relatorio(data_inicio=None, data_fim=None):
    movimentacoes = MovimentacaoCaixa.objects.select_related("usuario", "sessao").all()

    if data_inicio:
        movimentacoes = movimentacoes.filter(
            data_movimentacao__gte=datetime.combine(data_inicio, time.min)
        )
    if data_fim:
        movimentacoes = movimentacoes.filter(
            data_movimentacao__lte=datetime.combine(data_fim, time.max)
        )

    sumario = (
        movimentacoes.values("tipo")
        .annotate(total=Sum("valor"), quantidade=Count("id"))
        .order_by("tipo")
    )

    return {"movimentacoes": movimentacoes, "sumario": sumario}


def exportar_relatorio_excel(data_inicio=None, data_fim=None):
    dados = gerar_dados_relatorio(data_inicio, data_fim)
    movimentacoes = dados["movimentacoes"]

    dados_para_df = [
        {
            "Data": mov.data_movimentacao.strftime("%d/%m/%Y %H:%M"),
            "Tipo": mov.get_tipo_display(),
            "Valor (R$)": mov.valor,
            "Descrição": mov.descricao,
            "Usuário": mov.usuario.username,
            "ID Sessão": mov.sessao.id,
        }
        for mov in movimentacoes
    ]

    df = pd.DataFrame(dados_para_df)

    sumario_df = (
        df.groupby("Tipo")["Valor (R$)"]
        .agg(["sum", "count"])
        .reset_index()
        .rename(columns={"sum": "Valor Total", "count": "Quantidade"})
    )

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Movimentações Detalhadas", index=False)
        sumario_df.to_excel(writer, sheet_name="Sumário por Operação", index=False)
        # Você pode adicionar sua função de estilo `style_worksheet` aqui

    buffer.seek(0)
    return buffer
