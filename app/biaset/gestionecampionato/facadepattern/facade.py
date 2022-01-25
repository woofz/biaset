from __future__ import annotations

from django.contrib import messages
from django.forms import formset_factory, BaseFormSet, Form
from django.shortcuts import redirect, render

from gestionecampionato.models import Partita, Formazione
from gestionesquadra.models import Squadra


class Facade:
    """
    The Facade class provides a simple interface to the complex logic of one or
    several subsystems. The Facade delegates the client requests to the
    appropriate objects within the subsystem. The Facade is also responsible for
    managing their lifecycle. All of this shields the client from the undesired
    complexity of the subsystem.
    """

    def __init__(self, subsystem: InserimentoFormazione) -> None:
        """
        Depending on your application's needs, you can provide the Facade with
        existing subsystem objects or force the Facade to create them on its
        own.
        """

        self._subsystem1 = subsystem

    def operation(self) -> bool:
        """
        The Facade's methods are convenient shortcuts to the sophisticated
        functionality of the subsystems. However, clients get only to a fraction
        of a subsystem's capabilities.
        """
        return self._subsystem1.insert()


class InserimentoFormazione:
    """
    The Subsystem can accept requests either from the facade or client directly.
    In any case, to the Subsystem, the Facade is yet another client, and it's
    not a part of the Subsystem.
    """

    def __init__(self, request, formset: BaseFormSet, formType: Form, tipoFormazione: str):
        self.request = request
        self._formset = formset
        self._form = formType
        self._tipoFormazione = tipoFormazione
        self._form_portieri = None
        self._form_difensori = None
        self._form_centrocampisti = None
        self._form_attaccanti = None

    def insert(self) -> bool:
        # Recupero la squadra e il campionato dalla sessione
        squadra = Squadra.objects.get(pk=self.request.session.get('squadra_id'))
        campionato = squadra.campionato
        # Recupero la giornata corrente per inserire la formazione Titolare
        partita = Partita.objects.filter(squadra=squadra).filter(
            giornata=campionato.giornata_corrente).first()

        FormSetBase = formset_factory(self._form, formset=self._formset)
        
        portieriFormKwargs = {'squadra': self.request.user.squadra, 'ruolo': 'P'}
        difensoriFormKwargs = {'squadra': self.request.user.squadra, 'ruolo': 'D'}
        centrocampistiFormKwargs = {'squadra': self.request.user.squadra, 'ruolo': 'C'}
        attaccantiFormKwargs = {'squadra': self.request.user.squadra, 'ruolo': 'A'}
        
        if self._tipoFormazione == 'R':
            titolari = Formazione.objects.filter(
                partita=partita, tipo='T', squadra=squadra).first()
            portieriFormKwargs.update({'titolari': titolari})
            difensoriFormKwargs.update({'titolari': titolari})
            centrocampistiFormKwargs.update({'titolari': titolari})
            attaccantiFormKwargs.update({'titolari': titolari})

        self._form_portieri = FormSetBase(self.request.POST, form_kwargs=portieriFormKwargs, prefix='portiere')
        self._form_difensori = FormSetBase(self.request.POST, form_kwargs=difensoriFormKwargs, prefix='difensori')
        self._form_centrocampisti = FormSetBase(self.request.POST, form_kwargs=centrocampistiFormKwargs, prefix='centrocampisti')
        self._form_attaccanti = FormSetBase(self.request.POST, form_kwargs=attaccantiFormKwargs, prefix='attaccanti')

        formazione_giornata = Formazione.objects.filter(
            partita=partita, squadra=squadra).filter(tipo=self._tipoFormazione).first()

        if formazione_giornata.giocatore.exists():
            formazione_giornata.giocatore.clear()

        if self._form_portieri.is_valid() and self._form_difensori.is_valid(
        ) and self._form_centrocampisti.is_valid() and self._form_attaccanti.is_valid():
            for form in self._form_portieri:
                form.save(formazione=formazione_giornata)
            for form in self._form_difensori:
                form.save(formazione=formazione_giornata)
            for form in self._form_centrocampisti:
                form.save(formazione=formazione_giornata)
            for form in self._form_attaccanti:
                form.save(formazione=formazione_giornata)
            return True
        else:
            return False

    @property
    def form_attaccanti(self):
        return self._form_attaccanti

    @property
    def form_centrocampisti(self):
        return self._form_centrocampisti

    @property
    def form_difensori(self):
        return self._form_difensori

    @property
    def form_portieri(self):
        return self._form_portieri
