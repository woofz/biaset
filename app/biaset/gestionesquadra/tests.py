from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.urls import reverse
from model_bakery import baker

from gestionesquadra.forms import InserisciSquadraForm, AssociaGiocatoreForm
from gestionesquadra.models import Squadra
from gestionecampionato.exceptions import CalendarioPresenteException
from gestionecampionato.forms import CreaCampionatoForm, SelezionaModuloForm
from gestionecampionato.models import Campionato, Partita


class GestioneSquadraTestCases(TestCase):

    def setUp(self):
        # Creo il modello utente per i test
        self.user = baker.make(User)
        # Creo i profili
        self.profilo_allenatore = baker.make('gestioneutenza.Profilo', nome='Allenatore')
        self.profilo_ca = baker.make('gestioneutenza.Profilo', nome='Championship Admin')
        self.profilo_la = baker.make('gestioneutenza.Profilo', nome='League Admin')

        self.url_creazione_campionato = reverse('gestionecampionato:inserisci_campionato')
        # Creo il campionato, la squadra dell'utente e i giocatori della squadra.
        self.campionato = baker.make('gestionecampionato.Campionato', championship_admin=self.user)
        self.squadra = baker.make('gestionesquadra.Squadra', allenatore=self.user, campionato=self.campionato)
        self.set_giocatori = baker.make('gestionesquadra.Giocatore', _quantity=25)
        for giocatore in self.set_giocatori:
            giocatore.squadra.add(self.squadra)
        # Creo un set di squadre e l'associo al campionato di Test
        self.set_squadre = baker.make('gestionesquadra.Squadra', _quantity=5, campionato=self.campionato, make_m2m=True)
        self.kw = {'profile': self.profilo_la.nome, 'user': self.user}

        self.data = {
            'nome_campionato': self.campionato.nome_campionato,
            'championship_admin': self.campionato.championship_admin,
            'giornata_corrente': self.campionato.giornata_corrente,
            'partecipanti': self.campionato.partecipanti
        }
        self.login = self.client.force_login(self.user)
        self.partita = baker.make('gestionecampionato.Partita')
        self.partita.squadra.add(self.squadra)
        self.formazione_titolare = baker.make('gestionecampionato.Formazione', tipo='T', partita=self.partita,
                                              squadra=self.squadra)

    def test_inserisci_squadra_tc_1_3_1(self):
        self.profilo_ca.user.add(self.user)
        nomeSquadra = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        form = InserisciSquadraForm(data={'nome': nomeSquadra,
                                          'allenatore': self.user,
                                          'campionato': self.campionato}, **self.kw)
        self.profilo_la.user.remove(self.user)
        self.assertFalse(form.is_valid())

    def test_inserisci_squadra_tc_1_3_2(self):
        self.profilo_ca.user.add(self.user)
        nomeSquadra = 'Squadra!!'
        form = InserisciSquadraForm(data={'nome': nomeSquadra,
                                          'allenatore': self.user,
                                          'campionato': self.campionato}, **self.kw)
        self.profilo_la.user.remove(self.user)
        self.assertFalse(form.is_valid())

    def test_inserisci_squadra_tc_1_3_3(self):
        self.profilo_ca.user.add(self.user)
        Squadra.objects.all().delete()
        nomeSquadra = 'Squadra'
        ca_kw = {'profile': self.profilo_ca.nome, 'user': self.user}
        form = InserisciSquadraForm(data={'nome': nomeSquadra,
                                          'allenatore': self.user,
                                          'campionato': self.campionato}, **ca_kw)
        self.profilo_ca.user.remove(self.user)
        self.assertTrue(form.is_valid())
        self.assertIsInstance(form.save(), Squadra)

    def test_inserisci_squadra_no_ca(self):
        self.profilo_la.user.add(self.user)
        Squadra.objects.all().delete()
        nomeSquadra = 'Squadra'
        form = InserisciSquadraForm(data={'nome': nomeSquadra,
                                          'allenatore': self.user,
                                          'campionato': self.campionato}, **self.kw)
        self.assertTrue(form.is_valid())

    def test_modifica_squadra_tc_1_4_1(self):
        nomeSquadra = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        lorenzo = baker.make(User)
        self.profilo_allenatore.user.add(lorenzo)
        form = InserisciSquadraForm(data={'nome': nomeSquadra,
                                          'allenatore': lorenzo,
                                          'campionato': self.campionato}, **self.kw)
        self.assertFalse(form.is_valid())

    def test_modifica_squadra_tc_1_4_2(self):
        nomeSquadra = 'Squadra'
        camilla = baker.make(User, first_name='Camilla')
        self.profilo_allenatore.user.add(camilla)
        squadraCamilla = baker.make(Squadra, campionato=self.campionato, allenatore=camilla)
        form = InserisciSquadraForm(data={'nome': nomeSquadra,
                                          'allenatore': camilla,
                                          'campionato': self.campionato}, **self.kw)
        self.assertFalse(form.is_valid())

    def test_modifica_squadra_tc_1_4_3(self):
        nomeSquadra = 'Squadra'
        lorenzo = baker.make(User)
        self.profilo_allenatore.user.add(lorenzo)
        form = InserisciSquadraForm(data={'nome': nomeSquadra,
                                          'allenatore': lorenzo,
                                          'campionato': self.campionato}, **self.kw)
        self.assertTrue(form.is_valid())
        self.assertIsInstance(form.save(), Squadra)

    def test_associa_giocatore_fail_no_squadre(self):
        self.profilo_ca.user.add(self.user)
        self.client.get(reverse('dashboard_index'))
        Squadra.objects.all().delete()
        response = self.client.get(reverse('gestionesquadra:associa_giocatore'))
        self.assertEquals(response.status_code, 302)

    def test_associa_giocatore_get(self):
        self.profilo_ca.user.add(self.user)
        self.client.get(reverse('dashboard_index'))
        response = self.client.get(reverse('gestionesquadra:associa_giocatore'))
        self.assertEquals(response.status_code, 200)

    def test_associa_giocatore_success(self):
        self.profilo_ca.user.add(self.user)
        self.client.get(reverse('dashboard_index'))
        giocatore = baker.make('gestionesquadra.Giocatore')
        form_kw = {'campionato': self.campionato}
        data = {'giocatore': giocatore, 'squadra': self.squadra}
        form = AssociaGiocatoreForm(data=data, **form_kw)
        response = self.client.post(reverse('gestionesquadra:associa_giocatore'), data={'giocatore': giocatore.id,
                                                                                        'squadra': self.squadra.id})
        self.assertEquals(response.status_code, 302)

    def test_associa_giocatore_form_fail(self):
        self.profilo_ca.user.add(self.user)
        self.client.get(reverse('dashboard_index'))
        giocatore = baker.make('gestionesquadra.Giocatore')
        form_kw = {'campionato': self.campionato}
        data = {'giocatore': giocatore, 'squadra': self.squadra}
        form = AssociaGiocatoreForm(data=data, **form_kw)
        response = self.client.post(reverse('gestionesquadra:associa_giocatore'), data={'giocatore': giocatore,
                                                                                        'squadra': self.squadra.id})
        self.assertEquals(response.status_code, 200)

    def test_visualizza_squadra_ownership(self):
        self.profilo_ca.user.add(self.user)
        self.client.get(reverse('dashboard_index'))
        url = reverse('gestionesquadra:visualizza_squadra', kwargs={'pk': self.squadra.id})
        response = self.client.get(url)
        self.assertTrue(response.context['ownership'])

    def test_visualizza_squadra_no_ownership(self):
        self.profilo_allenatore.user.add(self.user)
        self.client.get(reverse('dashboard_index'))
        allenatore2 = baker.make(User)
        squadra2 = baker.make(Squadra, campionato=self.campionato, allenatore=allenatore2)
        url = reverse('gestionesquadra:visualizza_squadra', kwargs={'pk': squadra2.id})
        response = self.client.get(url)
        self.assertFalse(response.context['ownership'])

    def test_visualizza_squadra_no_ownership_different_championship(self):
        self.profilo_allenatore.user.add(self.user)
        self.client.get(reverse('dashboard_index'))
        allenatore2 = baker.make(User)
        squadra2 = baker.make(Squadra, campionato=self.campionato, allenatore=allenatore2)
        url = reverse('gestionesquadra:visualizza_squadra', kwargs={'pk': squadra2.id})
        response = self.client.get(url)
        self.assertFalse(response.context['ownership'])