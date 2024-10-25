from django.urls import path
from pdv import views as v

app_name = "pdv"

urlpatterns = [
    path("", v.pdv, name="pdv"),
    path("remove_item/", v.remove_item, name="remove_item"),
    path("clear_checkout/", v.clear_checkout, name="clear_checkout"),
    path("<int:pk>/purchase/", v.purchase_details, name="purchase_details"),
]
