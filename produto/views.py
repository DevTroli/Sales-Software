from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy

from django.db.models import Q

from produto.models import Produto
from produto.forms import ProdutoForm

@login_required
def index(request):
    template_name = "index.html"
    
    query = request.GET.get('q')
    objects = Produto.objects.all()
    
    if query:
        queries = query.split()
        q_objects = Q()
        for q in queries:
            q_objects |= Q(produto__icontains=q) | Q(ncm__icontains=q) | Q(preco_venda__icontains=q)
        objects = objects.filter(q_objects)
    
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