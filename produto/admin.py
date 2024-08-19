from decimal import Decimal
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import path
from django.contrib.admin import helpers
from django.template.response import TemplateResponse

from produto.forms import ProdutoForm
from .models import Produto, Categoria


# 1. Ação para aumentar o preço dos produtos
def aumentar_preco(modeladmin, request, queryset):
    aumento = Decimal("1.10")  # 10% de aumento
    for produto in queryset:
        produto.preco_venda *= aumento
        produto.save()
    modeladmin.message_user(request, "Preço dos produtos aumentados em 10%.")


aumentar_preco.short_description = "Aumentar Preço em 10%% para produtos selecionados"


# 2. Ação para aplicar desconto nos produtos
def aplicar_desconto(modeladmin, request, queryset):
    desconto = Decimal("0.90")  # 10% de desconto
    for produto in queryset:
        produto.preco_venda *= desconto
        produto.save()
    modeladmin.message_user(request, "Desconto de 10% aplicado nos produtos.")


aplicar_desconto.short_description = (
    "Aplicar 10%% de Desconto nos produtos selecionados"
)


# 3. Ação para editar o produto selecionado
def editar_produto_selecionado(modeladmin, request, queryset):
    if queryset.count() == 1:
        produto = queryset.get()
        return HttpResponseRedirect(f"editar_produto/{produto.pk}/")

    modeladmin.message_user(request, "Selecione apenas um produto para editar.")


editar_produto_selecionado.short_description = "Editar Produto Selecionado"


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

    actions = [
        aumentar_preco,
        aplicar_desconto,
        editar_produto_selecionado,
    ]  # Adiciona as ações personalizadas

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "editar_produto/<int:pk>/",
                self.admin_site.admin_view(self.editar_produto),
                name="editar_produto",
            ),
        ]
        return custom_urls + urls

    def editar_produto(self, request, pk):
        produto = get_object_or_404(Produto, pk=pk)
        if request.method == "POST":
            form = ProdutoForm(request.POST, instance=produto)
            if form.is_valid():
                form.save()
                self.message_user(request, "Produto atualizado com sucesso.")
                return redirect("..")
        else:
            form = ProdutoForm(instance=produto)

        context = {
            "title": "Editar Produto",
            "form": form,
            "opts": self.model._meta,
            "object": produto,
            "save_as_new": False,
            "has_view_permission": True,
            "has_add_permission": True,
            "has_change_permission": True,
            "has_delete_permission": True,
            "has_editable_inline_admin_formsets": False,
            "adminform": helpers.AdminForm(
                form, list([(None, {"fields": form.fields})]), {}
            ),
            "is_popup": False,
            "save_on_top": False,
            "add": False,
            "change": True,
        }
        return TemplateResponse(request, "editProduct_adm.html", context)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("__str__",)
    search_fields = ("categoria",)
