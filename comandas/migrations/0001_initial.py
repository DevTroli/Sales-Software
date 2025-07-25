# Generated by Django 5.0.6 on 2024-10-25 10:43

import django.db.models.deletion
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("produto", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
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
                # REMOVIDO: Campo telefone_cliente que causava o erro
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
                        auto_now_add=True, verbose_name="Data de Criação"
                    ),
                ),
                # ADICIONADO: Novos campos do seu modelo atual
                (
                    "status",
                    models.CharField(
                        choices=[('ATIVA', 'Ativa'), ('VAZIA', 'Vazia'), ('FECHADA', 'Fechada')],
                        db_index=True,
                        default='VAZIA',
                        max_length=10,
                        verbose_name='Status'
                    ),
                ),
                (
                    "data_fechamento",
                    models.DateTimeField(
                        blank=True,
                        null=True,
                        verbose_name="Data de Fechamento"
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
                    "data_criacao",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Data de Criação"
                    ),
                ),
                (
                    "adicionado_por",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
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
                        to="comandas.tab",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="tab",
            name="produtos",
            field=models.ManyToManyField(
                through="comandas.TabItem", to="produto.produto"
            ),
        ),
        # ADICIONADO: Modelo Comment que estava faltando
        migrations.CreateModel(
            name="Comment",
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
                    "content",
                    models.CharField(max_length=48, unique=True, verbose_name="Content"),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True),
                ),
                (
                    "author",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "tab",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="comments",
                        to="comandas.tab",
                    ),
                ),
            ],
        ),
    ]