#!/bin/bash

python -c "import experiment; experiment.parse_peer_logs()"

cp $TMPDIR/plots/*.plog ./

DATE=$(date -Iminutes | tr "+:" "-")
GPTITLE="Original WFQ (1S 2L same prio) $SWIFTBINARY" \
	gnuplot < plot1.gnuplot > $TMPDIR/plot1-$DATE.png
echo "Plot in: $TMPDIR/plot1-$DATE.png"
eog $TMPDIR/plot1-$DATE.png &

rm *.plog
