from django.core.management.base import BaseCommand, CommandError
from stationspinner.accounting.models import Capsuler
import sys

class Command(BaseCommand):
    args = '<username email password>'
    help = 'Create a new capsuler. Testing purposes only'

    def handle(self, *args, **options):
        if not len(args) == 3:
            print self.help
            sys.exit(1)
        capsuler = Capsuler.objects.create_user(args[0],
                                                args[1],
                                                args[2])
        capsuler.save()
        self.stdout.write("{0}".format(capsuler.pk))
