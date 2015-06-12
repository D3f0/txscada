#!/bin/sh
# This script is porinted by script option in .travis.yml. This should be run on travis
# on every commit to master branch.
# Based on https://gist.github.com/ndarville/3625246
# Break on first error
set -e

cd ./src/pysmve/nguru/
python manage.py syncdb --migrate --noinput
python manage.py migrate --noinput
py.test
