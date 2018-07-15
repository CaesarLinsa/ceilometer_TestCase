
from caesar import sample
import uuid
import datetime
from oslo_config import cfg
from caesar.impl_mongodb import  Connection
import itertools

conf = cfg.ConfigOpts()

OPTS = [
    cfg.StrOpt('database',
               default='mongodb',
               help='database'),

]
def list_opts():
    return [
        ('DEFAULT',
         itertools.chain(
                         OPTS))]
for group, options in list_opts():
    conf.register_opts(list(options),
                       group=None if group == "DEFAULT" else group)

resource_id = str(uuid.uuid4())
test_data = [
    sample.Sample(
        name='alpha',
        type=sample.TYPE_CUMULATIVE,
        unit='',
        volume=1,
        user_id='test',
        project_id='test',
        resource_id=resource_id,
        timestamp=datetime.datetime.utcnow().isoformat(),
        resource_metadata={'name': 'TestPublish'},
    ),
    sample.Sample(
        name='beta',
        type=sample.TYPE_CUMULATIVE,
        unit='',
        volume=1,
        user_id='test',
        project_id='test',
        resource_id=resource_id,
        timestamp=datetime.datetime.utcnow().isoformat(),
        resource_metadata={'name': 'TestPublish'},
    ),
    sample.Sample(
        name='gamma',
        type=sample.TYPE_CUMULATIVE,
        unit='',
        volume=1,
        user_id='test',
        project_id='test',
        resource_id=resource_id,
        timestamp=datetime.datetime.now().isoformat(),
        resource_metadata={'name': 'TestPublish'},
    ),
]

def meter_message_from_counter(sample):
    """Make a metering message ready to be published or stored.

    Returns a dictionary containing a metering message
    for a notification message and a Sample instance.
    """
    msg = {'source': sample.source,
           'counter_name': sample.name,
           'counter_type': sample.type,
           'counter_unit': sample.unit,
           'counter_volume': sample.volume,
           'user_id': sample.user_id,
           'project_id': sample.project_id,
           'resource_id': sample.resource_id,
           'timestamp': sample.timestamp,
           'resource_metadata': sample.resource_metadata,
           'message_id': sample.id,
           'monotonic_time': sample.monotonic_time,
           }
    return msg


conn = Connection(conf, 'mongodb://196.168.1.111:27017/test')
conn.record_metering_data([
    meter_message_from_counter(sample)
            for sample in test_data])
