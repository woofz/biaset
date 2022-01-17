from webbrowser import get
from django.shortcuts import render
from django.views import View
from django.views.generic import CreateView, UpdateView, ListView
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from gestionecampionato.commandpattern.invoker import Invoker
from gestionecampionato.commandpattern.generacalendariocommand import GeneraCalendarioCommand
from gestionecampionato.commandpattern.receiver import Receiver

from gestionecampionato.forms import CreaCampionatoForm, ModificaCampionatoForm
from gestionesquadra.models import Squadra
from core.decorators import check_user_permission_ca, check_ca_belonging
from .models import Campionato

decorators = [check_user_permission_ca]

@method_decorator(decorators, name='dispatch')
class CreaCampionatoView(SuccessMessageMixin, CreateView):
    """Classe View che permette la creazione di un campionato"""
    model = Campionato
    form_class = CreaCampionatoForm
    success_message = 'Campionato creato correttamente!'
    template_name = "front/pages/gestionecampionato/creacampionato.html"
    success_url = reverse_lazy('dashboard_index')
    

@method_decorator(decorators, name='dispatch')
@method_decorator(check_ca_belonging, name='dispatch')
class ModificaCampionatoView(SuccessMessageMixin, UpdateView):
    """Classe View che permette la modifica di un campionato"""
    model = Campionato
    form_class = ModificaCampionatoForm
    success_message = 'Campionato modificato correttamente!'
    template_name = 'front/pages/gestionecampionato/modifica-campionato.html'


@method_decorator(decorators, name='dispatch')
class GeneraCalendarioView(View):
    """Classe View che permette la generazione degli scontri di un campionato"""
    template_name = 'front/pages/gestionecampionato/generacalendario.html'
    
    def post(self, request, *args, **kwargs):
        """Il 'client' del pattern Command. Parametrizza un Invoker con un Receiver """
        user = User.objects.get(pk=request.user.id) # L'utente della sessione
        campionato = Campionato.objects.get(championship_admin=user) # Prendo il campionato
        invoker = Invoker() # Preparo l'invoker
        receiver = Receiver() # Inizializzo il Receiver 
        invoker.setCommand(GeneraCalendarioCommand(receiver=receiver, campionato=campionato)) # Chiamo il comando
        #invoker.doOperation()
        messages.success(request, 'Generazione calendario avvenuta con successo!')
        return redirect('dashboard_index')
    
    def get(self, request, *args, **kwargs):
        user = User.objects.get(pk=request.user.id) # L'utente della sessione
        campionato = Campionato.objects.get(championship_admin=user) # Prendo il campionato
        championship_teams = Squadra.objects.filter(campionato=campionato)
        return render(request, self.template_name, context={'championship_teams': championship_teams})
    