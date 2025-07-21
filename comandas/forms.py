from django import forms
from django.core.validators import RegexValidator
from comandas.models import Tab, Comment
from produto.models import Produto


class AbrirComandaForm(forms.ModelForm):
    class Meta:
        model = Tab
        fields = ['nome_cliente']
        widgets = {
            'nome_cliente': forms.TextInput(attrs={
                'class': 'form-input text-center mb-2 block py-2.5 px-0 w-full text-sm bg-transparent border-0 border-b-2 border-gray-300 appearance-none text-white border-gray-600 focus:border-blue-500 focus:outline-none focus:ring-0 focus:border-blue-600 peer',
                'placeholder': 'Ex: Mesa 04 ou João Silva',
                'oninput': 'this.value = this.value.toUpperCase()',
                'required': True,
            })
        }
    
    def clean_nome_cliente(self):
        nome = self.cleaned_data.get("nome_cliente")
        return nome.upper().strip() if nome else nome

    def _validar_comanda_existente(self, nome_cliente, telefone_cliente):
        """Método auxiliar para validar comandas existentes"""
        if (
            nome_cliente
            and Tab.objects.filter(nome_cliente=nome_cliente, aberta=True).exists()
        ):
            raise forms.ValidationError(
                "Já existe uma comanda aberta para este nome de cliente."
            )


class TabItemForm(forms.Form):
    quantidade = forms.IntegerField(
        min_value=1,
        max_value=999,
        initial=1,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-input text-center mb-2 block py-2.5 px-0 w-full text-sm bg-transparent border-0 border-b-2 border-gray-300 appearance-none text-white border-gray-600 focus:border-blue-500 focus:outline-none focus:ring-0 focus:border-blue-600 peer',
                'placeholder': 'Quantas Unidades?',
            }
        ),
    )

    codigo_barra = forms.CharField(
        label="Código de Barras",
        max_length=16,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'mb-2 block py-2.5 px-0 w-full text-sm bg-transparent border-0 border-b-2 border-gray-300 appearance-none text-white border-gray-600 focus:border-blue-500 focus:outline-none focus:ring-0 focus:border-blue-600 peer',
                'placeholder': 'Código de Barras aqui',
                'pattern': '[0-9]*',
                'inputmode': 'numeric',
            }
        ),
    )

    nome_produto = forms.CharField(
        label="Nome do Produto",
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-input mb-0.5 block py-2.5 px-0 w-full text-sm bg-transparent border-0 border-b-2 border-gray-300 appearance-none text-white border-gray-600 focus:border-blue-500 focus:outline-none focus:ring-0 focus:border-blue-600 peer',
                'placeholder': 'Nome do Produto aqui',
                'oninput': 'this.value = this.value.toUpperCase()',
            }
        ),
    )

    def clean_nome_produto(self):
        nome = self.cleaned_data.get("nome_produto")
        if nome:
            nome = nome.upper().strip()
        return nome

    def clean_codigo_barra(self):
        codigo = self.cleaned_data.get("codigo_barra")
        if codigo:
            codigo = "".join(filter(str.isdigit, codigo))
        return codigo

    def clean(self):
        cleaned_data = super().clean()
        codigo_barra = cleaned_data.get("codigo_barra")
        nome_produto = cleaned_data.get("nome_produto")

        if not codigo_barra and not nome_produto:
            raise forms.ValidationError(
                "Você deve fornecer um código de barras ou nome do produto."
            )

        produto = self.get_produto()
        if not produto:
            raise forms.ValidationError(
                "Produto não encontrado. Verifique o código ou nome informado."
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


class EditTabForm(forms.ModelForm):
    class Meta:
        model = Tab
        fields = ["nome_cliente"]
        widgets = {
            "nome_cliente": forms.TextInput(attrs={
                'class': 'form-input w-80 text-center resize-none bg-gray-900 text-white placeholder-gray-500 p-2',
                'oninput': 'this.value = this.value.toUpperCase()',
            })
        }

    def clean_nome_cliente(self):
        nome = self.cleaned_data.get("nome_cliente")
        if nome:
            nome = nome.upper().strip()
        return nome


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(attrs={
                'class': 'form-input w-80 text-center resize-none bg-gray-900 text-white placeholder-gray-500 p-2',
                'placeholder': 'Digite sua anotação...',
                'rows': '3',
            }),
        }  
