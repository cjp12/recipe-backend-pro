"""
Django command to wait for the database to be available.
This file structure allows for django to automatically
detect that this is a management command.
Anything that is a management
command will be available with python manage.py.
"""

import time

from psycopg2 import OperationalError as Psycopg2Error

from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command to wait for the db"""

    def handle(self, *args, **options):
        """
        Entry point for command.
        The handle method will get called whenever the command is called.
        """

        # stdout is the way that we are able to write to the console.
        self.stdout.write('Waiting for database')

        db_up = False

        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2Error, OperationalError):
                self.stdout.write('Database unavailable, waiting 1 second.')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database Available'))
