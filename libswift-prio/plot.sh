#!/bin/bash

cp $1/*.plog ./

gnuplot < plot1.gnuplot > plot1.png
xdg-open plot1.png

