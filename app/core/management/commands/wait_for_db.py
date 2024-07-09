'''
Wait for db to be available before starting the server
'''
import time

from psycopg import OperationalError as PsycopgOperationalError

from django.db.utils import OperationalError
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    '''Django command to pause execution until database is available'''
    def handle(self, *args, **options):
        '''Handle the command'''
        self.stdout.write('Waiting for database...')
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default']) # type: ignore
                db_up = True
            except (OperationalError, PsycopgOperationalError):
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database available!'))