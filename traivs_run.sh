#!/bin/sh

set -e

cd ./src/pysmve/nguru/
python manage.py migrate
python manage.py test
