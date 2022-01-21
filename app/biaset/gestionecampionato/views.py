from django.shortcuts import render
from django.views import View
from django.views.generic import CreateView, UpdateView, ListView
from django.forms import formset_factory
from django.contrib.auth.models import User
from django.forms import BaseFormSet
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.db.models import Count

from gestionecampionato.commandpattern.invoker import Invoker
from gestionecampionato.commandpattern.generacalendariocommand import GeneraCalendarioCommand
from gestionecampionato.commandpattern.receiver import Receiver

from gestionecampionato.forms import CreaCampionatoForm, ModificaCampionatoForm, SelezionaModuloForm, TitolariForm, TitolariFormSet, RiserveFormSet, RiserveForm
from gestionesquadra.models import Squadra
from core.decorators import check_user_permission_ca, check_ca_belonging
from .models import Campionato, Partita, Formazione

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
        user = User.objects.get(pk=request.user.id)  # L'utente della sessione
        campionato = Campionato.objects.get(
            championship_admin=user)  # Prendo il campionato
        invoker = Invoker()  # Preparo l'invoker
        receiver = Receiver()  # Inizializzo il Receiver
        invoker.setCommand(GeneraCalendarioCommand(
            receiver=receiver, campionato=campionato))  # Chiamo il comando
        invoker.doOperation()
        messages.success(
            request, 'Generazione calendario avvenuta con successo!')
        return redirect('dashboard_index')

    def get(self, request, *args, **kwargs):
        user = User.objects.get(pk=request.user.id)  # L'utente della sessione
        campionato = Campionato.objects.get(
            championship_admin=user)  # Prendo il campionato
        championship_teams = Squadra.objects.filter(campionato=campionato)
        return render(request, self.template_name, context={
                      'championship_teams': championship_teams})


class SelezionaModuloView(View):
    """Classe View per selezionare il modulo della formazione titolare"""
    template_name = 'front/pages/gestionecampionato/seleziona-modulo.html'

    def post(self, request, *args, **kwargs):
        form = SelezionaModuloForm(request.POST)
        if form.is_valid():
            return redirect('gestionecampionato:inserisci_titolari', d=form.cleaned_data['difensori'],
                            c=form.cleaned_data['centrocampisti'],
                            a=form.cleaned_data['attaccanti'])
        return render(request, self.template_name, context={'form': form})

    def get(self, request, *args, **kwargs):
        form = SelezionaModuloForm
        return render(request, self.template_name, context={'form': form})


