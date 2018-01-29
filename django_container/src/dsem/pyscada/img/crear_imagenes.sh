#! /bin/bash
# Scrip para randerizar las calles

if [ $# -lt 3 ]; then
    echo "Flatan parametros"
    echo "$0 mapa directorio_dest prefijo"
    exit -1
fi

MAPA=$1
PREFIJO=$2
DIRECTORIO_DESTINO=$3

if ! [ -f $MAPA ]; then
    echo "No existe $MAPA"
    exit -3
fi

if ! [ -d $DIRECTORIO_DESTINO ]; then

    echo "No existe el directorio destino $DIRECTORIO_DESTINO"
    exit -3
fi

echo $MAPA, $PREFIJO, $DIRECTORIO_DESTINO

for x in $(seq 20 11 92); do
    echo "Creando Imagen a $x DPI"
    inkscape -z -f $MAPA -e ${DIRECTORIO_DESTINO}/${PREFIJO}_$x.png -d $x -b FFFFFF
done
