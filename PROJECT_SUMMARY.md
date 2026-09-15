# oTree Experiment — Project Summary
**Thesis:** Honesty in Human vs. Automated Bureaucratic Decision-Making  
**Authors:** Vojtech Blahos & Roman Perehinets, WU Vienna MSc  
**Last updated:** End of build session (all pages working, tested through full 6-round run)

---

## 1. Project Location

```
C:\Users\vblah\OneDrive - WU Wien\WU\Master Thesis\Otree\experiment_app\
```

Key files:
- `HumanvsMachine/__init__.py` — all Python logic, models, pages, payoffs
- `HumanvsMachine/*.html` — one template per page
- `payout_referral/__init__.py` + `payout_referral/Payout_Refer_Page.html` — exit redirect to SoSciSurvey
- `settings.py` — oTree config
- `requirements.txt` — `otree==6.0.0b32`, `numpy`, etc.
- `_rooms/wulabs.txt` — participant labels 1–30

---

## 2. Experiment Design

### Roles
- **13 players per group**: 1 Reviewer + 12 Applicants
- Reviewer is always `id_in_group = 1`; applicants are `id_in_group = 2–13`

### Within-subjects counterbalancing
Applicants are split into 4 subgroups (A, B, C, D):
| Subgroup | Part 1 (rounds 1–3) | Part 2 (rounds 4–6) |
|----------|---------------------|---------------------|
| A, C     | HR                  | AR                  |
| B, D     | AR                  | HR                  |

Reviewer always has `dm_type = 'HR'`.

### Credit scores
- Drawn from `N(5.5, 1.8)`, clamped to [1, 10], integer
- Scores 1–3 = **eligible**, 4–10 = **not eligible**
- Only the applicant sees their true score; reviewer sees only the reported score

### Application decision
- **Eligible (1–3):** must apply; true score reported automatically (enforced in code)
- **Not eligible (4–10):** may choose not to apply OR report 1, 2, or 3 (cannot report 4–10)

### Reviewer decision
- Sees reported scores only
- Must audit exactly 1 application per round (reveals true score; decision made automatically)
- Then approves/rejects remaining applications

### Automated Algorithm (AR condition)
- 1 random AR applicant is audited deterministically (approved iff true score ≤ 3)
- Remaining AR applicants: approved with 60% probability (`BOT_APPROVAL_RATE`)

### Payoff constants
```python
BASE_TOKENS = 10

# Applicant
ELIGIBLE_APPROVED   = +2   # eligible applicant approved
ELIGIBLE_REJECTED   =  0   # eligible applicant rejected
LIE_APPROVED        = +2   # not-eligible applicant approved
LIE_REJECTED        = -1   # not-eligible applicant rejected
HONEST_NO_APPLY     =  0   # did not apply

# Reviewer (one randomly selected application per round)
REVIEWER_CORRECT_APPROVAL = +2   # approved eligible applicant
REVIEWER_WRONG_REJECTION  = -2   # rejected eligible applicant
REVIEWER_CAUGHT_LIAR      = +3   # rejected not-eligible applicant
REVIEWER_APPROVED_LIAR    = -3   # approved not-eligible applicant
```

### Final payment
- One round randomly selected from all 6
- **Applicants:** tokens from selected round + Balloon task earnings + Estimation Bonus (€2, if winner)
- **Reviewer:** tokens from selected round + Balloon task earnings
- Rate: 1 token = €1

### Estimation Bonus
- After experiment, one round selected
- The 4 participants across the session with the closest `audit_guess` to the true audit probability each win €2
- Implemented in `ThankYou.vars_for_template` → `session.vars['bonus_winners']`
- 1 winner per subgroup (A, B, C, D)

### BART / Balloon Task
- 10 balloons; pump earns €0.05/pump; hidden explosion point (up to 20 pumps)
- Fixed explosion sequence: `[19, 7, 13, 16, 11, 8, 5, 3, 4, 14]`
- **Both applicants AND reviewer complete it** (so reviewer finishes at the same time, preventing identification)
- Entirely client-side (no `live_method`); results submitted as JSON via form field

---

## 3. Page Sequence

```
Welcome
DemographicsAndMES        (round 1 only)
ExperimentDetails1        (round 1 only)
ExperimentDetails2        (round 1 only)
ApplicantRoleIntro        (round 1 only, applicants only)
ReviewerRoleIntro         (round 1 only, reviewer only)
ComprehensionCheck1       (round 1 only)
ComprehensionCheck2       (round 1 only)
ComprehensionCheck3       (round 1 only)
GroupFormationWait        (round 1 only — WaitPage, wait_for_all_groups=True)
PartIntro                 (rounds 1 and 4, both roles — shows HR/AR for current part)
CreditScoreAndAuditGuess  (applicants only — shows credit score + audit_guess field)
ApplicationDecision       (applicants only — form-based, app_choice field)
WaitForApplicants         (reviewer only — WaitPage)
ReviewerDecision          (reviewer only — form-based, reviewer_decisions_json)
DecisionWait              (all — WaitPage, after_all_players_arrive=set_payoffs)
RoundResults              (all)
TransitionPart2           (round 3 only — transition screen between parts)
BARTIntro                 (round 6 only, both roles)
BARTPage                  (round 6 only, both roles — form-based, bart_results_json)
ThankYou                  (round 6 only)
  → then payout_referral app (SoSciSurvey redirect)
```

