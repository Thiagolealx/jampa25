from django.urls import path
from .views import InscricaoWizard, buscar_dados_cpf

urlpatterns = [
    path('inscricao/', InscricaoWizard.as_view(), name='inscricao'),
    path('api/buscar-dados-cpf/<str:cpf>/', buscar_dados_cpf, name='buscar_dados_cpf'),
]