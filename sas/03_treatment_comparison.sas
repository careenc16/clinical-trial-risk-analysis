

data lab_data;
  input USUBJID $ TRTA $ LBTESTCD $ VISIT $ BASE AVAL;
  CHG = AVAL - BASE;
  PCHG = ((AVAL - BASE) / BASE) * 100;
  label CHG  = "Change from Baseline"
        PCHG = "Percent Change from Baseline";
  datalines;
001 Drug_A ALT Baseline 22 22
001 Drug_A ALT Week4 22 28
001 Drug_A ALT Week8 22 24
002 Drug_A ALT Baseline 31 31
002 Drug_A ALT Week4 31 45
002 Drug_A ALT Week8 31 38
003 Placebo ALT Baseline 25 25
003 Placebo ALT Week4 25 27
003 Placebo ALT Week8 25 26
004 Drug_A ALT Baseline 18 18
004 Drug_A ALT Week4 18 21
004 Drug_A ALT Week8 18 19
005 Placebo ALT Baseline 33 33
005 Placebo ALT Week4 33 35
005 Placebo ALT Week8 33 34
006 Drug_A CREAT Baseline 0.9 0.9
006 Drug_A CREAT Week4 0.9 1.1
006 Drug_A CREAT Week8 0.9 1.0
007 Placebo CREAT Baseline 1.0 1.0
007 Placebo CREAT Week4 1.0 1.0
007 Placebo CREAT Week8 1.0 1.1
008 Drug_A CREAT Baseline 0.8 0.8
008 Drug_A CREAT Week4 0.8 0.9
008 Drug_A CREAT Week8 0.8 0.9
009 Placebo CREAT Baseline 1.1 1.1
009 Placebo CREAT Week4 1.1 1.2
009 Placebo CREAT Week8 1.1 1.1
010 Drug_A ALT Baseline 27 27
010 Drug_A ALT Week4 27 31
010 Drug_A ALT Week8 27 29
;
run;

/* Step 1: Summary stats by treatment and lab test */
proc means data=lab_data n mean std stderr lclm uclm maxdec=2;
  where VISIT ne 'Baseline';
  var BASE AVAL CHG PCHG;
  class TRTA LBTESTCD;
  title "Lab Summary — Baseline, Post-Treatment, Change from Baseline";
  title2 "Weeks 4 and 8 Combined";
run;

/* Step 2: T-test comparing change from baseline between arms */
proc ttest data=lab_data;
  where LBTESTCD = 'ALT' and VISIT ne 'Baseline';
  class TRTA;
  var CHG;
  title "Treatment Comparison: Change from Baseline in ALT";
  title2 "Independent Samples T-Test: Drug_A vs Placebo";
run;

/* Step 3: Change from baseline by visit */
proc means data=lab_data n mean std maxdec=2;
  where LBTESTCD = 'ALT';
  var CHG;
  class TRTA VISIT;
  title "Mean Change from Baseline in ALT by Visit and Treatment";
run;

/* Step 4: Flag abnormal values */
data lab_flagged;
  set lab_data;
  where VISIT ne 'Baseline';
  if LBTESTCD = 'ALT' and AVAL > 40 then ABNFL = 'HIGH';
  else if LBTESTCD = 'ALT' then ABNFL = 'NORMAL';
  else if LBTESTCD = 'CREAT' and AVAL > 1.2 then ABNFL = 'HIGH';
  else ABNFL = 'NORMAL';
run;

proc freq data=lab_flagged;
  tables TRTA * LBTESTCD * ABNFL / nocum norow nopercent;
  title "Lab Abnormality Shift Table — Normal vs High";
  title2 "Post-Baseline Values Only";
run;

/* Step 5: PROC REPORT summary */
proc report data=lab_data nowd headline headskip;
  where VISIT ne 'Baseline';
  column TRTA LBTESTCD BASE AVAL CHG;
  define TRTA     / group  "Treatment"   width=10;
  define LBTESTCD / group  "Lab Test"    width=8;
  define BASE     / mean   "Mean Base"   format=8.2;
  define AVAL     / mean   "Mean Post"   format=8.2;
  define CHG      / mean   "Mean CFB"    format=8.2;
  title "Lab Parameter Summary — Change from Baseline";
  title2 "CFB = Change from Baseline (AVAL - BASE)";
run;
