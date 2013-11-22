# encoding: utf-8
from __future__ import print_function

import os

from fabric import colors
from fabric.api import (abort, cd, env, get, hide, lcd, local, prefix, run,
                        settings, sudo, task)
from fabric.context_managers import quiet
from fabric.contrib import files
from fabric.contrib.console import confirm
from fabsettings import HOSTS as HOST_SETTINGS
from fabutils.common import get_host_settings, prepeare_hosts
from fabutils.requirements import pip_freeze_to_file
from fabutils.supervisor import configure_gunicorn, hold, install_supervisor

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


def update_static_media():
    with cd(env.code_path):
        with prefix(env.venv_prefix):
            print(colors.green("Installing dependencies"))
            run('python manage.py collectstatic --noinput')


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
def update(host=''):
    """Updates deployment to upstream git version"""
    h = get_host_settings(host)
    with settings(**h):
        procs = ('gunicorn_production', 'poll_mara')
        with hold(procs):
            get_repo()
            install_dependencies()
            #update_static_media()


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

@task
def get_remote_dump(host='', backupfile='/tmp/backup.dmp'):
    h = get_host_settings(host)
    with settings(**h):
        print(colors.yellow("Getting remote database: {database}".format(**env.database)))
        cmd = 'pg_dump -Fc {database} -f {backupfile}'
        cmd = cmd.format(backupfile=backupfile, **env.database)
        sudo('su postgres -c "{}"'.format(cmd))
        get(backupfile, backupfile)
        run('rm -f %s' % backupfile)
    return backupfile

SQL_CREATE_USER = ("DROP ROLE IF EXISTS {user};"
                   "CREATE ROLE {user} LOGIN PASSWORD '{password}';")


@task
def copy_database(host=''):
    path = get_remote_dump(host=host)
    with settings(**get_host_settings(host)):
        if confirm(colors.red('Replace local database with dump?', True)):
            with hide('running', 'stdout'):
                print(colors.yellow("Droping and creating fresh database"))
                with settings(warn_only=True):
                    local('dropdb {database}'.format(**env.database))

                local('createdb {database}'.format(**env.database))
                print(colors.yellow("Creating user"))
                local(('psql -d {database} -c "'+SQL_CREATE_USER+'"').format(**env.database))
                print(colors.yellow("Restoring data", True))
                local('pg_restore -d {database} {path}'.format(path=path, **env.database))

