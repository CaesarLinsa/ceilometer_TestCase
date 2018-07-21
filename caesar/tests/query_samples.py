from oslo_config import cfg
from caesar.storage import get_connection
from caesar.storage import SampleFilter

conf = cfg.ConfigOpts()
conn = get_connection(conf, 'mongodb+mongodb://196.168.1.112:27017/test')
filter = SampleFilter(meter='river')
samples = conn.get_samples(filter,limit=1)
for sample in samples:
    for k, v in sample.as_dict().items():
        print("%s = %s") % (k,v)
