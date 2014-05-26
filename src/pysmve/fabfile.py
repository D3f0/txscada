# encoding: utf-8
from __future__ import print_function

import os

from fabric import colors
from fabric.api import (abort, cd, env, get, hide, lcd, local, prefix, run,
                        settings, sudo, task, prompt)
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
            local('git add {} {}'.format(
                DEV_REQUIEREMENTS_FILE, REQUIEREMENTS_FILE))
            with settings(warn_only=True):
                result = local(
                    'git commit -m "Requirements update"', capture=True)
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
        changes = local("git status -s", capture=True)
    return not changes.strip()


def push_all():
    local('git push --all')
    local('git push --tags')


def create_virtualenv():
    if not files.exists('/home/{user}/.virtualenvs/{virtualenv}'.format(**env)):
        print(colors.yellow("Creating virtualenv"), env.virtualenv)
        print("No existe el virtualenv %s" % colors.red(env['virtualenv']))
        run(('source /usr/local/bin/virtualenvwrapper.sh '
             '&& mkvirtualenv {virtualenv}').format(**env))
    else:
        print(print(colors.green("Virtualenv exists"), env.virtualenv))
    with prefix(env.venv_prefix):
        run('{proxy_command} pip install -U pip'.format(**env))
    run('mkdir -p /home/{user}/.pip_download_cache'.format(**env))


def create_project_dir():
    """Project path will contain the repository"""
    if not files.exists(env.repo_path):
        run('mkdir -p {repo_path}'.format(**env))


def get_repo(tag=''):
    with cd(env.repo_path):
        if not files.exists('.git'):
            print(colors.yellow("Cloning repo"), env.repo_url)
            run('{proxy_command} git clone {repo_url} .'.format(**env))
        else:
            print(colors.green("Pulling code"))
            run('git checkout -- .')
            run('{proxy_command} git fetch -t'.format(**env))
            run('git checkout {}'.format(tag, **env))


def create_app_dirs():
    with cd(env.repo_path):
        run('mkdir -p scripts logs')


def install_dependencies():
    with cd(env.code_path):
        with prefix(env.venv_prefix):
            print(colors.green("Installing dependencies"))
            run('{proxy_command} pip install -r '
                'setup/requirements/production.txt'.format(**env))


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


def update_permissions():
    with cd(env.code_path):
        with prefix(env.venv_prefix):
            run('python manage.py update_permissions')


def syncdb():
    with cd(env.code_path):
        with prefix(env.venv_prefix):
            run('python manage.py syncdb')


def migrate(app=''):
    with cd(env.code_path):
        with prefix(env.venv_prefix):
            run('python manage.py migrate %s' % app)


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


def get_tags():
    '''Get local tags'''
    tags = local('git tag -l', True)
    tags = tags.split()
    return tags


def _validate_tag(tag):
    tag = tag.strip()
    if tag:
        available_tags = get_tags()
        if tag in available_tags:
            raise ValueError('This tag is already given')
        return tag
    else:
        raise ValueError('Should be a non empty text')


@task
def tag():
    '''Tag code'''
    print('Last release tag is:')
    with hide('running'):
        local('git describe --tags `git rev-list --tags --max-count=1`')

    print('Insert release tag number to create.\n'
          'Format: X.Y.Z, (sometimes just X.Y).\n'
          'If deploying a new iteration, change the Y value.\n'
          'If re-deploying with minor changes on same iteration, increment the Z value.')
    new_tag = prompt('Number: ', validate=_validate_tag)

    if confirm('Will create and push tag %s. Are you sure to continue?' % new_tag):
        pass


def get_release(release):
    with cd(env.repo_path):
        run('{proxy_command} git fetch origin --tags')
        run('git checkout {}'.format(release))
        run('git checout -- .')  # Reset repo

