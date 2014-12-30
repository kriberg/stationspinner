from django.views.generic import View
from django.http import HttpResponse
from stationspinner.libs.eveapihandler import EveAPIHandler
import json


class ServerStatusView(View):
    def get(self, request):
        handler = EveAPIHandler()
        api = handler.get_eveapi()
        try:
            status = api.server.ServerStatus()
            response = json.dumps({"serverOpen": status.serverOpen,
                                   "onlinePlayers": status.onlinePlayers})

        except:
            response = '{"serverOpen": "False", "onlinePlayers": 0}'
        return HttpResponse(response)




