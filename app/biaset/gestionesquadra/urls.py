from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import VisualizzaSquadraView, AssociaGiocatoreASquadra, licenziaGiocatore, InserisciSquadraView, \
    VisualizzaSquadreLAView, ModificaNomeSquadraView, ModificaSquadraView, eliminaSquadra

app_name = 'gestionesquadra'
urlpatterns = [
    path('visualizzasquadra/<int:pk>/', login_required(VisualizzaSquadraView.as_view()), name='visualizza_squadra'),
    path('ajax/licenziagiocatore/', login_required(licenziaGiocatore), name='licenzia_giocatore_ajax'),
    path('ajax/eliminasquadra/', login_required(eliminaSquadra), name='elimina_squadra_ajax'),
    path('associagiocatore/', login_required(AssociaGiocatoreASquadra.as_view()), name='associa_giocatore'),
    path('inseriscisquadra/', login_required(InserisciSquadraView.as_view()), name='inserisci_squadra'),
    path('modificanomesquadra/<pk>/', login_required(ModificaNomeSquadraView.as_view()), name='modifica_squadra'),
    path('modificasquadra/<pk>/', login_required(ModificaSquadraView.as_view()), name='modifica_squadra_superuser'),
    path('list/', login_required(VisualizzaSquadreLAView.as_view()), name='visualizza_squadre'),
]
