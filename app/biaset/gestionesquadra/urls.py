from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import VisualizzaSquadraView, AssociaGiocatoreASquadra, licenziaGiocatore, InserisciSquadraView, \
    VisualizzaSquadreLAView

app_name = 'gestionesquadra'
urlpatterns = [
    path('visualizzasquadra/<int:pk>/', login_required(VisualizzaSquadraView.as_view()), name='visualizza_squadra'),
    path('ajax/licenziagiocatore/', login_required(licenziaGiocatore), name='licenzia_giocatore_ajax'),
    path('associagiocatore/', login_required(AssociaGiocatoreASquadra.as_view()), name='associa_giocatore'),
    path('inseriscisquadra/', login_required(InserisciSquadraView.as_view()), name='inserisci_squadra'),
    path('list/', login_required(VisualizzaSquadreLAView.as_view()), name='visualizza_squadre'),
]
