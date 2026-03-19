import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
import os

warnings.filterwarnings('ignore')

plt.rcParams['figure.dpi'] = 150
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False

os.makedirs('outputs', exist_ok=True)

# ── LOAD DATA ─────────────────────────────────────────────────
dm   = pd.read_csv('data/processed/dm_clean.csv')
ae   = pd.read_csv('data/processed/ae_clean.csv', dtype={'AESER': str})
adsl = pd.read_csv('data/processed/adsl_derived.csv')

# Convert Y/N flags to numeric immediately after loading
adsl['READMFL_N'] = (adsl['READMFL'] == 'Y').astype(int)
adsl['AEFL_N']    = (adsl['AEFL']    == 'Y').astype(int)

print("="*55)
print("CLINICAL EDA — DATASET OVERVIEW")
print("="*55)
print(f"DM  (Demographics): {dm.shape[0]:,} subjects")
print(f"AE  (Adverse Events): {ae.shape[0]:,} events")
print(f"ADSL (Analysis):    {adsl.shape[0]:,} subjects")

# ── SECTION 1: DEMOGRAPHICS ───────────────────────────────────
print("\n" + "="*55)
print("SECTION 1: DEMOGRAPHICS — TABLE 14.1")
print("="*55)

print("\nAge Group (AGEGR1):")
print(dm['AGEGR1'].value_counts().sort_index())

print("\nSex (SEX):")
print(dm['SEX'].value_counts())

print("\nRace (RACE):")
print(dm['RACE'].value_counts())

# ── SECTION 2: ADVERSE EVENTS ─────────────────────────────────
print("\n" + "="*55)
print("SECTION 2: ADVERSE EVENT ANALYSIS")
print("="*55)

print("\nAE Severity (AESEV):")
print(ae['AESEV'].value_counts())

print("\nAE Body System (AEBODSYS):")
print(ae['AEBODSYS'].value_counts().head(8))

sae_count = (ae['AESER'] == 'Y').sum()
sae_rate  = (ae['AESER'] == 'Y').mean()
print(f"\nSerious AEs (AESER = Y):")
print(f"  Total SAEs: {sae_count:,} ({sae_rate:.1%} of all AEs)")

print("\nTop 10 Primary Diagnoses (AEDECOD):")
print(ae['AEDECOD'].value_counts().head(10))

# ── SECTION 3: OUTCOME ANALYSIS ───────────────────────────────
print("\n" + "="*55)
print("SECTION 3: OUTCOME ANALYSIS — READMISSION")
print("="*55)

overall_rate = adsl['READMFL_N'].mean()
print(f"\nOverall 30-day readmission rate: {overall_rate:.1%}")

print("\nReadmission by Age Group:")
age_r = adsl.groupby('AGEGR1')['READMFL_N'].agg(['mean','count'])
age_r.columns = ['Rate','N']
age_r['Rate'] = (age_r['Rate']*100).round(1)
print(age_r.sort_values('Rate', ascending=False).to_string())

print("\nReadmission by Treatment (TRTA):")
trta_r = adsl.groupby('TRTA')['READMFL_N'].agg(['mean','count'])
trta_r.columns = ['Rate','N']
trta_r['Rate'] = (trta_r['Rate']*100).round(1)
print(trta_r.sort_values('Rate', ascending=False).to_string())

print("\nReadmission by AE Flag (AEFL):")
ae_r = adsl.groupby('AEFL')['READMFL_N'].agg(['mean','count'])
ae_r.columns = ['Rate','N']
ae_r['Rate'] = (ae_r['Rate']*100).round(1)
print(ae_r.to_string())

print("\nReadmission by Diabetes Medication (DIABMEDFL):")
med_r = adsl.groupby('DIABMEDFL')['READMFL_N'].agg(['mean','count'])
med_r.columns = ['Rate','N']
med_r['Rate'] = (med_r['Rate']*100).round(1)
print(med_r.to_string())

