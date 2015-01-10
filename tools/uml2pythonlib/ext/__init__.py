import os
import sys
import platform
import logging

import ident3

logger = logging.getLogger(__name__)


def npath(*args):
    x = os.path.join(*args)
    x = os.path.expanduser(x)
    x = os.path.realpath(x)
    x = os.path.normpath(x)
    x = os.path.abspath(x)
    return x


def rpartition(text, sep):
    if not sep in text:
        return ('', '', text,)
    i = text.rindex(sep)
    return (text[:i], sep, text[i+1:],) 


def setup(modulelist=None, systemtag=None):
    if not modulelist:
        return None

    systemtag = systemtag and systemtag or ident3.system_indentify()
    if not systemtag:
        raise RuntimeError( 'undetected system' )
    logger.debug("systemtag set to '%s'" % systemtag)

    for mname in modulelist:
        data = mname.split('-')
        name, _, version = rpartition(mname, '-')
        name = name and name or mname
        pathname = None
        for subdir in [ '', systemtag, ]:
            pathname = ident3.npath(__file__, '..', subdir, mname)
            if os.path.exists(pathname):
                break
            pathname = None

        if not pathname:
            logger.warning('no dir found for %s' % mname)
            continue

        sys.path.insert(0, pathname)
        try:
            m = __import__(name)
        except ImportError:
            del sys.path[0]
            logger.warning('failed import %s from %s' % (mname, pathname)) 
            continue

        logger.debug('imported %s from %s' % ( 
            mname, m and m.__file__ or None ) )

