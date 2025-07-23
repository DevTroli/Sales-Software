from django.urls import path

from . import views as v

app_name = "caixa"

urlpatterns = [
    path("", v.dashboard_caixa, name="dashboard"),
    path("abrir/", v.abrir_caixa, name="abrir"),
    path("fechar/", v.fechar_caixa, name="fechar"),
    path(
        "movimentacao/<str:tipo>/",
        v.registrar_movimentacao_view,
        name="registrar_movimentacao",
    ),
    path("relatorio/", v.relatorio_caixa, name="relatorio"),
    path("relatorio/exportar/", v.exportar_relatorio_caixa, name="exportar"),
]
