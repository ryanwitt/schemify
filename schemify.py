"""
usage: schemify file1 [file2 [...]]
    
    Spits out observed data paterns for json objects of arbitrary depth.
    Includes number of times a key is seen, histogram of it's types, histogram of it's values, etc.

    Files should be arrays of json per line.

    We'll make it more complicated later.
"""

import sys
import json

keys_histogram = {}
values_histogram = {}

#
# Data format:
# {
#   'key.name.potentially.multi.level': {
#       'count': count,
#       'type_histogram': { int: 2, string: 2354 }
#       'value_histogram': { value: count }
#    }
# }
#

class Counter(object):

    def __init__(self):
        self.data = {}
        self.count = 0

    def add(self, key, value):

        if isinstance(value, dict):
            for k, v in value.items():
                self.add(key+'.'+k, v)
        elif isinstance(value, list):
            for v in value:
                self.add(key, v)
        else:
            self.data[key] = self.data.get(key, {'count': 0})
            self.data[key]['count'] += 1
            self.data[key]['type_histogram'] = self.data[key].get('type_histogram', {})
            self.data[key]['type_histogram'][type(value).__name__] = self.data[key]['type_histogram'].get(type(value).__name__, 0) + 1
            self.data[key]['value_histogram'] = self.data[key].get('value_histogram', {})
            self.data[key]['value_histogram'][value] = self.data[key]['value_histogram'].get(value, 0) + 1

    def __unicode__(self):
        return u'\n'.join(
            u', '.join((
                key,
                str(value.get('count')),
                str(float(value.get('count'))/self.count),
                json.dumps('; '.join([u'%s:%s' % (v,k) for k,v in sorted(value.get('type_histogram').items(), key=lambda x: -x[1])[:5]])),
                json.dumps('; '.join([u'%s:%s' % (v,k) for k,v in sorted(value.get('value_histogram').items(), key=lambda x: -x[1])[:5]])),
             )) for (key, value) in sorted(self.data.items(), key=lambda x: -x[1].get('count',0))
         )

    def __str__(self):
        return str(self.__unicode__())

c = Counter()
#for j in (json.loads(line) for line in sys.stdin):
for fname in sys.argv[1:]:
    print >>sys.stderr, 'Processing', fname
    try:
        for item in json.load(file(fname)):
            c.count += 1
            for key, value in item.items():
                c.add(key, value)
    except Exception, e:
        print >>sys.stderr, 'Skipping previous file, errors', e
        pass

#import pprint
#pprint.pprint(c.data)
print c
