from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

from gestionecampionato.models import Campionato, Partita
from gestionesquadra.models import Squadra
from gestioneutenza.models import Profilo


class HomeView(View):
    """Definisce la view della dashboard (area privata utente)"""
    template_name = "front/pages/dashboard-index.html"
    error_page = "front/error.html"

    def get(self, request, *args, **kwargs):
        utente = User.objects.get(pk=request.user.pk)
        profilo = None or Profilo.objects.filter(user=utente).first()
        dati_piattaforma = {}
        campionato = None
        if not profilo:
            return redirect(reverse('gestioneutenza:registrazione'))

        if not request.session.get('profilo'):
            request.session['profilo'] = profilo.nome  # Setto la variabile di sessione per il profilo
        if request.session.get('profilo') == 'Championship Admin':
            if not Campionato.objects.filter(championship_admin=utente).exists():
                messages.error(request, 'Non hai ancora creato un campionato! Procedi alla creazione.')
                return redirect('gestionecampionato:inserisci_campionato')

        self.set_session_variables(request, user=utente)

        if request.session.get('profilo') == 'League Admin':
            dati_piattaforma.update({'campionati': Campionato.objects.all(),
                                     'n_campionati': Campionato.objects.all().count(),
                                     'n_utenti': User.objects.all().count(),
                                     'utenti': User.objects.all(),
                                     'n_squadre': Squadra.objects.all().count(),
                                     'squadre': Squadra.objects.all(),
                                     'n_partite': Partita.objects.all().count()
                                     })
        else:
            try:
                campionato = Campionato.objects.get(pk=request.session.get('campionato_id'))
            except Exception:
                return render(request, self.error_page, context={'error': 'Hai un profilo, ma non fai parte di un'
                                                                          ' Campionato. Probabilmente ti stanno '
                                                                          ' assegnando una squadra. '
                                                                          'Attendi pazientemente.'})
        squadre_campionato = Squadra.objects.filter(campionato__id=request.session.get('campionato_id'))

        return render(request, self.template_name, context={'profilo': profilo,
                                                            'utente': utente,
                                                            'campionato_id': request.session.get('campionato_id'),
                                                            'squadra_id': request.session.get('squadra_id'),
                                                            'squadre': squadre_campionato,
                                                            'campionato': campionato,
                                                            'dati_piattaforma': dati_piattaforma})

    def set_session_variables(self, request, user: User):
        profilo = request.session.get('profilo')

        if Squadra.objects.filter(allenatore=user).exists():
            squadra = None or Squadra.objects.filter(allenatore=user).first()
            request.session['campionato_id'] = squadra.campionato.id
            request.session['squadra_id'] = squadra.id
            request.session['nome_campionato'] = Campionato.objects.get(
                pk=request.session.get('campionato_id')).nome_campionato
            request.session['giornata_corrente'] = Campionato.objects.filter(
                pk=request.session['campionato_id']).first() \
                .giornata_corrente
            if Partita.objects.filter(squadra=squadra, giornata=request.session.get('giornata_corrente')).exists():
                partita_corrente = Partita.objects.filter(squadra=squadra, giornata=request.session.get('giornata_corrente')).first()
                request.session['partita_corrente'] = f"{partita_corrente.squadra.first()} vs {partita_corrente.squadra.last()}"
                request.session['partita_id'] = partita_corrente.id

        if profilo == 'Championship Admin':
            request.session['campionato_id'] = Campionato.objects.filter(championship_admin=user).first().id
            # elif profilo == 'Allenatore':
            #     request.session['campionato_id'] = None or squadra.campionato.id
            request.session['nome_campionato'] = Campionato.objects.get(
                pk=request.session.get('campionato_id')).nome_campionato
            request.session['giornata_corrente'] = Campionato.objects.filter(
                pk=request.session['campionato_id']).first() \
                .giornata_corrente
