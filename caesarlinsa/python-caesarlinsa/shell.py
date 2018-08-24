import sys
import argparse


class shellmain(object):

    def get_base_parse(self):
        parser = argparse.ArgumentParser(
            prog='caesarlinsa',
            description='',
            epilog='see caesarlinsa command for help',
            add_help=False
        )

        parser.add_argument('-v','--version',
                            action='version',
                            version='0.1'
                            )
        parser.add_argument('-h','--help',
                            help="command caesarlisa for help")

        return parser

    def import_modules(self, path):
        __import__(path)
        modules = sys.modules(path)
        return modules

    def get_subcommand_parser(self):
        parser = self.get_base_parse()
        subparser= parser.add_subparsers(metavar='<command>')
        sub_modules = self.import_modules('python-caesarlinsa.v2.meter')
        for fn_name in (func for func in dir(sub_modules) if func.startswith('do_')):
            command = fn_name[3:].replace('_','-')
            callback = getattr(sub_modules,fn_name)
            desc=callback.__doc__ or ''
            help=desc.strip()[0]
            arguments = getattr(callback,'arguments',[])
            subparser_s = subparser.add_parser(
                                             command,
                                             description=desc,
                                             add_help=False
                                            )
            for (args,kwargs) in arguments:
                subparser_s.add_argument(*args, **kwargs)
            subparser_s.set_default(func=callback)
        return parser

    def parse_args(self,argv):
        parser = self.get_base_parse()
        (option,args) = parser.parse_known_args(argv)
        subcommand_parser= self.get_subcommand_parser()
        return subcommand_parser.parse_args(argv)

    def main(self,argv):
        parse = self.parse_args(argv)
        parse.func(argv)


def main(argv=None):
    if argv:
        argv = sys.argv[1:]

    shell = shellmain()
    shell.main(argv)