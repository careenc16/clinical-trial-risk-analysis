# ============================================================
# Quick fix: Re-download with patient IDs included
# The UCI library separates IDs from features — we need both
# ============================================================

import pandas as pd
from ucimlrepo import fetch_ucirepo

print("Re-downloading with patient IDs included...")
dataset = fetch_ucirepo(id=296)

# Combine features + IDs + target into one dataframe
df = dataset.data.features.copy()
df['readmitted'] = dataset.data.targets.iloc[:, 0].values

# Add the ID columns (encounter_id and patient_nbr)
for col in dataset.data.ids.columns:
    df[col] = dataset.data.ids[col].values

print(f"Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
print(f"\npatient_nbr column: {'✓ FOUND' if 'patient_nbr' in df.columns else '✗ MISSING'}")
print(f"Unique patients: {df['patient_nbr'].nunique():,}")
print(f"Total encounters: {len(df):,}")

# Overwrite the old file
df.to_csv('data/raw/diabetic_data.csv', index=False)
print(f"\n✓ Saved to data/raw/diabetic_data.csv (now with patient_nbr)")