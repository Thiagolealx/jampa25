from django.db.models import Sum
from django.shortcuts import render
from formtools.wizard.views import SessionWizardView # type: ignore
from .forms import InscricaoStep1Form, InscricaoStep2Form
from apps.user import forms

# def caixa_view(request):
#     total_parcelas = Congressista.objects.aggregate(total_parcelas=Sum('get_total_parcelas'))['total_parcelas'] or 0
#     total_entrada = Entrada.objects.aggregate(total_entrada=Sum('get_valor_total'))['total_entrada'] or 0
#     total_saida = Saida.objects.aggregate(total_saida=Sum('get_valor_total'))['total_saida'] or 0

#     valor_total_caixa = total_parcelas + total_entrada - total_saida

#     context = {
#         'total_parcelas': total_parcelas,
#         'total_entrada': total_entrada,
#         'total_saida': total_saida,
#         'valor_total_caixa': valor_total_caixa,
#     }

#     return render(request, 'caixa.html', context)


FORMS = [("step1", InscricaoStep1Form),
         ("step2", InscricaoStep2Form)]

TEMPLATES = {"step1": "user/inscricao_step1.html",
             "step2": "user/inscricao_step2.html"}

class InscricaoWizard(SessionWizardView):
    form_list = FORMS  # Certifique-se de que FORMS é uma lista de formulários

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        form_data = [form.cleaned_data for form in form_list]
        # Salve os dados da inscrição aqui
        return render(self.request, 'user/inscricao_done.html', {
            'form_data': form_data,
        })