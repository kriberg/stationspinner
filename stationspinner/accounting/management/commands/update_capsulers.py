from django.core.management.base import BaseCommand, CommandError
from stationspinner.accounting.models import Capsuler
from stationspinner.accounting.tasks import update_capsuler

class Command(BaseCommand):
    args = ''
    help = 'Starts a refresh job for a given capsuler'

    def handle(self, *args, **options):
        capsulers = Capsuler.objects.all()
        for capsuler in capsulers:
            self.stdout.write('Updating capsuler %s.' % capsuler)
            update_capsuler(capsuler.pk)