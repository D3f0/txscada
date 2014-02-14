#!/bin/bash


if [ $# -gt 1 ]; then
    echo "Este comando solo acepta un argumento (el archivo cfg de landslide)"
    exit
fi

LANDSLIDE_CFG=$1


if [ $# -eq 1 ]; then
    if [ ! -f $LANDSLIDE_CFG ]; then
        echo "$LANDSLIDE_CFG no existe"
        exit
    fi
    CMD="landslide $LANDSLIDE_CFG"
else
    CMD="landslide presentacion.cfg"
fi


function check_installed {
    which $1 >/dev/null
    status=$?
    if [ $status -ne 0 ]; then
        echo "Could not execute $1. Please install it first!"
        exit 1
    fi
}

check_installed inotifywait

DESTINATION=`grep "destination" $LANDSLIDE_CFG | cut -d = -f 2 | sed 's/\s//'`
echo "BUILDING: $DESTINATION"
$CMD
xdg-open $DESTINATION

echo "Autobuiding doc on RST changes"
while true
    do
    inotifywait -r -e modify -e move -e create -e delete *.md *.css *.js
    {
        echo "Generating HTML..."
        $CMD
        notify-send "Se compilo el HTML"
    }
done
