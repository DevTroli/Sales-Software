# Generated by Django 5.0.6 on 2024-07-05 11:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("produto", "0003_alter_produto_nivel_estoque_alter_produto_produto"),
    ]

    operations = [
        migrations.AlterField(
            model_name="produto",
            name="nivel_estoque",
            field=models.BooleanField(verbose_name="Nivel do Estoque:"),
        ),
    ]
