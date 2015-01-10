#!/usr/bin/env python
import os
import sys
import logging
import tempfile
import re

try:
    import subprocess
except ImportError:
    subprocess = None

PY3 = sys.version_info > ( 3, 0, 0 )

if PY3:
    unicode = str
    basestring = (str,)


def npath(*args):
    return os.path.normpath(os.path.abspath(os.path.expanduser(os.path.join(*args))))


def mkstemp(mode='wb'):
    fd, name = tempfile.mkstemp()
    os.close(fd)
    return open(name, mode)


class Xlog(object):
    def __init__(self):
        self.logger = None
    def __getattr__(self, name):
        if not self.logger:
            self.logger = logging.getLogger(__name__)
        return getattr( self.logger, name )
logger = Xlog()


class RunError(Exception):
    def __init__(self, cmd, returncode, out, err):
        self.cmd, self.returncode, self.out, self.err = cmd, returncode, out, err
        msg = []
        msg += [ 'failed to run (retcode %i): %s' %( self.returncode, ' '.join(cmd)), ]
        msg += [ 'stderr:', ]
        msg.extend([ ' '*3+ '.' + l for l in err.split('\n') ])
        msg += [ 'stdout:', ]
        msg.extend([ ' '*3+ '.' +l for l in out.split('\n') ])
        super(LaunchError, self).__init__( '\n'.join(msg) )


def run(cmd):
    out = mkstemp()
    err = mkstemp()
    oname = out.name
    ename = err.name
    try:
        if subprocess:
            p = subprocess.Popen(cmd, stdout=out, stderr=err)
            p.communicate()
            out.flush(); out.close()
            err.flush(); err.close()
            retcode = p.returncode
        else:
            command = []
            for c in cmd:
                if ' ' in c:
                    command.append( '"%s"' % c )
                else:
                    command.append( c )
            command = ' '.join(command)
            command += ' >"%s"' % oname
            command += ' 2>"%s"' % ename
            p = os.popen(command, 'w' )
            retcode = p.close()
            if retcode == None:
                retcode = 0
        if retcode != 0:
            raise RunError(cmd, p.returncode, 
                            open(oname, 'rb').read(), 
                            open(ename, 'rb').read())
    except:
        os.unlink(oname)
        os.unlink(ename)
        raise

    text = open(oname, 'rb').read()
    result = unicode(text, encoding=sys.getfilesystemencoding())
    os.unlink(oname)
    os.unlink(ename)
    return result


def sexists(filename, root=None):
    if root:
        filename = npath(root, filename)
    else:
        filename = npath('/', filename)
    if os.path.exists(filename):
        return filename
    else:
        return None


def scat(filename, root=None):
    if root:
        filename = npath(root, filename)
    else:
        filename = npath('/', filename)
    text = open(filename, 'rb').read()
    try:
        text = unicode(text, encoding=sys.getfilesystemencoding())
    except UnicodeDecodeError:
        text = unicode(text, encoding='utf-8')
    return text.split('\n')


def sscan(expr, filename, root=None):
    if isinstance(expr, basestring):
        expr = re.compile(expr)

    result = []
    for l in scat(filename, root):
        m = expr.search(l)
        if m:
            result.append(m.group('var'))
    return result      

def show_help( abort=None ):
    if abort:
        msg = "invalid command: %s" % abort
    else:
        msg = '''
ident3.py [options] 

options:

    -v|--verbose    display more message
    -d|--debug      tracing info

'''
    sys.stderr.write(msg)
    ret = 0
    if abort:
        ret = 1
    sys.exit(ret)


def parse_args(args):
    logging.basicConfig()
    logging.getLogger().setLevel(logging.WARNING)

    class Options(object): pass
    result = Options()
    result.args = []
    result.root = None
    result.noext = False
    i = 0
    while i < len(args):
        a = args[i]
        if a in [ '-h', '--help' ]:
            show_help()
            i += 1; continue
        if a in [ '-v', '--verbose' ]:
            logging.getLogger().setLevel(logging.INFO)
            i += 1; continue
        if a in [ '-d', '--debug' ]:
            logging.getLogger().setLevel(logging.DEBUG)
            i += 1; continue
        if a in [ '-R', '--root', ]:
            result.root = args[i+1]
            i += 2; continue
        if a in [ '-n', '-no-external' ]:
            result.noext = True
            i += 1; continue
        result.args.append(a)
        i += 1
    return result

