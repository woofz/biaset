from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import formset_factory
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import CreateView, UpdateView, ListView

from core.decorators import check_user_permission_ca, check_ca_belonging, check_championship_existence, \
    handle_view_exception
from gestionecampionato.commandpattern.generacalendariocommand import GeneraCalendarioCommand
from gestionecampionato.commandpattern.invoker import Invoker
from gestionecampionato.commandpattern.receiver import Receiver
from gestionecampionato.forms import CreaCampionatoForm, ModificaCampionatoForm, SelezionaModuloForm, TitolariForm, \
    TitolariFormSet, RiserveFormSet, RiserveForm
from gestionesquadra.models import Squadra
from .caricamentovoti.ImportVoti import ImportVoti
from .facadepattern.facade import Facade, InserimentoFormazione
from .models import Campionato, Partita, Formazione, Voto
from .exceptions import NumeroPartecipantiNonRaggiuntoException, VotiPresentiException, CalendarioPresenteException

decorators = [check_user_permission_ca, handle_view_exception]


def get_or_none(classmodel, **kwargs):
    """Funzione per fetchare un valore eventualmente nullo dal database"""
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.MultipleObjectsReturned as e:
        print('ERR====>', e)

    except classmodel.DoesNotExist:
        return None

@method_decorator(decorators, name='dispatch')
@method_decorator(check_championship_existence, name='dispatch')
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
    success_url = reverse_lazy('dashboard_index')


@method_decorator(decorators, name='dispatch')
@method_decorator(handle_view_exception, name='dispatch')
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
        if championship_teams.count() < campionato.partecipanti:
            raise NumeroPartecipantiNonRaggiuntoException(
                f"Il tuo campionato non ha raggiunto il numero di partecipanti. {championship_teams.count()}/{campionato.partecipanti}")
        if Partita.objects.filter(squadra__campionato=campionato).count() > 0:
            print(Partita.objects.filter(squadra__campionato=campionato).count())
            raise CalendarioPresenteException('Il calendario per questo campionato è già stato generato!')
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
        if not Formazione.objects.filter(squadra_id=request.session['squadra_id']).exists():
            messages.error(request, 'Non è presente alcuna partita per il tuo campionato!')
            return redirect('dashboard_index')

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

        subsystemInserimentoFormazione = InserimentoFormazione(request=request,
                                                               formset=TitolariFormSet,
                                                               formType=TitolariForm,
                                                               tipoFormazione='T')

        facade = Facade(subsystem=subsystemInserimentoFormazione)
        if facade.operation():
            messages.success(request, 'Formazione titolare inserita correttamente!')
            return redirect('gestionecampionato:inserisci_riserve')
        else:
            return render(request, self.template_name,
                          context={'form_portiere': subsystemInserimentoFormazione.form_portieri,
                                   'form_difensori': subsystemInserimentoFormazione.form_difensori,
                                   'form_centrocampisti': subsystemInserimentoFormazione.form_centrocampisti,
                                   'form_attaccanti': subsystemInserimentoFormazione.form_attaccanti})


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
        subsystemInserimentoRiserve = InserimentoFormazione(request=request,
                                                            formset=RiserveFormSet,
                                                            formType=RiserveForm,
                                                            tipoFormazione='R')

        facade = Facade(subsystem=subsystemInserimentoRiserve)
        if facade.operation():
            messages.success(request, 'Formazione titolare riserve correttamente!')
            return redirect('dashboard_index')
        else:
            return render(request, self.template_name,
                          context={'form_portiere': subsystemInserimentoRiserve.form_portieri,
                                   'form_difensori': subsystemInserimentoRiserve.form_difensori,
                                   'form_centrocampisti': subsystemInserimentoRiserve.form_centrocampisti,
                                   'form_attaccanti': subsystemInserimentoRiserve.form_attaccanti})


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

        partita = Partita.objects.filter(
            giornata=giornata,
            squadra__id=squadra_id).first()

        # Recupero i titolari e le riserve di entrambe le squadre
        try:
            titolari_prima_squadra = Formazione.objects.filter(tipo='T', partita=partita,
                                                               squadra__id=partita.squadra.first().id).first().giocatore.all() \
                .order_by('gestionecampionato_formazione_giocatore.id')
            riserve_prima_squadra = Formazione.objects.filter(tipo='R', partita=partita,
                                                              squadra__id=partita.squadra.first().id).first().giocatore.all() \
                .order_by('gestionecampionato_formazione_giocatore.id')

        except AttributeError:
            titolari_prima_squadra = ''
            riserve_prima_squadra = ''

        try:
            titolari_seconda_squadra = Formazione.objects.filter(tipo='T', partita=partita,
                                                                 squadra__id=partita.squadra.last().id).first().giocatore.all() \
                .order_by('gestionecampionato_formazione_giocatore.id')
            riserve_seconda_squadra = Formazione.objects.filter(tipo='R', partita=partita,
                                                                squadra__id=partita.squadra.last().id).first().giocatore.all() \
                .order_by('gestionecampionato_formazione_giocatore.id')

        except AttributeError:
            titolari_seconda_squadra = ''
            riserve_seconda_squadra = ''

        sq1 = self.populateGiocatoriFromQs(qs=titolari_prima_squadra, giornata=giornata)
        sq1_ris = self.populateGiocatoriFromQs(qs=riserve_prima_squadra, giornata=giornata)

        sq2 = self.populateGiocatoriFromQs(qs=titolari_seconda_squadra, giornata=giornata)
        sq2_ris = self.populateGiocatoriFromQs(qs=riserve_seconda_squadra, giornata=giornata)

        squadra1 = sq1['giocatori_voto']
        squadra1_riserve = sq1_ris['giocatori_voto']
        squadra2 = sq2['giocatori_voto']
        squadra2_riserve = sq2_ris['giocatori_voto']

        gol_squadra1 = 0
        gol_squadra2 = 0

        return render(request, self.template_name, context={'partita': partita,
                                                            'titolari_prima_squadra': squadra1,
                                                            'titolari_seconda_squadra': squadra2,
                                                            'riserve_prima_squadra': squadra1_riserve,
                                                            'riserve_seconda_squadra': squadra2_riserve,
                                                            'gol_squadra1': gol_squadra1,
                                                            'gol_squadra2': gol_squadra2})


    @staticmethod
    def populateGiocatoriFromQs(qs, giornata: int):
        """Metodo che popola il dizionario relativo ai giocatori di una giornata, partendo da un QuerySet."""
        dc = dict()
        for giocatore in qs:
            voto = get_or_none(Voto, giornata=giornata, id_voti=giocatore.id_voti)
            dc.update({
                giocatore.id: {
                    'nome': giocatore.nome_completo,
                    'voto': voto,
                    'ruolo': giocatore.ruolo,
                }
            })
        return {'giocatori_voto': dc}


@method_decorator(decorators, name='dispatch')
class CaricamentoVotiView(View):
    template_name = 'front/pages/gestionecampionato/caricamento-voti.html'

    def get(self, request, *args, **kwargs):
        giornata_corrente = request.session['giornata_corrente']
        if Voto.objects.filter(giornata=giornata_corrente).exists():
            raise VotiPresentiException('I voti per questa giornata sono già presenti')
        worker = ImportVoti(giornata=giornata_corrente)
        worker.vote_download()
        messages.success(request, 'Voti caricati con successo!')
        return redirect('dashboard_index')
