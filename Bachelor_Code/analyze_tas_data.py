"""Script to analyze TAS Schafer Excel data and compare with existing dataset structure."""
import pandas as pd
import sys
from pathlib import Path

# Path to the Excel file
excel_path = Path(__file__).parent.parent / "Shrink disc 3-part (1).xlsx"

try:
    # Read Excel - first row (index 0) contains headers
    df_raw = pd.read_excel(excel_path, header=None)
    
    # Extract headers from first row (index 0)
    headers = df_raw.iloc[0].tolist()
    # Clean headers
    headers = [str(h).strip() if pd.notna(h) else f"col_{i}" for i, h in enumerate(headers)]
    
    # Use data from row 1 onwards (skip header row)
    df_tas = df_raw.iloc[1:].copy()
    df_tas.columns = headers
    df_tas = df_tas.reset_index(drop=True)
    
    # Convert numeric columns
    numeric_cols = ['d (mm)', 'dw  (mm)', 'M max (Nm)', 'D (mm)', 'I (mm)', 'e (mm)', 
                    'H (mm)', 'A (mm)', 'd1 (mm)', 'MA (Nm)', 'Z (Stk.)', 'nmax (min-1)', 
                    'pN  (N/mm²)', 'I (kgm²)', 'Gewicht (kg)']
    for col in numeric_cols:
        if col in df_tas.columns:
            df_tas[col] = pd.to_numeric(df_tas[col], errors='coerce')
    
    print("=" * 80)
    print("TAS SCHAFER DATA ANALYSIS")
    print("=" * 80)
    print(f"\nShape: {df_tas.shape} (rows, columns)")
    print(f"\nColumns ({len(df_tas.columns)}):")
    for i, col in enumerate(df_tas.columns, 1):
        print(f"  {i}. {col}")
    
    print(f"\n\nData Types:")
    print(df_tas.dtypes)
    
    print(f"\n\nFirst 10 rows:")
    print(df_tas.head(10).to_string())
    
    print(f"\n\nMissing values per column:")
    missing = df_tas.isnull().sum()
    print(missing[missing > 0])
    
    print(f"\n\nSample statistics for numeric columns:")
    print(df_tas.describe())
    
    print(f"\n\nUnique values for categorical columns:")
    for col in df_tas.columns:
        if df_tas[col].dtype == 'object':
            unique_count = df_tas[col].nunique()
            print(f"\n{col}: {unique_count} unique values")
            if unique_count < 20:
                print(f"  Values: {df_tas[col].unique()}")
    
except Exception as e:
    print(f"Error reading Excel file: {e}")
    sys.exit(1)

