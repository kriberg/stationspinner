from django.core.management.base import BaseCommand, CommandError
from stationspinner.accounting.models import APIUpdate, APICall
from stationspinner.character.models import CharacterSheet
from stationspinner.corporation.models import CorporationSheet
import sys
class Command(BaseCommand):
    args = '<character/corporation name> <call type> <call name>'
    help = 'Find the APIUpdate PK for a specific call associated with a character/corporation.'

    def handle(self, *args, **options):
        if not len(args) == 3:
            print self.help, self.args
            sys.exit(1)
        try:
            entity = CharacterSheet.objects.get(name=args[0])
        except CharacterSheet.DoesNotExist:
            try:
                entity = CorporationSheet.objects.get(corporationName=args[0])
            except CorporationSheet.DoesNotExist:
                self.stdout.write('No character/corporation named "{0}" exists.'.format(args[0]))
                sys.exit(1)
        key = entity.owner_key
        try:
            call = APICall.objects.get(type__iexact=args[1],
                                       name__iexact=args[2])
        except APICall.DoesNotExist:
            self.stdout.write('No API Call by that name.')
            sys.exit(1)

        if not call.accessMask & key.accessMask > 0:
            self.stdout.write('Key {0} has not the correct mask for "{1}.{2}".'.format(
                key.keyID,
                call.type,
                call.name
            ))
            sys.exit(1)

        updates = APIUpdate.objects.filter(apicall=call,
                                           apikey=key,
                                           owner=entity.pk)
        if updates.count() == 0:
            self.stdout.write('APICall for "{0}.{1}" does not exist.'.format(
                call.type,
                call.name
            ))
            sys.exit(1)
        for update in updates:
            self.stdout.write('PK {0}, characterID {4} keyID {3}, last updated {1}, cached until {2}.'.format(
                update.pk,
                update.last_update,
                update.cached_until,
                update.apikey.keyID,
                entity.pk
            ))

