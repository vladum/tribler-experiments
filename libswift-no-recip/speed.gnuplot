H=400.00
W=1000.00

#set terminal pngcairo color enhanced font "arial,10" fontscale 1.0 rounded size W,H
set terminal svg fname 'Helvetica' fsize 9 rounded size W,H
set output plotsdir . "/speed.svg"

set linetype  1 lc rgb "dark-violet" lw 1
set linetype  2 lc rgb "#009e73" lw 1
set linetype  3 lc rgb "#56b4e9" lw 1
set linetype  4 lc rgb "#e69f00" lw 1
set linetype  5 lc rgb "#f0e442" lw 1
set linetype  6 lc rgb "#0072b2" lw 1
set linetype  7 lc rgb "#e51e10" lw 1
set linetype  8 lc rgb "black"   lw 1
set linetype  9 lc rgb "gray50"  lw 1
set linetype cycle  9

set tmargin 0
set bmargin 0
set lmargin 10
set rmargin 12

set datafile separator " "

set palette maxcolors 6
set palette defined (\
    0 '#A8DA16', \
    10 '#AB1181', \
    20  '#E69B17', \
    30  '#1A5396', \
    40  '#D71900', \
    50  '#000000')
set cbtics ("keep alive" 0, "ping pong" 1, "slow start" 2, "aimd" 3, "ledbat" 4, "close" 5)
set colorbox user vertical origin graph 0.9,1.2 size screen 12.0/W, screen 80.0/H
set cbrange [-0.5:5.5]
set zrange [0:5]
set boxwidth 1 relative
set style fill solid 1 noborder

set multiplot title "Transfer Statistics"

set size 1,(290.0/H)
set origin 0.0,((40.0+30.0)/H)

set ylabel "Speed (MiB/s)"
set y2label "Hints (B)"
#set logscale y2
set datafile separator " "
set key left bottom
set grid
set ytics offset 0,0.3
set y2tics

unset xtics

stats logdir . "/seeder/speed.parsed" using 2
set xr [STATS_min - 10:STATS_max + 10]

pindex(p) = strstrt(peers, p)

plot logdir . "/seeder/speed.parsed" using 2:($4/1024/1024) with lines axes x1y1 title 'upload speed (seeder)', \
	 logdir . "/seeder/speed.parsed" using 2:5 with lines axes x1y2 title 'hints in (seeder)', \
     for [p in peers] logdir. "/" . p . "/speed.parsed" using 2:($21/1024/1024) with lines axes x1y1 title "dwload speed (". p . ")", \
     for [p in peers] logdir. "/" . p . "/speed.parsed" using 2:23 with lines axes x1y2 title "hints out (" . p . ")"

unset title
unset ylabel
unset logscale
unset key
unset y2label
unset y2tics
unset ytics

set yrange [0:words(peers)+1]

set size 1,(30.0/H)
set origin 0,(40.0/H)

set ytics ("leecher2" 0.5, "leecher1" 1.5, "seeder" 2.5)


set timefmt "%d"
set format x "%s"
set xlabel "Time in experiment (s)"

plot logdir . "/seeder/speed.parsed" using 2:(words(peers)+1):6 with boxes lc palette title 'send control (seeder)', \
     for [p = 1:words(peers)] logdir . "/" . word(peers,p) . "/speed.parsed" using 2:(words(peers)-p+1):24 with boxes lc palette title "send control (" . word(peers,p) . ")"

unset multiplot

