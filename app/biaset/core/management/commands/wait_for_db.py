from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError
import time


class Command(BaseCommand):
    """ Django command per mettere in pausa l'esecuzione fin quando il database non è disponbile"""
    def handle(self, *args, **kwargs):
        self.stdout.write('waiting for db ...')
        db_conn = None
        while not db_conn:
            try:
                # Prendiamo il tipo di database dalle connessioni
                db_conn = connections['default']
                # prints success messge in green
                self.stdout.write(self.style.SUCCESS('db Disponibile'))
            except OperationalError:
                self.stdout.write("Database non disponibile, attendo 1 secondo...")
                time.sleep(1)
