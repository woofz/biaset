class CampionatoGiaAssociatoException(Exception):
    """L'eccezione viene lanciata quando un CA prova a creare un campionato,
    ma ne ha già uno associato"""
    pass


class CalendarioPresenteException(Exception):
    """L'eccezione viene lanciata quando un CA prova a generare il calendario,
    ma sono già presenti scontri"""
    pass


class NumeroPartecipantiNonRaggiuntoException(Exception):
    """L'eccezione viene lanciata quando un CA prova a generare il calendario, 
    ma il campionato non ha raggiunto il numero di partecipanti richiesto"""
    pass


class VotiPresentiException(Exception):
    """L'eccezione veien lanciata quando un CA prova a caricare i voti per la giornata,
    ma sono già presenti"""
    pass