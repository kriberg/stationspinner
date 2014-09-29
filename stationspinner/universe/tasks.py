from stationspinner.celery import app
from stationspinner.libs.eveapihandler import EveAPIHandler
from stationspinner.universe.models import Alliance,\
    RefType, ConquerableStation, Sovereignty, APICallGroup, APICall
from celery.utils.log import get_task_logger

log = get_task_logger(__name__)


@app.task(name='universe.fetch_alliances')
def fetch_alliances():
    handler = EveAPIHandler()
    api = handler.get_eveapi()
    apiData = api.eve.AllianceList()
    allianceIDs = handler.autoparseList(apiData.alliances,
                                      Alliance,
                                      unique_together=('allianceID',))
    log.info('Updated {0} alliances.'.format(len(allianceIDs)))
    #closed = Alliance.objects.exclude(pk__in=allianceIDs)
    #for alliance in closed:
    #    alliance.closed = True
    #    alliance.endDate = datetime.now()
    #    alliance.save()

    #log.info('Closed {0} alliances.'.format(closed.count()))


@app.task(name='universe.fetch_reftypes')
def fetch_reftypes():
    handler = EveAPIHandler()
    api = handler.get_eveapi()
    apiData = api.eve.RefTypes()
    rIDs = handler.autoparseList(apiData.refTypes,
                          RefType,
                          unique_together=('refTypeID',),
                          pre_save=True)
    log.info('Updated {0} ref types.'.format(len(rIDs)))


@app.task(name='universe.fetch_conquerable_stations')
def fetch_conquerable_stations():
    handler = EveAPIHandler()
    api = handler.get_eveapi()
    apiData = api.eve.ConquerableStationList()
    stationIDs = handler.autoparseList(apiData.outposts,
                          ConquerableStation,
                          unique_together=('stationID',),
                          pre_save=True)
    log.info('Updated {0} conquerable stations.'.format(len(stationIDs)))


@app.task(name='universe.fetch_sovereignty')
def fetch_sovereignty():
    handler = EveAPIHandler()
    api = handler.get_eveapi()
    apiData = api.map.Sovereignty()
    sovIDs = handler.autoparseList(apiData.solarSystems,
                          Sovereignty,
                          unique_together=('solarSystemID',),
                          pre_save=True)
    log.info('Updated sovereignty for {0} systems.'.format(len(sovIDs)))


@app.task(name='universe.fetch_apicalls')
def fetch_apicalls():
    handler = EveAPIHandler()
    api = handler.get_eveapi()
    apiData = api.api.CallList()
    cgIDs = handler.autoparseList(apiData.callGroups,
                          APICallGroup,
                          unique_together=('groupID',),
                          pre_save=True)
    cIDs = handler.autoparseList(apiData.calls,
                          APICall,
                          unique_together=('accessMask', 'type'),
                          pre_save=True)

    log.info('Added {0} call groups and {1} calls.'.format(cgIDs, cIDs))