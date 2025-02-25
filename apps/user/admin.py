from os import path
from django.contrib import admin
from .models import Lote,Categoria,TipoEvento,Evento,Camisas,Planejamento,Profissional,Inscricao,InscricaoEvento, Pagamento
from .forms import ProfissionalForm
from django.db.models import Sum
from .forms import InscricaoFormAdmin


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
        "contador_barco"
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

@admin.register(Inscricao)
class InscricaoAdmin(admin.ModelAdmin):
    form = InscricaoFormAdmin
    list_display = ['nome', 'categoria', 'lote', 'eventos_cadastrados', 'calcular_valor_total', 'parcelas','calcular_parcela']
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
            'fields': ('lote','desconto', 'parcelas', 'valor_total' )
        }),
    )
    readonly_fields = ['valor_total']
    
    change_form_template = "user/change_form_inscricao.html"
    
    
from django.contrib import admin
from .models import Entradas, Saidas

class EntradasAdmin(admin.ModelAdmin):
    list_display = ['descricao', 'valor_unitario', 'quantidade', 'valor_total', 'data']
    search_fields = ['descricao']
    list_filter = ['data']
    change_list_template = "user/change_list_entradas.html"

class SaidasAdmin(admin.ModelAdmin):
    list_display = ['descricao', 'valor_unitario', 'quantidade', 'valor_total', 'data']
    search_fields = ['descricao']
    list_filter = ['data']
    change_list_template = "user/change_list_saidas.html"

# Registrando os modelos no Admin
admin.site.register(Entradas, EntradasAdmin)
admin.site.register(Saidas, SaidasAdmin)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ['inscricao', 'parcela', 'valor_pago', 'data_pagamento', 'valor_parcela']
    search_fields = ['inscricao__nome']
    list_filter = ['parcela']
    readonly_fields = ['valor_parcela']  # Adiciona o campo valor_parcela como somente leitura

    def valor_parcela(self, obj):
        if obj and obj.inscricao:
            return obj.inscricao.calcular_parcela()  # Chama o método para calcular o valor da parcela
        return 0  # Retorna 0 se não houver objeto ou inscrição

    valor_parcela.short_description = 'Valor da Parcela'  # Título da coluna na interface admin

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:  # Se estamos editando um pagamento existente
            form.base_fields['valor_pago'].initial = obj.inscricao.calcular_parcela()  # Preencher com o valor da parcela
            form.base_fields['valor_parcela'] = self.valor_parcela(obj)  # Adiciona o valor da parcela ao formulário
        return form

admin.site.register(Pagamento, PagamentoAdmin)
