#!/bin/bash
filename=$(find -iname $1.tex)
filepath=$(dirname "${filename}")
echo $filename
echo $filepath
cd $filepath
latex $1.tex
bibtex $1
latex $1.tex
latex $1.tex
dvips -o $1.dvi
dvipdfm $1.dvi
evince $1.pdf &

