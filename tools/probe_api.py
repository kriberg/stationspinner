import sys
import pprint
import yaml
import eveapi
from cache import MyCacheHandler

eveapi.set_user_agent('Armada prober//Vittoros@#eve-dev')

def probe(keys, endpoints):
    output = {}

    for namespace in ('Corp','Char'):
        api = eveapi.EVEAPIConnection(cacheHandler=MyCacheHandler(debug=False))
        auth = api.auth(keyID=keys[namespace]['keyID'], vCode=keys[namespace]['vCode'])
        characterID = keys[namespace]['characterID']
        output[namespace] = {}
        for endpoint in endpoints[namespace]:
            sys.stderr.write('Probing %s %s\n' % (namespace, endpoint))
            if len(endpoints[namespace][endpoint]['keys']) > 1:
                continue
            output[namespace][endpoint] = {}
            try:
                #FIXME: should use keys from endpoints to determine what parameters to pass
                res = getattr(getattr(auth, namespace), endpoint)(characterID=characterID)
            except Exception, e:
                sys.stderr.write('%s: %s\n' % (endpoint, e))
                output[namespace][endpoint] = '#FIXME'
                continue
            attributes = filter(lambda l: not l.startswith('_'), dir(res))
            for attribute in attributes:
                attribute_type = type(getattr(res, attribute)).__name__
                if not attribute_type == 'IndexRowset':
                    output[namespace][endpoint][attribute] = attribute_type
                else:
                    rowset = getattr(res, attribute)
                    columns = rowset.columns.split(',')
                    subtable = {}
                    try:
                        sample_row = rowset[0]
                        for column in columns:
                            column = column.strip()
                            subtable[str(column)] = str(type(getattr(sample_row, column)).__name__)
                    except IndexError:
                        for column in columns:
                            subtable[str(column)] = '#FIXME'
                    except AttributeError:
                        sys.stderr.write('Error parsing "%s", columns: "%s"\n' % (attribute, columns))
                    output[namespace][endpoint][attribute] = subtable
            output[namespace][endpoint]['_fk'] = endpoints[namespace][endpoint]['keys']
    return output






if __name__ == '__main__':
    if not len(sys.argv) == 3:
        print 'usage: probe_api.py keysfile.yaml endpoints.yaml'
        sys.exit(1)
    with open(sys.argv[1], 'r') as f:
        keys = yaml.load(f)
    with open(sys.argv[2], 'r') as f:
        endpoints = yaml.load(f)
    output = probe(keys, endpoints)

    print yaml.dump(output, encoding='utf-8', allow_unicode=True, default_flow_style=False)
