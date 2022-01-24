# Check esistenza profilo
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from gestionecampionato.models import Campionato
from gestionesquadra.models import Squadra
from django.contrib.auth.models import User
from django.utils.functional import wraps


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
        if request.session.get('profilo') != 'Championship Admin':
            messages.error(request, 'Non hai i permessi per visualizzare questa pagina')
            return redirect('dashboard_index')
        return function(request, *args, **kwargs)
    return wrapper_func


def check_ca_belonging(function=None):
    '''Controlla se l'utente appartiene al campionato nel quale 
    sta effettuando una data operazione'''
    @wraps(function)
    def wrapper_func(request, pk: int, *args, **kwargs):
        user = User.objects.get(pk=request.user.id)
        campionato = Campionato.objects.filter(championship_admin=user).first() # Controllo se è un CA
        if int(campionato.id) != int(pk):
            messages.error(request, "Non sei l'amministratore di questo campionato.")
            return redirect('dashboard_index')
        return function(request, *args, **kwargs)
    return wrapper_func


def check_team_belonging(function=None):
    '''Controlla se la squadra appartiene al campionato nel quale 
    sta effettuando una data operazione'''
    @wraps(function)
    def wrapper_func(request, *args, **kwargs):
        pk = request.GET.get('squadra_id', None)
        user = User.objects.get(pk=request.user.id)
        squadra = Squadra.objects.get(pk=pk)
        campionato = Campionato.objects.filter(championship_admin=user).first() # Controllo se è un CA
        if int(squadra.allenatore.id) != int(request.user.id) and request.session.get('profilo') != 'Championship Admin':
            messages.error(request, "Non hai i permessi per licenziare questo giocatore.")
            return redirect('dashboard_index')
        return function(request, *args, **kwargs)
    return wrapper_func


def check_user_permission_la(function=None):
    '''Controlla se un utente ha un profilo da League Admin'''
    def wrapper_func(request, *args, **kwargs):
        print(request.session.get('profilo'))
        if request.session.get('profilo') != 'League Admin':
            messages.error(request, 'Non hai i permessi per visualizzare questa pagina')
            return redirect('dashboard_index')
        return function(request, *args, **kwargs)
    return wrapper_func


def check_user_permission_la_ca(function=None):
    '''Controlla se un utente ha un profilo da LA/CA'''
    def wrapper_func(request, *args, **kwargs):
        if request.session.get('profilo') == 'Allenatore':
            messages.error(request, 'Non hai i permessi per visualizzare questa pagina')
            return redirect('dashboard_index')
        return function(request, *args, **kwargs)
    return wrapper_func
