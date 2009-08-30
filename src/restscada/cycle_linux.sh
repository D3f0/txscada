#!/bin/bash
# Based on http://docs.python.org/library/optparse.html

# inotify must be installed

PID=0

function respawn() {
	if [ $PID -gt 0 ]; then
		echo "Reiniciando"
		kill -9 $PID
	fi
	python main.py &
	PID=$!		
}
function exit_requested () {
	echo "hola"
	
	
}

function kill_proc() {
	kill $PID
}

trap kill_proc SIGINT SIGTERM

# Lanzar por primera vez
respawn
echo "Lanzado con" $PID
while inotifywait  -r -e MODIFY *.py 2>/dev/null; do
	respawn
	
done



