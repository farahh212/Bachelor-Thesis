#!/bin/bash
echo "========================================"
echo "Cleaning old BibTeX files and compiling"
echo "========================================"
echo ""

echo "Step 1: Deleting old BibTeX files..."
rm -f bachelor.bbl bachelor.blg bachelor.aux
echo "Old files deleted."
echo ""

echo "Step 2: First pdflatex pass..."
pdflatex -interaction=nonstopmode bachelor.tex || exit 1
echo ""

echo "Step 3: Running biber (NOT bibtex!)..."
biber bachelor || {
    echo ""
    echo "ERROR: biber failed!"
    echo "Make sure biber is installed."
    echo "On macOS: brew install biber"
    echo "On Linux: sudo apt-get install biber"
    echo ""
    exit 1
}
echo ""

echo "Step 4: Second pdflatex pass..."
pdflatex -interaction=nonstopmode bachelor.tex
echo ""

echo "Step 5: Third pdflatex pass (for cross-references)..."
pdflatex -interaction=nonstopmode bachelor.tex
echo ""

echo "========================================"
echo "Compilation complete!"
echo "Check bachelor.pdf for results."
echo "========================================"


