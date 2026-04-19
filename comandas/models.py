import re
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone

from produto.models import Produto


class Tab(models.Model):
    # MODIFICAÇÃO: Adicionando as opções de Status
    STATUS_CHOICES = (
        ('ATIVA', 'Ativa'),
        ('VAZIA', 'Vazia'),
        ('FECHADA', 'Fechada'),
    )

    nome_cliente = models.CharField("Nome do Cliente", max_length=100)

    produtos = models.ManyToManyField(Produto, through="TabItem")
    subtotal = models.DecimalField(
        "Subtotal", max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    
    # O campo 'aberta' será controlado pelo status. Manteremos por ora para evitar quebras.
    aberta = models.BooleanField("Tab Aberta", default=True)
    
    # MODIFICAÇÃO: Campo de status explícito
    status = models.CharField("Status", max_length=10, choices=STATUS_CHOICES, default='VAZIA', db_index=True)

    data_criacao = models.DateTimeField("Data de Criação", auto_now_add=True)
    data_fechamento = models.DateTimeField("Data de Fechamento", null=True, blank=True)

    def __str__(self):
        return f"Comanda de {self.nome_cliente} - {self.get_status_display()}"

    def clean(self):
        if self.aberta and Tab.objects.filter(nome_cliente=self.nome_cliente, aberta=True).exclude(pk=self.pk).exists():
            raise ValidationError(f'Já existe uma comanda aberta para o cliente "{self.nome_cliente}".')

    def save(self, *args, **kwargs):
        self.full_clean() # Executa a validação do `clean()`
        self.aberta = self.status != 'FECHADA'
        super().save(*args, **kwargs)

    def atualizar_status_e_subtotal(self):
        """Recalcula o subtotal usando SQL aggregation em vez de Python loop."""
        if self.status == 'FECHADA':
            return

        # Otimização: usar SQL aggregation em vez de soma em Python
        # Isso elimina N+1 queries e é muito mais rápido
        from django.db.models import Sum, F
        result = self.itens.aggregate(
            total=Sum(F('quantidade') * F('preco_unitario'))
        )
        total = result['total'] or Decimal('0.00')

        novo_status = 'ATIVA' if total > 0 else 'VAZIA'

        self.subtotal = total
        self.status = novo_status
        self.aberta = novo_status != 'FECHADA'
        self.save(update_fields=['subtotal', 'status', 'aberta'])

    # MODIFICAÇÃO: Lógica de fechamento encapsulada
    def fechar(self):
        """Fecha a comanda, ajusta o status e data de fechamento."""
        # A lógica de estoque será movida para a view que chama este método.
        self.status = 'FECHADA'
        self.aberta = False
        self.data_fechamento = timezone.now()
        self.save(update_fields=['status', 'aberta', 'data_fechamento'])

    # MODIFICAÇÃO: Lógica para reabrir uma comanda
    def reabrir(self):
        """Reabre uma comanda fechada."""
        self.data_fechamento = None
        self.aberta = True
        self.save(update_fields=['data_fechamento', 'aberta'])
        # Chama a atualização para definir o status como ATIVA ou VAZIA
        self.atualizar_status_e_subtotal()


class TabItem(models.Model):
    tab = models.ForeignKey(Tab, related_name="itens", on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=7, decimal_places=2)
    adicionado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    data_criacao = models.DateTimeField("Data de Criação", auto_now_add=True)

    def subtotal(self):
        return self.preco_unitario * self.quantidade

    def __str__(self):
        return f"{self.quantidade}x {self.produto.produto} - {self.tab.nome_cliente}"

    def save(self, *args, **kwargs):
        # Armazena quantidade anterior para otimizar o signal
        if self.pk:
            try:
                self._pre_save_quantidade = TabItem.objects.get(pk=self.pk).quantidade
            except TabItem.DoesNotExist:
                self._pre_save_quantidade = None
        super().save(*args, **kwargs)


# MODIFICAÇÃO: Signal otimizado para atualização da comanda
@receiver([post_save, post_delete], sender=TabItem)
def on_item_change_update_tab(sender, instance, **kwargs):
    """Atualiza comanda pai apenas quando necessário."""
    # Só recalcula em criação (created=True) ou deleção
    if kwargs.get('created'):
        instance.tab.atualizar_status_e_subtotal()
    elif kwargs.get('signal') == post_delete:
        instance.tab.atualizar_status_e_subtotal()
    else:
        # Para updates, verifica se quantidade mudou para evitar recálculos desnecessários
        pre_save_qty = getattr(instance, '_pre_save_quantidade', None)
        if pre_save_qty is not None and pre_save_qty != instance.quantidade:
            instance.tab.atualizar_status_e_subtotal()

# O modelo Comment permanece o mesmo.
class Comment(models.Model):
    tab = models.ForeignKey("Tab", related_name="comments", on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.CharField("Content", max_length=48, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comentário por {self.author} em {self.created_at}"
