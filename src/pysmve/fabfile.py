# encoding: utf-8
from __future__ import print_function
import os

from bunch import Bunch, bunchify
from fabric.api import abort, cd, env, local, run, settings, sudo, task, prefix
from fabric.context_managers import quiet
from fabric.contrib import files
from fabric.contrib.console import confirm
from fabric import colors
from fabsettings import HOSTS as HOST_SETTINGS
from fabutils.requirements import pip_freeze_to_file

DEV_REQUIEREMENTS_FILE = 'setup/requirements/develop.txt'
REQUIEREMENTS_FILE = 'setup/requirements/production.txt'

def build_hosts(config_dict):
    hosts = Bunch()
    for name, values in config_dict.items():
        if not values:
            continue
        h = bunchify(values)
        h.repo_path = os.path.join('/home', h.user, h.project_base, h.project_name)
        h.code_path = os.path.join(h.repo_path, h.code_subdir)
        h.host_string = '{user}@{remote_ip}:{port}'.format(**h)
        h.venv_prefix = ('source '
                        '/home/{user}/.virtualenvs/{virtualenv}/bin/activate'.format(**h))
        hosts[name] = h
    return hosts

HOSTS = build_hosts(HOST_SETTINGS)

def get_host_settings(host, hosts=HOSTS):
    if isinstance(host, str):
        if host not in hosts:
            abort('Incorrect or empty host. Possible hosts: ' + ','.join(hosts.keys()))
        return hosts[host]
    else:
        return hosts

@task
def freeze(host=''):
    with settings(**get_host_settings(host)):
        print("Dumping", colors.yellow(DEV_REQUIEREMENTS_FILE))
        pip_freeze_to_file(DEV_REQUIEREMENTS_FILE)
        print("Dumping", colors.green(REQUIEREMENTS_FILE))
        pip_freeze_to_file(REQUIEREMENTS_FILE, filter_dev_only=True)


@task
def docs():
    '''Muestra la documentación'''
    local('restview README.rst')


def clean_repo():
    with quiet():
        changes =  local("git status -s", capture=True)
    return not changes.strip()


def push_all():
    local('git push --all')
    local('git push --tags')

# @task
# def deploy_vm(host='virtualbox_coop', check_git='yes'):
#     h = HOSTS.get(host, {})
#     if check_git == 'yes':
#         if not clean_repo() and not confirm("Deploy leaving unstaged changes?"):
#             abort("Aborting at user request.")
#     with settings(**h):
#         push_all()
#         with cd(env.remote_location):
#             run('git pull origin master')
#             run('git pull origin master')
#             run('pwd')
#             run('git submodule update --init')


def create_virtualenv():
    if not files.exists('/home/{user}/.virtualenvs/{virtualenv}'.format(**env)):
        print("No existe el virtualenv %s" % colors.red(env['virtualenv']))
        run('source /usr/local/bin/virtualenvwrapper.sh && mkvirtualenv {virtualenv}'.format(**env))


def create_project_dir():
    """Project path will contain the repository"""
    if not files.exists(env.repo_path):
        run('mkdir -p {repo_path}'.format(**env))

def get_repo(branch='master'):
    with cd(env.repo_path):
        if not files.exists('.git'):
            run('git clone {repo_url} .'.format(**env))
        else:
            run('git checkout -- .')
            run('git pull origin {}', branch)

def install_dependencies():
    with cd(env.code_path):
        with prefix(env.venv_prefix):
            run('pip install -r setup/requirements/production.txt')


@task
def install(host=''):
    h = get_host_settings(host)
    with settings(**h):
        #run('ifconfig')
        create_virtualenv()
        create_project_dir()
        get_repo()
        install_dependencies()


