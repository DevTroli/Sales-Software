from django import forms
from produto.models import Produto, Compra, Tab, TabItem


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = "__all__"
        widgets = {
            "margem_vendas": forms.HiddenInput(),
            "nivel_estoque": forms.HiddenInput(),
            "produto": forms.Textarea(
                attrs={"rows": 2, "cols": 50}
            ),  # Define o tamanho do textarea
        }


class UploadFileForm(forms.Form):
    file = forms.FileField()


class CompraForm(forms.ModelForm):
    valor_compra = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(
            attrs={
                "id": "valorCompra",
                "class": "hidden",
            }
        ),
    )

    valor_entregue = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(
            attrs={
                "id": "valorEntregue",
                "class": "hidden",
            }
        ),
    )

    valor_troco = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(
            attrs={
                "id": "valorTroco",
                "readonly": True,
                "class": "hidden",
            }
        ),
    )

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
                "class": "mb-2 block py-2.5 px-0 w-full text-sm bg-transparent border-0 border-b-2 border-gray-300 appearance-none text-white border-gray-600 focus:border-blue-500 focus:outline-none focus:ring-0 focus:border-blue-600 peer autofocus",
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


class AbrirComandaForm(forms.Form):
    nome_cliente = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control block w-full px-4 py-3 border border-gray-600 rounded-md shadow-sm bg-transparent text-black focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent",
                "placeholder": "Digite o nome do cliente",
            }
        ),
    )
    telefone_cliente = forms.CharField(
        max_length=12,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control block w-full px-4 py-3 border border-gray-600 rounded-md shadow-sm bg-transparent text-black focus:outline-none focus:ring-2 focus:border-transparent",
                "placeholder": "Digite o telefone do cliente",
            }
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        telefone_cliente = cleaned_data.get("telefone_cliente")
        nome_cliente = cleaned_data.get("nome_cliente")

        if not telefone_cliente and not nome_cliente:
            raise forms.ValidationError(
                "Você deve fornecer um número de telefone ou um nome de cliente."
            )

        # Verifica se a comanda já está aberta para o telefone ou nome fornecido
        if telefone_cliente:
            if Tab.objects.filter(
                telefone_cliente=telefone_cliente, aberta=True
            ).exists():
                raise forms.ValidationError(
                    "Já existe uma comanda aberta para este número de telefone."
                )

        if nome_cliente:
            if Tab.objects.filter(nome_cliente=nome_cliente, aberta=True).exists():
                raise forms.ValidationError(
                    "Já existe uma comanda aberta para este nome de cliente."
                )

        return cleaned_data


class TabItemForm(forms.Form):
    quantidade = forms.IntegerField(
        min_value=1,
        initial=1,
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
        codigo_barra = cleaned_data.get("codigo_barra")
        nome_produto = cleaned_data.get("nome_produto")

        if not codigo_barra and not nome_produto:
            raise forms.ValidationError(
                "Você deve fornecer um código de barras ou nome do produto."
            )

        return cleaned_data

    def get_produto(self):
        cleaned_data = self.cleaned_data
        codigo_barra = cleaned_data.get("codigo_barra")
        nome_produto = cleaned_data.get("nome_produto")

        if codigo_barra:
            return Produto.objects.filter(codigoBarra=codigo_barra).first()
        elif nome_produto:
            return Produto.objects.filter(produto__icontains=nome_produto).first()

        return None
