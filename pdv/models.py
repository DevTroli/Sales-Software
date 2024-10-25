from django.db import models
from decimal import Decimal
from django.utils import timezone
from produto.models import Produto


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
