from django.shortcuts import render, get_object_or_404
from produto.models import Produto


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
