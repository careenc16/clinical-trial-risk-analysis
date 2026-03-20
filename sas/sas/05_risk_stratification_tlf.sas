/* ================================================
   SAS Program 5: Risk Stratification Summary
   Final TLF — Combines all analyses
   ================================================ */

/* Simulate patient-level risk data
   (mirrors our Python risk model output) */
data patient_risk;
  input USUBJID $ TRTA $ AGEGR $ LOS NUMMED NUMDIAG AEFL $ RISK_GROUP $;
  datalines;
001 Drug_A 65_74  3 12  6 Y Medium_Risk
002 Drug_A 45_64  7 18  9 Y High_Risk
003 Placebo 45_64  2  8  4 N Low_Risk
004 Drug_A 65_74  5 15  8 Y Medium_Risk
005 Placebo 45_64  1  6  3 N Low_Risk
006 Drug_A 45_64 11 25 10 Y High_Risk
007 Placebo 75plus  4 14  7 Y Medium_Risk
008 Drug_A 45_64  2  9  5 N Low_Risk
009 Placebo 65_74  8 20  9 Y High_Risk
010 Drug_A 45_64  3 11  6 Y Medium_Risk
011 Placebo 75plus  6 16  8 Y Medium_Risk
012 Drug_A 65_74 12 26 11 Y High_Risk
013 Placebo 45_64  2  7  4 N Low_Risk
014 Drug_A 45_64  1  5  3 N Low_Risk
015 Placebo 65_74  9 22 10 Y High_Risk
;
run;

/* Step 1: Risk group distribution */
proc freq data=patient_risk;
  tables RISK_GROUP / nocum;
  title "Patient Risk Stratification — Distribution";
  title2 "Based on Logistic Regression Model (Python)";
run;

/* Step 2: Clinical profile by risk group */
proc means data=patient_risk n mean std min max maxdec=1;
  var LOS NUMMED NUMDIAG;
  class RISK_GROUP;
  title "Clinical Profile by Risk Group";
  title2 "Mean LOS, Medications, Diagnoses";
run;

/* Step 3: Risk group by treatment arm */
proc freq data=patient_risk;
  tables TRTA * RISK_GROUP / nocum norow nopercent;
  title "Risk Group Distribution by Treatment Arm";
run;

/* Step 4: Risk group by age */
proc freq data=patient_risk;
  tables AGEGR * RISK_GROUP / nocum norow nopercent;
  title "Risk Group Distribution by Age Group";
run;

/* Step 5: Final integrated summary — PROC REPORT */
proc report data=patient_risk nowd headline headskip;
  column RISK_GROUP TRTA LOS NUMMED NUMDIAG AEFL;
  define RISK_GROUP / group  "Risk Group"    width=12;
  define TRTA       / group  "Treatment"     width=10;
  define LOS        / mean   "Mean LOS"      format=8.1;
  define NUMMED     / mean   "Mean Meds"     format=8.1;
  define NUMDIAG    / mean   "Mean Diag"     format=8.1;
  define AEFL       / display "AE Flag"      width=7;
  title "Final Risk Stratification Summary";
  title2 "Integration of Clinical Variables and Risk Model Output";
  title3 "Clinical Trial Risk Analysis Project — Careen Chowrappa";
run;

/* Step 6: Macro for reusable risk summary — shows SAS macro skills */
%macro risk_summary(dataset=, risk_var=, outcome_var=);
  proc means data=&dataset n mean maxdec=2;
    var &outcome_var;
    class &risk_var;
    title "Risk Summary: &outcome_var by &risk_var";
  run;
%mend risk_summary;

%risk_summary(dataset=patient_risk, risk_var=RISK_GROUP, outcome_var=LOS);
%risk_summary(dataset=patient_risk, risk_var=RISK_GROUP, outcome_var=NUMMED);
%risk_summary(dataset=patient_risk, risk_var=RISK_GROUP, outcome_var=NUMDIAG);