from django.urls import path
from .views import InscricaoWizard, buscar_dados_cpf, vagas_restantes_view

urlpatterns = [
    path('inscricao/', InscricaoWizard.as_view(), name='inscricao'),
    path('api/buscar-dados-cpf/<str:cpf>/', buscar_dados_cpf, name='buscar_dados_cpf'),
    path('api/vagas_restantes/<int:evento_id>/', vagas_restantes_view, name='vagas_restantes'),
]