# Clinical Trial Risk Analysis
### End-to-End Patient Risk Stratification | SAS · Python · CDISC · Healthcare Analytics

> **Built to demonstrate:** SDTM data structuring · Adverse event analysis · Survival analysis · Patient risk modeling · Clinical TLF generation
>
> **Target roles:** Statistical Programmer · Clinical Data Analyst · SAS Analyst · Healthcare Data Analyst
>
> **Target companies:** IQVIA · Parexel · ICON · Medpace · Fortrea · Covance · Syneos Health

---

## Problem Statement

In clinical trials and hospital settings, not all patients respond to treatment the same way. Some patients experience severe adverse events while others don't. Some are readmitted to the hospital within 30 days — a costly and preventable outcome.

**This project answers one core clinical question:**

> *"Which patients are at highest risk for adverse outcomes and what clinical factors drive that risk?"*

This is the exact analytical question that Statistical Programmers and Clinical Data Analysts solve every day at CROs and pharmaceutical companies.

---

## Dataset

| Source | Size | Description |
|--------|------|-------------|
| Diabetes 130-US Hospitals (UCI / Kaggle) | 101,766 encounters · 50 variables | Real inpatient records from 130 U.S. hospitals, 1999–2008 |

**Why this dataset?**
It contains the same types of variables found in clinical trial data — patient demographics, diagnoses, medications, lab procedures, treatment type, and outcomes. This makes it ideal for applying CDISC SDTM standards and clinical trial analysis methodology to a real-world healthcare problem.

---

## What I Built

### Part 1 — SDTM Data Structuring (Python)
Transformed raw hospital data into **CDISC SDTM-aligned domains** — the FDA-required standard for clinical trial data submissions.

| SDTM Domain | Description | Records |
|-------------|-------------|---------|
| **DM** — Demographics | One row per subject: USUBJID, RACE, SEX, AGEGR1, ARM, SAFFL | 71,518 subjects |
| **AE** — Adverse Events | One row per event: AEDECOD, AESEV, AESER, AEBODSYS, AEDUR | 101,766 events |
| **ADSL** — Analysis Dataset | ADaM-style subject-level: TRTA, READMFL, AEFL, NUMDIAG, LOS | 71,518 subjects |

**Key SDTM variables created:**
- `USUBJID` — Unique subject identifier
- `AESEV` — AE severity (MILD / MODERATE / SEVERE)
- `AESER` — Serious AE flag (Y/N) — 11,357 SAEs identified (11.2%)
- `READMFL` — 30-day readmission flag (primary outcome)
- `AEFL` — High adverse event burden flag

---

### Part 2 — Clinical EDA (Python)
Exploratory analysis structured exactly like a **Clinical Study Report (CSR)** — the document submitted to FDA after every clinical trial.

**Demographics (Table 14.1 equivalent):**
- 71,518 unique patients
- Female: 53.2% | Male: 46.8%
- Caucasian: 74.8% | AfricanAmerican: 18.0% | Hispanic: 2.1%
- Age range: [0-10) through [90-100)

**Adverse Event Analysis:**
- 101,766 total AE records
- 11,357 Serious Adverse Events (SAEs) — 11.2% rate
- Top System Organ Class: **Cardiovascular** (30,389 events)
- Severity: MODERATE 48.3% · MILD 30.9% · SEVERE 20.8%

**Outcome Analysis:**
- Overall 30-day readmission rate: **8.8%**
- Patients aged 80-90 had highest readmission: **10.4%**
- High AE burden patients: **9.4%** readmission vs 7.0% low burden
- Insulin "Down" group: **10.3%** — highest among treatment types

---

### Part 3 — Patient Risk Stratification Model (Python)
Built a **logistic regression model** to predict 30-day readmission — the standard first-line model for clinical risk scoring.

**Features used:**
- Length of Stay (LOS)
- Number of Medications (NUMMED)
- Number of Diagnoses (NUMDIAG)
- AE Burden Flag (AEFL)
- Age Group, Sex, Treatment Type, Diabetes Medication

**Model Performance:**
| Metric | Value |
|--------|-------|
| AUC-ROC | 0.581 |
| Training set | 57,214 subjects (80%) |
| Test set | 14,304 subjects (20%) |

**Risk Stratification Results:**
| Risk Group | N Patients | Actual Readmission Rate | Mean LOS | Mean Medications |
|------------|------------|------------------------|----------|-----------------|
| Low Risk | 13,854 | **5.7%** | 2.3 days | 10.9 meds |
| Medium Risk | 52,618 | **9.3%** | 4.2 days | 16.2 meds |
| High Risk | 5,046 | **11.8%** | 10.4 days | 24.1 meds |

**Key finding:** High-risk patients have **2x the readmission rate** of low-risk patients and stay **4x longer** in hospital.

**Top Risk Drivers (Odds Ratios):**
1. Diabetes Medication — OR = **1.30** (strongest predictor)
2. AE Burden Flag — OR = **1.08**
3. Age Group — OR = **1.08**
4. Length of Stay — OR = **1.05**

---

### Part 4 — SAS Clinical Programming (5 Programs)
Replicated the analysis in SAS — the **industry-standard tool** used by 90% of CROs and pharmaceutical companies for regulatory submissions.

#### Program 1: Demographics Table 14.1
```
PROC MEANS · PROC FREQ · PROC REPORT
```
Produced the standard demographic summary table found in every Clinical Study Report — age, sex, race by treatment arm.

