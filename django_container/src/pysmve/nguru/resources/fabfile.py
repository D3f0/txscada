import os
from fabric.api import local
from glob import glob


def _pngext(filename):
    """Replace extension with png"""
    base = os.path.splitext(filename)[0]
    return '%s.png' % base


def _is_outdated(source, dest):
    """Returns True if source is newer than dest or if dest does not exist"""
    if not os.path.exists(dest):
        return False
    return os.path.getmtime(source) > os.path.getmtime(dest)


def _inkscape(source, dest):
    local('inkscape -z -f {source} -e {dest}'.format(**locals()))


def build_svg():
    to_convert = [(fname, _pngext(fname)) for fname in glob('*.svg')]
    for source, dest in to_convert:
        if _is_outdated(source, dest):
            _inkscape(source, dest)
