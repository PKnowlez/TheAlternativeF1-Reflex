# Walkthrough: Full Season Prediction Options (TAF1APP-SDDFEAT-16)

## Summary of Implementation
We executed the **Execution Prompt - Updated** for feature **TAF1APP-SDDFEAT-16 (Predictions Market Tab)**, introducing the new **Full Season Prediction Options** alongside the existing Next Race prediction market capabilities.

All 20 downstream requirements for this feature have a verified status of **Approved (ID: 293)**.

---

## Key Features & Requirements Implemented

### 1. [TAF1APP-SDDREQ-171] Next Race vs. Full Season Option
- Added a two-option segmented control button (`Next Race` vs `Full Season`) styled identically to the Single Prediction vs Parlay Prediction toggle in the Submit a Prediction modal.
- Switching between `Next Race` and `Full Season` dynamically reconfigures the available categories, prediction targets, stance options, and payout multipliers without closing the modal.

### 2. [TAF1APP-SDDREQ-172] Full Season Wager Options
- Supported both **Single Prediction** and **Parlay Prediction** for Full Season wagers:
  - **Constructor Champion**: Prediction target includes all active Season 5 constructors (`Audi`, `Cadillac`, `Ferrari`, `Haas`, `McLaren`, `Mercedes`, `Red Bull`, `Williams`); stance allows `FOR` or `AGAINST`.
  - **Top 3 Constructor**: Prediction target includes all active Season 5 constructors; stance allows `FOR` or `AGAINST`.
  - **Constructor Champion Win Margin**: Prediction target offers brackets in tens (`1-10 pts`, `11-20 pts`, ..., `150+ pts`); no stance required (stance input hidden, displays as neutral `—`).
  - **Driver Champion**: Prediction target includes all active Season 5 drivers (`Boz`, `Brently`, `Del`, `Eddie`, `Evelo`, `Grayson`, `Jaden`, `Jairo`, `Josh`, `Josh C.`, `Joshua`, `Leo`, `Matthew`, `Nick`, `Patrick`, `Randy`); stance is locked to `FOR` only.
  - **Top 3 Driver**: Prediction target includes all active Season 5 drivers; stance is locked to `FOR` only.
  - **Driver Champion Win Margin**: Prediction target offers brackets in tens (`1-10 pts`, `11-20 pts`, ..., `150+ pts`); no stance required.
- In Parlay mode, each leg dynamically adapts its category, target options, and stance rules based on whether the leg is targeting constructors, drivers, or win margin points.

### 3. [TAF1APP-SDDREQ-173] Full Season Wager Payout & Multiplier
- Implemented the exact full season payout equations factoring in remaining non-sprint feature races at submission time:
  - **Single Wager**:
    - Incorrect: 0 payout.
    - Correct: `Wager + (Wager * (0.15 + (<# of races remaining> * 0.1)))`
  - **Parlay Wager**:
    - Miss: 0 payout.
    - All legs hit: `Wager + (Wager * (0.15 + (<# of legs> * 0.1) + (<# of races remaining> * 0.1)))`
- Added real-time boost badges inside the modal displaying the live boost percentage and potential payout preview for both Single and Parlay wagers.
- Integrated automated end-of-season settlement in `settle_completed_predictions` when feature races conclude.

### 4. [TAF1APP-SDDREQ-174] Full Season Indicator
- In the Submitted Predictions table, all full season predictions display with `[Full Season]` prefixed before the category name (e.g., `[Full Season] Constructor Champion`, `[Full Season] Driver Champion`, `[Full Season] Parlay (2 Legs)`).
- Table displays driver constructor colors, team colored indicators, and remaining feature race counts under the Line column (`12 races rem.`).

---

## File Changes
- [`the_alternative_f1/seasons/predictions_market.py`](file:///c:/Users/pacma/OneDrive/Documents/Antigravity%20Coding/TheAlternativeF1-Reflex/the_alternative_f1/seasons/predictions_market.py):
  - Added helpers: `get_active_constructors`, `get_active_drivers`, `get_driver_constructor`, `get_remaining_feature_races`, `WIN_MARGIN_OPTIONS`.
  - Added state properties & event handlers: `wager_scope`, `set_wager_scope`, `target_label`, `has_stance`, `is_stance_for_only`, `current_leg_target_options`, `current_leg_target_label`, `current_leg_has_stance`, `current_leg_is_stance_for_only`.
  - Added live preview calculations: `remaining_feature_races_count`, `full_season_single_multiplier_pct`, `full_season_single_payout_preview`, `full_season_parlay_multiplier_pct`, `full_season_parlay_payout_preview`.
  - Updated `submit_prediction` to store `[Full Season]` category tags and remaining feature races.
  - Added full season settlement engine in `settle_completed_predictions`.
  - Updated `_submit_prediction_modal` with Wager Scope control, dynamic target labels, conditional stance controls, and live payout boost callouts.
  - Updated `all_predictions_list` to enforce `[Full Season]` in the Category column and format line/target displays.

---

## Manual Verification Steps for User
1. Navigate to the **Predictions Market** tab.
2. Ensure you are logged in with Discord (100 Alternative Points granted on first login).
3. Click the blue **Submit a Prediction** button:
   - Notice the two option buttons at the top: `[Next Race | Full Season]` and `[Single Prediction | Parlay Prediction]`.
   - Toggle to **Full Season**:
     - Verify Stat Categories dropdown displays the 6 options (`Constructor Champion`, `Top 3 Constructor`, `Constructor Champion Win Margin`, `Driver Champion`, `Top 3 Driver`, `Driver Champion Win Margin`).
     - Select `Driver Champion`: verify target dropdown switches to active drivers and stance displays `FOR (Only Option)`.
     - Select `Constructor Champion Win Margin`: verify target dropdown displays point brackets (`1-10 pts`, `11-20 pts`, etc.) and the stance selector is omitted.
     - Notice the Full Season Boost badge displays `+135%` (12 remaining feature races) with the calculated potential win.
   - Switch to **Parlay Prediction**:
     - Verify legs can configure full season categories.
     - Notice the Full Season Parlay Boost badge displays `+155%` (2 legs + 12 remaining feature races).
4. Submit a Full Season wager:
   - Expand the **Submitted Predictions** table.
   - Verify the Category column shows `[Full Season] <Category>` (e.g. `[Full Season] Constructor Champion`).
   - Verify the Line column shows `12 races rem.`.
