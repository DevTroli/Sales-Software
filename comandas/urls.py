from django.urls import path
from comandas import views as v

app_name = "comandas"

urlpatterns = [
    path("abrir_comanda/", v.abrir_comanda, name="abrir_comanda"),
    path("excluir/<int:pk>/", v.excluir_comanda, name="excluir_comanda"),
    path("<int:pk>/", v.detalhes_tab, name="detalhes_tab"),
    path("", v.listar_tabs, name="listar_tabs"),
    path("fechar_comanda/<int:pk>/", v.fechar_tab, name="fechar_tab"),
    path(
        "att_item/<int:pk>/",
        v.atualizar_quantidade_item,
        name="atualizar_quantidade_item",
    ),
    path(
        "rm_item_comanda/<int:pk>/",
        v.remover_item_comanda,
        name="remover_item_comanda",
    ),
]
