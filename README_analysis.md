# Replication materials

Honesty in Human versus Automated Bureaucratic Decision-Making:
Experimental Evidence from a Benefit Eligibility Task

Blahos, V. & Perehinets, R. — WU Vienna

These materials reproduce every statistic, table and figure reported in
Chapter 5 and Appendix B of the thesis, starting from the raw oTree export.

## Contents

data/
  All_sessions_combined.csv        raw oTree export, 102 participants x 132 columns
  long_format_applicants_v2.csv    analysis dataset, 564 applicant-round observations



output/
  full_statistical_output.txt   complete console output of the analysis scripts
  results_v2.txt                validation of the dataset after demographic recovery

figures/                        Figures 5.1-5.8 as rendered in the thesis

Statistical_Analysis.ipynb
  Self-contained notebook reproducing the full analysis from the raw export,
  with a reconciliation table listing every statistic reported in Chapter 5
  beside its computed value.

## Running

Python 3.12 with numpy, pandas, scipy, statsmodels, matplotlib.

    python reshape.py          # produces long_format_applicants_v2.csv
    python results_main.py
    python results_explor.py
    python results_bart.py
    python med.py
    python robust_full.py
    python figures.py

Scripts read and write absolute paths at the top of each file; adjust these
before running. All resampling procedures use fixed seeds, so re-execution
returns identical values.

## Notes on the data

94 of the 102 participants served as applicants; 8 served as human reviewers
and are excluded from applicant-level analyses.

The Moral Expansiveness Scale is unavailable for 18 applicants in session
1fqoznxz, where the form recorded only the first of the ten entity ratings.
reshape.py sets all ten items to missing for these records rather than
retaining a partial score.

Two applicants did not report gender.
