from gestionecampionato.commandpattern.command import Command
from gestionecampionato.commandpattern.receiver import Receiver
from gestionecampionato.models import Campionato

class GeneraCalendarioCommand(Command):
    """
    Il comando delega le operazioni di creazione del calendario
    ad un Receiver.
    """

    def __init__(self, receiver: Receiver, campionato: Campionato) -> None:
        self._receiver = receiver
        self._campionato = campionato

    def execute(self) -> None:
        """
        Delega al Receiver
        """
        self._receiver.generaCalendario(campionato=self._campionato)