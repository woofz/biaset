# Check esistenza profilo
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from gestionecampionato.models import Campionato
from django.contrib.auth.models import User


def check_if_profile_exists(function=None):
    '''Controlla se l'utente ha un profilo associato (CA, LA, Allenatore)'''
    def wrapper_func(request, *args, **kwargs):
        if request.session.get('profilo'):
            return redirect(reverse('dashboard_index'))
        return function(request, *args, **kwargs)
    return wrapper_func


def check_user_permission_ca(function=None):
    '''Controlla se un utente ha un profilo da Championship Admin'''
    def wrapper_func(request, *args, **kwargs):
        profilo = request.session.get('profilo')
        if profilo != 'Championship Admin':
            messages.error(request, 'Non hai i permessi per visualizzare questa pagina')
            return redirect('dashboard_index')
        return function(request, *args, **kwargs)
    return wrapper_func


def check_ca_belonging(function=None):
    '''Controlla se l'utente appartiene al campionato nel quale 
    sta effettuando una data operazione'''
    def wrapper_func(request, *args, **kwargs):
        user = User.objects.get(pk=request.user.id)
        campionato = Campionato.objects.filter(championship_admin=user).first() # Controllo se è un CA
        if campionato:
            messages.error(request, "Non sei l'amministratore di questo campionato.")
            return redirect('dashboard_index')
        return function(request, *args, **kwargs)
    return wrapper_func
        