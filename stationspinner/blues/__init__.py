from stationspinner.libs.eveapi import eveapi
from django.conf import settings


class AuthorizationList(object):
    def __init__(self):
        self.authorized_characters = settings.BLUES_AUTHORIZATION_LIST['characters']
        self.authorized_corporations = settings.BLUES_AUTHORIZATION_LIST['corporations']
        self.authorized_alliances = settings.BLUES_AUTHORIZATION_LIST['alliances']
    def authorize(self, characterID):
        api = eveapi.EVEAPIConnection()
        try:
            apidata = api.eve.CharacterInfo(characterID=characterID)
        except eveapi.ServerError:
            print 'AuthorizationList denied {0} because of server error'.format(characterID)
            return False

        if apidata.characterName in self.authorized_characters:
            return True
        if apidata.corporation in self.authorized_corporations:
            return True
        if apidata.alliance in self.authorized_alliances:
            return True
        return False