@task
def update(host='', release=''):
    """Updates deployment to upstream git version"""

    h = get_host_settings(host)

    available_tags = get_tags()
    if release:
        if release not in available_tags:
            abort(("Release {} is not a valid tag (Latest tags were: {})."
                  " Run fab tag first").format(
                        colors.red(release, True),
                        colors.green('; '.join(available_tags[-3:]))
                    )
            )
    else:
        if confirm('Create tag from current code?'):
            release = tag()


    local('git push --tags')
    local('git push origin master')
    # update local repo (needed?)
    local('git fetch')
    with settings(**h):
        procs = ('poll_mara')
        with hold(procs):
            get_repo()
            install_dependencies()
            syncdb()
            migrate()
            update_static_media()
            update_permissions()
        # Gunicorn refuses to restart, so killing it will force supervisor to restart it
        run('pkill -KILL gunicorn')


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

                call(['xdg-open', '../' + fname])

SMVE_DEFAULT_BACKUP_PATH = '/tmp/smve_backup.dmp'


@task
def get_remote_dump(host='', backupfile=SMVE_DEFAULT_BACKUP_PATH):
    h = get_host_settings(host)
    with settings(**h):
        print(
            colors.yellow("Getting remote database: {database}".format(
                          **env.database))
        )
        cmd = 'pg_dump -Fc {database} -f {backupfile}'
        cmd = cmd.format(backupfile=backupfile, **env.database)
        sudo('su postgres -c "{}"'.format(cmd))
        with hide('warnings'):
            get(backupfile, backupfile)
        run('rm -f %s' % backupfile)
    return backupfile

SQL_CREATE_USER = ("DROP ROLE IF EXISTS {user};"
                   "CREATE ROLE {user} LOGIN PASSWORD '{password}';")


@task
def restore_database(path=SMVE_DEFAULT_BACKUP_PATH, dbsettings=None, no_confirm=False):
    if not os.path.isfile(path):
        abort("Path not given or invalid file. Please indicate a path: %s" % path)
    with hide('running', 'stdout'):
        print(colors.yellow("Droping and creating fresh database"))
        with settings(warn_only=True):

            local('dropdb {database}'.format(**dbsettings))

        local('createdb {database}'.format(**dbsettings))
        print(colors.yellow("Creating user"))

        cmd = ('psql -d {database} -c "' + SQL_CREATE_USER + '"').format(**dbsettings)
        local(cmd)
        print(colors.yellow("Restoring data", True))
        local('pg_restore -d {database} {path}'.format(path=path, **dbsettings))
        print("Running migrations")
        local('python manage.py migrate')

@task
def copy_database(host='', no_confirm=False):
    path = get_remote_dump(host=host)
    with settings(**get_host_settings(host)):
        msg = colors.red('Replace local database ''with dump?')
        if no_confirm or confirm(msg):
            restore_database(path=path, dbsettings=env.database, no_confirm=no_confirm)


def extract_path_from_stdout(path):
    path = path.strip().replace('\'', '').replace('"', '')
    if not path.endswith('/'):
        path = '%s/' % path
    return path


@task
def get_remote_media(host='', no_confirm=False):
    """Gets remote media"""
    media_cmd = 'python manage.py diffsettings | grep MEDIA_ROOT | cut -d = -f 2'
    with settings(**get_host_settings(host)):
        if no_confirm or confirm(colors.red('Replace local media with dump?', True)):
            with cd(os.path.join(env.repo_path, 'src/pysmve/nguru')):
                with hide():
                    local_media_root = extract_path_from_stdout(
                        local(media_cmd, True))

                    local_media_root = os.path.abspath(
                        os.path.join(local_media_root, '..'))
                    with prefix(env.venv_prefix):
                        remote_meida_root = extract_path_from_stdout(
                            run(media_cmd, True))

                print(remote_meida_root, '=>', local_media_root)
                with hide('warnings'):
                    get(remote_meida_root, local_media_root)


@task
def local_media():
    print()


@task
def get_remote_all(host='', no_confirm=False):
    get_host_settings(host)  # Check
    if no_confirm or confirm(colors.red('Replace local data with remote?')):
        copy_database(host=host, no_confirm=no_confirm)
        get_remote_media(host=host, no_confirm=no_confirm)


@task
def install_sentry(host=''):
    with settings(**get_host_settings(host)):
        run("ls")
