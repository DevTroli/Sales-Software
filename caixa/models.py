from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, Sum
from django.utils import timezone


class SessaoCaixaManager(models.Manager):
    def get_sessao_aberta(self):
        """Retorna a sessão de caixa atualmente aberta, ou None."""
        return self.filter(status="ABERTO").first()


class SessaoCaixa(models.Model):
    STATUS_CHOICES = (("ABERTO", "Aberto"), ("FECHADO", "Fechado"))

    usuario_abertura = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="sessoes_abertas"
    )
    usuario_fechamento = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="sessoes_fechadas",
        null=True,
        blank=True,
    )

    valor_abertura = models.DecimalField(max_digits=10, decimal_places=2)
    valor_fechamento_calculado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total que o sistema calculou no fechamento",
    )
    valor_fechamento_informado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total que o usuário contou no caixa",
    )
    diferenca = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )

    data_abertura = models.DateTimeField(auto_now_add=True)
    data_fechamento = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="ABERTO")

    objects = SessaoCaixaManager()

    def __str__(self):
        return f"Caixa de {self.data_abertura.strftime('%d/%m/%Y')} por {self.usuario_abertura.username}"

    def clean(self):
        if (
            self.status == "ABERTO"
            and SessaoCaixa.objects.filter(status="ABERTO").exclude(pk=self.pk).exists()
        ):
            raise ValidationError(
                "Já existe um caixa aberto. Feche-o antes de abrir um novo."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def calcular_saldo_atual(self):
        """Calcula o saldo em tempo real da sessão de caixa aberta."""
        if self.status == "FECHADO":
            return self.valor_fechamento_calculado

        movs = self.movimentacoes.aggregate(
            entradas=Sum(
                "valor", filter=Q(tipo__in=["ABERTURA", "SUPRIMENTO", "VENDA"])
            ),
            saidas=Sum("valor", filter=Q(tipo="SANGRIA")),
        )
        entradas = movs.get("entradas") or Decimal("0.00")
        saidas = movs.get("saidas") or Decimal("0.00")
        return entradas - saidas


class MovimentacaoCaixa(models.Model):
    TIPO_CHOICES = (
        ("ABERTURA", "Abertura de Caixa"),
        ("SUPRIMENTO", "Suprimento (Entrada)"),
        ("VENDA", "Venda em Dinheiro"),
        ("SANGRIA", "Sangria (Retirada)"),
    )

    sessao = models.ForeignKey(
        SessaoCaixa, on_delete=models.PROTECT, related_name="movimentacoes"
    )
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    descricao = models.CharField(max_length=200, blank=True)
    data_movimentacao = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.get_tipo_display()} - R$ {self.valor}"
