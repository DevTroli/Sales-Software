from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse_lazy
from django.utils import timezone
from decimal import Decimal
from django.core.exceptions import ValidationError
import re


class Produto(models.Model):
    nivel_estoque = models.BooleanField("Nível do Estoque", default=False)
    produto = models.TextField("Produto", max_length=100, unique=True)
    preco_custo = models.DecimalField(
        "Preço de Custo", max_digits=7, decimal_places=2, default=Decimal("0.00")
    )
    preco_venda = models.DecimalField(
        "Preço de Venda", max_digits=7, decimal_places=2, default=Decimal("0.00")
    )
    margem_vendas = models.DecimalField(
        "Margem de Vendas", max_digits=6, decimal_places=2, blank=True, null=True
    )
    estoque = models.IntegerField("Estoque Atual")
    estoque_minimo = models.PositiveIntegerField("Estoque Mínimo", default=0)
    codigoBarra = models.CharField("Codigo de Barra", max_length=16, blank=True, null=True)
    categoria = models.ForeignKey(
        "Categoria", on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return self.produto

    def get_absolute_url(self):
        return reverse_lazy("produto:product_detail", kwargs={"pk": self.pk})

    # Função para atualizar o nível de estoque e calcular a margem de vendas
    def save(self, *args, **kwargs):
        # Atualizar o nível de estoque
        if self.estoque >= self.estoque_minimo and self.estoque > 0:
            self.nivel_estoque = True
        else:
            self.nivel_estoque = False

        # Calcular a margem de vendas
        if self.preco_custo > Decimal("0.00"):  # Evitar divisão por zero
            margem = (self.preco_venda / self.preco_custo - Decimal("1.00")) * Decimal(
                "100.00"
            )
            self.margem_vendas = margem
        else:
            self.margem_vendas = Decimal(
                "0.00"
            )  # Margem de vendas é 0 se o preço de custo for 0

        super().save(*args, **kwargs)

    def formatted_margem_vendas(self):
        if self.margem_vendas is not None:
            return f"{self.margem_vendas:.2f}%"
        return "0.00%"


class Meta:
    ordering = ("produto",)


class Categoria(models.Model):
    categoria = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ("categoria",)

    def __str__(self):
        return self.categoria


class Compra(models.Model):
    METODO_PAGAMENTO = [
        ("PIX", "PIX"),
        ("CREDITO", "Crédito"),
        ("DEBITO", "Débito"),
        ("DINHEIRO", "Dinheiro"),
    ]

    data = models.DateTimeField(default=timezone.now)
    metodo_pagamento = models.CharField(max_length=10, choices=METODO_PAGAMENTO)
    total = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )

    def __str__(self):
        return f"Compra {self.id} - {self.data.strftime('%d/%m/%Y %H:%M')}"


class ItemCompra(models.Model):
    compra = models.ForeignKey(Compra, related_name="itens", on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=7, decimal_places=2)

    def subtotal(self):
        return self.preco_unitario * self.quantidade

    def __str__(self):
        return f"{self.quantidade}x {self.produto.produto} - {self.compra.id}"


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
    data_criacao = models.DateTimeField("Data de Criação", default=timezone.now)

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

    def subtotal(self):
        return self.preco_unitario * self.quantidade

    def __str__(self):
        return f"{self.quantidade}x {self.produto.produto} - {self.tab.nome_cliente}"
