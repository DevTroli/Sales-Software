from django.urls import path
from core import views as v

app_name = "core"

urlpatterns = [
    path("", v.index, name="index"),
    path("menu/", v.menu, name="index"),
    path("novidades/", v.novidades, name="novidades"),

]
