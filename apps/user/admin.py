from os import path
from django.contrib import admin
from .models import Lote,Categoria,TipoEvento,Evento,Camisas,Planejamento,Profissional,Inscricao,InscricaoEvento,Pagamento,Caixa
from .models import Entradas, Saidas
from .forms import ProfissionalForm
from django.db.models import Sum
from .forms import InscricaoFormAdmin
from django.utils.safestring import mark_safe
from django.forms import inlineformset_factory
from django.forms import ModelForm
from .forms import PagamentoForm
from django.db.models import F, Sum, ExpressionWrapper, DecimalField


class LoteAdmin(admin.ModelAdmin):
    
    list_display = [
        "descricao",
        "valor_unitario",
        "unidades",
        "status"
    ]
    ordering = ['-id']
    search_fields = ['status', 'descricao']

admin.site.register(Lote, LoteAdmin)

class CategoriaAdmin(admin.ModelAdmin):

    list_display = [
        "descricao",

    ]
    ordering = ['-id']
    search_fields = ['descricao']

admin.site.register(Categoria, CategoriaAdmin)

class TipoEventoAdmin(admin.ModelAdmin):

    list_display = [
        "descricao",

    ]
    ordering = ['-id']
    search_fields = ['descricao']

admin.site.register(TipoEvento, TipoEventoAdmin)

class EventoAdmin(admin.ModelAdmin):
    
    list_display = [
        "descricao",
        "tipo",        
        "data",
        "valor_planejado",
        "valor_arrecadado",
        "valor_do_evento",
        "quantidade_pessoas",
        "contador_inscricoes",
         ]

    ordering = ['-id']
    search_fields = ['descricao', 'tipo', 'data',]

admin.site.register(Evento, EventoAdmin)

class CamisasAdmin(admin.ModelAdmin):
    
    list_display = [
        "descricao",
        "tipo",
        "tamanho",
    ]
    ordering = ['-id']
    search_fields = ['descricao', 'tipo']

admin.site.register(Camisas, CamisasAdmin)


class PlanejamentoAdmin(admin.ModelAdmin):
    
    list_display = [
        "descricao",
        "valor_planejado",        
        "valor_pago",
    ]
    ordering = ['-id']
    change_list_template = "user/change_list_planejamento.html"
    search_fields = ['descricao']

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        total_valor_planejado = Planejamento.objects.aggregate(Sum('valor_planejado'))['valor_planejado__sum'] or 0
        extra_context['total_valor_planejado'] = total_valor_planejado
        return super(PlanejamentoAdmin, self).changelist_view(request, extra_context=extra_context)

admin.site.register(Planejamento, PlanejamentoAdmin)

class ProfissionalAdmin(admin.ModelAdmin):
    form = ProfissionalForm
    list_display = [
        "nome",
        "funcao",
        "cache",
        "jack_jill",
        # "barco_com_quantidade_pessoas"
    ]
    ordering = ['-id']
    search_fields = ['nome', 'funcao__nome']
    # change_form_template = "congressita/change_forms_profissional.html"
    def delete_queryset(self, request, queryset):
        evento = Evento.objects.first()  # Ajuste conforme necessário para obter o evento correto
        barco_count = queryset.filter(barco=True).count()
        if evento:
            evento.contador_barco -= barco_count
            evento.save()
        queryset.delete()


admin.site.register(Profissional, ProfissionalAdmin)

class InscricaoEventoInline(admin.TabularInline):
    model = InscricaoEvento
    extra = 1
    fields = ('evento', 'confirmar', 'vagas_restantes')
    readonly_fields = ('vagas_restantes',)

    def vagas_restantes(self, obj):
        return obj.vagas_restantes() if obj.evento else "Selecionar evento"

    class Media:
        js = ('js/inscricao_evento.js',)  


@admin.register(Inscricao)

