#!/bin/bash
echo "Cleaning old BibTeX files..."
rm -f bachelor.bbl bachelor.blg bachelor.aux
echo "Old files deleted. Now compile with: pdflatex → biber → pdflatex → pdflatex"


