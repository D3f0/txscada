#! /bin/bash

#
#   Watch de archivos
#

function die(){
    echo "Error:" $1
    valor= $2 || 255
    exit $valor
}

if ! which inotifywatch > /dev/null; then
    die "Intente instalar inotify-tools"
fi
# Encontramos inotify watch

while inotifywait -r -e modify *.tex; do
    make
    echo
    echo "---------------------------------------------------------"
    echo "Construcción realizada el $(date)"
    echo "---------------------------------------------------------"
    echo

done


