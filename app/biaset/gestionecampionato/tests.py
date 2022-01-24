from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from model_bakery import baker

from gestionesquadra.models import Squadra
from .forms import CreaCampionatoForm, SelezionaModuloForm
from .models import Campionato


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


    def test_crezione_campionato_success(self):
        '''Test success di creazione campionato'''
        login = self.client.force_login(self.user)
        response = self.client.post(self.url_creazione_campionato, data=self.data)
        latest_obj = Campionato.objects.last()
        self.assertTrue(self.campionato.id, None)
        self.assertEquals(latest_obj.nome_campionato, self.campionato.nome_campionato)

    def test_creazione_campionato_fail(self):
        '''Test fail campionato già esistente'''
        login = self.client.force_login(self.user)
        self.campionato.save()
        campionato_form = CreaCampionatoForm(data=self.data)
        self.assertFalse(campionato_form.is_valid())

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
        fail_url = reverse('gestionecampionato:inserisci_titolari', kwargs={'d': '4', 'c': '4', 'a': '2'})
        response = self.client.get(fail_url)
        self.assertTrue(response.status_code, 200)

    def test_genera_calendario_get(self):
        self.profilo_ca.user.add(self.user)
        self.client.get(reverse('dashboard_index'))
        url = reverse('gestionecampionato:genera_calendario')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_genera_calendario_6_squadre(self):
        self.profilo_ca.user.add(self.user)
        self.client.get(reverse('dashboard_index'))
        from gestionesquadra.models import Squadra
        url = reverse('gestionecampionato:genera_calendario')
        response = self.client.post(url)
        self.assertEquals(response.status_code, 302)

    def test_genera_calendario_8_squadre(self):
        self.profilo_ca.user.add(self.user)
        squadre = baker.make('gestionesquadra.Squadra', _quantity=2, campionato=self.campionato, make_m2m=True)

        self.client.get(reverse('dashboard_index'))
        url = reverse('gestionecampionato:genera_calendario')
        response = self.client.post(url)
        self.assertEquals(response.status_code, 302)

    def test_genera_calendario_10_squadre(self):
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
        self.client.get(reverse('dashboard_index'))
        response = self.client.get(reverse('gestionecampionato:inserisci_riserve'))
        self.assertEquals(response.status_code, 200)
