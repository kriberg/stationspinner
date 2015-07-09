from stationspinner.sde.models import MapDenormalize, \
    MapRegion, \
    MapSolarSystem, \
    MapConstellation, \
    StaStation, \
    DgmAttributeCategory, \
    DgmTypeAttribute
from stationspinner.universe.models import ConquerableStation
from datetime import datetime
from pytz import UTC


def get_attributes_by_categories(item):
    type_attributes = DgmTypeAttribute.objects.filter(type=item)
    attribute_types = item.attribute
    attribute_categories = DgmAttributeCategory.objects.filter(pk__in=attribute_types)
    return (type_attributes, attribute_types, attribute_categories)

#SELECT case
#  when a.locationID BETWEEN 66000000 AND 66014933 then
#    (SELECT s.stationName FROM dbo.staStations AS s
#      WHERE s.stationID=a.locationID-6000001)
#  when a.locationID BETWEEN 66014934 AND 67999999 then
#    (SELECT c.stationName FROM api.ConqStations AS c
#      WHERE c.stationID=a.locationID-6000000)
#  when a.locationID BETWEEN 60014861 AND 60014928 then
#    (SELECT c.stationName FROM api.ConqStations AS c
#      WHERE c.stationID=a.locationID)
#  when a.locationID BETWEEN 60000000 AND 61000000 then
#    (SELECT s.stationName FROM dbo.staStations AS s
#      WHERE s.stationID=a.locationID)
#  when a.locationID>=61000000 then
#    (SELECT c.stationName FROM api.ConqStations AS c
#      WHERE c.stationID=a.locationID)
#  else (SELECT m.itemName FROM dbo.mapDenormalize AS m
#    WHERE m.itemID=a.locationID) end
#AS location,a.locationId AS locID FROM aleAssetItems AS a
#GROUP BY a.locationID;

def get_location_name(location_id):
    if type(location_id) in (str, unicode):
        try:
            location_id = int(location_id)
        except:
            return location_id
    if location_id >= 66000000 and location_id <= 66014933:
        try:
            loc = StaStation.objects.get(pk=(int(location_id)-6000001))
            return loc.stationName
        except:
            pass
    elif location_id >= 66014934 and location_id <= 67999999:
        try:
            loc = ConquerableStation.objects.get(pk=(int(location_id)-6000000))
            return loc.stationName
        except ConquerableStation.DoesNotExist:
            pass
    elif location_id >= 60014861 and location_id <= 60014928:
        try:
            loc = ConquerableStation.objects.get(pk=location_id)
            return loc.stationName
        except ConquerableStation.DoesNotExist:
            pass
    elif location_id >= 60000000 and location_id <= 61000000:
        try:
            loc = StaStation.objects.get(pk=location_id)
            return loc.stationName
        except:
            pass
    elif location_id >= 61000000:
        try:
            loc = ConquerableStation.objects.get(pk=location_id)
            return loc.stationName
        except ConquerableStation.DoesNotExist:
            pass
    else:
        try:
            loc = MapDenormalize.objects.get(pk=location_id)
            return loc.itemName
        except MapDenormalize.DoesNotExist:
            pass
    return location_id

def get_location_id(location_name):
    try:
        loc =StaStation.objects.get(stationName=location_name)
        if loc.pk >= 60000000 and loc.pk <= 60014932:
            return loc.pk+6000001
        else:
            return loc.pk
    except:
        pass

    try:
        loc = ConquerableStation.objects.get(stationName=location_name)
        if loc.pk >= 60014934 and loc.pk <= 61999999:
            return int(loc.pk)+6000000
        else:
            return loc.pk
    except:
        pass

    return MapDenormalize.objects.get(itemName=location_name).pk

def get_location(location_id):
    if type(location_id) in (str, unicode):
        try:
            location_id = int(location_id)
        except:
            return location_id
    if location_id >= 66000000 and location_id <= 66014933:
        try:
            loc = StaStation.objects.get(pk=(int(location_id)-6000001))
            return loc
        except:
            pass
    elif location_id >= 66014934 and location_id <= 67999999:
        try:
            loc = ConquerableStation.objects.get(pk=(int(location_id)-6000000))
            return loc
        except ConquerableStation.DoesNotExist:
            pass
    elif location_id >= 60014861 and location_id <= 60014928:
        try:
            loc = ConquerableStation.objects.get(pk=location_id)
            return loc
        except ConquerableStation.DoesNotExist:
            pass
    elif location_id >= 60000000 and location_id <= 61000000:
        try:
            loc = StaStation.objects.get(pk=location_id)
            return loc
        except:
            pass
    elif location_id >= 61000000:
        try:
            loc = ConquerableStation.objects.get(pk=location_id)
            return loc
        except ConquerableStation.DoesNotExist:
            pass
    else:
        try:
            loc = MapDenormalize.objects.get(pk=location_id)
            return loc
        except MapDenormalize.DoesNotExist:
            pass
    return location_id

