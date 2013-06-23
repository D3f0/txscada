#!/bin/bash

while true; do\
    inotifywait -r -e close_write *.rst
    landslide presentation.cfg
done
