from django import forms
from django.core.validators import RegexValidator
from django.forms import TextInput
from .models import Profissional, Evento, Inscricao

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
        if evento:
            vagas_disponiveis = evento.quantidade_pessoas - evento.contador_barco
            self.fields['barco'].help_text = f'<span style="font-size: 1.5em;">Vagas disponíveis: {vagas_disponiveis}</span>'
        else:
            self.fields['barco'].help_text = '<span style="font-size: 1.5em;">Evento não encontrado.</span>'
    
    # def clean(self):
    #     evento = Evento.objects.first()
    #     if not evento:
    #         raise forms.ValidationError("Evento não encontrado.")
    
    #     if self.cleaned_data.get('barco'):
    #         if evento.contador_barco >= evento.quantidade_pessoas:
    #             raise forms.ValidationError("Não há vagas disponíveis no barco.")
    #     return self.cleaned_data



class InscricaoStep1Form(forms.ModelForm):
    class Meta:
        model = Inscricao
        fields = ['nome', 'cpf', 'categoria']

class InscricaoStep2Form(forms.ModelForm):
    class Meta:
        model = Inscricao
        fields = ['lote', 'evento']