class Detect(object):
    def __init__(self):
        self._mode = None
        self.value = None
    
    def _mode_get( self ):
        return self._mode
    def _mode_set( self, value ):
        if value in [ 'heuristic', 'runtime', 'fixed', None, ]:
            self._mode = value
        else:
            raise ValueError('invalid value for mode')
    mode = property(_mode_get, _mode_set)


def get_platform(root=None, noext=False):
    result = Detect()
    for n in [ 'etc/redhat-release',
               'etc/fedora-release',
               'etc/mandrake-release',
               'etc/centos-release',
               'etc/SuSE-release',
           ]:
        fullpath = npath('/', n)
        if root:
            fullpath = npath(root, n)
        if os.path.exists(fullpath):
            result.mode, result.value = 'heuristic', 'linux'
            logger.debug('platform detection using "%s"' % fullpath)
            for line in scat(fullpath):
                logger.debug('.%s' % line)

    if noext:
        return result

    logger.debug('using runtime detection')
    out = run([ 'uname', '-s']).strip().upper()
    if 'LINUNX' in out:
        result.mode, result.value = 'runtime', 'linux'
    elif 'OPENBSD' in out:
        result.mode, result.value = 'runtime', 'openbsd'
    elif 'FREEBSD' in out:
        result.mode, result.value = 'runtime', 'freebsd'
    elif 'DARWIN' in out:
        result.mode, result.value = 'runtime', 'darwin'
        
    return result
                

def get_distro(platform, root=None, noext=False):
    result = Detect()

    if platform == 'darwin':
        result.mode, result.value = 'fixed', 'macosx'
    elif platform == 'linux':
        relfiles = [ 
                     'etc/fedora-release',
                     'etc/redhat-release',
                     'etc/mandrake-release',
                     'etc/centos-release',
                     'etc/SuSE-release',
                   ]
        for relfile in relfiles:
            relfullpath = npath('/', relfile)
            if root:
                relfullpath = npath(root, relfile)
            if not os.path.exists(relfullpath):
                continue
            if relfullpath.endswith('SuSE-release' ):
                result.mode, result.value = 'heuristic', 'suse'
                tag = scat(relfullpath)[-1]
                if [ x for x in scat(relfullpath) if 'SUSE Linux Enterprise Server' in x ]:
                    result.mode, result.value = 'heuristic', 'sle'
                break
            if relfullpath.endswith('mandrake-release'):
                result.mode, result.value = 'heuristic', 'mandrake'
                break
            if relfullpath.endswith('fedora-release'):
                result.mode, result.value = 'heuristic', 'fedora'
                break
            if relfullpath.endswith('centos'):
                result.mode, result.value = 'heuristic', 'centos'
                break
            if relfullpath.endswith('redhat-release'):
                result.mode, result.value = 'heuristic', 'redhat'
                if [ x for x in scat(relfullpath) if 'Red Hat Enterprise Linux ' in x]:
                    result.mode, result.value = 'heuristic', 'rhel'
                elif [ x for x in scat(relfullpath) if 'CentOS release' in x]:
                    result.mode, result.value = 'heuristic', 'centos'
                break
            if relfullpath.endswith('slackware-release'):
                result.mode, result.value = 'heuristic', 'slackware'
                break
            if relfullpath.endswith('xandros-desktop-version'):
                result.mode, result.value = 'heuristic', 'xandros'
                break

    if noext:
        return result

    return result