# ── SECTION 4: VISUALIZATIONS ─────────────────────────────────
print("\n" + "="*55)
print("SECTION 4: GENERATING PLOTS")
print("="*55)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Readmission by Age Group
age_plot = adsl.groupby('AGEGR1')['READMFL_N'].mean()*100
age_plot = age_plot.sort_index()
axes[0,0].bar(range(len(age_plot)), age_plot.values,
              color='#42A5F5', edgecolor='black', linewidth=0.5)
axes[0,0].set_xticks(range(len(age_plot)))
axes[0,0].set_xticklabels(age_plot.index, rotation=45, ha='right', fontsize=8)
axes[0,0].axhline(overall_rate*100, color='red', linestyle='--',
                  alpha=0.7, label=f'Overall {overall_rate:.1%}')
axes[0,0].set_ylabel("30-Day Readmission Rate (%)")
axes[0,0].set_title("Readmission by Age Group", fontweight='bold')
axes[0,0].legend(fontsize=8)

# Plot 2: AE Severity
sev = ae['AESEV'].value_counts()
colors_sev = {'MILD':'#43A047','MODERATE':'#FB8C00','SEVERE':'#E53935'}
bar_colors = [colors_sev.get(s, '#90A4AE') for s in sev.index]
axes[0,1].bar(sev.index, sev.values,
              color=bar_colors, edgecolor='black', linewidth=0.5)
axes[0,1].set_ylabel("Number of Events")
axes[0,1].set_title("AE Severity Distribution", fontweight='bold')
for i, v in enumerate(sev.values):
    axes[0,1].text(i, v+200, f'{v:,}', ha='center', fontsize=9)

# Plot 3: Readmission by Treatment
trta_plot = adsl.groupby('TRTA')['READMFL_N'].mean()*100
trta_plot = trta_plot.sort_values(ascending=False)
axes[1,0].barh(range(len(trta_plot)), trta_plot.values,
               color='#AB47BC', edgecolor='black', linewidth=0.5)
axes[1,0].set_yticks(range(len(trta_plot)))
axes[1,0].set_yticklabels(trta_plot.index, fontsize=9)
axes[1,0].set_xlabel("30-Day Readmission Rate (%)")
axes[1,0].set_title("Readmission by Treatment (TRTA)", fontweight='bold')
axes[1,0].axvline(overall_rate*100, color='red', linestyle='--', alpha=0.7)
axes[1,0].invert_yaxis()

# Plot 4: AE Body System
soc = ae['AEBODSYS'].value_counts().head(8)
axes[1,1].barh(range(len(soc)), soc.values,
               color='#5C6BC0', edgecolor='black', linewidth=0.5)
axes[1,1].set_yticks(range(len(soc)))
axes[1,1].set_yticklabels([s[:30] for s in soc.index], fontsize=8)
axes[1,1].set_xlabel("Number of Events")
axes[1,1].set_title("AE by Body System (SOC)", fontweight='bold')
axes[1,1].invert_yaxis()

plt.suptitle("Clinical EDA — Safety & Outcome Overview",
             fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig('outputs/fig1_clinical_eda.png', bbox_inches='tight')
plt.show()
print("✅ Saved: outputs/fig1_clinical_eda.png")

# ── SECTION 5: KEY FINDINGS ───────────────────────────────────
print("\n" + "="*55)
print("SECTION 5: KEY FINDINGS SUMMARY")
print("="*55)
print(f"""
1. POPULATION:  {dm.shape[0]:,} unique patients
2. AE RECORDS:  {ae.shape[0]:,} total adverse event records
   - SAEs:      {sae_count:,} ({sae_rate:.1%})
   - Top SOC:   {ae['AEBODSYS'].value_counts().index[0]}
3. OUTCOME:     {overall_rate:.1%} overall 30-day readmission rate
4. AGE RISK:    Older patients show higher readmission rates
5. TREATMENT:   Different insulin regimens show different risk profiles
""")
print("✅ EDA complete. Next: python3 python/03_risk_stratification.py")