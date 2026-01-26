# Fix Bibliography Issues

## Problem
- Citations not showing
- References section not appearing
- Error: `bachelor.bbl` not created by biblatex

## Solution: Clean and Recompile with Biber

### Step 1: Delete Old BibTeX Files

Delete these files in the `thesis/` directory:
- `bachelor.bbl` (old BibTeX file)
- `bachelor.blg` (old BibTeX log)
- `bachelor.aux` (will be regenerated)

**On Windows (PowerShell):**
```powershell
cd thesis
Remove-Item bachelor.bbl, bachelor.blg, bachelor.aux -ErrorAction SilentlyContinue
```

**On Mac/Linux:**
```bash
cd thesis
rm -f bachelor.bbl bachelor.blg bachelor.aux
```

### Step 2: Compile with Biber (NOT BibTeX)

**Correct compilation sequence:**

```bash
cd thesis

# Step 1: First pdflatex pass
pdflatex bachelor.tex

# Step 2: Run biber (NOT bibtex!)
biber bachelor

# Step 3: Second pdflatex pass
pdflatex bachelor.tex

# Step 4: Third pdflatex pass (for cross-references)
pdflatex bachelor.tex
```

### Step 3: Using Your LaTeX Editor

**TeXstudio:**
1. Options → Configure TeXstudio → Build
2. Set **Default Bibliography** to **biber** (not BibTeX)
3. Build → Clean Auxiliary Files
4. Build → Build & View (F5)

**TeXworks:**
1. Edit → Preferences → Typesetting
2. Add new processing tool:
   - Name: `Biber`
   - Program: `biber`
   - Arguments: `$basename`
3. Use processing sequence: pdfLaTeX → Biber → pdfLaTeX → pdfLaTeX

**Overleaf:**
1. Menu → Compiler → **pdfLaTeX**
2. Menu → Bibliography → **biber** (NOT BibTeX)
3. Click "Recompile" multiple times

**VS Code with LaTeX Workshop:**
Add to `settings.json`:
```json
{
  "latex-workshop.latex.recipes": [
    {
      "name": "pdflatex → biber → pdflatex × 2",
      "tools": ["pdflatex", "biber", "pdflatex", "pdflatex"]
    }
  ],
  "latex-workshop.latex.tools": [
    {
      "name": "biber",
      "command": "biber",
      "args": ["%DOCFILE%"]
    }
  ]
}
```

### Step 4: Verify It Worked

After compilation, check:
- ✅ `bachelor.bbl` exists (created by biber)
- ✅ `bachelor.bcf` exists (biber control file)
- ✅ Citations show as numbers: [1], [2], [3]
- ✅ References section appears at end
- ✅ DOIs are visible in references

### Step 5: If Still Not Working

**Check references.bib location:**
- Should be in `thesis/references.bib`
- Verify `\addbibresource{references.bib}` in `bachelor.tex` matches the filename

**Check for BibTeX commands:**
- Make sure there's NO `\bibliographystyle` or `\bibliography` commands
- Should only have `\printbibliography`

**Verify biber is installed:**
```bash
biber --version
```

If not installed:
- **Windows (MiKTeX)**: MiKTeX Package Manager → Install `biber`
- **Windows (TeX Live)**: Should be included
- **macOS**: `brew install biber` or included with MacTeX
- **Linux**: `sudo apt-get install biber`

## Quick Fix Script

**Windows (PowerShell):**
```powershell
cd thesis
Remove-Item bachelor.bbl, bachelor.blg, bachelor.aux -ErrorAction SilentlyContinue
pdflatex bachelor.tex
biber bachelor
pdflatex bachelor.tex
pdflatex bachelor.tex
```

**Mac/Linux:**
```bash
cd thesis
rm -f bachelor.bbl bachelor.blg bachelor.aux
pdflatex bachelor.tex
biber bachelor
pdflatex bachelor.tex
pdflatex bachelor.tex
```

---

**Remember**: Always use **biber**, never **bibtex**!


