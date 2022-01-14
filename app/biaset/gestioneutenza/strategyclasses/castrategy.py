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

class CaStrategy(Strategy):
    """Concrete Strategy - Championship Admin (CA)
    La classe mappa semplicemente un User con un profilo CA
    """
    
    def doOperation(self, user: User) -> bool:  
        """È il metodo core della classe. 

        Args:
            user (User): l'utente da mappare

        Returns:
            bool: ritorna True se l'operazione è andata a buon fine, 
                  False se ha fallito
        """
        profilo = Profilo.objects.get(nome='Championship Admin') # Prendo il profilo da CA
        profilo.user.add(user)
        return True