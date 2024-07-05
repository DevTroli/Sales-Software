from django.contrib import admin
from .models import Produto

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ("produto", "ncm", "preco", "estoque", "estoque_minimo", "nivel_estoque")
    search_fields = ("produto", "ncm")  # Defina os campos pelos quais você deseja buscar
    list_filter = ("nivel_estoque",)

    


