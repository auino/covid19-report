#!/bin/bash
mkdir out 2> /dev/null
mkdir out/img 2> /dev/null
python3 prepare.py
cp report_template.tex out/report.tex
cd out
pdflatex report.tex
pdflatex report.tex
mv report.pdf ../report-latest.pdf
cd ..
rm -rf out/