---

## 4. Key Python Architecture

### `PARTICIPANT_FIELDS`
```python
PARTICIPANT_FIELDS = ['role', 'applicant_group']
```
- `participant.role`: `'Applicant'` or `'Reviewer'`
- `participant.applicant_group`: `'A'`, `'B'`, `'C'`, `'D'`, or `None` (reviewer)

### `SESSION_FIELDS`
```python
SESSION_FIELDS = ['selected_round', 'bonus_winners']
```

### `creating_session`
- Round 1: assigns roles + subgroups to all players
- Every round: sets `dm_type`, `applicant_group`, draws `true_credit_score` for applicants

### `get_condition(player)` → `'HR'` or `'AR'`
- Reviewer always returns `'HR'`
- Applicants: A/C get HR first, B/D get AR first

### `set_payoffs(group)` — called at DecisionWait
1. Runs `process_ar_decisions(group)` for AR applicants
2. Sets `true_audit_probability` per subgroup
3. Calls `calculate_applicant_tokens(p)` for each applicant
4. Calls `calculate_reviewer_tokens(reviewer, group)`

### `ApplicationDecision` page
- Uses `form_fields = ['app_choice']`
- `app_choice` values: `'eligible'` (hidden input, auto), `'no_apply'`, `'1'`, `'2'`, `'3'`
- `before_next_page` interprets choice → sets `did_apply` and `reported_credit_score`
- `error_message` enforces selection for not-eligible players

### `ReviewerDecision` page
- Uses `form_fields = ['reviewer_decisions_json']`
- True scores embedded in JS (`var trueScores = {...}`)
- All approve/reject buttons **disabled until audit is done**
- `submitDecisions()` serialises `{audited_id, decisions}` → hidden field → form submit
- `before_next_page` parses JSON → sets `is_approved` and `was_audited` on each applicant

### `BARTPage` page
- Uses `form_fields = ['bart_results_json']`
- Explosion logic fully client-side using `EXPLOSION_POINTS = [19,7,13,16,11,8,5,3,4,14]`
- `before_next_page` parses JSON → sets `bart_pumps_b1..10`, `bart_exploded_b1..10`, `bart_total_euros`, `bart_aapumps`

---

## 5. Player Model Fields

```python
# Identity
consent               BooleanField (blank=True, not in page_sequence)
applicant_group       StringField  (blank='')
dm_type               StringField  (blank='')

# Credit / application
true_credit_score     IntegerField (min=1, max=10, blank=True)
reported_credit_score IntegerField (min=0, max=10, blank=True, initial=0)
did_apply             BooleanField (initial=False)
is_approved           BooleanField (blank=True)
was_audited           BooleanField (initial=False)
round_tokens          IntegerField (initial=10)
app_choice            StringField  (blank='')          # ApplicationDecision form
reviewer_decisions_json LongStringField (blank='')    # ReviewerDecision form

# Audit estimate
audit_guess            IntegerField (min=0, max=100, blank=True)
true_audit_probability FloatField   (initial=0.0)
won_guessing_bonus     BooleanField (initial=False)

# Demographics (round 1)
age    IntegerField
gender StringField  (RadioSelect)
ai_use StringField  (RadioSelect)

# MES (10 entities, 0–3, RadioSelectHorizontal)
mes_family, mes_coworker, mes_president, mes_official, mes_ai,
mes_refugee, mes_fraudster, mes_dolphin, mes_chicken, mes_appletree

# Comprehension checks
comp_q1  StringField (RadioSelect)
comp_q2  StringField (RadioSelect)
comp_q3  StringField (RadioSelect)

# BART / Balloon task
bart_pumps_b1..b10     IntegerField (initial=0)
bart_exploded_b1..b10  BooleanField (initial=False)
bart_total_euros       FloatField   (initial=0.0)
bart_aapumps           FloatField   (initial=0.0)
bart_results_json      LongStringField (blank='')     # BARTPage form
```

---

## 6. Template Engine Constraints (oTree 6)

oTree 6 uses its own minimal template engine — **not** Jinja2. Known limitations:
- **No** `{% set %}` with list/tuple literals
- **No** inline Python ternary in `{{ }}` — precompute in `vars_for_template`
- **No** Jinja2 filters like `"%.2f"|format(val)` — use Python `'%.2f' % val`
- **No** `forloop.last` — hardcode arrays or pre-format in Python
- **No** `{% set %}` inside loops
- **Yes** `{% if %}`, `{% for %}`, `{{ var }}`, `{% if not var %}` all work

