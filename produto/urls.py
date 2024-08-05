from django.urls import path
from produto import views as v

app_name = "produto"

urlpatterns = [
    path("", v.index, name="index"),
    path("<int:pk>/", v.product_detail, name="product_detail"),
    path("add/", v.ProductCreate.as_view(), name="product_add"),
    path("<int:pk>/edit/", v.ProdutoUpdate.as_view(), name="edit"),
    path("insights/", v.gerar_insights, name="gerar_insights"),
    path('upload/', v.upload_file, name='upload'),
    path('import/', v.import_data, name='import'),
]