class InserisciFormazioneTitolariView(View):
    """Classe View per inserire la formazione titolare"""
    template_name = 'front/pages/gestionecampionato/inserisci-titolari.html'

    def get(self, request, d: int, c: int, a: int):
        """Ulteriore controllo sul totale dei giocatori selezionati nel modulo"""
        if (d + c + a) != 10:
            messages.error(request, 'La somma del modulo non è uguale a 10!')
            return redirect('gestionecampionato:seleziona_modulo')

        PortieriFormSet = formset_factory(TitolariForm, extra=1)
        DifensoriFormSet = formset_factory(TitolariForm, extra=d)
        CentrocampistiFormSet = formset_factory(TitolariForm, extra=c)
        AttaccantiFormSet = formset_factory(TitolariForm, extra=a)

        portieri_formset = PortieriFormSet(
            form_kwargs={'squadra': request.user.squadra, 'ruolo': 'P'}, prefix='portiere')
        difensori_formset = DifensoriFormSet(
            form_kwargs={'squadra': request.user.squadra, 'ruolo': 'D'}, prefix='difensori')
        centrocampisti_formset = CentrocampistiFormSet(
            form_kwargs={'squadra': request.user.squadra, 'ruolo': 'C'}, prefix='centrocampisti')
        attaccanti_formset = AttaccantiFormSet(
            form_kwargs={'squadra': request.user.squadra, 'ruolo': 'A'}, prefix='attaccanti')

        return render(request, self.template_name, context={'form_portiere': portieri_formset,
                                                            'form_difensori': difensori_formset,
                                                            'form_centrocampisti': centrocampisti_formset,
                                                            'form_attaccanti': attaccanti_formset,
                                                            'modulo': str(d) + "-" + str(c) + "-" + str(a)})

    def post(self, request, *args, **kwargs):
        """Metodo per la gestione del metodo POST"""
        FormSetBase = formset_factory(TitolariForm, formset=TitolariFormSet)
        form_portieri = FormSetBase(request.POST, form_kwargs={
                                    'squadra': request.user.squadra, 'ruolo': 'P'}, prefix='portiere')
        form_difensori = FormSetBase(request.POST, form_kwargs={
                                     'squadra': request.user.squadra, 'ruolo': 'D'}, prefix='difensori')
        form_centrocampisti = FormSetBase(request.POST, form_kwargs={
                                          'squadra': request.user.squadra, 'ruolo': 'C'}, prefix='centrocampisti')
        form_attaccanti = FormSetBase(request.POST, form_kwargs={
                                      'squadra': request.user.squadra, 'ruolo': 'A'}, prefix='attaccanti')
        

            
        # Recupero la squadra e il campionato dalla sessione
        squadra = Squadra.objects.get(pk=request.session.get('squadra_id'))
        campionato = squadra.campionato
        # Recupero la giornata corrente per inserire la formazione Titolare
        partita = Partita.objects.filter(squadra=squadra).filter(
            giornata=campionato.giornata_corrente).first()

        formazione_giornata = Formazione.objects.filter(
            partita=partita, squadra=squadra).filter(tipo='T').first()

        if formazione_giornata.giocatore.exists():
            print('esiste')
            formazione_giornata.giocatore.clear()
            
        if form_portieri.is_valid() and form_difensori.is_valid(
        ) and form_centrocampisti.is_valid() and form_attaccanti.is_valid():
            for form in form_portieri:
                form.save(formazione=formazione_giornata)
            for form in form_difensori:
                form.save(formazione=formazione_giornata)
            for form in form_centrocampisti:
                form.save(formazione=formazione_giornata)
            for form in form_attaccanti:
                form.save(formazione=formazione_giornata)

            messages.success(
                request, 'Formazione titolare inserita con successo!')
            return redirect('gestionecampionato:inserisci_riserve')

        return render(request, self.template_name, context={'form_portiere': form_portieri,
                                                            'form_difensori': form_difensori,
                                                            'form_centrocampisti': form_centrocampisti,
                                                            'form_attaccanti': form_attaccanti})


class InserisciRiserveView(View):
    template_name = 'front/pages/gestionecampionato/inserisci-riserve.html'

    def get(self, request, *args, **kwargs):
        # Recupero la squadra e il campionato dalla sessione
        squadra = Squadra.objects.get(pk=request.session.get('squadra_id'))
        campionato = Campionato.objects.get(
            pk=request.session.get('campionato_id'))
        # Recupero la giornata corrente per inserire la formazione Titolare
        partita = Partita.objects.filter(squadra=squadra).filter(
            giornata=campionato.giornata_corrente).first()
        formazione_giornata = Formazione.objects.filter(
            partita=partita, tipo='T', squadra=squadra).first()

        FormSetBase = formset_factory(
            RiserveForm, formset=RiserveFormSet, extra=3)
        form_portieri = FormSetBase(form_kwargs={
                                    'squadra': request.user.squadra, 'ruolo': 'P', 'titolari': formazione_giornata}, prefix='portiere')
        form_difensori = FormSetBase(form_kwargs={
                                     'squadra': request.user.squadra, 'ruolo': 'D', 'titolari': formazione_giornata}, prefix='difensori')
        form_centrocampisti = FormSetBase(form_kwargs={
                                          'squadra': request.user.squadra, 'ruolo': 'C', 'titolari': formazione_giornata}, prefix='centrocampisti')
        form_attaccanti = FormSetBase(form_kwargs={
                                      'squadra': request.user.squadra, 'ruolo': 'A', 'titolari': formazione_giornata}, prefix='attaccanti')

        return render(request, self.template_name, context={'form_portiere': form_portieri,
                                                            'form_difensori': form_difensori,
                                                            'form_centrocampisti': form_centrocampisti,
                                                            'form_attaccanti': form_attaccanti})

    def post(self, request, *args, **kwargs):
        """Metodo per la gestione del metodo POST"""

        squadra = Squadra.objects.get(pk=request.session.get('squadra_id'))
        campionato = Campionato.objects.get(
            pk=request.session.get('campionato_id'))
        # Recupero la giornata corrente per inserire la formazione Titolare
        partita = Partita.objects.filter(squadra=squadra).filter(
            giornata=campionato.giornata_corrente).first()
        formazione_giornata = Formazione.objects.filter(
            partita=partita, tipo='T', squadra=squadra).first()

        FormSetBase = formset_factory(RiserveForm, formset=RiserveFormSet)
        form_portieri = FormSetBase(request.POST, form_kwargs={
                                    'squadra': request.user.squadra, 'ruolo': 'P', 'titolari': formazione_giornata}, prefix='portiere')
        form_difensori = FormSetBase(request.POST, form_kwargs={
                                     'squadra': request.user.squadra, 'ruolo': 'D', 'titolari': formazione_giornata}, prefix='difensori')
        form_centrocampisti = FormSetBase(request.POST, form_kwargs={
                                          'squadra': request.user.squadra, 'ruolo': 'C', 'titolari': formazione_giornata}, prefix='centrocampisti')
        form_attaccanti = FormSetBase(request.POST, form_kwargs={
                                      'squadra': request.user.squadra, 'ruolo': 'A', 'titolari': formazione_giornata}, prefix='attaccanti')

        riserve_giornata = Formazione.objects.filter(
            partita=partita, tipo='R', squadra=squadra).first()

        if form_portieri.is_valid() and form_difensori.is_valid(
        ) and form_centrocampisti.is_valid() and form_attaccanti.is_valid():
            for form in form_portieri:
                form.save(formazione=riserve_giornata)
            for form in form_difensori:
                form.save(formazione=riserve_giornata)
            for form in form_centrocampisti:
                form.save(formazione=riserve_giornata)
            for form in form_attaccanti:
                form.save(formazione=riserve_giornata)

            messages.success(
                request, 'Formazione riserve inserita con successo!')
            return redirect('dashboard_index')

        return render(request, self.template_name, context={'form_portiere': form_portieri,
                                                            'form_difensori': form_difensori,
                                                            'form_centrocampisti': form_centrocampisti,
                                                            'form_attaccanti': form_attaccanti})