def get_location_regionName(location):
    if type(location) in (MapDenormalize, ConquerableStation):
        return location.regionName()
    elif type(location) is MapRegion:
        return location.regionName
    elif type(location) in (MapConstellation, MapSolarSystem, StaStation):
        return location.region.regionName
    elif type(location) is ConquerableStation:
        return location.regionName()

def get_location_regionID(location):
    if type(location) in (MapDenormalize, ConquerableStation):
        return location.regionID()
    elif type(location) is MapRegion:
        return location.pk
    elif type(location) in (MapConstellation, MapSolarSystem, StaStation):
        return location.region.pk
    elif type(location) is ConquerableStation:
        return location.regionID()

def get_location_solarSystemName(location):
    if type(location) in (MapDenormalize, ConquerableStation):
        return location.solarSystemName()
    elif type(location) is MapSolarSystem:
        return location.solarSystemName
    elif type(location) is StaStation:
        return location.solarSystem.solarSystemName
    elif type(location) is ConquerableStation:
        return location.solarSystemName()

def get_location_solarSystemID(location):
    if type(location) is MapDenormalize:
        return location.solarSystemID()
    elif type(location) is MapSolarSystem:
        return location.pk
    elif type(location) is StaStation:
        return location.solarSystem.pk
    elif type(location) is ConquerableStation:
        return location.solarSystemID

def get_current_time():
    #try:
    #    api = eveapi.EVEAPIConnection()
    #    status = api.server.ServerStatus()
    #    return datetime.fromtimestamp(status._meta.currentTime, tz=UTC)
    #except:
    return datetime.now(tz=UTC)


PACKAGED_VOLUME = {
    12: {  # Cargo Container
           3296: 65,  # Large Standard Container
           3293: 33,  # Medium Standard Container
           3297: 10  # Small Standard Container
           },
    340: {  # Secure Cargo Container
            11489: 300,  # Giant Secure Container
            11488: 150,  # Huge Secure Container
            3465: 65,  # Large Secure Container
            3466: 33,  # Medium Secure Container
            3467: 10  # Small Secure Container
            },
    448: {  # Audit Log Secure Container
            17368: 100000,  # Station Warehouse Container
            17367: 50000,  # Station Vault Container
            17366: 10000,  # Station Container
            17365: 65,  # Large Audit Log Secure Container
            17364: 33,  # Medium Audit Log Secure Container
            17363: 10  # Small Audit Log Secure Container
            },
    649: {  # Freight Container
            33005: 5000,  # Huge Freight Container
            33003: 2500,  # Enormous Freight Container
            24445: 1200,  # Giant Freight Container
            33007: 1000,  # Large Freight Container
            33009: 500,  # Medium Freight Container
            33011: 100  # Small Freight Container
            },
    25: 2500,  # Frigate
    26: 10000,  # Cruiser
    27: 50000,  # Battleship
    28: 20000,  # Industrial
    30: 10000000,  # Titan
    31: 500,  # Shuttle
    237: 2500,  # Rookie ship
    324: 2500,  # Assault Frigate
    358: 10000,  # Heavy Assault Cruiser
    380: 20000,  # Deep Space Transport
    419: 15000,  # Combat Battlecruiser
    420: 5000,  # Destroyer
    463: 3750,  # Mining Barge
    485: 1300000,  # Dreadnought
    513: 1300000,  # Freighter
    540: 15000,  # Command Ship
    541: 5000,  # Interdictor
    543: 3750,  # Exhumer
    547: 1300000,  # Carrier
    659: 1300000,  # Supercarrier
    830: 2500,  # Covert Ops
    831: 2500,  # Interceptor
    832: 10000,  # Logistics
    833: 10000,  # Force Recon Ship
    834: 2500,  # Stealth Bomber
    883: 1300000,  # Capital Industrial Ship
    893: 2500,  # Electronic Attack Ship
    894: 10000,  # Heavy Interdiction Cruiser
    898: 50000,  # Black Ops
    900: 50000,  # Marauder
    902: 1300000,  # Jump Freighter
    906: 10000,  # Combat Recon Ship
    941: 500000,  # Industrial Command Ship
    963: 5000,  # Strategic Cruiser
    1022: 500,  # Prototype Exploration Ship
    1201: 15000,  # Attack Battlecruiser
    1202: 20000  # Blockade Runner
}

class UnknownPackagedItem(BaseException):
    pass

def get_item_packaged_volume(groupID, typeID):
    if groupID in PACKAGED_VOLUME:
        if type(PACKAGED_VOLUME[groupID]) is int:
            return PACKAGED_VOLUME[groupID]
        else:
            if typeID in PACKAGED_VOLUME[groupID]:
                return PACKAGED_VOLUME[groupID][typeID]
    raise UnknownPackagedItem('typeID {0} with groupID {1} is unknown.'.format(typeID, groupID))

