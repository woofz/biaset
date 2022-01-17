from gestionecampionato.commandpattern.command import Command


class Invoker:
    """
    L'Invoker è associato a uno o più comandi. Esso invia
    la richiesta al Comando.
    """

    command = None

    """
    Inizializza il/ comando/i.
    """

    def setCommand(self, command: Command):
        self.command = command

    def doOperation(self) -> None:
        """
        L'invoker passa una richiesta ad un receiver indirettamente, eseguendo
        un comando.
        """
        if isinstance(self.command, Command):
            self.command.execute()