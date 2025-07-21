from django.urls import path
from comandas import views as v

app_name = "comandas"

urlpatterns = [
    # MODIFICAÇÃO: A rota principal agora é o dashboard.
    path("", v.dashboard_comandas, name="dashboard"),
    
    path("abrir/", v.abrir_comanda, name="abrir_comanda"),
    # path("excluir/<int:pk>/", v.excluir_comanda, name="excluir_comanda"),
    path("<int:pk>/", v.detalhes_tab, name="detalhes_tab"),
    
    # MODIFICAÇÃO: A rota de fechar agora é mais clara e usa POST.
    path("fechar/<int:pk>/", v.fechar_tab, name="fechar_tab"),
    
    # MODIFICAÇÃO: Nova rota para reabrir uma comanda.
    path("reabrir/<int:pk>/", v.reabrir_tab, name="reabrir_tab"),

    path("item/atualizar/<int:pk>/", v.atualizar_quantidade_item, name="atualizar_quantidade_item"),

    path("item/remover/<int:pk>/", v.remover_item_comanda, name="remover_item_comanda"),
    path("comentario/excluir/<int:pk>/", v.excluir_comentario, name="excluir_comentario"),
]
