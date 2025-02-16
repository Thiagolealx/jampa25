from django import forms
from django.core.validators import RegexValidator
from django.forms import TextInput
from .models import Profissional, Evento

# from .models import Congressista
# class CongressistaFormAdmin(forms.ModelForm):
#     model = Congressista
#     fields = ("nome_completo", "cpf", "categoria", "lote", "ano", "cep",  "bairro", "cidade", "uf", "proxima_parcela")
#     widgets = {
#         "logradouro": TextInput(attrs={"readonly": "readonly", "style": "width: 270px; background: #f0f0f0;"}),
#         "bairro": TextInput(attrs={"readonly": "readonly", "style": "width: 270px; background: #f0f0f0;"}),
#         "cidade": TextInput(attrs={"readonly": "readonly", "style": "width: 270px; background: #f0f0f0;"}),
#         "uf": TextInput(attrs={"readonly": "readonly", "style": "width: 270px; background: #f0f0f0;"})
#     }

#     def __init__(self, *args, **kwargs):
#         super(CongressistaFormAdmin, self).__init__(*args, **kwargs)
#         self.fields['cep'].widget.attrs['class'] = 'mask-cep'



#     cep = forms.CharField(max_length=9, label='CEP', required=False, validators=[
#         RegexValidator(
#             regex='^\d{5}-\d{3}$',
#             message='CEP com formato inválido.',
#             code='invalid_cep'
#         )
#     ])


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
        quantidade_pessoas = evento.quantidade_pessoas if evento else 0
        self.fields['barco'].help_text = f'<span style="font-size: 1.5em;">Vagas disponíveis: {quantidade_pessoas}</span>'