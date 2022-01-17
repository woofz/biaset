from django.urls import path, include
from .views import CreaCampionatoView, ModificaCampionatoView, GeneraCalendarioView
from django.contrib.auth.decorators import login_required

app_name = 'gestionecampionato'

urlpatterns = [
    path('creacampionato/', login_required(CreaCampionatoView.as_view()), name='inserisci_campionato'),
    path('modificacampionato/<pk>', login_required(ModificaCampionatoView.as_view()), name='modifica_campionato'),
    path('generacalendario/', login_required(GeneraCalendarioView.as_view()), name='genera_calendario'),
]