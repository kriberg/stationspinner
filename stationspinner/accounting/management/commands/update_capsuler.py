from django.core.management.base import BaseCommand, CommandError
from stationspinner.accounting.models import Capsuler
from stationspinner.accounting.tasks import update_capsuler

class Command(BaseCommand):
    args = '<capsuler_pk capsuler_pk ...>'
    help = 'Starts a refresh job for a given capsuler'

    def handle(self, *args, **options):
        for name in args:
            try:
                capsuler = Capsuler.objects.get(username=name)
            except Capsuler.DoesNotExist:
                raise CommandError('Capsuler "%s" does not exist' % name)

            self.stdout.write('Updating capsuler %s.' % capsuler)
            update_capsuler(capsuler.pk)