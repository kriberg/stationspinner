from stationspinner.celery import app
from stationspinner.libs.eveapihandler import EveAPIHandler
from stationspinner.universe.models import Alliance,\
    RefType, ConquerableStation, Sovereignty, APICallGroup, APICall, UniverseUpdate
from celery.utils.log import get_task_logger
from celery import group
from stationspinner.libs.pragma import get_current_time
from datetime import datetime
from pytz import UTC

log = get_task_logger(__name__)


@app.task(name='universe.update_universe')
def update_universe():
    batch = []
    for name, taskfn in API_MAP.items():
        target, created = UniverseUpdate.objects.get_or_create(apicall=name)
        current_time = get_current_time()
        if created:
            batch.append(taskfn.s())
        else:
            if not target.cached_until:
                batch.append(taskfn.s())
            elif target.cached_until < current_time:
                batch.append(taskfn.s())

    group(batch).apply_async()
    log.info('Universe update scheduled')


@app.task(name='universe.fetch_alliances')
def fetch_alliances():
    handler = EveAPIHandler()
    api = handler.get_eveapi()
    apiData = api.eve.AllianceList()
    allianceIDs = handler.autoparseList(apiData.alliances,
                                      Alliance,
                                      unique_together=('allianceID',))
    log.info('Updated {0} alliances.'.format(len(allianceIDs)))
    closed = Alliance.objects.exclude(pk__in=allianceIDs)
    for alliance in closed:
        alliance.closed = True
        alliance.endDate = datetime.now(tz=UTC)
        alliance.save()
    log.info('Closed {0} alliances.'.format(closed.count()))

    update, created = UniverseUpdate.objects.get_or_create(apicall='AllianceList')
    update.updated(apiData)



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
    update, created = UniverseUpdate.objects.get_or_create(apicall='RefTypes')
    update.updated(apiData)


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
    update, created = UniverseUpdate.objects.get_or_create(apicall='ConquerableStationList')
    update.updated(apiData)


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
    update, created = UniverseUpdate.objects.get_or_create(apicall='Sovereignty')
    update.updated(apiData)


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
    update, created = UniverseUpdate.objects.get_or_create(apicall='CallList')
    update.updated(apiData)

API_MAP = {
    'CallList': fetch_apicalls,
    'RefTypes': fetch_reftypes,
    'AllianceList': fetch_alliances,
    'ConquerableStationList': fetch_conquerable_stations,
    'Sovereignty': fetch_sovereignty,
    }