# ============================================================
# STEP 0: Download Diabetes Dataset + Verify ALL Data
# Run this ONCE to get everything set up
# ============================================================

import pandas as pd
import numpy as np
import os

# ── PART 1: Download Diabetes 130-US Dataset ─────────────────
print("=" * 60)
print("PART 1: Downloading Diabetes 130-US dataset...")
print("(This may take 30-60 seconds — be patient)")
print("=" * 60)

from ucimlrepo import fetch_ucirepo

dataset = fetch_ucirepo(id=296)
df = dataset.data.features.copy()
df['readmitted'] = dataset.data.targets.iloc[:, 0].values

# Save to data/raw/
os.makedirs('data/raw', exist_ok=True)
df.to_csv('data/raw/diabetic_data.csv', index=False)

print(f"\n  ✓ Downloaded: {df.shape[0]:,} rows × {df.shape[1]} columns")
print(f"  ✓ Saved to: data/raw/diabetic_data.csv")

# Quick look at the data
print(f"\n  First 3 rows:")
print(df.head(3).to_string())

# Check key columns
print(f"\n  ── KEY COLUMNS ──")
key_cols = ['patient_nbr', 'age', 'gender', 'race',
            'time_in_hospital', 'num_medications', 'number_diagnoses',
            'A1Cresult', 'insulin', 'diabetesMed', 'readmitted']

for col in key_cols:
    if col in df.columns:
        print(f"    ✓ {col}")
    else:
        print(f"    ✗ {col} — MISSING!")

# Readmission breakdown (your target variable)
print(f"\n  ── READMISSION BREAKDOWN ──")
print(df['readmitted'].value_counts().to_string())
readmit_30 = (df['readmitted'] == '<30').sum()
print(f"\n  30-day readmissions: {readmit_30:,} / {len(df):,} ({readmit_30/len(df):.1%})")

# ── PART 2: Verify CDISC .xpt Files ─────────────────────────
print("\n" + "=" * 60)
print("PART 2: Verifying CDISC Pilot .xpt files...")
print("=" * 60)

xpt_files = ['dm.xpt', 'ae.xpt', 'lb.xpt', 'vs.xpt', 'ex.xpt']
for f in xpt_files:
    path = os.path.join('data', 'raw', f)
    if os.path.exists(path):
        try:
            temp = pd.read_sas(path, format='xport', encoding='utf-8')
            print(f"  ✓ {f:10s} — {temp.shape[0]:,} rows × {temp.shape[1]} columns")
        except Exception as e:
            print(f"  ⚠ {f:10s} — file exists but error reading: {e}")
    else:
        print(f"  ✗ {f:10s} — NOT FOUND")

# ── PART 3: Quick peek at DM domain ─────────────────────────
print("\n" + "=" * 60)
print("PART 3: Quick look at DM (Demographics) domain")
print("=" * 60)

dm = pd.read_sas('data/raw/dm.xpt', format='xport', encoding='utf-8')
print(f"\n  Columns: {list(dm.columns)}")
print(f"\n  Treatment Arms:")
if 'ARM' in dm.columns:
    print(dm['ARM'].value_counts().to_string())
elif 'arm' in [c.lower() for c in dm.columns]:
    arm_col = [c for c in dm.columns if c.lower() == 'arm'][0]
    print(dm[arm_col].value_counts().to_string())

print("\n" + "=" * 60)
print("ALL DONE! Both datasets are ready.")
print("Your data/raw/ folder now has:")
print("  • diabetic_data.csv  (Dataset 2 — 101K rows)")
print("  • dm.xpt, ae.xpt, lb.xpt, etc.  (Dataset 1 — CDISC)")
print("=" * 60)