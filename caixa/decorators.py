from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from .models import SessaoCaixa


def caixa_aberto_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not SessaoCaixa.objects.get_sessao_aberta():
            messages.error(
                request, "O caixa está fechado! Abra o caixa para registrar vendas."
            )
            return redirect("caixa:dashboard")
        return view_func(request, *args, **kwargs)

    return _wrapped_view
