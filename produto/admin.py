from django.contrib import admin
from .models import Produto


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = (
        "nivel_estoque",
        "produto",
        "preco_custo",
        "preco_venda",
        "estoque",
        "estoque_minimo",
        "codigoBarra",
    )
    search_fields = (
        "produto",
        "codigoBarra",
    )  # Defina os campos pelos quais você deseja buscar
    list_filter = ("nivel_estoque",)
