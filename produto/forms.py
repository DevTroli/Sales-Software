from django import forms
from produto.models import Produto, Compra


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = "__all__"
        widgets = {
            "margem_vendas": forms.HiddenInput(),
            "nivel_estoque": forms.HiddenInput(),
        }


class UploadFileForm(forms.Form):
    file = forms.FileField()


class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = ["metodo_pagamento"]
        widgets = {
            "metodo_pagamento": forms.Select(
                attrs={
                    "class": "m-2 block py-2.5 px-0 w-full text-sm bg-slate-700 border-0 border-b-2 border-gray-300 appearance-none text-white border-gray-900 focus:border-blue-500 focus:outline-none focus:ring-0 focus:border-blue-600 peer",
                }
            ),
        }


class ItemCompraForm(forms.Form):
    quantidade = forms.IntegerField(
        min_value=1,
        initial=1,  # Define a quantidade padrão como 1
        widget=forms.NumberInput(
            attrs={
                "class": "mb-2 block py-2.5 px-0 w-full text-sm bg-transparent border-0 border-b-2 border-gray-300 appearance-none text-white border-gray-600 focus:border-blue-500 focus:outline-none focus:ring-0 focus:border-blue-600 peer",
                "placeholder": "Quantas Unidades?",
            }
        ),
    )
    codigo_barra = forms.CharField(
        label="Código de Barras",
        max_length=16,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "mb-2 block py-2.5 px-0 w-full text-sm bg-transparent border-0 border-b-2 border-gray-300 appearance-none text-white border-gray-600 focus:border-blue-500 focus:outline-none focus:ring-0 focus:border-blue-600 peer",
                "placeholder": "Digite o Código de Barras",
            }
        ),
    )
    nome_produto = forms.CharField(
        label="Nome do Produto",
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "mb-0.5 block py-2.5 px-0 w-full text-sm bg-transparent border-0 border-b-2 border-gray-300 appearance-none text-white border-gray-600 focus:border-blue-500 focus:outline-none focus:ring-0 focus:border-blue-600 peer",
                "placeholder": "Digite o Nome do Produto",
            }
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        # produto_id = cleaned_data.get("produto_id")
        codigo_barra = cleaned_data.get("codigo_barra")
        nome_produto = cleaned_data.get("nome_produto")

        if not codigo_barra and not nome_produto:
            raise forms.ValidationError(
                "Você deve fornecer um ID, um código de barras ou um nome do produto."
            )

        return cleaned_data

    def get_produto(self):
        cleaned_data = self.cleaned_data
        # produto_id = cleaned_data.get("produto_id")
        codigo_barra = cleaned_data.get("codigo_barra")
        nome_produto = cleaned_data.get("nome_produto")

        if codigo_barra:
            return Produto.objects.filter(codigoBarra=codigo_barra).first()
        elif nome_produto:
            return Produto.objects.filter(produto__icontains=nome_produto).first()

        return None
