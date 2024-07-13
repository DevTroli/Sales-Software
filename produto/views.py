from django.shortcuts import render

from produto.models import Produto


def index(request):
    template_name = "produto/index.html"
    objects = Produto.objects.all()
    context = {"object_list": objects}
    return render(request, template_name, context)
