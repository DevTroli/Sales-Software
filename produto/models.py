from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse_lazy
from decimal import Decimal


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
    codigoBarra = models.CharField("codigoBarra", max_length=8)

    class Meta:
        ordering = ("-produto",)

    def __str__(self):
        return self.produto

    def get_absolute_url(self):
        return reverse_lazy("produto:product_detail", kwargs={"pk": self.pk})

    # Função para atualizar o nível de estoque e calcular a margem de vendas
    def save(self, *args, **kwargs):
        # Atualizar o nível de estoque
        if self.estoque > self.estoque_minimo:
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
