
#!/bin/sh
# stress.sh <module> <N>

RUNS=$2
K=0

clear
while [ $K -lt $RUNS ]
  do
  K=$(($K+1))
  echo "RUN $K OF $RUNS..."
  date '+%s' |xargs -i trial --reporter=text --random {} test.$1
done
