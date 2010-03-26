#!/bin/bash
TARGET=informe_final.txt
FILES="$TARGET"
while inotifywait -e modify $FILES; do
    rst2pdf $TARGET
done

