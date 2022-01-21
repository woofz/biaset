# Setting up Django Env
from typing import List
from gestionecampionato.models import Campionato, Partita, Formazione
from gestionesquadra.models import Squadra
from competitions.scheduler.roundrobin import RoundRobinScheduler
import django
import sys
import os
sys.path.append("/app/biaset")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biaset.settings')
django.setup()


class Receiver:
    """
    La classe Receiver contiene la logica di business per l'esecuzione delle operazioni
    richieste dal comando.
    """

    def generaCalendario(self, campionato: Campionato) -> None:
        """Metodo per generare gli scontri del campionato [GeneraCalendarioCommand]

        Args:
            teams (List): la lista contenente le squadre
        """
        # 6 squadre = 7 meetings
        # 8 squadre = 5 meetings
        # 10 squadre = 4 meetings
        meetings = 4  # Default per 10 squadre

        # prendo le squadre del campionato
        squadre = Squadra.objects.filter(campionato=campionato)
        teams = list(squadre)  # Converto le squadre in lista per l'algoritmo

        if len(teams) == 8:
            meetings = 5
        elif len(teams) == 6:
            meetings = 7

        scheduler = RoundRobinScheduler(
            teams, meetings=meetings)  # Algoritmo di scheduling
        scheduling = scheduler.generate_schedule()
        # Creo le entità Partita per ogni match generato
        for i in range(0, len(scheduling)):
            
            for squadra in scheduling[i]:
                partita = Partita()
                partita.giornata = i + 1
                partita.save()
                partita.squadra.add(squadra[0])
                partita.squadra.add(squadra[1])
                Formazione.objects.create(tipo='T', partita=partita)
                Formazione.objects.create(tipo='R', partita=partita)
