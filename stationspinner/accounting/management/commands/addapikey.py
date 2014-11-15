from django.core.management.base import BaseCommand, CommandError
from stationspinner.accounting.models import Capsuler, APIKey
import sys
class Command(BaseCommand):
    args = '<capsuler> <key name> <keyID> <vCode>'
    help = 'Add an API key to a capsuler. For testing purposes only.'

    def handle(self, *args, **options):
        if not len(args) == 4:
            print self.help, self.args
            sys.exit(1)
        capsuler = Capsuler.objects.get(username=args[0])
        key = APIKey(name=args[1],
                     keyID=args[2],
                     vCode=args[3],
                     owner=capsuler)
        key.save()
        self.stdout.write("{0}".format(key.pk))
