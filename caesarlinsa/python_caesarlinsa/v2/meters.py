
from caesarlinsa.python_caesarlinsa.util import args

@args('-m', '--meter', metavar='<METER>', help="help for find sample with meter_name")
@args('-l', '--limit', metavar='<NUMBER>', help='help for find samples number')
def do_sample_list(args):
    print("meter:%s limit:%s" %(args.meter, args.limit))

