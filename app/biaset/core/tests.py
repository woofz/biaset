from django.contrib.auth.models import User
from django.http import HttpResponse
from django.urls import reverse
from model_bakery import baker
from unittest.mock import patch
from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase

from core.decorators import check_championship_existence
from gestionecampionato.models import Campionato
from gestionesquadra.models import Squadra


class CoreTestCase(TestCase):

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

    def test_dashboard_home_view_no_profilo(self):
        url = reverse('dashboard_index')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)

    def test_dashboard_home_view_no_campionato(self):
        Campionato.objects.filter(pk=self.campionato.id).first().delete()
        self.profilo_ca.user.add(self.user)
        url = reverse('dashboard_index')
        response = self.client.get(url)
        self.assertRedirects(response, expected_url=reverse('gestionecampionato:inserisci_campionato'))

    def test_dashboard_home_view_la(self):
        self.profilo_la.user.add(self.user)
        url = reverse('dashboard_index')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_dashboard_home_view_no_squadra(self):
        self.profilo_ca.user.add(self.user)
        Squadra.objects.filter(allenatore=self.user).first().delete()
        url = reverse('dashboard_index')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_dashboard_home_view_set_variables(self):
        url = reverse('dashboard_index')
        self.profilo_ca.user.add(self.user)
        first_response = self.client.get(url)
        second_response = self.client.get(url)
        self.assertEquals(second_response.status_code, 200)


class CommandTests(TestCase):
    """ we create a command wait_for_db to check if database is
    available before running server. Here we test if this command"""

    # check if the command works when db is available
    def test_wait_for_db_ready(self):
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.return_value = True
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 1)

    # check if command works when db is not connected
    # by default, we ll have sleep function to wait for 1s if database is not available
    # we dont want this sleep to wait for this test
    @patch('time.sleep', return_value=True)
    def test_wait_for_db(self, ts):
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            # make the patch return error for first five calls
            # and return true on sixth call
            gi.side_effect = [OperationalError]*5 + [True]
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 6)