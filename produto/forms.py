from django import forms
from produto.models import Produto


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = "__all__"
        widgets = {
            "margem_vendas": forms.HiddenInput(),
        }
