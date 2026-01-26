@echo off
echo Cleaning old BibTeX files...
del /Q bachelor.bbl 2>nul
del /Q bachelor.blg 2>nul
del /Q bachelor.aux 2>nul
echo Old files deleted. Now compile with: pdflatex -^> biber -^> pdflatex -^> pdflatex
pause


