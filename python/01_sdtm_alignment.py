# ============================================================
# STEP 1: SDTM-ALIGNED DATA STRUCTURE
# Transform Diabetes 130-US into clinical-trial-like format
# This shows recruiters you understand CDISC SDTM domains
# ============================================================

import pandas as pd
import numpy as np
import os

os.makedirs('data/processed', exist_ok=True)

# ── LOAD RAW DATA ────────────────────────────────────────────
print("Loading Diabetes 130-US dataset...")
df = pd.read_csv('data/raw/diabetic_data.csv')
df.replace('?', np.nan, inplace=True)
print(f"  Loaded: {df.shape[0]:,} rows × {df.shape[1]} columns\n")

# ══════════════════════════════════════════════════════════════
# DM DOMAIN (Demographics) — One row per subject
# In a real trial, DM has: USUBJID, ARM, AGE, SEX, RACE
# ══════════════════════════════════════════════════════════════
print("=" * 60)
print("Creating DM domain (Demographics)...")
print("=" * 60)

dm_like = df.drop_duplicates('patient_nbr')[
    ['patient_nbr', 'race', 'gender', 'age']
].copy()

dm_like.rename(columns={
    'patient_nbr': 'USUBJID',
    'race':        'RACE',
    'gender':      'SEX',
    'age':         'AGEGR1'       # already grouped: [50-60) etc.
}, inplace=True)

dm_like['STUDYID'] = 'DIAB130US'
dm_like['DOMAIN']  = 'DM'
dm_like['ARM']     = 'Observational'   # not a randomized trial
dm_like['SAFFL']   = 'Y'              # all patients in safety population

# Make USUBJID a proper string ID
dm_like['USUBJID'] = 'DIAB-' + dm_like['USUBJID'].astype(str)

print(f"  ✓ DM domain: {dm_like.shape[0]:,} unique subjects")
print(f"  Columns: {list(dm_like.columns)}")
print(f"\n  Demographics breakdown:")
print(f"    Sex:  {dm_like['SEX'].value_counts().to_dict()}")
print(f"    Race: {dm_like['RACE'].value_counts().head(5).to_dict()}")
print(f"\n  Sample rows:")
print(dm_like.head(3).to_string(index=False))

# Save
dm_like.to_csv('data/processed/dm_clean.csv', index=False)
print(f"\n  ✓ Saved: data/processed/dm_clean.csv")

# ══════════════════════════════════════════════════════════════
# AE DOMAIN (Adverse Events) — One row per encounter/event
# In a real trial: USUBJID, AEDECOD, AESEV, AESER, AEBODSYS
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("Creating AE domain (Adverse Events)...")
print("=" * 60)

ae_like = df[['patient_nbr', 'diag_1', 'diag_2', 'diag_3',
              'number_diagnoses', 'time_in_hospital', 'readmitted']].copy()

ae_like.rename(columns={
    'patient_nbr':      'USUBJID',
    'diag_1':           'AEDECOD',     # primary diagnosis = AE term proxy
    'number_diagnoses': 'AECNT',       # comorbidity count
    'time_in_hospital': 'AEDUR'        # length of stay = AE duration proxy
}, inplace=True)

ae_like['USUBJID'] = 'DIAB-' + ae_like['USUBJID'].astype(str)
ae_like['STUDYID'] = 'DIAB130US'
ae_like['DOMAIN']  = 'AE'

# Severity flag (proxy: length of stay)
# LOS >= 7 days = SEVERE, 3-6 = MODERATE, < 3 = MILD
ae_like['AESEV'] = np.where(ae_like['AEDUR'] >= 7, 'SEVERE',
                   np.where(ae_like['AEDUR'] >= 3, 'MODERATE', 'MILD'))

# Serious AE flag (proxy: readmitted within 30 days = serious outcome)
ae_like['AESER'] = np.where(ae_like['readmitted'] == '<30', 'Y', 'N')

# Map ICD-9 diagnosis codes to body systems (simplified)
def map_icd9_to_bodysys(code):
    """Map ICD-9 code to SDTM-like Body System (AEBODSYS)"""
    try:
        code = str(code)
        if code.startswith('250'):
            return 'ENDOCRINE/METABOLIC'
        elif code.startswith(('390','391','392','393','394','395','396',
                              '397','398','399','40','41','42','43','44','45')):
            return 'CARDIOVASCULAR'
        elif code.startswith(('460','461','462','463','464','465','466',
                              '47','48','49','50','51','52')):
            return 'RESPIRATORY'
        elif code.startswith(('520','521','522','523','524','525','526',
                              '527','528','529','53','54','55','56','57','58')):
            return 'GASTROINTESTINAL'
        elif code.startswith(('580','581','582','583','584','585','586',
                              '587','588','589','59')):
            return 'RENAL/URINARY'
        elif code.startswith(('710','711','712','713','714','715','716',
                              '717','718','719','72','73')):
            return 'MUSCULOSKELETAL'
        elif code.startswith(('800','801','802','803','804','805','806',
                              '807','808','809','81','82','83','84','85',
                              '86','87','88','89','9')):
            return 'INJURY/POISONING'
        elif code.startswith('V'):
            return 'SUPPLEMENTARY'
        elif code.startswith('E'):
            return 'EXTERNAL CAUSES'
        else:
            return 'OTHER'
    except:
        return 'UNKNOWN'

