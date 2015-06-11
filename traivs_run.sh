#!/bin/sh
# Break on first error
set -e

cd ./src/pysmve/nguru/
python manage.py migrate
python manage.py test
