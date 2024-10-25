from datetime import timezone
from decimal import Decimal
import re
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from produto.models import Produto


def validar_telefone_brasileiro(telefone):
    """Valida se o número de telefone segue o padrão brasileiro com 11 dígitos e DDD."""
    padrao = re.compile(r"^\d{2}\d{9}$")
    if not padrao.match(telefone):
        raise ValidationError(
            "O número de telefone deve conter 11 dígitos, incluindo o DDD."
        )


class Tab(models.Model):
    nome_cliente = models.CharField("Nome do Cliente", max_length=100)
    telefone_cliente = models.CharField(
        "Telefone do Cliente",
        max_length=11,
        unique=True,
        validators=[validar_telefone_brasileiro],
    )
    produtos = models.ManyToManyField(Produto, through="TabItem")
    subtotal = models.DecimalField(
        "Subtotal", max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    aberta = models.BooleanField("Tab Aberta", default=True)
    data_criacao = models.DateTimeField(
        "Data de Criação", auto_now_add=True  # Define automaticamente a data ao criar
    )

    def __str__(self):
        return f"Tab {self.nome_cliente} - {self.telefone_cliente}"

    @classmethod
    def criar_ou_reutilizar_tab(cls, nome_cliente, telefone_cliente, produtos):
        """Reutiliza uma tab existente ou cria uma nova para o cliente."""
        tab, criada = cls.objects.get_or_create(
            telefone_cliente=telefone_cliente, defaults={"nome_cliente": nome_cliente}
        )
        if not criada:
            tab.nome_cliente = nome_cliente  # Atualiza o nome do cliente se necessário
        for produto in produtos:
            TabItem.objects.create(tab=tab, produto=produto)
        tab.atualizar_subtotal()
        return tab

    def atualizar_subtotal(self):
        """Atualiza o subtotal com base nos itens da tab."""
        self.subtotal = sum(item.subtotal() for item in self.itens.all())
        self.save()


class TabItem(models.Model):
    tab = models.ForeignKey(Tab, related_name="itens", on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=7, decimal_places=2)
    adicionado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    data_criacao = models.DateTimeField(
        "Data de Criação", auto_now_add=True  # Define automaticamente a data ao criar
    )

    def subtotal(self):
        return self.preco_unitario * self.quantidade

    def __str__(self):
        return f"{self.quantidade}x {self.produto.produto} - {self.tab.nome_cliente}"