ae_like['AEBODSYS'] = ae_like['AEDECOD'].apply(map_icd9_to_bodysys)

print(f"  ✓ AE domain: {ae_like.shape[0]:,} event records")
print(f"  Columns: {list(ae_like.columns)}")
print(f"\n  Severity breakdown:")
print(f"    {ae_like['AESEV'].value_counts().to_dict()}")
print(f"\n  Serious AE rate: {(ae_like['AESER']=='Y').mean():.1%}")
print(f"\n  Top Body Systems:")
print(ae_like['AEBODSYS'].value_counts().head(5).to_string())

# Save
ae_like.to_csv('data/processed/ae_clean.csv', index=False)
print(f"\n  ✓ Saved: data/processed/ae_clean.csv")

# ══════════════════════════════════════════════════════════════
# ADSL DOMAIN (Analysis Subject Level) — One row per subject
# This is the ADaM analysis-ready dataset
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("Creating ADSL domain (Analysis Subject Level)...")
print("=" * 60)

# Get one row per patient with key variables
adsl_cols = ['patient_nbr', 'race', 'gender', 'age', 'diabetesMed',
             'insulin', 'num_medications', 'number_diagnoses',
             'time_in_hospital', 'A1Cresult', 'readmitted']

adsl_like = df.drop_duplicates('patient_nbr')[adsl_cols].copy()

adsl_like.rename(columns={
    'patient_nbr':      'USUBJID',
    'race':             'RACE',
    'gender':           'SEX',
    'age':              'AGEGR1',
    'insulin':          'TRTA',        # treatment arm proxy
    'num_medications':  'NUMMED',
    'number_diagnoses': 'NUMDIAG',
    'time_in_hospital': 'LOS',
    'diabetesMed':      'DIABMEDFL'
}, inplace=True)

adsl_like['USUBJID'] = 'DIAB-' + adsl_like['USUBJID'].astype(str)
adsl_like['STUDYID'] = 'DIAB130US'
adsl_like['SAFFL']   = 'Y'

# Key outcome flag: readmitted within 30 days
adsl_like['READMFL'] = np.where(adsl_like['readmitted'] == '<30', 'Y', 'N')

# AE proxy flag: high comorbidity burden
adsl_like['AEFL'] = np.where(adsl_like['NUMDIAG'] > 5, 'Y', 'N')

# Drop the raw readmitted column (we now have READMFL)
adsl_like.drop(columns=['readmitted'], inplace=True)

print(f"  ✓ ADSL domain: {adsl_like.shape[0]:,} subjects")
print(f"  Columns: {list(adsl_like.columns)}")
print(f"\n  30-day readmission rate: {(adsl_like['READMFL']=='Y').mean():.1%}")
print(f"  High comorbidity (AE flag): {(adsl_like['AEFL']=='Y').mean():.1%}")
print(f"\n  Treatment (insulin) breakdown:")
print(f"    {adsl_like['TRTA'].value_counts().to_dict()}")

# Save
adsl_like.to_csv('data/processed/adsl_derived.csv', index=False)
print(f"\n  ✓ Saved: data/processed/adsl_derived.csv")

# ══════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("SDTM ALIGNMENT COMPLETE!")
print("=" * 60)
print(f"""
  Your processed datasets (data/processed/):
  ┌──────────────────┬─────────────┬──────────────────────────┐
  │ File             │ Rows        │ Purpose                  │
  ├──────────────────┼─────────────┼──────────────────────────┤
  │ dm_clean.csv     │ {dm_like.shape[0]:>9,}  │ Demographics (1/subject) │
  │ ae_clean.csv     │ {ae_like.shape[0]:>9,}  │ Adverse Events (1/event) │
  │ adsl_derived.csv │ {adsl_like.shape[0]:>9,}  │ Analysis dataset (ADaM)  │
  └──────────────────┴─────────────┴──────────────────────────┘

  SDTM domains created:
    • DM  — USUBJID, RACE, SEX, AGEGR1, ARM, SAFFL
    • AE  — USUBJID, AEDECOD, AESEV, AESER, AEBODSYS, AEDUR
    • ADSL — USUBJID, TRTA, READMFL, AEFL, NUMDIAG, LOS

  Next step: python3 python/02_eda_clinical.py
""")