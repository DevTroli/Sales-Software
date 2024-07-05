from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class Produto(models.Model):
    ncm = models.CharField("NCM", max_length=8)
    produto = models.TextField("produto", max_length=100, unique=True)
    preco = models.DecimalField("preço", max_digits=7, decimal_places=2)
    estoque = models.IntegerField("estoque atual")
    estoque_minimo = models.PositiveIntegerField("estoque mínimo", default=0)
    nivel_estoque = models.BooleanField("Nivel do Estoque")

    class Meta:
        ordering = ("produto",)

    def __str__(self):
        return self.produto
    
    # Função para atualizar o nível de estoque
    def save(self, *args, **kwargs):
        if self.estoque > self.estoque_minimo:
            self.nivel_estoque = True
        else:
            self.nivel_estoque = False
        super().save(*args, **kwargs)

