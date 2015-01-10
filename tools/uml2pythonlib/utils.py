import os


def npath(*args):
    x = os.path.join(*args)
    x = os.path.expanduser(x)
    x = os.path.realpath(x)
    x = os.path.normpath(x)
    x = os.path.abspath(x)
    return x

