from django.shortcuts import render
from django.views import View
from django.views.generic import CreateView, UpdateView, ListView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator

from gestionecampionato.forms import CreaCampionatoForm, ModificaCampionatoForm
from core.decorators import check_user_permission_ca, check_ca_belonging
from .models import Campionato

decorators = [check_user_permission_ca]

@method_decorator(decorators, name='dispatch')
class CreaCampionatoView(SuccessMessageMixin, CreateView):
    model = Campionato
    form_class = CreaCampionatoForm
    success_message = 'Campionato creato correttamente!'
    template_name = "front/pages/gestionecampionato/creacampionato.html"
    success_url = reverse_lazy('dashboard_index')
    

@method_decorator(decorators, name='dispatch')
@method_decorator(check_ca_belonging, name='dispatch')
class ModificaCampionatoView(SuccessMessageMixin, UpdateView):
    model = Campionato
    form_class = ModificaCampionatoForm
    success_message = 'Campionato modificato correttamente!'
    template_name = 'front/pages/gestionecampionato/modifica-campionato.html'


@method_decorator(decorators, name='dispatch')
class GeneraCalendarioView(View):
    pass


