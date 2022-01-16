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
        squadra = Squadra.objects.filter(allenatore=utente).first()
        request.session['profilo'] = profilo.nome # Setto la variabile di sessione per il profilo
        
        return render(request, self.template_name, context={'profilo': profilo,
                                                            'utente': utente,})


class LoginView(View):
    '''Definisce la login view'''
    template_name = "front/pages/gestioneutenza/login.html"
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, context={})