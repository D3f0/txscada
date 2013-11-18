# -*- coding: utf-8 -*-
from __future__ import print_function
import re
from functools import partial
from fabric.api import local, env

is_git = partial(re.match, r'\-e git\+')
is_hg = partial(re.match, r'\-e hg\+')

# qtreactor.git@82ec1802f04fbe54527884a55dafc859cd997c49
git_line = re.compile(r'(?P<name>[\d\w\-\_]+)\.git@(?P<version>[\d\w]+)')
# django-tastypie-jqgrid@fe7aa6a246f902f50c45d585473b83449be081db
hg_line = re.compile(r'(?P<name>[\d\w\-\_]+)@(?P<version>[\d\w]+)')


class CommentLine(Exception):
    pass

class NotValidReqLine(Exception):
    pass


def split_package_version(line):
    """Returns package name and version from pip freeze line as tuple"""

    if not line or line.startswith('#'):
        raise CommentLine(line)
    elif '==' in line or '>=' in line or '<=' in line:
        return line.split('==')
    elif is_git(line):
        data = git_line.search(line)
        return data.group('name'), data.group('version')
    elif is_hg(line):
        data = hg_line.search(line)
        if not data:
            raise NotValidReqLine("pip freeze line not understood hg line: %s" % line)
        return data.group('name'), data.group('version')
    else:
        raise NotValidReqLine("pip freeze line not understood: %s" % line)


def is_excluded(line_of_pip_freeze):
    """Given a line of pip freeze checks if package name is included in env dev only pkgs
    """
    try:
        package, version = split_package_version(line_of_pip_freeze)
    except NotValidReqLine as e:
        print(e)
        return True
    excluded = env.dev_only_packages.split('\n')
    if excluded.count(package):
        return True
    return False


def pip_freeze_to_file(destination, filter_dev_only=False):
    '''Freezar los requerimientos del virtualenv'''

    reqs = local('pip freeze', True)
    with open(destination, 'wb') as f:
        for package in reqs.split('\n'):
            try:
                if filter_dev_only and is_excluded(package):
                    continue
                f.write('{}\n'.format(package))
            except CommentLine as e:
                pass


