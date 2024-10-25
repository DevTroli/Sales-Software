# produto/migrations/0014_tab_tabitem_tab_produtos.py
from django.core.exceptions import ValidationError
from django.db import migrations, models
import django.db.models.deletion
from decimal import Decimal

def validar_telefone_brasileiro(valor):
    if not valor.isdigit():
        raise ValidationError('O telefone deve conter apenas números')
    if len(valor) != 11:
        raise ValidationError('O telefone deve ter 11 dígitos (DDD + número)')
    if valor[0] not in '1234567899':
        raise ValidationError('DDD inválido')

class Migration(migrations.Migration):

    dependencies = [
        ("produto", "0013_compra_itemcompra"),
    ]

    operations = [
        migrations.CreateModel(
            name="Tab",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "nome_cliente",
                    models.CharField(max_length=100, verbose_name="Nome do Cliente"),
                ),
                (
                    "telefone_cliente",
                    models.CharField(
                        max_length=11,
                        unique=True,
                        validators=[validar_telefone_brasileiro],
                        verbose_name="Telefone do Cliente",
                    ),
                ),
                (
                    "subtotal",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0.00"),
                        max_digits=10,
                        verbose_name="Subtotal",
                    ),
                ),
                (
                    "aberta",
                    models.BooleanField(default=True, verbose_name="Tab Aberta"),
                ),
                (
                    "data_criacao",
                    models.DateTimeField(
                        auto_now_add=True,
                        verbose_name="Data de Criação",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TabItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("quantidade", models.PositiveIntegerField()),
                ("preco_unitario", models.DecimalField(decimal_places=2, max_digits=7)),
                (
                    "produto",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="produto.produto",
                    ),
                ),
                (
                    "tab",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="itens",
                        to="produto.tab",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="tab",
            name="produtos",
            field=models.ManyToManyField(
                through="produto.TabItem", to="produto.produto"
            ),
        ),
    ]