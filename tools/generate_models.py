import sys
import yaml

TYPE_TO_MODELS = {
        'int': "models.IntegerField(null=True)",
        'float': "models.DecimalField(max_digits=30, decimal_places=2, null=True)",
        'unicode': "models.CharField(max_length=255, blank=True, null=True)",
        'str': "models.CharField(max_length=255, blank=True, null=True)",
        'bigint': "models.BigIntegerField(null=True)",
        }

def yaml2model(name, data):
    if data == '#FIXME':
        return []
    name = name[0].upper() + name[1:]
    output = ['\n\nclass %s(models.Model):' % name]
    subtables = []

    try:
        foreign_keys = data.pop('_fk')
    except KeyError:
        foreign_keys = []

    if len(data.keys()) == 1 and type(data.items()[0][1]) == dict:
        # Endpoint with a single rowset. just shift the rowset up so we don't
        # get an unneccessary link table
        data = data.items()[0][1]
    for column, ctype in data.items():
        if type(ctype) == dict:
            ctype['_fk'] = [name]
            subtables.append((column, ctype))
        else:
            if ctype in TYPE_TO_MODELS:
                output.append('    %s = %s' % (column.lower(), TYPE_TO_MODELS[ctype]))
            else:
                output.append('#FIXME: %s = ' % column.lower())


    if len(foreign_keys) > 0:
        for fk in foreign_keys:
            output.append('    %s = models.ForeignKey() #FIXME' % fk.lower())

    output.append('''
    class Meta:
        verbose_name_plural = "%s"''' % (name))
    if len(subtables) > 0:
        for subname, subdata in subtables:
            output.extend(yaml2model(subname, subdata))
    return output


if __name__ == '__main__':
    if not len(sys.argv) > 2:
        print 'usage: generate_models.py apidata.yaml namespace:endpoint [namespace:endpoint ...]'
        sys.exit(1)
    with open(sys.argv[1], 'r') as f:
        apidata = yaml.load(f)


    for pair in sys.argv[2:]:
        if ':' in pair:
            namespace, endpoint = pair.split(':')
            output = yaml2model(endpoint, apidata[namespace][endpoint])
            print '\n'.join(output)
        else:
            namespace = pair
            for endpoint in apidata[namespace]:
                output = yaml2model(endpoint, apidata[namespace][endpoint])
                print '\n'.join(output)


