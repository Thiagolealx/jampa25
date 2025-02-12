from os import path
from django.contrib import admin
from .models import Lote,Categoria,TipoEvento,Evento,Camisas,Planejamento
from django.db.models import Sum



class LoteAdmin(admin.ModelAdmin):

    list_display = [
        "descricao",
        "valor_unitario",
    ]
    ordering = ['-id']

admin.site.register(Lote, LoteAdmin)

class CategoriaAdmin(admin.ModelAdmin):

    list_display = [
        "descricao",
    ]
    ordering = ['-id']

admin.site.register(Categoria, CategoriaAdmin)

class TipoEventoAdmin(admin.ModelAdmin):

    list_display = [
        "descricao",
    ]
    ordering = ['-id']

admin.site.register(TipoEvento, TipoEventoAdmin)

class EventoAdmin(admin.ModelAdmin):
    
    list_display = [
        "descricao",
        "tipo",        
        "data",
        "valor_planejado",
        "valor_arrecadado",
        "valor_do_evento",
    ]
    ordering = ['-id']

admin.site.register(Evento, EventoAdmin)

class CamisasAdmin(admin.ModelAdmin):
    
    list_display = [
        "descricao",
        "tipo",
        "tamanho",
    ]
    ordering = ['-id']

admin.site.register(Camisas, CamisasAdmin)


class PlanejamentoAdmin(admin.ModelAdmin):
    
    list_display = [
        "descricao",
        "valor_planejado",        
        "valor_pago",
    ]
    ordering = ['-id']
    change_list_template = "congressita/change_list_planejamento.html"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        total_valor_planejado = Planejamento.objects.aggregate(Sum('valor_planejado'))['valor_planejado__sum'] or 0
        extra_context['total_valor_planejado'] = total_valor_planejado
        return super(PlanejamentoAdmin, self).changelist_view(request, extra_context=extra_context)

admin.site.register(Planejamento, PlanejamentoAdmin)