from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse
from model_bakery import baker

from core.decorators import check_championship_existence
from gestionesquadra.models import Squadra, Giocatore
from .caricamentovoti.ImportVoti import ImportVoti
from .exceptions import CalendarioPresenteException, CampionatoGiaAssociatoException
from .forms import CreaCampionatoForm, SelezionaModuloForm
from .models import Campionato, Partita, Voto, Formazione


class GestioneCampionatoTestCases(TestCase):

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
        self.set_portieri = baker.make('gestionesquadra.Giocatore', _quantity=3, ruolo='P')
        self.set_difensori = baker.make('gestionesquadra.Giocatore', _quantity=7, ruolo='D')
        self.set_centrocampisti = baker.make('gestionesquadra.Giocatore', _quantity=7, ruolo='C')
        self.set_attaccanti = baker.make('gestionesquadra.Giocatore', _quantity=7, ruolo='A')

        for giocatore in self.set_difensori:
            giocatore.squadra.add(self.squadra)

        for giocatore in self.set_centrocampisti:
            giocatore.squadra.add(self.squadra)

        for giocatore in self.set_attaccanti:
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
        self.client.force_login(self.user)

    def test_crezione_campionato_success(self):
        '''Test success di creazione campionato'''
        login = self.client.force_login(self.user)
        response = self.client.post(self.url_creazione_campionato, data=self.data)
        latest_obj = Campionato.objects.last()
        self.assertTrue(self.campionato.id, None)
        self.assertEquals(latest_obj.nome_campionato, self.campionato.nome_campionato)

    def test_creazione_campionato_fail(self):
        '''Test fail campionato gi?? esistente'''
        login = self.client.force_login(self.user)
        self.campionato.save()
        campionato_form = CreaCampionatoForm(data=self.data)
        self.assertFalse(campionato_form.is_valid())

    def test_decorator_championship_existence(self):
        request = self.client.get('gestionecampionato:inserisci_campionato')
        request.user = self.user
        self.assertRaises(CampionatoGiaAssociatoException)

    def test_seleziona_modulo_fail(self):
        form = SelezionaModuloForm(data={'difensori': 5, 'centrocampisti': 5, 'attaccanti': 3})
        response = self.client.post(reverse('gestionecampionato:seleziona_modulo'),
                                    data={'difensori': 5, 'centrocampisti': 5, 'attaccanti': 3})
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors)

    def test_seleziona_modulo_success(self):
        form = SelezionaModuloForm(data={'difensori': 4, 'centrocampisti': 4, 'attaccanti': 2})
        response = self.client.post(reverse('gestionecampionato:seleziona_modulo'),
                                    data={'difensori': 4, 'centrocampisti': 4, 'attaccanti': 2})
        self.assertTrue(form.is_valid())
        self.assertFalse(form.errors)
        self.assertTrue(response.status_code, 302)

    def test_inserimento_formazione_fail_modulo(self):
        fail_url = reverse('gestionecampionato:inserisci_titolari', kwargs={'d': '5', 'c': '4', 'a': '3'})
        response = self.client.get(fail_url)
        self.assertTrue(response.status_code, 302)

    def test_inserimento_formazione_success_modulo(self):
        self.profilo_allenatore.user.add(self.user)
        fail_url = reverse('gestionecampionato:inserisci_titolari', kwargs={'d': '4', 'c': '4', 'a': '2'})
        self.client.get(reverse('dashboard_index'))
        response = self.client.get(fail_url)
        self.assertTrue(response.status_code, 200)

    def test_inserimento_formazione_fail_no_formazione(self):
        self.profilo_allenatore.user.add(self.user)
        Formazione.objects.all().delete()
        fail_url = reverse('gestionecampionato:inserisci_titolari', kwargs={'d': '4', 'c': '4', 'a': '2'})
        self.client.get(reverse('dashboard_index'))
        response = self.client.get(fail_url)
        self.assertTrue(response.status_code, 302)

    def test_inserimento_formazione_post_fail(self):
        self.profilo_allenatore.user.add(self.user)
        fail_url = reverse('gestionecampionato:inserisci_titolari', kwargs={'d': '4', 'c': '4', 'a': '2'})
        self.client.get(reverse('dashboard_index'))
        response = self.client.post(fail_url)
        self.assertTrue(response.status_code, 200)

    def test_inserimento_riserve_post_fail(self):
        self.profilo_allenatore.user.add(self.user)
        Formazione.objects.all().delete()
        fail_url = reverse('gestionecampionato:inserisci_riserve')
        self.client.get(reverse('dashboard_index'))
        response = self.client.post(fail_url)
        self.assertTrue(response.status_code, 200)

    def test_genera_calendario_get(self):
        Partita.objects.all().delete()
        self.profilo_ca.user.add(self.user)
        self.client.get(reverse('dashboard_index'))
        url = reverse('gestionecampionato:genera_calendario')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_genera_calendario_esistente_fail(self):
        self.profilo_ca.user.add(self.user)
        self.client.get(reverse('dashboard_index'))
        url = reverse('gestionecampionato:genera_calendario')
        response = self.client.get(url)
        self.assertRaises(CalendarioPresenteException)

    def test_genera_calendario_no_minimo_squadre_fail(self):
        self.profilo_ca.user.add(self.user)
        self.client.get(reverse('dashboard_index'))
        url = reverse('gestionecampionato:genera_calendario')
        Squadra.objects.all().delete()
        response = self.client.get(url)
        self.assertRaises(CalendarioPresenteException)

    def test_genera_calendario_6_squadre(self):
        Partita.objects.all().delete()
        self.profilo_ca.user.add(self.user)
        self.client.get(reverse('dashboard_index'))
        from gestionesquadra.models import Squadra
        url = reverse('gestionecampionato:genera_calendario')
        response = self.client.post(url)
        self.assertEquals(response.status_code, 302)

    def test_genera_calendario_8_squadre(self):
        Partita.objects.all().delete()
        self.profilo_ca.user.add(self.user)
        squadre = baker.make('gestionesquadra.Squadra', _quantity=2, campionato=self.campionato, make_m2m=True)

        self.client.get(reverse('dashboard_index'))
        url = reverse('gestionecampionato:genera_calendario')
        response = self.client.post(url)
        self.assertEquals(response.status_code, 302)

    def test_genera_calendario_10_squadre(self):
        Partita.objects.all().delete()
        self.profilo_ca.user.add(self.user)
        squadre = baker.make('gestionesquadra.Squadra', _quantity=4, campionato=self.campionato, make_m2m=True)
        self.client.get(reverse('dashboard_index'))
        url = reverse('gestionecampionato:genera_calendario')
        response = self.client.post(url)
        self.assertEquals(response.status_code, 302)

    def test_modifica_campionato_fail_permessi(self):
        baker_user = baker.make(User)
        self.profilo_ca.user.add(self.user)
        campionato_baker = baker.make('gestionecampionato.Campionato', championship_admin=baker_user)
        url = reverse('gestionecampionato:modifica_campionato', kwargs={'pk': campionato_baker.id})
        self.client.get(reverse('dashboard_index'))
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)

    def test_modifica_campionato_success_permessi(self):
        self.profilo_ca.user.add(self.user)
        url = reverse('gestionecampionato:modifica_campionato', kwargs={'pk': self.campionato.id})
        self.client.get(reverse('dashboard_index'))
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_inserimento_riserve_get(self):
        self.profilo_allenatore.user.add(self.user)
        self.partita = baker.make('gestionecampionato.Partita')
        self.partita.squadra.add(self.squadra)
        self.client.get(reverse('dashboard_index'))
        response = self.client.get(reverse('gestionecampionato:inserisci_riserve'))
        self.assertEquals(response.status_code, 200)

    def test_form_crea_campionato_tc_1_2_1(self):
        Campionato.objects.all().delete()
        nomeCampionato = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        partecipanti = 10
        form = CreaCampionatoForm(data={'championship_admin': self.user,
                                        'nome_campionato': nomeCampionato,
                                        'partecipanti': partecipanti})
        self.assertEquals(form.is_valid(), False)

    def test_form_crea_campionato_tc_1_2_2(self):
        Campionato.objects.all().delete()
        nomeCampionato = 'Campionato!!'
        partecipanti = 10
        form = CreaCampionatoForm(data={'championship_admin': self.user,
                                        'nome_campionato': nomeCampionato,
                                        'partecipanti': partecipanti})
        self.assertEquals(form.is_valid(), False)
        self.assertIn('nome_campionato', form.errors.keys())

    def test_form_crea_campionato_tc_1_2_3(self):
        Campionato.objects.all().delete()
        nomeCampionato = 'Campionato'
        partecipanti = 3
        form = CreaCampionatoForm(data={'championship_admin': self.user,
                                        'nome_campionato': nomeCampionato,
                                        'partecipanti': partecipanti})
        self.assertEquals(form.is_valid(), False)
        self.assertIn('partecipanti', form.errors.keys())

    def test_form_crea_campionato_tc_1_2_4(self):
        Campionato.objects.all().delete()
        nomeCampionato = 'Campionato'
        partecipanti = 15
        form = CreaCampionatoForm(data={'championship_admin': self.user,
                                        'nome_campionato': nomeCampionato,
                                        'partecipanti': partecipanti})
        self.assertEquals(form.is_valid(), False)
        self.assertIn('partecipanti', form.errors.keys())

    def test_form_crea_campionato_tc_1_2_5(self):
        Campionato.objects.all().delete()
        nomeCampionato = 'Campionato'
        partecipanti = 9
        form = CreaCampionatoForm(data={'championship_admin': self.user,
                                        'nome_campionato': nomeCampionato,
                                        'partecipanti': partecipanti})
        self.assertEquals(form.is_valid(), False)
        self.assertIn('partecipanti', form.errors.keys())

    def test_form_crea_campionato_tc_1_2_6(self):
        Campionato.objects.all().delete()
        nomeCampionato = 'Campionato'
        partecipanti = 10
        form = CreaCampionatoForm(data={'championship_admin': self.user,
                                        'nome_campionato': nomeCampionato,
                                        'partecipanti': partecipanti})
        self.assertEquals(form.is_valid(), True)
        self.assertIsInstance(form.save(), Campionato)

    def test_import_voti(self):
        importVoti = ImportVoti(giornata=1)
        importVoti.vote_download()
        self.assertGreater(Voto.objects.all().count(), 0)

    def test_inserimento_titolari(self):
        print(Giocatore.objects.filter(squadra=self.squadra).first().ruolo)
