from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", include("core.urls")),
    path("admin/", admin.site.urls),
    path("produtos/", include("produto.urls")),
    path("estoque/", include("estoque.urls")),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),

]
