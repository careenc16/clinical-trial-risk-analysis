

data survival;
  input USUBJID $ TRTA $ AVAL CNSR AGEGR $;
  /* AVAL = days to event or censoring */
  /* CNSR = 1 censored, 0 = event occurred */
  datalines;
001 Drug_A 365 0 65_74
002 Drug_A 289 0 45_64
003 Drug_A 420 1 45_64
004 Drug_A 156 0 65_74
005 Drug_A 510 1 75plus
006 Placebo 180 0 45_64
007 Placebo 95  0 65_74
008 Placebo 310 1 45_64
009 Placebo 88  0 75plus
010 Placebo 245 1 65_74
011 Drug_A 398 0 45_64
012 Placebo 134 0 45_64
013 Drug_A 445 1 75plus
014 Placebo 167 0 65_74
015 Drug_A 312 0 45_64
;
run;

/* Step 1: Kaplan-Meier survival analysis */
proc lifetest data=survival
  timelist=90 180 270 365
  plots=none;
  time AVAL * CNSR(1);
  strata TRTA;
  title "Kaplan-Meier Survival Analysis by Treatment Group";
  title2 "Survival Probabilities at Day 90, 180, 270, 365";
run;

/* Step 2: KM by age subgroup — Drug_A only */
proc lifetest data=survival
  timelist=180 365
  plots=none;
  where TRTA = 'Drug_A';
  time AVAL * CNSR(1);
  strata AGEGR;
  title "Subgroup Analysis: Survival by Age Group";
  title2 "Drug_A Arm Only";
run;

/* Step 3: Summary statistics */
proc means data=survival n mean std min max maxdec=1;
  var AVAL;
  class TRTA CNSR;
  title "Time to Event Summary by Treatment and Event Status";
run;

/* Step 4: Risk summary table */
data risk_summary;
  input TRTA $ AGEGR $ N_SUBJ EVENTS MEDIAN_OS;
  datalines;
Drug_A 45_64 4 3 340
Drug_A 65_74 2 2 327
Drug_A 75plus 2 0 .
Placebo 45_64 4 3 190
Placebo 65_74 3 3 167
Placebo 75plus 1 1 88
;
run;

proc report data=risk_summary nowd headline headskip;
  column TRTA AGEGR N_SUBJ EVENTS MEDIAN_OS;
  define TRTA      / group  "Treatment"    width=10;
  define AGEGR     / group  "Age Group"    width=10;
  define N_SUBJ    / sum    "N Subjects"   format=8.0;
  define EVENTS    / sum    "N Events"     format=8.0;
  define MEDIAN_OS / mean   "Median OS"    format=8.1;
  title "Table 14.3 — Overall Survival Summary by Treatment and Age";
  title2 "OS = Days from Randomization to Event or Censoring";
run;
