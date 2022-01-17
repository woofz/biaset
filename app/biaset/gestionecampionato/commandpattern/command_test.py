from invoker import Invoker
from generacalendariocommand import GeneraCalendarioCommand
from receiver import Receiver

if __name__ == "__main__":
    """
    The client code can parameterize an invoker with any commands.
    """

    invoker = Invoker()
    receiver = Receiver()
    invoker.setCommand(GeneraCalendarioCommand(receiver=receiver))


    invoker.doOperation()