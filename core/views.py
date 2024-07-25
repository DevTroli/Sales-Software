from django.shortcuts import render


def index(request):
    return render(request, "core/index.html")


def novidades(request):
    return render(request, "core/novidades.html")
