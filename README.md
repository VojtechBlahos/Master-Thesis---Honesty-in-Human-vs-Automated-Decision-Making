# Honesty in Human vs. Automated Bureaucratic Decision-Making

**WU Vienna MSc Thesis**: Vojtech Blahos & Roman Perehinets

Experimental Evidence from a Benefit Eligibility Task: an oTree 6 lab experiment testing whether applicants misreport eligibility more to automated vs. human reviewers.

This repository has two parts:

- **`experiment_app/`**: the oTree 6 lab experiment used to collect the data (deployment, design, data export)
- **`stat_analysis/`**: everything needed to reproduce every statistic, table and figure in Chapter 5 and Appendix B of the thesis, starting from the raw oTree export

And also, a transcript a conversation with Claude Code is uploaded. Some conversations, namely with Microsof Copilot, were not able to export as it served only a small editorial role with suggestions only.  

---

## Repository structure

```
.
├── experiment_app/            oTree 6 lab experiment (see Part 1)
│   ├── HumanvsMachine/         Main experiment app (6 rounds)
│   │   ├── __init__.py         All Python logic: models, pages, payoffs
│   │   └── *.html              One template per page
│   ├── payout_referral/        Exit app, redirects to SoSciSurvey
│   │   ├── __init__.py
│   │   └── Payout_Refer_Page.html
│   ├── _rooms/
│   │   └── wulabs.txt          Participant labels 1-26
│   ├── settings.py             oTree config, room, session config
│   ├── requirements.txt        otree==6.0.0b32, psycopg2, numpy
│   ├── runtime.txt             python-3.11.9 (Heroku)
│   └── Procfile                Heroku process config
│
└── Stat analysis/     Analysis & replication (see Part 2)
    ├── data/
    │   └── All_sessions_combined.csv        raw oTree export, 102 participants x 132 columns   
    ├── output/
    │   └── full_statistical_output.txt    Complete console output of the analysis scripts
    ├── figures/                           Figures 5.1-5.8 as rendered in the thesis
    └── Statistical_Analysis.ipynb         Self-contained notebook reproducing the full analysis
    └── Estim.py                           Appendix B1 - estimates taken
    └── Reshape.py                         How lie is encoded, MES and what records have been excluded
```

> Note: if you name the two folders differently on GitHub, update the paths above and the two part headers below to match.

---

# Part 1: Experiment app (`experiment_app/`)

## Quick start

```bash
# Activate your virtual environment, then:
cd experiment_app
otree devserver        # development (localhost:8000)
otree prodserver       # production
```

**Room:** Admin → Rooms → wulabs → share the room-wide link (one URL for all participants; they type their seat number).
**Session config:** `HumanvsMachine`, `num_participants=26`

---

## Folder structure

```
experiment_app/
├── HumanvsMachine/         Main experiment app (6 rounds)
│   ├── __init__.py         All Python logic: models, pages, payoffs
│   └── *.html              One template per page
├── payout_referral/        Exit app, redirects to SoSciSurvey
│   ├── __init__.py
│   └── Payout_Refer_Page.html
├── _rooms/
│   └── wulabs.txt          Participant labels 1-26
├── settings.py             oTree config, room, session config
├── requirements.txt        otree==6.0.0b32, psycopg2, numpy
├── runtime.txt             python-3.11.9 (Heroku)
└── Procfile                Heroku process config
```

---

## Experiment design

### Roles (13 players per group)

| Role | id_in_group | Count |
|------|-------------|-------|
| Reviewer | 1 | 1 |
| Applicant | 2-13 | 12 |

With 26 participants there are 2 groups running in parallel.

### Within-subjects counterbalancing

Applicants are split into 4 subgroups. Each subgroup faces one reviewer type per part:

| Subgroup | Part 1 (rounds 1-3) | Part 2 (rounds 4-6) |
|----------|---------------------|---------------------|
| A, C | HR (Human Reviewer) | AR (Automated Algorithm) |
| B, D | AR | HR |

The Reviewer always operates in HR mode.

### Credit scores

- Drawn each round from N(5.5, 1.8), clamped to [1, 10], integer
- **1-3 = Eligible** for financial aid; **4-10 = Not eligible**
- Only the applicant sees their true score; the reviewer sees only the reported score

### Application rules

- **Eligible (1-3):** must apply; true score reported automatically
- **Not eligible (4-10):** may choose not to apply, OR report a false score of 1, 2, or 3 (cannot report 4-10)

### Reviewer decision

- Sees only reported scores
- Must audit exactly 1 application per round (reveals the true score; decision then automatic)
- Approves or rejects all remaining applications manually

### Automated Algorithm (AR condition)

- 1 randomly selected applicant is audited and approved/rejected based on true score
- All others approved with 60% probability (`BOT_APPROVAL_RATE = 0.60`)

---

## Payoff structure

### Base tokens

Every player starts each round with **10 tokens** (1 token = €1).

### Applicant token changes

| Situation | Change |
|-----------|--------|
| Did not apply | 0 |
| Eligible, approved | +2 |
| Eligible, rejected | 0 |
| Not eligible, approved (lied) | +2 |
| Not eligible, rejected (lied) | -1 |

### Reviewer token changes

One randomly selected HR applicant determines the reviewer's outcome:

| Situation | Change |
|-----------|--------|
| Approved an eligible applicant | +2 |
| Rejected an eligible applicant | -2 |
| Rejected a not-eligible applicant (caught liar) | +3 |
| Approved a not-eligible applicant | -3 |

### Final payment

- One round randomly selected from all 6
- Tokens from that round + BART earnings + estimation bonus (if won)
- Stored in `final_payment_euros` on the round 6 player record, use this column in the data export

### Estimation bonus

