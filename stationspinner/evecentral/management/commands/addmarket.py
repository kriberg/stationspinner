from django.core.management.base import BaseCommand, CommandError
from stationspinner.evecentral.models import Market
from stationspinner.sde.models import MapDenormalize
import sys
class Command(BaseCommand):
    args = '<location name>'
    help = 'Add a market to the list of indexed markets.'

    def handle(self, *args, **options):
        if not len(args) == 1:
            print self.help, self.args
            sys.exit(1)

        try:
            location = MapDenormalize.objects.get(itemName__iexact=args[0])
        except MapDenormalize.DoesNotExist:
            self.stdout.write("Unknown location")
            sys.exit(1)

        market = Market(locationID=location.pk)
        market.save()

        self.stdout.write('Added "{0}" to indexed markets.'.format(location.itemName))
