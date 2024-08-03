from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy

from produto.models import Produto
from produto.forms import ProdutoForm

@login_required
def index(request):
    template_name = "index.html"
    query = request.GET.get('q')  # Obtém o valor do campo 'q' da URL
    if query:
        # Filtra os produtos com base no valor de 'q'
        objects = Produto.objects.filter(
            Q(produto__icontains=query) | 
            Q(ncm__icontains=query) | 
            Q(preco_custo__icontains=query) | 
            Q(preco_venda__icontains=query)
        )
    else:
        # Caso não haja busca, retorna todos os produtos
        objects = Produto.objects.all()
    context = {"object_list": objects}
    return render(request, template_name, context)


def product_detail(request, pk):
    template_name = "product_detail.html"
    obj = get_object_or_404(Produto, pk=pk)
    context = {"object": obj}
    return render(request, template_name, context)

@login_required
def product_add(request):
    template_name = "product_form.html"
    return render(request, template_name)


class ProductCreate(LoginRequiredMixin, CreateView):
    model = Produto
    template_name = "product_form.html"
    form_class = ProdutoForm
    login_url = '/login'

class ProdutoUpdate(LoginRequiredMixin, UpdateView):
    model = Produto
    template_name = "product_form.html"
    form_class = ProdutoForm
    success_url = reverse_lazy("produto:index")
    login_url = '/login'