#### Program 2: Adverse Event Analysis
```
PROC FREQ (with CHISQ) · PROC SORT · PROC REPORT
```
- TEAE incidence by treatment arm
- AE frequency by System Organ Class (SOC)
- Severity breakdown with chi-square test
- Serious Adverse Events (SAE) summary table

#### Program 3: Treatment Comparison — Change from Baseline
```
PROC MEANS · PROC TTEST · PROC REPORT
```
- Derived `CHG = AVAL - BASE` (change from baseline — primary efficacy variable)
- Drug_A ALT mean CFB: **+4.88** vs Placebo: **+1.50** (p = 0.059)
- Lab abnormality shift table (Normal → High flagging)

#### Program 4: Kaplan-Meier Survival Analysis
```
PROC LIFETEST · Log-rank test · Age subgroup analysis
```
- **Log-rank p = 0.0341** — statistically significant survival difference
- Drug_A median survival: **381.5 days** vs Placebo: **167 days**
- Age subgroup analysis: 75+ patients showed 0 events in Drug_A arm
- Survival probabilities at Day 90, 180, 270, 365

#### Program 5: Risk Stratification TLF + SAS Macro
```
PROC REPORT · PROC MEANS · %MACRO · PROC FREQ
```
- Integrated risk model output into formatted clinical TLF
- Reusable SAS macro (`%risk_summary`) for automated reporting
- Final summary: High-risk group — mean LOS 9.4 days, 22 medications

---

## Key Clinical Findings

1. **Age is a significant risk modifier** — patients aged 80-90 have 5x the readmission rate of patients under 10 (10.4% vs 1.9%)

2. **Diabetes medication is the strongest readmission predictor** — patients on diabetes medication are 30% more likely to be readmitted (OR = 1.30), reflecting disease severity

3. **High AE burden drives readmission** — patients with high comorbidity (AEFL = Y) readmit at 9.4% vs 7.0% — a 34% relative increase

4. **Risk stratification enables targeted intervention** — High-risk patients (11.8% readmission) can be identified at discharge for enhanced follow-up, reducing CMS HRRP penalties

5. **Drug_A shows statistically significant survival benefit** — log-rank p = 0.034, median survival 2.3x longer than Placebo (381 vs 167 days)

---

## Clinical Recommendations

Based on this analysis, the following interventions are recommended for clinical operations teams:

| Priority | Action | Target Group |
|----------|--------|--------------|
| HIGH | Enhanced discharge planning | High-Risk patients (top tier) |
| HIGH | 7-day post-discharge follow-up call | Medium + High Risk |
| MEDIUM | Mandatory medication reconciliation | Patients on 20+ medications |
| MEDIUM | Diabetes education program | Insulin-dependent patients |
| LOW | Quarterly readmission rate monitoring | All patient groups |

---

## Project Structure

```
clinical-trial-risk-analysis/
│
├── data/
│   ├── raw/                    # Original dataset
│   └── processed/
│       ├── dm_clean.csv        # DM domain — 71,518 subjects
│       ├── ae_clean.csv        # AE domain — 101,766 events
│       └── adsl_derived.csv    # ADSL — analysis-ready dataset
│
├── python/
│   ├── 01_sdtm_alignment.py    # CDISC SDTM data transformation
│   ├── 02_eda_clinical.py      # Clinical exploratory analysis
│   └── 03_risk_stratification.py # Logistic regression risk model
│
├── sas/
│   ├── 01_demographics_table14_1.sas   # Table 14.1
│   ├── 02_adverse_event_analysis.sas   # AE safety tables
│   ├── 03_treatment_comparison.sas     # CFB + t-test
│   ├── 04_survival_analysis.sas        # KM + log-rank
│   └── 05_risk_stratification_tlf.sas  # Final TLF + macro
│
└── outputs/
    ├── fig1_clinical_eda.png           # EDA visualization
    └── fig2_risk_stratification.png    # Risk model visualization
```

---

## Tools & Technologies

| Category | Tools |
|----------|-------|
| **SAS** | DATA step · PROC MEANS · PROC FREQ · PROC TTEST · PROC LIFETEST · PROC REPORT · SAS Macros |
| **Python** | pandas · numpy · scikit-learn · matplotlib |
| **Standards** | CDISC SDTM · ADaM concepts · ICH E9 statistical principles |
| **Clinical** | Adverse events · SAEs · Change from baseline · Kaplan-Meier · ITT population · TLF generation |
| **Healthcare** | CMS HRRP · 30-day readmission · Comorbidity scoring · Discharge planning |

---

## Skills Demonstrated

- ✅ CDISC SDTM domain creation (DM, AE, ADSL)
- ✅ ADaM-style derived variables (READMFL, AEFL, CHG, PCHG)
- ✅ Clinical safety analysis — TEAE, SAE, SOC tables
- ✅ Change from baseline derivation and statistical testing
- ✅ Kaplan-Meier survival analysis with log-rank test
- ✅ Patient risk stratification with logistic regression
- ✅ SAS PROC REPORT for TLF generation
- ✅ SAS macro programming for reusable reporting
- ✅ Clinical findings communicated to non-technical stakeholders

---

## About

**Careen Chowrappa**
MS Data Science — University of New Haven (May 2025)

Open to: Statistical Programmer · Clinical Data Analyst · SAS Analyst · Healthcare Data Analyst 

📧 careen1622@gmail.com | 📍 Connecticut, US | 🔗 [LinkedIn]:https://www.linkedin.com/in/careen-c-961018195/


---

*This project was built to demonstrate clinical data analysis skills relevant to CRO and pharmaceutical industry roles. All data is publicly available and de-identified.*
