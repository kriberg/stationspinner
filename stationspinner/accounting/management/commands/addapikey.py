from django.core.management.base import BaseCommand, CommandError
from stationspinner.accounting.models import Capsuler, APIKey
class Command(BaseCommand):
    args = '<capsuler name keyID vCode>'
    help = 'Add an API key to a capsuler. For testing purposes only.'

    def handle(self, *args, **options):
        capsuler = Capsuler.objects.get(username=args[0])
        key = APIKey(name=args[1],
                     keyID=args[2],
                     vCode=args[3],
                     owner=capsuler)
        key.save()
        self.stdout.write("{0}".format(key.pk))
