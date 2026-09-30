# Implementation Plan: Predictions Market Tab (TAF1APP-SDDFEAT-16) - Full Season Prediction Options

## Overview & Scope
Incorporate approved requirements **TAF1APP-SDDREQ-171 (Next Race vs. Full Season Option)**, **TAF1APP-SDDREQ-172 (Full Season Wager Options)**, **TAF1APP-SDDREQ-173 (Full Season Wager Payout & Multiplier)**, and **TAF1APP-SDDREQ-174 (Full Season Indicator)** into the Predictions Market Tab for feature **TAF1APP-SDDFEAT-16 (Predictions Market Tab)**.

All 20 downstream requirements for TAF1APP-SDDFEAT-16 have a status of **Approved (ID: 293)**. No requirements are skipped.

Per Execution Prompt rules:
- No diagnostics or automated test suites (e.g. pytest/vitest) are executed.
- Testing is manually completed by the user.
- Upon completion, an SDD Implementation Summary will be created in Jama Set 9281 and linked to Feature 10567 and all approved downstream requirements.

---

## Approved Requirements Addressed

### 1. [TAF1APP-SDDREQ-171] Next Race vs. Full Season Option
- The application shall provide the user a two option button (same as the single prediction / parlay prediction two option button) for next race and full season wagers.
- Styled consistently using cyan segmented control in the Submit a Prediction modal: `["Next Race", "Full Season"]`.

### 2. [TAF1APP-SDDREQ-172] Full Season Wager Options
- The application shall provide the user with the following options for a full season wager:
  - Single Prediction or Parlay Prediction (same as in a next race wager)
  - **Constructor Champion**: prediction target = all active constructors as options, stance = for/against
  - **Top 3 Constructor**: prediction target = all active constructors as options, stance = for/against
  - **Constructor Champion Win Margin**: prediction target = points by tens (`1-10 pts`, `11-20 pts`, ..., `150+ pts`), no stance
  - **Driver Champion**: prediction target = all active drivers as options, stance = for only
  - **Top 3 Driver**: prediction target = all active drivers as options, stance = for only
  - **Driver Champion Win Margin**: prediction target = points by tens (`1-10 pts`, `11-20 pts`, ..., `150+ pts`), no stance

### 3. [TAF1APP-SDDREQ-173] Full Season Wager Payout & Multiplier
- Replace standard next race payout logic with full season multipliers based on remaining feature races (excluding sprints):
  - **Single Wager**:
    - If missed: 0 payout
    - If correct: `Wager + (Wager * (0.15 + (<# of races remaining> * 0.1)))`
  - **Parlay Wager**:
    - If any leg missed: 0 payout
    - If all legs hit: `Wager + (Wager * (0.15 + (<# of legs> * 0.1) + (<# of races remaining> * 0.1)))`
- Submitting records the count of remaining feature races (`len(remaining_feature_races)`) at the time of submission.
- Real-time preview badges in modal calculate and display the exact boost percentage and potential payout.

### 4. [TAF1APP-SDDREQ-174] Full Season Indicator
- The application shall indicate if the wager is full season in the Category column of the Submitted Predictions table by including `[Full Season]` before the category name (e.g. `[Full Season] Constructor Champion`, `[Full Season] Parlay (2 Legs)`).

---

## Technical Architecture & State Updates

1. **State Management (`PredictionsMarketState`)**:
   - `wager_scope`: `"next_race"` vs `"full_season"` (defaults to `"next_race"`).
   - Dynamic `category_options`: returns standard categories when `"next_race"`, and the 6 full season categories when `"full_season"`.
   - Dynamic `target_options`: switches between active constructors, active drivers, and win margin point brackets (`1-10 pts` through `150+ pts`).
   - Dynamic `stance_options`: switches between `["FOR", "AGAINST"]` (constructors), `["FOR"]` (drivers), and hidden/`—` (win margins).
   - Parlay support for Full Season: legs configure full season categories, targets, and stances with multi-leg full season payout calculation.
   - Live boost & preview calculations: `full_season_single_multiplier_pct`, `full_season_single_payout_preview`, `full_season_parlay_multiplier_pct`, `full_season_parlay_payout_preview`.

2. **Submission & Storage (`submit_prediction`)**:
   - For Full Season single: prepends `[Full Season]` to the category name, stores remaining feature race count in `line_value` for schema safety.
   - For Full Season parlay: names category `[Full Season] Parlay (<N> Legs)`, embeds enriched leg dicts in JSON target, stores remaining feature race count in `line_value`.
   - Preserves Supabase compatibility without altering existing database table schema.

3. **Settlement Engine (`settle_completed_predictions`)**:
   - Auto-detects season completion (`len(remaining_feature_races) == 0`).
   - Computes final constructor and driver standings (main + sprint points) and win margins.
   - Evaluates full season single and parlay wagers against final season outcomes and awards calculated payouts.

4. **UI Presentation (`_submit_prediction_modal` & Submitted Predictions Table)**:
   - Adds the Scope segmented control button (`Next Race` / `Full Season`) matching the Prediction Mode control (`Single Prediction` / `Parlay Prediction`).
   - Dynamic target input labels (`(DRIVER)`, `(CONSTRUCTOR)`, `(POINTS WIN MARGIN)`).
   - Full Season boost badges with live breakdown of remaining races and leg boosts.
   - Submitted Predictions table displays `[Full Season]` in the Category column, displays driver constructor colors, and displays remaining races under Line.
