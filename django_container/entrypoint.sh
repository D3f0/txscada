#!/bin/bash
set -e
cmd="$@"

if [ "${ENV:prod}" == "dev" ]; then
    if [ "${NO_INSTALL}" != "1" ]; then
        echo "Installing development requirements:"
        pip install --user -r /setup/packages/dev.txt \
            --no-index \
            --find-links /setup/packages/
        echo "Finished installing dev packages"
    else
        echo "Skipping installing development packages because of NO_INSTALL=1"
    fi
    export PYTHONPATH=${PYTHONPATH}:${HOME}/.local/lib/python2.7/site-packages/
    export PATH=${PATH}:${HOME}/.local/bin
fi

exec $cmd
