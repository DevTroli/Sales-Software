from django import forms
from django.core.validators import RegexValidator
from produto.models import Produto
from decimal import Decimal


class ProdutoForm(forms.ModelForm):
    # Validador para código de barras
    codigo_barras_regex = RegexValidator(
        regex=r"^\d{7,16}$", message="O código de barras deve ter entre 7 e 16 dígitos."
    )

    # Override dos campos para adicionar validações
    codigoBarra = forms.CharField(
        label="Código de Barras",
        validators=[codigo_barras_regex],
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Digite o código de barras",
                "pattern": "[0-9]{7,16}",
                "inputmode": "numeric",
            }
        ),
    )

    produto = forms.CharField(
        label="Nome do Produto",
        widget=forms.Textarea(
            attrs={
                "rows": 2,
                "cols": 48,
                "class": "form-control",
                "placeholder": "Digite o nome do produto",
                "oninput": "this.value = this.value.toUpperCase()",
            }
        ),
    )

    preco_custo = forms.DecimalField(
        label="Preço de custo",
        min_value=Decimal("0.01"),
        max_digits=5,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "R$ 0,00", "step": "0.01"}
        ),
    )

    preco_venda = forms.DecimalField(
        label="Preço de venda",
        min_value=Decimal("0.01"),
        max_digits=5,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "R$ 0,00", "step": "0.01"}
        ),
    )

    estoque = forms.IntegerField(
        label="estoque",
        min_value=0,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Quantidade em estoque"}
        ),
    )

    class Meta:
        model = Produto
        fields = "__all__"
        widgets = {
            "margem_vendas": forms.HiddenInput(),
            "nivel_estoque": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        # Marca campos obrigatórios
        for field_name, field in self.fields.items():
            if field.required:
                field.label = f"{field.label}*"


class UploadFileForm(forms.Form):
    file = forms.FileField(
        label="Selecione o arquivo",
        help_text="Arquivos permitidos: CSV, XLS, XLSX",
        widget=forms.FileInput(
            attrs={"class": "form-control", "accept": ".csv,.xls,.xlsx"}
        ),
    )

    def clean_file(self):
        file = self.cleaned_data.get("file")
        if file:
            ext = file.name.split(".")[-1].lower()
            if ext not in ["csv", "xls", "xlsx"]:
                raise forms.ValidationError(
                    "Formato de arquivo não suportado. Use CSV, XLS ou XLSX."
                )
        return file
