from django import forms
from django.core.validators import RegexValidator
from django.forms import TextInput
from django.forms import inlineformset_factory
from .models import Profissional, Evento, Inscricao, InscricaoEvento,Pagamento


class InscricaoFormAdmin(forms.ModelForm):
    class Meta:
        model = Inscricao
        fields = ("nome", "cpf", "categoria", "lote", "cep", "cidade", "uf")
        widgets = {
            "cpf": TextInput(attrs={"class": "cpf-input", "onchange": "buscarDadosPorCPF(this.value)"}),
            "logradouro": TextInput(attrs={"readonly": "readonly", "style": "width: 270px; background: #f0f0f0;"}),
            "bairro": TextInput(attrs={"readonly": "readonly", "style": "width: 270px; background: #f0f0f0;"}),
            "cidade": TextInput(attrs={"readonly": "readonly", "style": "width: 270px; background: #f0f0f0;"}),
            "uf": TextInput(attrs={"readonly": "readonly", "style": "width: 270px; background: #f0f0f0;"})
        }

    def __init__(self, *args, **kwargs):
        super(InscricaoFormAdmin, self).__init__(*args, **kwargs)
        self.fields['cep'].widget.attrs['class'] = 'mask-cep'



    cep = forms.CharField(max_length=9, label='CEP', required=False, validators=[
        RegexValidator(
            regex='^\d{5}-\d{3}$',
            message='CEP com formato inválido.',
            code='invalid_cep'
        )
    ])


# from django import forms

# class LancamentoParcelaForm(forms.Form):
#     nome_ou_cpf = forms.CharField(label="Nome ou CPF", max_length=50)
#     valor_parcela = forms.DecimalField(label="Valor da Parcela")


class ProfissionalForm(forms.ModelForm):
    class Meta:
        model = Profissional
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        evento = Evento.objects.first()  # Ajuste conforme necessário para obter o evento correto
        if evento:
            vagas_disponiveis = evento.quantidade_pessoas - evento.contador_barco
            self.fields['barco'].help_text = f'<span style="font-size: 1.5em;">Vagas disponíveis: {vagas_disponiveis}</span>'
        else:
            self.fields['barco'].help_text = '<span style="font-size: 1.5em;">Evento não encontrado.</span>'
    


class InscricaoStep1Form(forms.ModelForm):
    class Meta:
        model = Inscricao
        fields = ['nome', 'cpf', 'categoria']

class InscricaoStep2Form(forms.ModelForm):
    class Meta:
        model = Inscricao
        fields = ['lote']

InscricaoEventoFormSet = inlineformset_factory(Inscricao, InscricaoEvento, fields=('evento', 'confirmar'), extra=1)


class PagamentoForm(forms.ModelForm):
    class Meta:
        model = Pagamento
        fields = ['inscricao', 'valor_pago', 'parcela']

    def __init__(self, *args, **kwargs):
        super(PagamentoForm, self).__init__(*args, **kwargs)
        if 'inscricao' in self.data:
            try:
                inscricao_id = int(self.data.get('inscricao'))
                inscricao = Inscricao.objects.get(id=inscricao_id)
                self.fields['parcela'].queryset = range(1, inscricao.parcelas + 1)  # Gera lista de parcelas
                self.initial['valor_pago'] = inscricao.calcular_parcela()  # Define o valor da parcela
            except (ValueError, TypeError, Inscricao.DoesNotExist):
                pass  # Caso a inscrição não seja válida
        else:
            self.fields['parcela'].queryset = Inscricao.objects.none()