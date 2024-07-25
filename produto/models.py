from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse_lazy


class Produto(models.Model):
    nivel_estoque = models.BooleanField("Nivel do Estoque")
    produto = models.TextField("produto", max_length=100, unique=True)
    preco_custo = models.DecimalField(
        "preço de custo", max_digits=7, decimal_places=2, default=0.00
    )
    preco_venda = models.DecimalField(
        "preço de venda", max_digits=7, decimal_places=2, default=0.00
    )
    margem_vendas = models.DecimalField(
        "margem de vendas", max_digits=6, decimal_places=2, null=True, blank=True
    )
    estoque = models.IntegerField("estoque atual")
    estoque_minimo = models.PositiveIntegerField("estoque mínimo", default=0)
    ncm = models.CharField("NCM", max_length=8)

    class Meta:
        ordering = ("-produto",)

    def __str__(self):
        return self.produto

    def get_absolute_url(self):
        return reverse_lazy("produto:product_detail", kwargs={"pk": self.pk})

    # Função para atualizar o nível de estoque
    def save(self, *args, **kwargs):
        if self.estoque > self.estoque_minimo:
            self.nivel_estoque = True
        else:
            self.nivel_estoque = False
        super().save(*args, **kwargs)

    @property
    def calcular_margem(self):
        if self.preco_custo == 0:
            return None
        margem = (self.preco_venda / self.preco_custo) - 1
        return f"{margem:.2%}"

    @receiver(post_save, sender=Produto)
    def atualizar_margem_vendas(sender, instance, **kwargs):
    instance.margem_vendas = instance.calcular_margem
    instance.save()
