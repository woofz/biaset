# Check esistenza profilo
import functools
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from gestionecampionato.models import Campionato
from gestionesquadra.models import Squadra
from django.contrib.auth.models import User
from django.utils.functional import wraps
from gestionecampionato.exceptions import CampionatoGiaAssociatoException
from django.shortcuts import render


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


def check_if_user_is_allenatore_squadra(function=None):
    """Controlla se l'utente è l'allenatore della squadra che vuole modificare"""
    def wrapper_func(request, pk: int, *args, **kwargs):
        squadra = Squadra.objects.get(pk=pk)
        if squadra.allenatore_id != request.user.id:
            messages.error(request, 'Puoi modificare solo la tua squadra!')
            return redirect('dashboard_index')
        return function(request, *args, **kwargs)
    return wrapper_func


def check_championship_existence(function=None):
    '''Controlla se un CA ha un campionato associato'''
    def wrapper_func(request, *args, **kwargs):
        if Campionato.objects.filter(championship_admin__id=request.user.id).exists():
            raise CampionatoGiaAssociatoException('Campionato già esistente.')
        return function(request, *args, **kwargs)
    return wrapper_func


def handle_view_exception(func):
    """Decorator per gestire le eccezioni."""
    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        try:
            response = func(request, *args, **kwargs)
        except Exception as e:
            context = {
              'error': str(e),
            }
            response = render(request, 'front/error.html', context=context)
        return response

    return wrapper