from django.contrib.auth.models import User
from django.urls import reverse
from model_bakery import baker
from unittest.mock import patch
from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase
import logging
from gestionecampionato.models import Campionato
from gestionesquadra.models import Squadra
from gestioneutenza.forms import CreaInvitoForm
from gestioneutenza.models import Invito, Profilo
from gestioneutenza.strategyclasses.invitenotfound import InviteNotFoundException


class GestioneUtenzaTestCases(TestCase):

    def setUp(self):
        pass
        # Creo il modello utente per i test
        self.user = baker.make(User, email='test@user.com')
        # Creo i profili
        self.profilo_allenatore = baker.make('gestioneutenza.Profilo', nome='Allenatore')
        self.profilo_ca = baker.make('gestioneutenza.Profilo', nome='Championship Admin')
        self.profilo_la = baker.make('gestioneutenza.Profilo', nome='League Admin')
        # Creo il campionato, la squadra dell'utente e i giocatori della squadra.
        self.campionato = baker.make('gestionecampionato.Campionato', championship_admin=self.user, partecipanti=8)
        self.login = self.client.force_login(self.user)


    def test_form_crea_invito_tc_1_1_1(self):
        destinatario_fail = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        expire_dt = '2022-04-22'
        form = CreaInvitoForm(data={'user': self.user,
                                    'destinatario': destinatario_fail,
                                    'expire_dt': expire_dt})
        self.assertEquals(form.is_valid(), False)

    def test_form_crea_invito_tc_1_1_2(self):
        destinatario_fail = 'ciao@gmail'
        expire_dt = '2022-04-22'
        form = CreaInvitoForm(data={'user': self.user,
                                    'destinatario': destinatario_fail,
                                    'expire_dt': expire_dt})
        self.assertEquals(form.is_valid(), False)

    def test_form_crea_invito_tc_1_1_3(self):
        destinatario = 'ciao@gmail.it'
        expire_dt = '2021-04-22'
        form = CreaInvitoForm(data={'user': self.user,
                                    'destinatario': destinatario,
                                    'expire_dt': expire_dt})
        self.assertEquals(form.is_valid(), False)

    # def test_form_crea_invito_tc_1_1_4(self):
    #     destinatario = 'ciao@gmail.it'
    #     expire_dt = '22-04-2022'
    #     form = CreaInvitoForm(data={'user': self.user,
    #                                 'destinatario': destinatario,
    #                                 'expire_dt': expire_dt})
    #     self.assertRaises(TypeError, form.is_valid())

    def test_form_crea_invito_tc_1_1_5(self):
        destinatario = 'ciao@gmail.it'
        expire_dt = '2022-04-22'
        form = CreaInvitoForm(data={'user': self.user,
                                    'destinatario': destinatario,
                                    'expire_dt': expire_dt})
        self.assertEquals(form.is_valid(), True)
        self.assertIsInstance(form.save(), Invito)

    def test_strategyregistration_view_no_invito_allenatore(self):
        #self.client.get(reverse('dashboard_index'))
        Invito.objects.all().delete()
        url = reverse('gestioneutenza:registrazione_ca', kwargs={'regtype': 'allenatore'})
        response = self.client.get(url)
        self.assertContains(response, 'Invito non valido')

    def test_strategyregistration_view_ca_success(self):
        self.client.get(reverse('dashboard_index'))
        url = reverse('gestioneutenza:registrazione_ca', kwargs={'regtype': 'ca'})
        response = self.client.get(url)
        response = self.client.get(url)
        self.assertTrue(Profilo.objects.filter(nome='Championship Admin').first().user.filter(pk=self.user.id).exists())

    def test_strategyregistration_view_allenatore_fail_invito_scaduto(self):
        self.client.get(reverse('dashboard_index'))
        import datetime
        date_time_str = '2019-01-27 08:15:27.243860'
        date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')
        invito = baker.make('gestioneutenza.Invito', destinatario=self.user.email, campionato=self.campionato,
                            expire_dt=date_time_obj.date())
        url = reverse('gestioneutenza:registrazione_ca', kwargs={'regtype': 'allenatore'})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)


    def test_strategyregistration_view_allenatore_fail_campionato_pieno(self):
        self.client.get(reverse('dashboard_index'))
        set_squadre = baker.make('gestionesquadra.Squadra', _quantity=8, campionato=self.campionato)
        import datetime
        date_time_str = '2029-06-29 08:15:27.243860'
        date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')
        invito = baker.make('gestioneutenza.Invito', destinatario=self.user.email, campionato=self.campionato,
                            expire_dt=date_time_obj.date())
        url = reverse('gestioneutenza:registrazione_ca', kwargs={'regtype': 'allenatore'})
        response = self.client.get(url)
        self.assertRaises(InviteNotFoundException)

    def test_strategyregistration_view_allenatore_success(self):
        self.client.get(reverse('dashboard_index'))
        Squadra.objects.all().delete()
        import datetime
        date_time_str = '2029-06-29 08:15:27.243860'
        date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')
        invito = baker.make('gestioneutenza.Invito', destinatario=self.user.email, campionato=self.campionato,
                            expire_dt=date_time_obj.date())
        url = reverse('gestioneutenza:registrazione_ca', kwargs={'regtype': 'allenatore'})
        response = self.client.get(url)
        self.assertTrue(Profilo.objects.filter(nome='Allenatore').first().user.filter(pk=self.user.id).exists())
        self.assertTrue(Squadra.objects.filter(allenatore=self.user).exists())
