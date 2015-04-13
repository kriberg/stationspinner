from django.core.management.base import BaseCommand, CommandError
from stationspinner.celery import app
from stationspinner.universe.models import APICall

class Command(BaseCommand):
    args = ''
    help = 'Bootstraps the stationspinner database if no initial data is present'

    def handle(self, *args, **options):
        if APICall.objects.all().count() == 0:
            result = app.send_task('update_universe', [], **options).get()
            if result:
                self.stdout.write('Result: {0}'.format(result))
        else:
            self.stdout.write('Already bootstrapped')
