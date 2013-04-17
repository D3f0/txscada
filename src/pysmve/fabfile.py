# encoding: utf-8
from fabric.api import env, task, settings, run, local, cd
from fabric.context_managers import quiet
from fabric.contrib.console import confirm
from os.path import join, dirname
from bunch import bunchify, Bunch

FAB_PATH = dirname(__file__)
DEV_REQUIEREMENTS_FILE = join(FAB_PATH, 'requirements/develop.txt')
_HOSTS = {
    'virtualbox_coop': {
        'remote_ip': '192.168.56.101',
        'port': 22,
        'user': 'ubuntu',
        'password': 'ubuntu',
        'virtualenv': 'txscada',
        'project_base': 'src',
        'project_name': 'txscada'
    },
    # 'demo': {
    # }
}

def build_hosts(config_dict):
    hosts = Bunch()
    for name, values in config_dict.items():
        h = bunchify(values)
        h.remote_location = join('/home', h.user, h.project_base, h.project_name)
        h.host_string = '{user}@{remote_ip}:{port}'.format(**h)
        h.venv_prefix = '/home/{user}/.virtualenv/{virtualenv}/bin/activate'.format(**h)
        hosts[name] = h
    return hosts

HOSTS = build_hosts(_HOSTS)


@task
def freeze():
    '''Freezar los requerimientos del virtualenv'''
    with open(DEV_REQUIEREMENTS_FILE, 'wb') as f:
        reqs = local('pip freeze', True)
        f.write(reqs)
    print "Requirements written to %s" % DEV_REQUIEREMENTS_FILE


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

@task
def deploy_vm(host='virtualbox_coop', check_git='yes'):
    h = HOSTS.get(host, {})
    if check_git == 'yes':
        if not clean_repo() and not confirm("Deploy leaving unstaged changes?"):
            abort("Aborting at user request.")
    with settings(**h):
        push_all()
        with cd(env.remote_location):
            run('git pull origin master')
            run('git pull origin master')
            run('pwd')
            run('git submodule update --init')

