from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("core.urls")),
    path("admin/", admin.site.urls),
    path("produtos/", include("produto.urls")),
    path("estoque/", include("estoque.urls")),
]
