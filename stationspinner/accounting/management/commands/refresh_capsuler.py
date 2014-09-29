from django.core.management.base import BaseCommand, CommandError
from stationspinner.accounting.models import Capsuler
from stationspinner.accounting.tasks import refresh_capsuler

class Command(BaseCommand):
    args = '<capsuler_pk capsuler_pk ...>'
    help = 'Starts a refresh job for a given capsuler'

    def handle(self, *args, **options):
        for capsuler_pk in args:
            try:
                capsuler = Capsuler.objects.get(pk=capsuler_pk)
            except Capsuler.DoesNotExist:
                raise CommandError('Capsuler "%s" does not exist' % capsuler_pk)

            self.stdout.write('Refreshing capsuler %s.' % capsuler)
            refresh_capsuler(capsuler.pk)