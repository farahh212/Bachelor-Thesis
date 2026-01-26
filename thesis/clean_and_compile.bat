@echo off
echo ========================================
echo Cleaning old BibTeX files and compiling
echo ========================================
echo.

echo Step 1: Deleting old BibTeX files...
if exist bachelor.bbl del /Q bachelor.bbl
if exist bachelor.blg del /Q bachelor.blg
if exist bachelor.aux del /Q bachelor.aux
echo Old files deleted.
echo.

echo Step 2: First pdflatex pass...
pdflatex -interaction=nonstopmode bachelor.tex
if errorlevel 1 (
    echo ERROR: pdflatex failed!
    pause
    exit /b 1
)
echo.

echo Step 3: Running biber (NOT bibtex!)...
biber bachelor
if errorlevel 1 (
    echo.
    echo ERROR: biber failed!
    echo Make sure biber is installed.
    echo On Windows with MiKTeX: Install via MiKTeX Package Manager
    echo On Windows with TeX Live: Should be included
    echo.
    pause
    exit /b 1
)
echo.

echo Step 4: Second pdflatex pass...
pdflatex -interaction=nonstopmode bachelor.tex
echo.

echo Step 5: Third pdflatex pass (for cross-references)...
pdflatex -interaction=nonstopmode bachelor.tex
echo.

echo ========================================
echo Compilation complete!
echo Check bachelor.pdf for results.
echo ========================================
pause


