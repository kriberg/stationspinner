from django.core.management.base import BaseCommand, CommandError
from stationspinner.character.models import CharacterSheet

class Command(BaseCommand):
    help = 'Lists all enabled characterIDs with their APIKey PKs. Handy for sending tasks'

    def handle(self, *args, **options):
        characters = CharacterSheet.objects.filter(enabled=True)
        for char in characters:
            self.stdout.write('CharacterID\t\t {0} APIKey\t\t {1}'.format(char.pk, char.owner_key.pk))