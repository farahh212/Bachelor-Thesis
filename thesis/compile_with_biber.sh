#!/bin/bash
echo "Compiling thesis with biblatex/biber..."
echo ""
echo "Step 1: First pdflatex pass..."
pdflatex bachelor.tex || exit 1

echo ""
echo "Step 2: Running biber..."
biber bachelor || exit 1

echo ""
echo "Step 3: Second pdflatex pass..."
pdflatex bachelor.tex

echo ""
echo "Step 4: Third pdflatex pass (for cross-references)..."
pdflatex bachelor.tex

echo ""
echo "Compilation complete! Check bachelor.pdf"


