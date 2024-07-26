from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy

from produto.models import Produto
from produto.forms import ProdutoForm


def index(request):
    template_name = "index.html"
    objects = Produto.objects.all()
    context = {"object_list": objects}
    return render(request, template_name, context)


def product_detail(request, pk):
    template_name = "product_detail.html"
    obj = get_object_or_404(Produto, pk=pk)
    context = {"object": obj}
    return render(request, template_name, context)


def product_add(request):
    template_name = "product_form.html"
    return render(request, template_name)


class ProductCreate(CreateView):
    model = Produto
    template_name = "product_form.html"
    form_class = ProdutoForm


class ProdutoUpdate(UpdateView):
    model = Produto
    template_name = "product_form.html"
    form_class = ProdutoForm
    success_url = reverse_lazy("produto:index")
