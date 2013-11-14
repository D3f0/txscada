# encoding: utf-8
from __future__ import print_function
import os

from bunch import Bunch, bunchify
from fabric.api import abort, cd, env, local, run, settings, sudo, task, prefix, lcd, hide
from fabric.context_managers import quiet
from fabric.contrib import files
from fabric.contrib.console import confirm
from fabric import colors
from fabsettings import HOSTS as HOST_SETTINGS
from fabutils.requirements import pip_freeze_to_file
from fabutils.common import prepeare_hosts, get_host_settings
from fabutils.supervisor import install_supervisor, configure_gunicorn
from contextlib import nested

DEV_REQUIEREMENTS_FILE = 'setup/requirements/develop.txt'
REQUIEREMENTS_FILE = 'setup/requirements/production.txt'

prepeare_hosts(HOST_SETTINGS, local_base=os.path.dirname(__file__))

@task
def freeze(host='', commit=False):
    """Conjela los requerimientos del virtualenv"""
    with settings(**get_host_settings(host)):
        print("Dumping", colors.yellow(DEV_REQUIEREMENTS_FILE))
        pip_freeze_to_file(DEV_REQUIEREMENTS_FILE)
        print("Dumping", colors.green(REQUIEREMENTS_FILE))
        pip_freeze_to_file(REQUIEREMENTS_FILE, filter_dev_only=True)
        if commit:
            local('git add {} {}'.format(DEV_REQUIEREMENTS_FILE, REQUIEREMENTS_FILE))
            with settings(warn_only=True):
                result = local('git commit -m "Requirements update"', capture=True)
            if result.failed:
                abort("Git up to date.")
            else:
                local('git push origin master')



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
        print(colors.yellow("Creating virtualenv"), env.virtualenv)
        print("No existe el virtualenv %s" % colors.red(env['virtualenv']))
        run('source /usr/local/bin/virtualenvwrapper.sh && mkvirtualenv {virtualenv}'.format(**env))
    else:
        print(print(colors.green("Virtualenv exists"), env.virtualenv))
    with prefix(env.venv_prefix):
        run('{proxy_command} pip install -U pip'.format(**env))
    run('mkdir -p /home/{user}/.pip_download_cache'.format(**env))

def create_project_dir():
    """Project path will contain the repository"""
    if not files.exists(env.repo_path):
        run('mkdir -p {repo_path}'.format(**env))

def get_repo(branch='master'):
    with cd(env.repo_path):
        if not files.exists('.git'):
            print(colors.yellow("Cloning repo"), env.repo_url)
            run('{proxy_command} git clone {repo_url} .'.format(**env))
        else:
            print(colors.green("Pulling code"))
            run('git checkout -- .')
            run('{proxy_command} git pull origin {}'.format(branch, **env))

def create_app_dirs():
    with cd(env.repo_path):
        run('mkdir -p scripts logs')

def install_dependencies():
    with cd(env.code_path):
        with prefix(env.venv_prefix):
            print(colors.green("Installing dependencies"))
            run('{proxy_command} pip install -r setup/requirements/production.txt'.format(**env))

def install_system_packages(update=False):
    packages = 'build-essential python-dev libc6-dev'

    sudo('{proxy_command} apt-get update'.format(**env))
    sudo('{proxy_command} apt-get install {}'.format(packages, **env))

@task
def pip_list(host=''):
    with settings(**get_host_settings(host)):
        with prefix(env.venv_prefix):
            run('pip freeze')

@task
def pip_uninstall(host='', package=''):
    if not package:
        abort("Please provide a package to uninstall")
    with settings(**get_host_settings(host)):
        with prefix(env.venv_prefix):
            run('pip uninstall -y {}'.format(package))

@task
def install(host=''):
    """Instala SMVE en servidor"""
    h = get_host_settings(host)
    with settings(**h):
        create_virtualenv()
        create_project_dir()
        get_repo()
        create_app_dirs()
        install_system_packages()
        install_dependencies()
        install_supervisor()
        configure_gunicorn()


@task
def shell(host=''):
    """Abre shell remota en host"""
    from fabric.operations import open_shell
    h = get_host_settings(host)
    with settings(**h):
        open_shell()

@task
def extract_strings():
    from subprocess import call
    root = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(root, 'nguru')
    #venv_prefix = 'source ~/.virtualenvs/txscada/bin/activate'
    with lcd(path):
        local('python manage.py makemessages -a')
        with hide('stdout'):
            out = local('git status --porcelain | grep \.po', True)
            for line in out.strip().split('\n'):
                fname = line.strip().split()[-1]

                call(['xdg-open', '../'+fname])


