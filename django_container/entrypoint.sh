#!/bin/bash
set -e
cmd="$@"

if [ "${ENV:prod}" == "dev" ]; then
    if [ -z "${NO_INSTALL}" ]; then
        echo "Installing development requirements in $(hostname):"
        pip install --user -r /pip_download/dev/dev.txt \
            --no-index \
            --find-links /pip_download/dev/
        echo "Finished installing dev packages"
    else
        echo "Skipping installing development packages because of NO_INSTALL=1"
    fi
    
    # Done in docker-compose
    # export PYTHONPATH=${PYTHONPATH}:${HOME}/.local/lib/python2.7/site-packages/
    # export PATH=${PATH}:${HOME}/.local/bin
fi

if [ -z "${NO_MIGRATE}" ]; then
    python manage.py syncdb --migrate --noinput
fi

if [ -z "${NO_STATIC}" ]; then
    python manage.py collectstatic --noinput
fi

if [ -z "${NO_UPDATEPERMISSIONS}" ]; then
    python manage.py update_permissions
fi

exec $cmd
