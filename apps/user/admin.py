from os import path
from django.contrib import admin
from .models import Lote,Categoria,TipoEvento,Evento,Camisas,Planejamento,Profissional,Inscricao
from .forms import ProfissionalForm
from django.db.models import Sum



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

from django.contrib import admin
from .models import Inscricao

@admin.register(Inscricao)
class InscricaoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cpf', 'categoria', 'lote', 'evento']
    search_fields = ['nome', 'cpf']
    list_filter = ['categoria', 'lote', 'evento']
    fieldsets = (
        ('Cadastro', {
            'fields': ('nome', 'cpf', 'categoria')
        }),
        ('Pagamentos', {
            'fields': ('lote', 'evento')
        }),
    )