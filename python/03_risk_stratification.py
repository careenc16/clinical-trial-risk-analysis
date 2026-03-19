import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
import os
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.preprocessing import LabelEncoder

warnings.filterwarnings('ignore')
os.makedirs('outputs', exist_ok=True)

plt.rcParams['figure.dpi'] = 150
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False

# ── LOAD DATA ─────────────────────────────────────────────────
adsl = pd.read_csv('data/processed/adsl_derived.csv')
adsl['READMFL_N'] = (adsl['READMFL'] == 'Y').astype(int)
adsl['AEFL_N']    = (adsl['AEFL']    == 'Y').astype(int)

print("="*55)
print("PATIENT RISK STRATIFICATION MODEL")
print("="*55)
print(f"Dataset: {adsl.shape[0]:,} subjects")
print(f"Outcome: 30-day readmission (READMFL)")
print(f"Overall rate: {adsl['READMFL_N'].mean():.1%}")

# ── FEATURE SELECTION ─────────────────────────────────────────
features = ['LOS', 'NUMMED', 'NUMDIAG', 'AEFL_N']

# Encode categoricals
adsl['SEX_N']  = LabelEncoder().fit_transform(adsl['SEX'].astype(str))
adsl['TRTA_N'] = LabelEncoder().fit_transform(adsl['TRTA'].astype(str))
adsl['AGE_N']  = LabelEncoder().fit_transform(adsl['AGEGR1'].astype(str))
adsl['MED_N']  = LabelEncoder().fit_transform(adsl['DIABMEDFL'].astype(str))

features += ['SEX_N', 'TRTA_N', 'AGE_N', 'MED_N']
feature_labels = ['Length of Stay', 'Num Medications',
                  'Num Diagnoses', 'AE Flag',
                  'Sex', 'Treatment', 'Age Group', 'Diabetes Med']

model_df = adsl[features + ['READMFL_N']].dropna()
X = model_df[features]
y = model_df['READMFL_N']

print(f"\nFeatures used: {features}")
print(f"Model dataset: {len(model_df):,} subjects after dropping missing")

# ── TRAIN MODEL ───────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

model = LogisticRegression(max_iter=1000, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

print("\n" + "="*55)
print("MODEL PERFORMANCE")
print("="*55)
print(classification_report(y_test, y_pred))
print(f"AUC-ROC: {roc_auc_score(y_test, y_prob):.3f}")

# ── FEATURE IMPORTANCE ────────────────────────────────────────
print("\n" + "="*55)
print("RISK DRIVERS — ODDS RATIOS")
print("="*55)
coef_df = pd.DataFrame({
    'Feature'    : feature_labels,
    'Coefficient': model.coef_[0],
    'Odds_Ratio' : np.exp(model.coef_[0])
}).sort_values('Coefficient', key=abs, ascending=False)
print(coef_df.to_string(index=False))

# ── RISK STRATIFICATION ───────────────────────────────────────
print("\n" + "="*55)
print("PATIENT RISK STRATIFICATION")
print("="*55)
all_prob = model.predict_proba(X)[:, 1]
model_df = model_df.copy()
model_df['RISK_SCORE'] = all_prob
model_df['RISK_GROUP'] = pd.cut(
    model_df['RISK_SCORE'],
    bins=[0, 0.07, 0.12, 1.0],
    labels=['Low Risk', 'Medium Risk', 'High Risk']
)

risk_summary = model_df.groupby('RISK_GROUP', observed=True).agg(
    N=('READMFL_N','count'),
    Actual_Readmit_Rate=('READMFL_N','mean'),
    Mean_LOS=('LOS','mean'),
    Mean_Medications=('NUMMED','mean'),
    Mean_Diagnoses=('NUMDIAG','mean')
).round(3)
risk_summary['Actual_Readmit_Rate'] = (
    risk_summary['Actual_Readmit_Rate']*100).round(1)
print(risk_summary.to_string())

# ── VISUALIZATIONS ────────────────────────────────────────────
print("\n" + "="*55)
print("GENERATING PLOTS")
print("="*55)

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Plot 1: Feature importance
axes[0].barh(coef_df['Feature'], coef_df['Coefficient'],
             color=['#E53935' if x > 0 else '#1E88E5'
                    for x in coef_df['Coefficient']],
             edgecolor='black', linewidth=0.5)
axes[0].axvline(0, color='black', linewidth=0.8)
axes[0].set_xlabel("Log-Odds Coefficient")
axes[0].set_title("Figure 2a: Risk Drivers\nfor 30-Day Readmission",
                  fontweight='bold')

# Plot 2: Risk group actual rates
actual = model_df.groupby('RISK_GROUP', observed=True)['READMFL_N'].mean()*100
axes[1].bar(actual.index, actual.values,
            color=['#43A047','#FB8C00','#E53935'],
            edgecolor='black', linewidth=0.5)
axes[1].axhline(adsl['READMFL_N'].mean()*100, color='black',
                linestyle='--', alpha=0.6, label='Overall rate')
axes[1].set_ylabel("Actual 30-Day Readmission Rate (%)")
axes[1].set_title("Figure 2b: Actual Readmission Rate\nby Risk Group",
                  fontweight='bold')
axes[1].legend()
for i, v in enumerate(actual.values):
    axes[1].text(i, v+0.2, f'{v:.1f}%', ha='center', fontsize=10)

plt.suptitle("Patient Risk Stratification — Adverse Outcome Model",
             fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig('outputs/fig2_risk_stratification.png', bbox_inches='tight')
plt.show()
print("✅ Saved: outputs/fig2_risk_stratification.png")

# ── FINAL SUMMARY ─────────────────────────────────────────────
print("\n" + "="*55)
print("CLINICAL INTERPRETATION")
print("="*55)
print(f"""
MODEL: Logistic Regression | AUC-ROC: {roc_auc_score(y_test, y_prob):.3f}

RISK GROUPS:
{risk_summary[['N','Actual_Readmit_Rate']].to_string()}

KEY FINDINGS:
1. Top risk driver: {coef_df.iloc[0]['Feature']} 
   (OR = {coef_df.iloc[0]['Odds_Ratio']:.2f})
2. High-risk patients readmit at {actual.get('High Risk', 0):.1f}% vs
   {actual.get('Low Risk', 0):.1f}% for low-risk patients
3. Model stratifies {len(model_df):,} patients into actionable tiers

RECOMMENDATION:
- Flag High Risk patients for enhanced discharge planning
- Schedule 7-day follow-up calls for Medium + High Risk
- Review medication reconciliation for high NUMMED patients
""")
print("✅ Risk model complete. Next: SAS programs in sas/ folder")