from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

from gestionecampionato.models import Campionato
from gestionesquadra.models import Squadra
from gestioneutenza.models import Profilo


class HomeView(View):
    """Definisce la view della dashboard (area privata utente)"""
    template_name = "front/pages/dashboard-index.html"

    def get(self, request, *args, **kwargs):
        utente = User.objects.get(pk=request.user.pk)
        profilo = None or Profilo.objects.filter(user=utente).first()
        if not profilo:
            return redirect(reverse('gestioneutenza:registrazione'))

        if not request.session.get('profilo'):
            request.session['profilo'] = profilo.nome  # Setto la variabile di sessione per il profilo
        if not request.session.get('campionato'):
            self.set_session_variables(request, user=utente)
        squadre_campionato = Squadra.objects.filter(campionato__id=request.session.get('campionato_id'))
        return render(request, self.template_name, context={'profilo': profilo,
                                                            'utente': utente,
                                                            'campionato_id': request.session.get('campionato_id'),
                                                            'squadra_id': request.session.get('squadra_id'),
                                                            'squadre': squadre_campionato})

    def set_session_variables(self, request, user: User):
        profilo = request.session.get('profilo')

        if Squadra.objects.filter(allenatore=user).exists():
            squadra = None or Squadra.objects.filter(allenatore=user).first()
            request.session['campionato_id'] = squadra.campionato.id
            request.session['squadra_id'] = squadra.id
            request.session['nome_campionato'] = Campionato.objects.get(pk=request.session.get('campionato_id')).nome_campionato
            request.session['giornata_corrente'] = Campionato.objects.filter(pk=request.session['campionato_id']).first() \
            .giornata_corrente

        if profilo == 'Championship Admin':
            request.session['campionato_id'] = Campionato.objects.filter(championship_admin=user).first().id
        # elif profilo == 'Allenatore':
        #     request.session['campionato_id'] = None or squadra.campionato.id
            request.session['nome_campionato'] = Campionato.objects.get(pk=request.session.get('campionato_id')).nome_campionato
            request.session['giornata_corrente'] = Campionato.objects.filter(pk=request.session['campionato_id']).first() \
            .giornata_corrente