- Each round, applicants guess the audit probability (0-100%)
- After the experiment, the applicant per subgroup (A/B/C/D) whose guess was closest to the true probability in the selected round wins **€2**

### BART / Balloon task (round 6)

- 10 balloons; €0.05 per pump; max 20 pumps; hidden explosion point
- Fixed explosion sequence: `[19, 7, 13, 16, 11, 8, 5, 3, 4, 14]`
- Both roles complete it (reviewer plays too to avoid identification by finish time)

---

## Page sequence

```
Welcome                     round 1 - all
DemographicsAndMES          round 1 - all (age, gender, AI use, 10-item MES)
ExperimentDetails1          round 1 - all
ExperimentDetails2          round 1 - all
ApplicantRoleIntro          round 1 - applicants only
ReviewerRoleIntro           round 1 - reviewer only
ComprehensionCheck1/2/3     round 1 - all
GroupFormationWait          round 1 - WaitPage (waits for all groups)
PartIntro                   rounds 1 & 4 - all (shows HR/AR for current part)
CreditScoreAndAuditGuess    every round - applicants only
ApplicationDecision         every round - applicants only
WaitForApplicants           every round - reviewer only (WaitPage)
ReviewerDecision            every round - reviewer only
DecisionWait                every round - all (WaitPage; triggers payoff calculation)
RoundResults                every round - all
BARTIntro                   round 6 - all
BARTPage                    round 6 - all
ThankYou                    round 6 - all
→ payout_referral           redirects to SoSciSurvey with ?pid=<seat_number>
```

---

## Data export

Download the CSV/Excel from the oTree admin panel. Key fields on the **round 6** player rows:

| Field | Description |
|-------|-------------|
| `final_payment_euros` | Total payment in euros (tokens + BART + bonus) |
| `bart_total_euros` | BART earnings only |
| `won_guessing_bonus` | True if won the €2 estimation bonus |
| `round_tokens` | Tokens earned in that specific round |

The `selected_round` is stored in session variables and visible in the session data export.

To pay a participant: look up their seat number (`participant_label`) in the round 6 rows and read `final_payment_euros`. Cross-reference with the SoSciSurvey export by matching the `pid` URL parameter.

---

## SoSciSurvey integration

After the experiment, participants are redirected to:

```
https://soscisurvey.wu.ac.at/humanandalgorithm/?pid=<seat_number>
```

They enter their IBAN there for bank transfer. The `pid` links each IBAN entry back to the oTree data row.

---

## Heroku deployment

### First-time setup

```bash
git init
git add .
git commit -m "Initial commit"

heroku create <app-name>
heroku addons:create heroku-postgresql:essential-0

heroku config:set OTREE_ADMIN_PASSWORD=yourpassword
heroku config:set OTREE_PRODUCTION=1
heroku config:set OTREE_SECRET_KEY=some-long-random-string

git push heroku main
heroku ps:scale worker=1
heroku run otree resetdb
```

### Required environment variables

| Variable | Purpose |
|----------|---------|
| `OTREE_ADMIN_PASSWORD` | Admin panel login |
| `OTREE_PRODUCTION` | Set to `1` for production mode |
| `OTREE_SECRET_KEY` | Django secret key |
| `DATABASE_URL` | Set automatically by Heroku Postgres |

### After any Player model change

Reset the database: Admin panel → Reset DB, or `heroku run otree resetdb`.

---

## Key implementation notes

- **Form-based submission throughout**: `live_method` (WebSocket) was replaced with hidden JSON fields (`app_choice`, `reviewer_decisions_json`, `bart_results_json`) due to oTree 6 compatibility issues.
- **oTree 6 template engine is not Jinja2**: no inline ternaries, no `{% set %}` with literals, no Jinja2 filters. Everything is precomputed in `vars_for_template`.
- **`field_maybe_none('field_name')`** must be used for any `blank=True` field that may be `None` at runtime (e.g. `is_approved` for players who did not apply).
- **`use_secure_urls=False`** in the wulabs room: required so the room-wide single-link entry form appears. With `True`, only individual per-participant URLs are generated.
- **True credit scores are embedded in `ReviewerDecision.html` JS**: acceptable for a controlled lab setting.
- **Consent page** exists in the model but is removed from `page_sequence`: participants sign paper consent beforehand.

---

# Part 2: Statistical Analysis (Stat_Analysis) 

These materials reproduce every statistic, table and figure reported in Chapter 5 and Appendix B of the thesis, starting from the raw oTree export.

## Contents

```
── Stat analysis/     Analysis & replication (see Part 2)
    ├── data/
    │   └── All_sessions_combined.csv        raw oTree export, 102 participants x 132 columns   
    ├── output/
    │   └── full_statistical_output.txt    Complete console output of the analysis scripts
    ├── figures/                           Figures 5.1-5.8 as rendered in the thesis
    └── Statistical_Analysis.ipynb         Self-contained notebook reproducing the full analysis
    └── Estim.py                           Appendix B1 - estimates taken
    └── Reshape.py                         How lie is encoded, MES and what records have been excluded
```

## Running

Python 3.12 with numpy, pandas, scipy, statsmodels, matplotlib.

```bash
python reshape.py          # produces long_format_applicants_v2.csv
python results_main.py
python results_explor.py
python results_bart.py
python med.py
python robust_full.py
python figures.py
```

Scripts read and write absolute paths at the top of each file; adjust these before running. All resampling procedures use fixed seeds, so re-execution returns identical values.

## Notes on the data

94 of the 102 participants served as applicants; 8 served as human reviewers and are excluded from applicant-level analyses.

The Moral Expansiveness Scale is unavailable for 18 applicants in session 1fqoznxz, where the form recorded only the first of the ten entity ratings. `reshape.py` sets all ten items to missing for these records rather than retaining a partial score.

Two applicants did not report gender.
