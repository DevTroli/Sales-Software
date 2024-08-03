from django.db import models
from django.contrib.auth.models import User

from core.models import TimeStampedModel
from produto.models import Produto

MOVIMENTO = (
    ("e", "entrada"),
    ("s", "saída"),
)


class Estoque(TimeStampedModel):
    funcionario = models.ForeignKey(User, on_delete=models.CASCADE)
    nf = models.PositiveIntegerField("Nota Fiscal", null=True, blank=True)
    MOVIMENTO = models.CharField(max_length=1, choices=MOVIMENTO)

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        if self.nf:
            return "{} - {} - {}".format(
                self.pk, self.nf, self.created.strftime("%d-%m-%Y")
            )
        return "{} --- {}".format(self.pk, self.created.strftime("%d-%m-%Y"))

    def nf_formated(self):
        if self.nf:
            return str(self.nf).zfill(3)
        return "---"


class EstoqueItens(models.Model):
    estoque = models.ForeignKey(Estoque, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
    saldo = models.PositiveIntegerField()

    class Meta:
        ordering = ("pk",)

    def __str__(self):
        return "{} - {} - {}".format(self.pk, self.estoque.pk, self.produto.pk)
