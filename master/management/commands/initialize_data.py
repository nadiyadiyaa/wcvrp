from django.core.management.base import BaseCommand
from django.core import management
from django.core.management.commands import loaddata
import os


class Command(BaseCommand):
    help = "Command to initialize data"

    def handle(self, *args, **kwargs):
        os.system("python3 manage.py loaddata */fixtures/*.json")
