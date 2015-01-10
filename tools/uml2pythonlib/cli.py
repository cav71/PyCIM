import os
import argparse
import logging

import utils
import ext.ident3


logger = logging.getLogger(__name__)


def pathtype(text):
    return utils.npath(text)


def parse_args(args, mainfile, packages_list=None):
    common_parser = argparse.ArgumentParser(add_help=False)
    g = common_parser.add_mutually_exclusive_group()
    g.add_argument('-v', '--verbose', dest="loglevel", action='store_const', const=logging.DEBUG)
    g.add_argument('-q', '--quiet', dest="loglevel", action='store_const', const=logging.WARN)
    common_parser.add_argument('--log', dest='logfile', default=None, help='logging to file')

    common_parser.add_argument('--prefix', type=pathtype, help='destination prefix', default=utils.npath('exe'))
    common_parser.add_argument('--scriptsdir', type=pathtype, help='scripts dir', default=utils.npath('scripts'))
    common_parser.add_argument('--downloads', type=pathtype, help='download cache', default=utils.npath('downloads'))
    common_parser.add_argument('--buildroot', type=pathtype, help='build root dir', default=utils.npath('build'))
    common_parser.add_argument('--build', help='build host tag', default=ext.ident3.system_indentify())
    common_parser.add_argument('--target', help='build target tag', default=ext.ident3.system_indentify())


    class MyFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter): pass
    parser = argparse.ArgumentParser(parents=[common_parser,], formatter_class=MyFormatter) 

    subparsers = parser.add_subparsers(help='sub-command help')
    
    def add(name, module, help):
        p = subparsers.add_parser(name, help=help, parents=[common_parser,], formatter_class=MyFormatter)
        if hasattr(module, 'cli_options'):
            module.cli_options(p)
        p.set_defaults(func=module.main)   

    import main.generate
    add('generate', main.generate, 'generates all classes')

    options = parser.parse_args(args)
    options.error = parser.error
    options.basedir = utils.npath(mainfile, '..')

    # set the log format and level
    logging.basicConfig()
    logging.getLogger().setLevel(options.loglevel and options.loglevel or logging.INFO) 
    class LFormatter(logging.Formatter):
        def __init__(self):
            fmt = '%(levelshort)s %(threadName)s:%(name)s:%(lineno)d:%(message)s'
            logging.Formatter.__init__(self, fmt)
        def format(self, record):
            record.levelshort = { 'CRITICAL': 'C',
                                  'ERROR'   : 'E', 
                                  'WARNING' : 'W',
                                  'WARN'    : 'W',
                                  'INFO'    : 'I', 
                                  'DEBUG'   : 'D', }.get(record.levelname, record.levelname)
            return logging.Formatter.format(self, record)
    logging.getLogger().handlers[0].formatter = LFormatter()

    if packages_list:
        import uml2pythonlib.ext
        uml2pythonlib.ext.setup(packages_list)
    return options
