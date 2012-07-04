#!/bin/bash
# Based on http://docs.python.org/library/optparse.html

# inotify must be installed

PID=0
ACTION="python test_server.py"

echo $(ACTION)

function launch {
	if [ $PID -gt 0 ]; then
		echo "Reiniciando"
		kill -9 $PID
	fi
	$ACTION&
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
launch
echo "Lanzado con" $PID
while inotifywait  -r -e MODIFY *.py 2>/dev/null; do
	launch
	
done



