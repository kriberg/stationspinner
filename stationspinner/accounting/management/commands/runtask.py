from django.core.management.base import BaseCommand, CommandError
from stationspinner.celery import app

class Command(BaseCommand):
    args = '<task_name [args ...] [options ...]>'
    help = 'Starts a task with the given arguments and options'

    def handle(self, *args, **options):
        task_name = args[0]
        app.send_task(task_name, list(args[1:]), **options)