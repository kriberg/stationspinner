from django.core.management.base import BaseCommand, CommandError
from stationspinner.celery import app

class Command(BaseCommand):
    args = ''
    help = 'Updates all capsulers'

    def handle(self, *args, **options):
        app.send_task('accounting.update_capsulers')