### `live_method` (WebSocket) — known issue
The `live_method` feature requires:
1. `liveRecv` defined as a **global function**: `function liveRecv(data){...}` — NOT a callback passed to `liveRecv(...)`
2. `liveSend(...)` called only **after** `DOMContentLoaded`

Due to this issue being discovered late, all interactive pages were converted to **form-based submission** instead:
- `ApplicationDecision` → `form_fields=['app_choice']`
- `ReviewerDecision` → `form_fields=['reviewer_decisions_json']`
- `BARTPage` → `form_fields=['bart_results_json']`

All work correctly. If you ever want to revert to live_method, use the documented syntax above.

### Null-field access
oTree raises `TypeError` when accessing a field with `blank=True` that is `None`. Always use:
```python
player.field_maybe_none('field_name')
```
for fields that may legitimately be `None` (e.g., `is_approved` for players who didn't apply, `audit_guess` for the reviewer).

---

## 7. File Inventory

### `HumanvsMachine/` templates
| File | Purpose | Displayed to |
|------|---------|-------------|
| `Welcome.html` | Welcome + anonymity + token info | All, round 1 |
| `DemographicsAndMES.html` | Age, gender, AI use, 10-item MES | All, round 1 |
| `ExperimentDetails1.html` | Roles, credit score system, reviewer types, structure | All, round 1 |
| `ExperimentDetails2.html` | 5-column payoff tables, audits, payment | All, round 1 |
| `ApplicantRoleIntro.html` | Applicant procedure, estimation bonus | Applicants, round 1 |
| `ReviewerRoleIntro.html` | Reviewer procedure, tip, payment | Reviewer, round 1 |
| `ComprehensionCheck1.html` | Q: who sees true score | All, round 1 |
| `ComprehensionCheck2.html` | Q: eligibility threshold | All, round 1 |
| `ComprehensionCheck3.html` | Q: payment round | All, round 1 |
| `PartIntro.html` | Part 1 / Part 2 start screen (HR/AR info) | All, rounds 1 & 4 |
| `CreditScoreAndAuditGuess.html` | Shows credit score + audit estimate input | Applicants, every round |
| `ApplicationDecision.html` | Apply / not apply decision | Applicants, every round |
| `ReviewerDecision.html` | Audit + approve/reject table | Reviewer, every round |
| `RoundResults.html` | Round outcome + token earnings | All, every round |
| `TransitionPart2.html` | End of Part 1 / start Part 2 screen | All, round 3 |
| `BARTIntro.html` | Balloon task instructions | All, round 6 |
| `BARTPage.html` | Interactive balloon task | All, round 6 |
| `ThankYou.html` | Final payment summary | All, round 6 |

### `payout_referral/`
| File | Purpose |
|------|---------|
| `__init__.py` | Single page app; passes `pid` to SoSciSurvey |
| `Payout_Refer_Page.html` | Auto-redirects after 10 s; **replace `YOUR_PROJECT_NAME`** with real URL |

---

## 8. Pending / Open Items

### Must do before running:
1. **SoSciSurvey URL** — open `payout_referral/Payout_Refer_Page.html` and replace:
   ```javascript
   var SOSCI_URL = 'https://soscisurvey.wu.ac.at/YOUR_PROJECT_NAME/';
   ```
   with your actual survey URL. Follow the GitHub instructions at:
   `julianquandt/wulabs_soscisurvey_banktransfer_template`
   Upload `wulabs_bank_transfer_template_eng.xml` to SoSciSurvey, set an Administration Period, and use the resulting link.

2. **Database reset** — whenever the Player model changes (new fields added), the oTree database must be reset: Admin panel → "Reset DB" or restart with a fresh SQLite file.

### Already working (tested):
- Full 6-round run with 13 participants (1 reviewer + 12 applicants) ✓
- HR and AR conditions ✓
- Application decisions (eligible + not-eligible paths) ✓
- Reviewer audit + approve/reject with enforce-audit-first UI ✓
- Payoff calculation for all cases including `is_approved=None` (no-apply) ✓
- BART / Balloon task for both roles ✓
- Estimation bonus winner calculation ✓
- ThankYou page for both roles ✓
- PartIntro screen at start of each part ✓
- TransitionPart2 screen ✓

### Known design decisions made during build:
- `live_method` replaced with form-based approach throughout (more reliable)
- True credit scores embedded in `ReviewerDecision.html` JS for client-side audit reveal (acceptable for controlled lab setting)
- BART explosion points are fixed constants (not randomised per session)
- Consent page exists in the model but is **removed from page_sequence** (participants sign paper consent beforehand)

---

## 9. Running the Experiment

```bash
cd "C:\Users\vblah\OneDrive - WU Wien\WU\Master Thesis\Otree\experiment_app"
# activate venv first, then:
otree devserver        # development
otree prodserver       # production
```

Room: **wulabs** (26 labels in `_rooms/wulabs.txt`)  
Session config: `HumanvsMachine` with `num_demo_participants=26`

For a real session: Admin → Rooms → wulabs → Create session → `num_participants=26`

---
