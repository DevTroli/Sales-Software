from django.contrib import admin
from .models import Produto, Categoria


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = (
        "nivel_estoque",
        "produto",
        "preco_custo",
        "preco_venda",
        "margem_vendas",
        "estoque",
        "estoque_minimo",
        "codigoBarra",
        "categoria",
    )
    search_fields = (
        "produto",
        "codigoBarra",
        "categoria__categoria",  # Use a notação __ para acessar o campo 'categoria' do modelo 'Categoria'
    )
    list_filter = (
        "nivel_estoque",
        "categoria",
    )


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("__str__",)
    search_fields = ("categoria",)
