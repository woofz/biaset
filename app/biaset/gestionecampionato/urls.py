from django.urls import path, include
from .views import CreaCampionatoView, InserisciRiserveView, ModificaCampionatoView, VisualizzaPartitaView, \
    GeneraCalendarioView, SelezionaModuloView, InserisciFormazioneTitolariView, VisualizzaCalendarioView, \
    CaricamentoVotiView, CreaCampionatoLAView
from django.contrib.auth.decorators import login_required

app_name = 'gestionecampionato'

urlpatterns = [
    path('creacampionato/', login_required(CreaCampionatoView.as_view()), name='inserisci_campionato'),
    path('creacampionato/la/', login_required(CreaCampionatoLAView.as_view()), name='inserisci_campionato_la'),
    path('modificacampionato/<pk>/', login_required(ModificaCampionatoView.as_view()), name='modifica_campionato'),
    path('generacalendario/', login_required(GeneraCalendarioView.as_view()), name='genera_calendario'),
    path('inserisciformazione/', login_required(SelezionaModuloView.as_view()), name='seleziona_modulo'),
    path('inserisciformazione/titolari/<int:d>/<int:c>/<int:a>/',
         login_required(InserisciFormazioneTitolariView.as_view()), name='inserisci_titolari'),
    path('inserisciformazione/riserve/', login_required(InserisciRiserveView.as_view()), name='inserisci_riserve'),
    path('calendario/list/', login_required(VisualizzaCalendarioView.as_view()), name='visualizza_calendario'),
    path('visualizzapartita/<giornata>/<squadra_id>/', login_required(VisualizzaPartitaView.as_view()),
         name='visualizza_partita'),
    path('caricamentovoti/', login_required(CaricamentoVotiView.as_view()), name='caricamento_voti')
]
