from django import forms
from produto.models import Produto


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