class VisualizzaCalendarioView(ListView):
    template_name = 'front/pages/gestionecampionato/list-calendario.html'

    def get_context_data(self, **kwargs):
        context = super(VisualizzaCalendarioView,
                        self).get_context_data(**kwargs)
        campionato_id = self.request.session.get('campionato_id')
        context['input'] = campionato_id
        return context

    def get_queryset(self):
        campionato = Campionato.objects.get(
            pk=self.request.session.get('campionato_id'))
        queryset = Partita.objects.filter(
            squadra__campionato=campionato).distinct().order_by('pk')
        return queryset


class VisualizzaPartitaView(View):
    template_name = 'front/pages/gestionecampionato/partita-corrente.html'

    def get(self, request, giornata: int, squadra_id: int, *args, **kwargs):
        campionato = Campionato.objects.get(pk=request.session.get('campionato_id'))
        partita = Partita.objects.filter(
            giornata=giornata,
            squadra__id=squadra_id).first()
        
        # Recupero i titolari e le riserve di entrambe le squadre
        try:
            titolari_prima_squadra = Formazione.objects.filter(tipo='T', partita=partita, squadra__id=partita.squadra.first().id).first().giocatore.all() \
                                     .order_by('gestionecampionato_formazione_giocatore.id')
            riserve_prima_squadra = Formazione.objects.filter(tipo='R', partita=partita, squadra__id=partita.squadra.first().id).first().giocatore.all() \
                                     .order_by('gestionecampionato_formazione_giocatore.id')

        except AttributeError:
            titolari_prima_squadra = ''
            riserve_prima_squadra = ''

        try:
            titolari_seconda_squadra = Formazione.objects.filter(tipo='T', partita=partita, squadra__id=partita.squadra.last().id).first().giocatore.all() \
                                     .order_by('gestionecampionato_formazione_giocatore.id')
            riserve_seconda_squadra = Formazione.objects.filter(tipo='R', partita=partita, squadra__id=partita.squadra.last().id).first().giocatore.all() \
                                     .order_by('gestionecampionato_formazione_giocatore.id')

        except AttributeError:
            titolari_seconda_squadra = ''
            riserve_seconda_squadra = ''

        return render(request, self.template_name, context={'partita': partita,
                                                            'titolari_prima_squadra': titolari_prima_squadra,
                                                            'titolari_seconda_squadra': titolari_seconda_squadra,
                                                            'riserve_prima_squadra': riserve_prima_squadra,
                                                            'riserve_seconda_squadra': riserve_seconda_squadra})
