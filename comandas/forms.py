from django import forms
from django.core.validators import RegexValidator
from comandas.models import Tab, Comment
from produto.models import Produto


class AbrirComandaForm(forms.Form):
    # Validator para telefone brasileiro
    phone_regex = RegexValidator(
        regex=r"^\d{10,11}$",
        message="O número deve estar no formato: '11999999999' ou '1199999999'. Entre 10 e 11 dígitos permitidos.",
    )

    nome_cliente = forms.CharField(
        max_length=18,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control block w-full px-4 py-3 border border-gray-600 rounded-md shadow-sm bg-transparent text-black focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent",
                "placeholder": "Digite o nome do cliente",
                "oninput": "this.value = this.value.toUpperCase()",  # Converte para maiúsculo enquanto digita
            }
        ),
    )

    telefone_cliente = forms.CharField(
        max_length=11,
        required=False,
        validators=[phone_regex],
        widget=forms.TextInput(
            attrs={
                "class": "form-control block w-full px-4 py-3 border border-gray-600 rounded-md shadow-sm bg-transparent text-black focus:outline-none focus:ring-2 focus:border-transparent",
                "placeholder": "Digite o telefone do cliente (apenas números)",
                "type": "tel",
                "pattern": "[0-9]{10,11}",
            }
        ),
    )

    def clean_nome_cliente(self):
        nome = self.cleaned_data.get("nome_cliente")
        if nome:
            nome = (
                nome.upper().strip()
            )  # Converte para maiúsculo e remove espaços extras
        return nome

    def clean_telefone_cliente(self):
        telefone = self.cleaned_data.get("telefone_cliente")
        if telefone:
            # Remove caracteres não numéricos
            telefone = "".join(filter(str.isdigit, telefone))

            # Valida o formato do telefone brasileiro
            if len(telefone) < 10 or len(telefone) > 11:
                raise forms.ValidationError(
                    "Telefone inválido. Use o formato: 11999999999 ou 1199999999"
                )
        return telefone

    def clean(self):
        cleaned_data = super().clean()
        telefone_cliente = cleaned_data.get("telefone_cliente")
        nome_cliente = cleaned_data.get("nome_cliente")

        if not telefone_cliente and not nome_cliente:
            raise forms.ValidationError(
                "Você deve fornecer um número de telefone ou um nome de cliente."
            )

        # Verifica comandas abertas
        self._validar_comanda_existente(nome_cliente, telefone_cliente)

        return cleaned_data

    def _validar_comanda_existente(self, nome_cliente, telefone_cliente):
        """Método auxiliar para validar comandas existentes"""
        if (
            telefone_cliente
            and Tab.objects.filter(
                telefone_cliente=telefone_cliente, aberta=True
            ).exists()
        ):
            raise forms.ValidationError(
                "Já existe uma comanda aberta para este número de telefone."
            )

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
                "pattern": "[0-9]*",
                "inputmode": "numeric",
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
                "oninput": "this.value = this.value.toUpperCase()",
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
            # Remove caracteres não numéricos
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

        # Verifica se o produto existe
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
    telefone_cliente = forms.CharField(
        max_length=11,
        required=False,
        validators=[AbrirComandaForm.phone_regex],
        widget=forms.TextInput(
            attrs={
                "class": "form-control block w-full px-4 py-3 border border-gray-600 rounded-md shadow-sm bg-transparent text-gray-300 focus:outline-none focus:ring-2 focus:border-transparent",
                "placeholder": "Digite o telefone do cliente (apenas números)",
                "type": "tel",
                "pattern": "[0-9]{10,11}",
            }
        ),
    )

    class Meta:
        model = Tab
        fields = ["nome_cliente", "telefone_cliente"]
        widgets = {
            "nome_cliente": forms.TextInput(
                attrs={
                    "class": "form-control block w-full px-4 py-3 border border-gray-600 rounded-md shadow-sm bg-transparent text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent",
                    "placeholder": "Digite o nome do cliente",
                    "oninput": "this.value = this.value.toUpperCase()",
                }
            ),
        }

    def clean_nome_cliente(self):
        nome = self.cleaned_data.get("nome_cliente")
        if nome:
            nome = nome.upper().strip()
        return nome

    def clean_telefone_cliente(self):
        telefone = self.cleaned_data.get("telefone_cliente")
        if telefone:
            telefone = "".join(filter(str.isdigit, telefone))
        return telefone


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": "w-fit p-2 bg-gray-700 text-gray-200 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500",
                    "rows": "2",
                    "placeholder": "Digite seu comentário...",
                }
            ),
        }
