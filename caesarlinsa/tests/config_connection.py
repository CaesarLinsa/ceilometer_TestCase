from oslo_config import cfg
import itertools
from caesarlinsa.storage import get_connection_from_config, SampleFilter
mongo_OPTS = [
    cfg.StrOpt('database',
               default='mongodb',
               help='database'),

]
OPTS = [
    cfg.IntOpt('max_retries',
                default=3,
                help="max connection to database times"
                      ),
    cfg.IntOpt('retry_interval',
               default=60,
               help='connection timeout 300 senconds'),
    cfg.StrOpt('connection',
               default='mongodb+mongodb://196.168.1.111:27017,'
                      '196.168.1.112:27017,'
                      '196.168.1.113:27017/test',
               help='connection mongodb url')
    ]

def list_opts():
    return [('database',itertools.chain(OPTS)),
            ('DEFAULT', itertools.chain(mongo_OPTS)),
            ]

conf = cfg.ConfigOpts()

for group, options in list_opts():
    conf.register_opts(list(options),
                       group=None if group == "DEFAULT" else group)

conn = get_connection_from_config(conf)
data = list (conn.meter_find())

