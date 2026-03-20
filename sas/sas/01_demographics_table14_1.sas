/* ================================================
   SAS Program 1: Demographics Table 14.1
   Clinical Trial Risk Analysis Project
   ================================================ */

data demographics;
  input USUBJID $ AGE AGEGR $ SEX $ RACE $ TRTA $;
  datalines;
001 45 65_74 M WHITE Drug_A
002 52 45_64 F BLACK Drug_A
003 38 18_44 F WHITE Placebo
004 61 45_64 M ASIAN Drug_A
005 49 45_64 M WHITE Placebo
006 55 45_64 F WHITE Drug_A
007 43 18_44 F BLACK Placebo
008 67 65_74 M WHITE Drug_A
009 51 45_64 F ASIAN Placebo
010 44 18_44 M WHITE Drug_A
011 72 65_74 F WHITE Placebo
012 58 45_64 M WHITE Drug_A
013 81 75plus F WHITE Placebo
014 76 75plus M BLACK Drug_A
015 69 65_74 F WHITE Placebo
;
run;

/* Age summary by treatment arm */
proc means data=demographics n mean std median min max maxdec=1;
  var AGE;
  class TRTA;
  title "Table 14.1 — Age Summary by Treatment Arm";
  title2 "Safety Population";
run;

/* Sex by treatment */
proc freq data=demographics;
  tables TRTA * SEX / nocum norow nopercent;
  title "Table 14.1 — Sex by Treatment Arm";
run;

/* Race by treatment */
proc freq data=demographics;
  tables TRTA * RACE / nocum norow nopercent;
  title "Table 14.1 — Race by Treatment Arm";
run;

/* Age group by treatment */
proc freq data=demographics;
  tables TRTA * AGEGR / nocum norow nopercent;
  title "Table 14.1 — Age Group by Treatment Arm";
run;

/* PROC REPORT — formatted TLF output */
proc report data=demographics nowd headline headskip;
  column TRTA AGE SEX RACE;
  define TRTA / group   "Treatment"  width=10;
  define AGE  / mean    "Mean Age"   format=8.1;
  define SEX  / display "Sex"        width=5;
  define RACE / display "Race"       width=15;
  title "Table 14.1 — Demographic Characteristics";
  title2 "Safety Population — Clinical Trial Risk Analysis";
run;