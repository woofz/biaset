from gestioneutenza.strategyclasses.invitenotfound import InviteNotFoundException
from gestioneutenza.strategyclasses.strategy import Strategy
import os, sys
import random
from datetime import datetime

# Setting up Django Env
sys.path.append("/app/biaset")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biaset.settings')
import django

django.setup()

from django.contrib.auth.models import User
from gestioneutenza.models import Invito, Profilo
from gestionecampionato.models import Campionato
from gestionesquadra.models import Squadra


class AllenatoreStrategy(Strategy):
    """Concrete Strategy - Allenatore
    La classe mappa semplicemente un User con un profilo Allenatore
    """

    def doOperation(self, user: User) -> bool:
        """È il metodo core della classe. 

        Args:
            user (User): l'utente da mappare

        Returns:
            bool: ritorna True se l'operazione è andata a buon fine, 
                  False se ha fallito
        """
        profilo = Profilo.objects.get(nome='Allenatore')  # Prendo il profilo da Allenatore
        invite = None or Invito.objects.filter(destinatario=user.email).first()
        print(invite)
        if invite is not None:
            if self.isInviteValid(invite):
                campionato = invite.campionato
                profilo.user.add(user)  # Associo il profilo 'Allenatore' all'utente
                return self.championshipSignUp(campionato, user, invite)  # Registro l'utente al campionato
        else:
            raise InviteNotFoundException
        return False

    def isInviteValid(self, invite: Invito) -> bool:
        """Controlla la validità di un Invito

        Args:
            invite (Invito): Invito da controllare

        Returns:
            bool: True se la data di scadenza dell'invito è inferiore alla data attuale, False altrimenti
        """
        now = datetime.now().date()
        expire_dt = invite.expire_dt
        return True if expire_dt > now else False

    def championshipSignUp(self, campionato: Campionato, utente: User, invite: Invito) -> bool:
        """Crea una squadra associata all'allenatore appena iscritto e la registra
        al campionato

        Args:
            campionato (Campionato): il campionato nel quale iscrivere l'utente
            utente (User): l'utente (allenatore) da iscrivere
            
        Returns:
            bool: True se l'iscrizione è andata a buon fine, False altrimenti
        """
        numero_iscritti = Squadra.objects.filter(campionato=campionato).count()
        if numero_iscritti < campionato.partecipanti:
            if Squadra.objects.filter(allenatore=utente).exists():
                return True
            squadra = Squadra(nome=f"Squadra di {utente.first_name} {utente.last_name}",
                              campionato=campionato,
                              allenatore=utente)
            squadra.save()
            # Cancello l'invito
            invite.delete()
            return True
        return False
