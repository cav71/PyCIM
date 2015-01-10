#!/usr/bin/env python
__version__ = '0.0.1'
import os, sys


try:
    import libs.cli
except ImportError:
    _ = os.path.abspath(__file__)
    _ = os.path.realpath(_)
    _ = os.path.dirname(_)
    sys.path.insert(0, _)
    import uml2pythonlib.cli


if __name__ == '__main__':
    options = uml2pythonlib.cli.parse_args(sys.argv[1:], __file__)
    ret = options.func(options)
    sys.exit(int(ret) if ret else 0)




