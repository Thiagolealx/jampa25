from django.urls import path
from .views import InscricaoWizard

urlpatterns = [
    path('inscricao/', InscricaoWizard.as_view(), name='inscricao'),
]