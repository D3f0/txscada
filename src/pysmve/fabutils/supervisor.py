# encoding: utf-8
from __future__ import print_function

import os

from fabric import colors
from fabric.api import env, put, sudo, abort, settings, run, hide
from fabric.contrib import files
from contextlib import contextmanager
from fabric import colors

supervisor_configs_dir = '/etc/supervisor/'


def install_supervisor(reinstall=False):
    sudo('pip install supervisor')
    # the apt supervisor package wouldn't need all this manual configs,
    # but we need to do this because we are using the pypi one.
    # we need the pypi one to have the stopasgroup setting :/
    if reinstall:
        uninstall_supervisord()

    logs_dir = '/var/log/supervisor/'
    config = '/etc/supervisord.conf'
    init_script = '/etc/init.d/supervisord'

    if files.exists(init_script):
        print(colors.green("Supervior script already exists"))
    else:

        sudo('mkdir -p ' + supervisor_configs_dir)
        sudo('mkdir -p ' + logs_dir)

        # TODO: Change to files.upload_template()
        put(os.path.join('setup', 'supervisor', 'supervisord.conf'),
            config,
            use_sudo=True)

        for path in (supervisor_configs_dir, logs_dir, config):
            sudo('chown root:root %s -R' % path)

        for path in (supervisor_configs_dir, logs_dir):
            sudo('chmod 755 %s -R' % path)

        sudo('chmod 644 ' + config)

        # add supervisord to the sistem start
        put(os.path.join('setup', 'supervisor', 'initd_supervisord'),
            init_script,
            use_sudo=True)

        sudo('chmod 755 ' + init_script)

        sudo('update-rc.d supervisord defaults')

    sudo(init_script + ' start')

def uninstall_supervisord():
    """Removes supervisord"""
    logs_dir = '/var/log/supervisor/'
    config_file = '/etc/supervisord.conf'
    init_script = '/etc/init.d/supervisord'
    print(colors.red("Uninstall supervisord"))
    with settings(warn_only=True):
        sudo(init_script + ' stop')
    sudo('rm -rf {} {} {}'.format(init_script, logs_dir, config_file))


def configure_gunicorn():
    # create the shell script
    name = env.django_project
    # constants
    django_dir = os.path.join(env.code_path, env.django_project)
    if not files.exists(os.path.join(django_dir, 'manage.py')):
        abort("%s does not have a manage.py file" % django_dir)

    script_dir = os.path.join(env.repo_path, 'scripts')
    script_dest = os.path.join(script_dir, 'gunicorn.sh')
    logs_dir = os.path.join(env.repo_path, 'logs')

    gunicorn_sh_context = dict(
        django_dir=django_dir,
        virtualenv=env.virtualenv,
        logs_dir=logs_dir,
        user=env.user,
        gunicorn_port=env.gunicorn_port,
        gunicorn_workers=env.gunicorn_workers
    )

    files.upload_template(
        filename='gunicorn.sh.template',
        template_dir='setup/supervisor/scripts',
        destination=script_dest,
        context=gunicorn_sh_context,
        mode=0755,
        backup=False,
        use_jinja=True
    )

    # add to supervisor
    gunicorn_conf_template = os.path.join(env.local_base,
                            'setup',
                            'supervisor',
                            'configs',
                            'gunicorn.conf.template')

    gunicorn_conf_context = dict(
        script_name=script_dest,
        name=env.name,
        django_dir=django_dir,
        scripts_dir=script_dir,
        logs_dir=logs_dir,
        user=env.user
    )

    config_name = 'guincorn_%s' % name
    add_supervisord_task(template=gunicorn_conf_template,
                         name=config_name, context=gunicorn_conf_context)




def add_supervisord_task(template, name, context, do_reload=True):
    """Adds a deamon/task to supervisor"""
    destination='/etc/supervisor/{}.conf'.format(name)
    template_dir, filename = os.path.split(template)
    files.upload_template(filename=filename,
                          template_dir=template_dir,
                          destination=destination,
                          context=context,
                          use_sudo=True,
                          mode=0600,
                          use_jinja=True)
    if do_reload:
        reload_supervisor()



def reload_supervisor():
    sudo('supervisorctl reload -y')

@contextmanager
def hold(names, use_sudo=True):
    """Stops and starts process after context manaer has stopped"""
    if use_sudo:
        op = sudo
    else:
        op = run

    if isinstance(names, basestring):
        names = [names]

    name = ' '.join(names)
    print(colors.red("Stopping supervisor services:"), names)
    with hide('stdout', 'stderr'):
        op('supervisorctl stop {}'.format(name))

    yield

    print(colors.green("Starting supervisor services:"), names)
    with hide('stdout', 'stderr'):
        op('supervisorctl start {}'.format(name))