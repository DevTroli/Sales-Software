from django import forms


class AberturaCaixaForm(forms.Form):
    valor_abertura = forms.DecimalField(label="Valor Inicial (Troco)", required=True)


class MovimentacaoForm(forms.Form):
    valor = forms.DecimalField(required=True)
    descricao = forms.CharField(required=False)


class FechamentoCaixaForm(forms.Form):
    valor_fechamento_informado = forms.DecimalField(
        label="Valor Contado no Caixa", required=True
    )

class RelatorioCaixaForm(forms.Form):
    data_inicio = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    data_fim = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
