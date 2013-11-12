# encoding: utf-8
import os
from bunch import Bunch, bunchify
from fabric.api import env, abort
from contextlib import contextmanager
from fabric.contrib import files

def prepeare_hosts(config_dict, local_base):
    """Prepare env global variable"""
    hosts = Bunch()
    for name, values in config_dict.items():
        if not values:
            continue
        h = bunchify(values)
        h.repo_path = os.path.join('/home', h.user, h.project_base, h.project_name)
        h.code_path = os.path.join(h.repo_path, h.code_subdir)
        h.host_string = '{user}@{remote_ip}:{port}'.format(**h)
        # Virtualenv
        h.venv_dir = '/home/{user}/.virtualenvs/{virtualenv}'.format(**h)
        h.venv_prefix = ('export  export PIP_DOWNLOAD_CACHE=~/.pip_download_cache;'
                         'source '
                         '{venv_dir}/bin/activate'.format(**h))
        # Proxy
        proxy = env.get('proxy', None)
        if proxy:
            h.proxy_settings = 'export http_proxy=%s export https_proxy=%s'
        else:
            h.proxy_settings = ''
        h.local_base = os.path.abspath(local_base)
        hosts[name] = h

    env._hosts = hosts


def get_host_settings(host, hosts=None):
    if hosts is None:
        try:
            hosts = env._hosts
        except KeyError:
            abort("fabfile error, prepeare_hosts(CONFIG) not called!")
    if isinstance(host, str):
        if host not in hosts:
            abort('Incorrect or empty host. Possible hosts: ' + ','.join(hosts.keys()))
        return hosts[host]
    else:
        return hosts

@contextmanager
def temporary_configuration(path, line):
    files.append(path, line, use_sudo=True)
    yield
    files.comment(path, line)