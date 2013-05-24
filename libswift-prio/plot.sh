#!/bin/bash

python -c "import experiment; experiment.parse_peer_logs()"

cp $1/*.plog ./

DATE=$(date -Iminutes | tr "+:" "-")
gnuplot < plot1.gnuplot > plot1-$DATE.png
echo "plot1-$DATE.png"
eog plot1-$DATE.png

rm *.plog
