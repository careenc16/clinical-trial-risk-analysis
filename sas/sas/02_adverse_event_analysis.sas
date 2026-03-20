/* ================================================
   SAS Program 2: Adverse Event Analysis
   Clinical Trial Risk Analysis Project
   ================================================ */

data adverse_events;
  input USUBJID $ TRTA $ AEBODSYS $ AEDECOD $ AESEV $ AESER $;
  datalines;
001 Drug_A CARDIOVASCULAR Hypertension MODERATE N
001 Drug_A GASTROINTESTINAL Nausea MILD N
002 Drug_A NERVOUS_SYSTEM Headache MILD N
003 Placebo CARDIOVASCULAR Chest_Pain SEVERE Y
003 Placebo GASTROINTESTINAL Vomiting MODERATE N
004 Drug_A CARDIOVASCULAR Palpitations MODERATE N
004 Drug_A RESPIRATORY Dyspnea SEVERE Y
005 Placebo NERVOUS_SYSTEM Dizziness MILD N
006 Drug_A GASTROINTESTINAL Diarrhea MILD N
007 Placebo CARDIOVASCULAR Hypertension MODERATE N
008 Drug_A ENDOCRINE Hyperglycemia MODERATE N
008 Drug_A CARDIOVASCULAR Edema MILD N
009 Placebo RESPIRATORY Cough MILD N
010 Drug_A NERVOUS_SYSTEM Fatigue MILD N
011 Placebo CARDIOVASCULAR Arrhythmia SEVERE Y
012 Drug_A RENAL Proteinuria MODERATE N
013 Placebo GASTROINTESTINAL Nausea MILD N
014 Drug_A CARDIOVASCULAR Hypertension SEVERE Y
015 Placebo NERVOUS_SYSTEM Headache MILD N
;
run;

/* Total subjects per arm (for rate calculation) */
data n_per_arm;
  input TRTA $ N;
  datalines;
Drug_A 8
Placebo 7
;
run;

/* Step 1: Subjects with at least 1 AE */
proc sort data=adverse_events nodupkey out=ae_unique;
  by USUBJID TRTA;
run;

proc freq data=ae_unique;
  tables TRTA;
  title "Subjects with At Least 1 AE by Treatment Arm";
run;

/* Step 2: AE by System Organ Class */
proc freq data=adverse_events order=freq;
  tables TRTA * AEBODSYS / nocum norow nopercent;
  title "Adverse Events by System Organ Class (SOC) and Treatment";
run;

/* Step 3: AE severity breakdown with chi-square */
proc freq data=adverse_events;
  tables TRTA * AESEV / nocum nopercent chisq;
  title "AE Severity by Treatment Group";
  title2 "Chi-Square Test for Independence";
run;

/* Step 4: Serious Adverse Events (SAEs) */
data saes;
  set adverse_events;
  where AESER = 'Y';
run;

proc freq data=saes;
  tables TRTA * AEBODSYS / nocum;
  title "Serious Adverse Events (SAE) by Treatment and Body System";
run;

/* Step 5: PROC REPORT — AE summary TLF */
proc report data=adverse_events nowd headline headskip;
  column TRTA AEBODSYS AESEV AESER;
  define TRTA     / group "Treatment"    width=10;
  define AEBODSYS / group "Body System"  width=20;
  define AESEV    / group "Severity"     width=10;
  define AESER    / group "Serious"      width=8;
  title "AE Summary by System Organ Class";
  title2 "Safety Population — Clinical Trial Risk Analysis";
run;