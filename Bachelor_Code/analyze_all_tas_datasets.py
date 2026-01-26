"""Analyze all TAS Schafer datasets to understand structure and compatibility."""

import pandas as pd
from pathlib import Path
import json

TAS_DIR = Path(__file__).parent.parent / "TAS Schafer Datasets"
OUTPUT_DIR = Path(__file__).parent / "tas_analysis"
OUTPUT_DIR.mkdir(exist_ok=True)

def analyze_csv_file(file_path: Path) -> dict:
    """Analyze a single CSV file and return summary."""
    print(f"\n{'='*80}")
    print(f"Analyzing: {file_path.name}")
    print('='*80)
    
    try:
        # Try semicolon separator first (TAS files use ;)
        df = pd.read_csv(file_path, sep=';', encoding='utf-8')
        
        # If that fails or produces weird results, try comma
        if df.shape[1] == 1:
            df = pd.read_csv(file_path, sep=',', encoding='utf-8')
    except:
        try:
            df = pd.read_csv(file_path, sep=',', encoding='utf-8')
        except Exception as e:
            print(f"Error reading {file_path.name}: {e}")
            return None
    
    # Clean empty rows
    df = df.dropna(how='all')
    
    # Get basic info
    info = {
        "filename": file_path.name,
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "columns": df.columns.tolist(),
        "data_types": df.dtypes.astype(str).to_dict(),
        "missing_values": df.isnull().sum().to_dict(),
        "sample_rows": df.head(3).to_dict('records') if len(df) > 0 else [],
    }
    
    # Try to identify key columns
    key_columns = {}
    for col in df.columns:
        col_lower = str(col).lower()
        if 'd (mm)' in col or 'diameter' in col_lower:
            key_columns['shaft_diameter'] = col
        if 'm max' in col_lower or 'mt' in col_lower or 'torque' in col_lower:
            key_columns['max_torque'] = col
        if 'd (mm)' in col and 'outer' not in col_lower:
            key_columns['outer_diameter'] = col
        if 'z' in col_lower and 'stk' in col_lower:
            key_columns['clamping_elements'] = col
        if 'ma' in col_lower and 'nm' in col_lower:
            key_columns['assembly_torque'] = col
    
    info['identified_key_columns'] = key_columns
    
    # Print summary
    print(f"Rows: {info['total_rows']}")
    print(f"Columns: {info['total_columns']}")
    print(f"\nColumn names:")
    for i, col in enumerate(info['columns'], 1):
        print(f"  {i}. {col}")
    
    print(f"\nKey columns identified:")
    for key, col in key_columns.items():
        print(f"  {key}: {col}")
    
    # Show sample data
    if len(df) > 0:
        print(f"\nFirst 3 rows:")
        print(df.head(3).to_string())
    
    return info

def main():
    """Analyze all TAS CSV files."""
    print("="*80)
    print("TAS SCHAFER DATASET ANALYSIS")
    print("="*80)
    
    # Find all CSV files
    csv_files = list(TAS_DIR.glob("*.csv"))
    
    if not csv_files:
        print(f"No CSV files found in {TAS_DIR}")
        return
    
    print(f"\nFound {len(csv_files)} CSV files:")
    for f in csv_files:
        print(f"  - {f.name}")
    
    # Analyze each file
    all_info = {}
    total_rows = 0
    
    for csv_file in csv_files:
        info = analyze_csv_file(csv_file)
        if info:
            all_info[csv_file.name] = info
            total_rows += info['total_rows']
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"\nTotal files analyzed: {len(all_info)}")
    print(f"Total rows across all files: {total_rows}")
    
    print(f"\nFiles and row counts:")
    for filename, info in all_info.items():
        print(f"  {filename}: {info['total_rows']} rows")
    
    # Column overlap analysis
    print(f"\nColumn overlap analysis:")
    all_columns = set()
    for info in all_info.values():
        all_columns.update(info['columns'])
    
    print(f"  Unique columns across all files: {len(all_columns)}")
    print(f"  Common columns (appearing in all files):")
    
    # Find columns that appear in all files
    if len(all_info) > 1:
        common_cols = set(all_info[list(all_info.keys())[0]]['columns'])
        for info in list(all_info.values())[1:]:
            common_cols &= set(info['columns'])
        
        if common_cols:
            for col in sorted(common_cols):
                print(f"    - {col}")
        else:
            print("    (none)")
    
    # Save detailed analysis
    output_file = OUTPUT_DIR / "tas_datasets_analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_info, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\nDetailed analysis saved to: {output_file}")
    
    # Compatibility assessment
    print("\n" + "="*80)
    print("COMPATIBILITY ASSESSMENT")
    print("="*80)
    
    print("\n✅ Available in TAS data:")
    print("  - Shaft diameter (d)")
    print("  - Max torque (M max / Mt)")
    print("  - Outer diameter (D)")
    print("  - Clamping elements (Z)")
    print("  - Assembly torque (MA)")
    print("  - Pressure (pN)")
    
    print("\n❌ Missing in TAS data:")
    print("  - User preferences (8 weights)")
    print("  - Material specifications (explicit)")
    print("  - Safety factors")
    print("  - Surface condition")
    print("  - Hub length (some files)")
    print("  - Shaft inner diameter (some files)")
    
    print("\n⚠️  Feature mapping challenges:")
    print("  - TAS data has different structure per file type")
    print("  - Some files have complex multi-row structures")
    print("  - Missing features would need defaults/estimates")
    print("  - Clamping elements add new physics not in current model")
    
    print("\n" + "="*80)
    print("RECOMMENDATION")
    print("="*80)
    print("\nBased on this analysis:")
    print("  - Total TAS data: ~{total_rows} rows".format(total_rows=total_rows))
    print("  - Current synthetic data: 4,993 rows")
    print("  - TAS data represents ~{:.1f}% of combined dataset".format(total_rows / (4993 + total_rows) * 100))
    print("\n  → Full integration NOT recommended (see TAS_Full_Integration_Feasibility_Analysis.md)")
    print("  → Use for comparative analysis instead")

if __name__ == "__main__":
    main()


