@echo off
echo Compiling thesis with biblatex/biber...
echo.
echo Step 1: First pdflatex pass...
pdflatex bachelor.tex
if errorlevel 1 (
    echo ERROR: pdflatex failed!
    pause
    exit /b 1
)

echo.
echo Step 2: Running biber...
biber bachelor
if errorlevel 1 (
    echo ERROR: biber failed! Make sure biber is installed.
    pause
    exit /b 1
)

echo.
echo Step 3: Second pdflatex pass...
pdflatex bachelor.tex

echo.
echo Step 4: Third pdflatex pass (for cross-references)...
pdflatex bachelor.tex

echo.
echo Compilation complete! Check bachelor.pdf
pause


