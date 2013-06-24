#!/bin/bash

while true; do\
    inotifywait -r -e close_write *.rst
    landslide presentation.cfg && notify-send "PDF Built" || notify-send "PDF built with errors"
done