def get_version(platform, distro, root=None, noext=False):
    result = Detect()

    if (platform, distro) == ( 'linux', 'suse', ):
        result.mode, result.value = ( 'heuristic',
            [ l.split()[1] for l in scat('etc/SuSE-release', root) if l.startswith('openSUSE') ][-1], )
    if (platform, distro) == ( 'linux', 'sle', ):
        result.mode, result.value = ( 'heuristic',
            [ l.split('=')[1].strip() for l in scat('etc/SuSE-release', root) if l.startswith('VERSION') ][-1], )
        pl = [ l.split('=')[1].strip() for l in scat('etc/SuSE-release', root) if l.startswith('PATCHLEVEL') ]
        if pl:
            result.value += '.' + pl[-1].strip()
    if (platform, distro) == ( 'linux', 'fedora', ):
        if sexists('etc/os-release', root):
            result.mode, result.value = ( 'heuristic',
                [ l.split('=')[1] for l in scat('etc/os-release', root) if l.startswith('VERSION_ID') ][-1], )
    if (platform, distro) == ( 'linux', 'centos', ):
        if sexists('etc/redhat-release', root):
            result.mode, result.value = ( 'heuristic',
                [ l.split()[2] for l in scat('etc/redhat-release', root) if 'CentOS release' in l ][-1], )
    if (platform, distro) == ( 'linux', 'rhel', ):
        if sexists('etc/redhat-release', root):
            values = sscan( r'Red Hat Enterprise Linux (ES release|Server|Server release) (?P<var>\d+([.]\d+)*)', 'etc/redhat-release', root)
            if values:
                result.mode, result.value = ( 'heuristic', values[-1], )


    if noext:
        return result

    if (platform, distro) == ( 'darwin', 'macosx', ):
        out = [ n for n in run([ 'sw_vers', ]).split('\n') if n.strip().startswith('ProductVersion:') ]
        if out:
            result.mode, result.value = 'runtime', out[0].split(':')[1].strip()

    return result
           

def get_arch(platform, distro, version, root=None, noext=False):
    result = Detect()

    if (platform, distro) == ( 'linux', 'suse', ):
        result.mode, result.value = ( 'heuristic',
            [ l.split('(')[1].strip() for l in scat('etc/SuSE-release', root) if l.startswith('openSUSE') ][-1], )
        if result.value == 'i586':
            result.value = 'i686'

    if noext:
        return result

    result.mode, result.value = 'runtime', run(['uname', '-m',]).strip()
    return result


def system_indentify(root='/', noext=False):
    platform = get_platform(root, noext).value
    distro = get_distro(platform, root, noext).value
    version = get_version(platform, distro, root, noext).value
    arch = get_arch(platform, distro, version, root, noext).value
    fmt = "%(platform)s-%(distro)s-%(version)s-%(arch)s"
    return (fmt % {'platform' : platform, 'distro' : distro, 'version' : version, 'arch' :arch, })


def main(args):
    options = parse_args(args)
    logger.debug('using python "%s"' % (str(sys.version_info)))
    logger.debug('filesystem encoding "%s"' % (str(sys.getfilesystemencoding())))
    
    result = get_platform(options.root, options.noext)
    logger.info('detected platform "%s" using %s' % (result.value, result.mode) )
    platform = result.value

    result = get_distro(platform, options.root, options.noext)
    logger.info('detected distro "%s" using %s' % (result.value, result.mode) )
    distro = result.value

    result = get_version(platform, distro, options.root, options.noext)
    logger.info('detected version "%s" using %s' % (result.value, result.mode) )
    version = result.value

    result = get_arch(platform, distro, version, options.root, options.noext)
    logger.info('detected arch "%s" using %s' % (result.value, result.mode) )
    arch = result.value

    if hasattr(str, 'format'):
        fmt = "{platform}-{distro}-{version}-{arch}"
        print(fmt.format(platform=platform, distro=distro, version=version, arch=arch))
    else:
        fmt = "%(platform)s-%(distro)s-%(version)s-%(arch)s"
        print(fmt % {'platform' : platform, 'distro' : distro, 'version' : version, 'arch' :arch, })

    
if __name__ == "__main__":
    main(sys.argv[1:])
