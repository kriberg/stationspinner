import sys, yaml

def parse_file(csv_file):
    endpoints = {}
    with open(csv_file, 'r') as f:
        for line in f.readlines():
            params = map(lambda l: l.strip(), line.split(';'))
            namespace, context = params[1].split('/')
            if not namespace in endpoints:
                endpoints[namespace] = {}
            service = {'name': params[0],
                    'url': 'https://api.eveonline.com/{0}.xml.aspx'.format(params[1]),
                    'mask': params[2],
                    'style': params[3],
                    'cache_time': params[4]
                    }
            endpoints[namespace][context] = service
    return yaml.dump(endpoints, default_flow_style=False)


if __name__ == '__main__':
    print parse_file(sys.argv[1])
