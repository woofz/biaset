from multiprocessing import context
from django.shortcuts import redirect, render
from django.views import View
from django.core.mail import send_mail
from django.contrib.auth.models import User
from gestioneutenza.models import Profilo
from gestioneutenza import urls
from gestionecampionato.models import Campionato
from gestionesquadra.models import Squadra
from django.urls import reverse
from django.core import serializers


class HomeView(View):
    '''Definisce la view della dashboard (area privata utente)'''
    template_name = "front/pages/dashboard-index.html"
    
    def get(self, request, *args, **kwargs):
        utente = User.objects.get(pk=request.user.pk)
        profilo = None or Profilo.objects.filter(user=utente).first()
        if not profilo:
            return redirect(reverse('gestioneutenza:registrazione'))
    
        if not request.session.get('profilo'):
            request.session['profilo'] = profilo.nome # Setto la variabile di sessione per il profilo
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
        squadra = None or Squadra.objects.filter(allenatore=user).first()
        if profilo == 'Championship Admin':
            request.session['campionato_id'] = Campionato.objects.filter(championship_admin=user).first().id
        elif profilo == 'Allenatore': 
            request.session['squadra_id'] = None or squadra.id
            request.session['campionato_id'] = None or squadra.campionato.id
        request.session['giornata_corrente'] = Campionato.objects.filter(pk=request.session['campionato_id']).first().giornata_corrente



class LoginView(View):
    '''Definisce la login view'''
    template_name = "front/pages/gestioneutenza/login.html"
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, context={})