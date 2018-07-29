from oslo_config import cfg
from caesarlinsa.storage import get_connection
from caesarlinsa.storage import SampleFilter

conf = cfg.ConfigOpts()
conn = get_connection(conf,
                      'mongodb+mongodb://196.168.1.111:27017,'
                      '196.168.1.112:27017,'
                      '196.168.1.113:27017/test')
filter = SampleFilter(meter='caesarlinsa')
samples = conn.get_samples(filter,limit=1)
for sample in samples:
    for k, v in sample.as_dict().items():
        print("%s = %s") % (k,v)
