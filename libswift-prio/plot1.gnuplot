set datafile separator " "
set terminal png size 1300,600
set title "Original WFQ (1S 2L same prio)"
set ylabel "Speed (B/s)"
set y2label "Progress (%)"
set xlabel "Time (s)"
set y2tics border
#set xdata time
set timefmt "%s"
set format x "%s"
set key right top
set grid
plot "./leecher1.plog" using 1:2 with lines lw 2 lt 3 axes x1y2 title '% L1', \
     "./leecher2.plog" using 1:2 with lines lw 2 lt 1 axes x1y2 title '% L2', \
     "./leecher1.plog" using 1:8 with lines lw 2 lt 2 axes x1y1 title 'dw spd L1', \
     "./leecher2.plog" using 1:8 with lines lw 2 lt 4 axes x1y1 title 'dw spd L2', \
     "./leecher1.plog" using 1:7 with lines lw 2 lt 6 axes x1y1 title 'up spd L1', \
     "./leecher2.plog" using 1:7 with lines lw 2 lt 7 axes x1y1 title 'up spd L2', \
     "./seeder.plog" using 1:7 with lines lw 2 lt 5 axes x1y1 title 'up spd SD'
