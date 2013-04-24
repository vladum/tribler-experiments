set datafile separator " "
set terminal png size 1300,600
set title "WFQ with high priority second leecher"
set ylabel "Speed (B/s)"
set y2label "Progress (B)"
set xlabel "Time (s)"
set y2tics border
#set xdata time
set timefmt "%s"
set format x "%s"
set key right top
set grid
plot "./leecher1.plog" using 1:2 with lines lw 2 lt 3 axes x1y2 title 'pr leecher 1', \
     "./leecher2.plog" using 1:2 with lines lw 2 lt 1 axes x1y2 title 'pr leecher 2', \
     "./leecher1.plog" using 1:4 with lines lw 2 lt 2 axes x1y1 title 'dw leecher 1', \
     "./leecher2.plog" using 1:4 with lines lw 2 lt 4 axes x1y1 title 'dw leecher 2', \
     "./leecher1.plog" using 1:3 with lines lw 2 lt 6 axes x1y1 title 'up leecher 1', \
     "./leecher2.plog" using 1:3 with lines lw 2 lt 7 axes x1y1 title 'up leecher 2'
#     "./seeder.plog" using 1:3 with lines lw 2 lt 5 axes x1y1 title 'up seeder'