class InscricaoAdmin(admin.ModelAdmin):
    form = InscricaoFormAdmin
    change_list_template = "user/change_list_congressitas.html"
    list_display = ['nome', 'categoria', 'lote', 'eventos_cadastrados', 'calcular_valor_total_display', 'parcelas', 'parcela_display',
                    'valor_pago_total', 'valor_a_pagar', 'data_proximo_pagamento']
    search_fields = ['nome', 'cpf']
    list_filter = ['categoria', 'lote']
    fieldsets = (
        ('Cadastro', {
            'fields': ('nome', 'cpf', 'categoria', 'cep', 'cidade', 'uf')
        }),
    )
    inlines = [InscricaoEventoInline]
    fieldsets += (
        ('Pagamentos', {
            'fields': ('lote', 'desconto', 'parcelas', 'valor_total')
        }),
    )
    readonly_fields = ['valor_total']
    
    change_form_template = "user/change_form_inscricao.html"
    

    def calcular_valor_total_display(self, obj):
        return obj.calcular_valor_total()  

    calcular_valor_total_display.short_description = 'Total' 

    def parcela_display(self, obj):
        return f"{obj.calcular_parcela():.2f}" 

    parcela_display.short_description = 'Valor da Parcela'  

    def valor_pago_total(self, obj):
        return obj.valor_pago_total()  

    def valor_a_pagar(self, obj):
        return obj.valor_a_pagar()

    def data_proximo_pagamento(self, obj):
        pagamentos = obj.pagamento_set.order_by('-data_pagamento')
        return pagamentos.first().data_proximo_pagamento if pagamentos.exists() else None

    # def changelist_view(self, request, extra_context=None):
    #     extra_context = extra_context or {}
    #     # Agregando a soma do valor_pago dos pagamentos associados
    #     total_valor_inscritos = Inscricao.objects.aggregate(Sum('pagamento__valor_pago'))['pagamento__valor_pago__sum'] or 0
    #     print("Total Valor Inscritos:", total_valor_inscritos)
        
    #     extra_context['total_valor_inscritos'] = total_valor_inscritos
    #     return super(InscricaoAdmin, self).changelist_view(request, extra_context=extra_context)

 
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        total_valor_inscritos = Inscricao.objects.aggregate(Sum('pagamento__valor_pago'))['pagamento__valor_pago__sum'] or 0
        print("Total Valor Inscritos:", total_valor_inscritos)
    
        # Calcular o total de valor a pagar
        total_valor_a_pagar = sum(inscricao.valor_a_pagar() for inscricao in Inscricao.objects.all())
        
        print("Total Valor a Pagar:", total_valor_a_pagar)
    
        extra_context['total_valor_inscritos'] = total_valor_inscritos
        extra_context['total_valor_a_pagar'] = total_valor_a_pagar
        return super(InscricaoAdmin, self).changelist_view(request, extra_context=extra_context)

    
        

class EntradasAdmin(admin.ModelAdmin):
    list_display = ['descricao', 'valor_unitario', 'quantidade', 'valor_total']  # Mantenha valor_total aqui
    search_fields = ['descricao']
    list_filter = ['data']
    fieldsets = (
        ('Entradas', {
            'fields': ('descricao', 'valor_unitario', 'quantidade' )
        }),
    )
    change_list_template = "user/change_list_entradas.html"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        total_valor_entradas = Entradas.objects.aggregate(Sum('valor_total'))['valor_total__sum'] or 0
        extra_context['total_valor_entradas'] = total_valor_entradas
        return super(EntradasAdmin, self).changelist_view(request, extra_context=extra_context)

class SaidasAdmin(admin.ModelAdmin):
    list_display = ['descricao', 'valor_unitario', 'quantidade', 'valor_total']
    search_fields = ['descricao']
    list_filter = ['data','descricao']
    change_list_template = "user/change_list_saidas.html"

    fieldsets = (
        ('Saidas', {
            'fields': ('descricao', 'valor_unitario', 'quantidade', )
        }),
    )

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        total_valor_saidas = Saidas.objects.aggregate(Sum('valor_total'))['valor_total__sum'] or 0
        extra_context['total_valor_saidas'] = total_valor_saidas
        return super(SaidasAdmin, self).changelist_view(request, extra_context=extra_context)

# Registrando os modelos no Admin
admin.site.register(Entradas, EntradasAdmin)
admin.site.register(Saidas, SaidasAdmin)


class PagamentoAdmin(admin.ModelAdmin):
    form = PagamentoForm
    list_display = ['inscricao', 'valor_pago', 'parcela', 'data_pagamento']
    search_fields = ['inscricao__nome']
    list_filter = ['data_pagamento']
  

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            previous_payments = Pagamento.objects.filter(inscricao=obj.inscricao)
            form.previous_payments = previous_payments
        return form

admin.site.register(Pagamento, PagamentoAdmin)

class CaixaAdmin(admin.ModelAdmin):
    change_list_template = "user/change_list_caixa.html"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        total_inscricoes = Inscricao.objects.aggregate(Sum('valor_total'))['valor_total__sum'] or 0
        total_camisas = Camisas.objects.aggregate(Sum('valor_unitario'))['valor_unitario__sum'] or 0
        total_entradas = Entradas.objects.aggregate(Sum('valor_total'))['valor_total__sum'] or 0
        total_saidas = Saidas.objects.aggregate(Sum('valor_total'))['valor_total__sum'] or 0
        total_planejamento = Planejamento.objects.aggregate(Sum('valor_planejado'))['valor_planejado__sum'] or 0

        total_caixa = (total_inscricoes + total_camisas + total_entradas + total_planejamento) - total_saidas

        extra_context['total_inscricoes'] = total_inscricoes
        extra_context['total_camisas'] = total_camisas
        extra_context['total_entradas'] = total_entradas
        extra_context['total_saidas'] = total_saidas
        extra_context['total_planejamento'] = total_planejamento
        extra_context['total_caixa'] = total_caixa

        return super().changelist_view(request, extra_context=extra_context)

admin.site.register(Caixa, CaixaAdmin)

