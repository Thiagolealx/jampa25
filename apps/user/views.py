from django.db.models import Sum
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from formtools.wizard.views import SessionWizardView # type: ignore
from .forms import InscricaoStep1Form, InscricaoStep2Form
from apps.user import forms
from .models import Inscricao

@require_http_methods(['GET'])
def buscar_dados_cpf(request, cpf):
    try:
        inscricao = Inscricao.objects.filter(cpf=cpf).first()
        if inscricao:
            return JsonResponse({
                'success': True,
                'cidade': inscricao.cidade,
                'uf': inscricao.uf
            })
        return JsonResponse({
            'success': False,
            'error': 'CPF não encontrado no sistema'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao buscar dados: {str(e)}'
        })

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
    form_list = FORMS

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        if self.steps.current == 'step2':
            context.update({
                'eventos_formset': kwargs.get('eventos_formset', InscricaoEventoFormSet(queryset=InscricaoEvento.objects.none()))
            })
        return context

    def post(self, *args, **kwargs):
        self.object = self.get_form_instance()
        form = self.get_form(data=self.request.POST, files=self.request.FILES)
        if self.steps.current == 'step2':
            eventos_formset = InscricaoEventoFormSet(self.request.POST, queryset=InscricaoEvento.objects.none())
            if form.is_valid() and eventos_formset.is_valid():
                return self.render_done(form, eventos_formset)
            else:
                return self.render(form, eventos_formset=eventos_formset)
        return super().post(*args, **kwargs)

    def done(self, form_list, **kwargs):
        form_data = [form.cleaned_data for form in form_list]
        # Salve os dados da inscrição aqui
        return render(self.request, 'user/inscricao_done.html', {
            'form_data': form_data,
        })