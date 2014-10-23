from stationspinner.sde.models import MapDenormalize, \
    StaStation, \
    DgmAttributeCategory, \
    DgmTypeAttribute
from stationspinner.universe.models import ConquerableStation

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
    if location_id >= 66000000 and location_id <= 66014933:
        try:
            loc = StaStation.objects.get(pk=(int(location_id)-6000001))
            return loc.stationName
        except:
            pass
    elif location_id >= 66014934 and location_id <= 67999999:
        try:
            loc = ConquerableStation.objects.get(pk=(int(location_id)-6000000))
            return loc.name
        except ConquerableStation.DoesNotExist:
            pass
    elif location_id >= 60014861 and location_id <= 60014928:
        try:
            loc = ConquerableStation.objects.get(pk=location_id)
            return loc.name
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
            return loc.name
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
        loc =StaStation.objects.get(stationname=location_name)
        if loc.pk >= 60000000 and loc.pk <= 60014932:
            return loc.pk+6000001
        else:
            return loc.pk
    except:
        pass

    try:
        loc = ConquerableStation.objects.get(name=location_name)
        if loc.pk >= 60014934 and loc.pk <= 61999999:
            return int(loc.pk)+6000000
        else:
            return loc.pk
    except:
        pass

    return MapDenormalize.objects.get(itemname=location_name)

