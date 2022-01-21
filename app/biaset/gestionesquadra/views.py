from multiprocessing import context
from django.shortcuts import render
from django.views import View
from django.db.models import Sum
from django.views.generic import ListView, UpdateView
from .models import Squadra, Giocatore
from .forms import AssociaGiocatoreForm
from django.contrib import sessions
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from gestionecampionato.models import Campionato
from core.decorators import check_user_permission_ca, check_team_belonging

@check_team_belonging
def licenziaGiocatore(request):
    '''Licenzia un giocatore da una squadra [AJAX Function]'''
    giocatore_id = request.GET.get('giocatore_id', None)
    squadra_id = request.GET.get('squadra_id', None)
    data = {
        'status': 'ok'
    }
    try:
        giocatore = Giocatore.objects.get(pk=giocatore_id)
        squadra = Squadra.objects.get(pk=squadra_id)
        giocatore.squadra.remove(squadra)
    except Exception:
        messages.error(request, 'Il giocatore in questione non è registrato.')
    return JsonResponse(data)

def check_squadra_ownership(request, pk: int, *args, **kwargs) -> bool:
    user = User.objects.get(pk=request.user.id)
    squadra_passata = Squadra.objects.get(pk=pk)
    if (user != squadra_passata.allenatore and request.session.get('profilo') not in ('League Admin', 'Championship Admin') 
        or int(request.session.get('campionato_id')) != int(squadra_passata.campionato.id)):
        return False
    return True
    
    
class VisualizzaSquadraView(View):
    """Vista per la visualizzazione di una Squadra"""
    template_name='front/pages/gestionesquadra/list.html'
    
    def get(self, request, pk: int, *args, **kwargs):
        squadra = Squadra.objects.get(pk=pk)
        budget_disponibile = 0
        spesa_stipendi = 0
        ownership = False
        try:
            qs = Giocatore.objects.filter(squadra__id=squadra.pk).order_by('-ruolo', '-quotazione')
            stipendi = qs.aggregate(totale_quotazioni=Sum('quotazione'))
            budget_disponibile = 0 or round((50 - (stipendi['totale_quotazioni']/40))*3.14, 2)
            ownership = check_squadra_ownership(request=request, pk=pk)
            spesa_stipendi = round(stipendi['totale_quotazioni']/40, 2)
        except Exception:
            pass
        return render(request, self.template_name, context={ 'giocatori': qs, 'budget_disponibile': budget_disponibile, 
                                                            'stipendi': spesa_stipendi, 
                                                            'ownership': ownership, 
                                                            'squadra': squadra})


class AssociaGiocatoreASquadra(FormView):
    template_name='front/pages/gestionesquadra/associa-giocatore.html'
    
    def get(self, request, *args, **kwargs):
        campionato = Campionato.objects.get(pk=request.session.get('campionato_id'))
        squadra = Squadra.objects.get(pk=request.session.get('squadra_id'))
        form = AssociaGiocatoreForm(campionato=campionato, squadra=squadra)
        return render(request, self.template_name, context={'form': form})
    
    def post(self, request, *args, **kwargs):
        campionato = Campionato.objects.get(pk=request.session.get('campionato_id'))
        squadra = Squadra.objects.get(pk=request.session.get('squadra_id'))
        form = AssociaGiocatoreForm(request.POST, campionato=campionato, squadra=squadra)
        if form.is_valid():
            form.associaGiocatore()
            messages.success(request, 'Giocatore associato correttamente!')
            return redirect('gestionesquadra:associa_giocatore')
        return render(request, self.template_name, context={'form': form})