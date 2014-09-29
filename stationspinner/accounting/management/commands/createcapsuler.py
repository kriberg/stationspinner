from django.core.management.base import BaseCommand, CommandError
from stationspinner.accounting.models import Capsuler
class Command(BaseCommand):
    args = '<username email password>'
    help = 'Create a new capsuler. Testing purposes only'

    def handle(self, *args, **options):
        capsuler = Capsuler.objects.create_superuser(args[0],
                                                     args[1],
                                                     args[2])
        capsuler.save()
        self.stdout.write("{0}".format(capsuler.pk))
