# Tasks Executed: Full Season Prediction Options (TAF1APP-SDDFEAT-16)

1. **Requirements Discovery & Cache Refresh**:
   - Pulled downstream requirements for `TAF1APP-SDDFEAT-16` using the Jama Connect REST API suite.
   - Identified 4 new Approved requirements: `TAF1APP-SDDREQ-171` (Next Race vs. Full Season Option), `TAF1APP-SDDREQ-172` (Full Season Wager Options), `TAF1APP-SDDREQ-173` (Full Season Wager Payout & Multiplier), and `TAF1APP-SDDREQ-174` (Full Season Indicator).
   - Verified that all 20 downstream requirements have Approved status (ID: 293).

2. **Data & Helper Layer Updates**:
   - Added active drivers retriever (`get_active_drivers`) and active constructors retriever (`get_active_constructors`) querying Season 5 roster data.
   - Added `get_driver_constructor` to map drivers to their team colors for table rendering.
   - Added `get_remaining_feature_races` to calculate remaining non-sprint feature races for Season 5.
   - Defined `WIN_MARGIN_OPTIONS` spanning `1-10 pts` through `150+ pts`.

3. **State Management (`PredictionsMarketState`)**:
   - Implemented `wager_scope` property (`"next_race"` vs `"full_season"`) and `set_wager_scope` event handler.
   - Updated `category_options` to return the 6 Full Season categories when `wager_scope == "full_season"`.
   - Updated `target_options` and `target_label` to dynamically provide active drivers, active constructors, or win margin point brackets based on selected category.
   - Updated `stance_options`, `has_stance`, and `is_stance_for_only` according to SDDREQ-172 rules (constructors: FOR/AGAINST; drivers: FOR only; win margins: no stance).
   - Extended Parlay functionality to support Full Season legs, with dynamic per-leg target and stance options.
   - Implemented Full Season payout equations and multipliers for both Single and Parlay wagers per SDDREQ-173:
     - Single: `Wager + (Wager * (0.15 + (remaining_races * 0.1)))`
     - Parlay: `Wager + (Wager * (0.15 + (num_legs * 0.1) + (remaining_races * 0.1)))`
   - Added live preview properties: `full_season_single_multiplier_pct`, `full_season_single_payout_preview`, `full_season_parlay_multiplier_pct`, `full_season_parlay_payout_preview`.

4. **Submission & Storage (`submit_prediction`)**:
   - Prepend `[Full Season]` to the category name for all full season single and parlay wagers per SDDREQ-174.
   - Store the count of remaining feature races at the time of submission in `line_value` for lossless calculation.
   - Preserve Supabase table schema compatibility.

5. **Settlement Engine Updates (`settle_completed_predictions`)**:
   - Added full season settlement when all feature races have completed.
   - Tabulated final constructor and driver standings (main + sprint points) and win margins.
   - Evaluated Full Season single and parlay bets and distributed winnings with correct multipliers.

6. **UI Components (`_submit_prediction_modal` & Submitted Predictions Table)**:
   - Added the two-option segmented control button for `Next Race` vs `Full Season` (SDDREQ-171).
   - Displayed dynamic target labels and conditional stance controls in both Single and Parlay views.
   - Added Full Season boost preview callout boxes displaying remaining feature race counts and potential win amounts.
   - Formatted Submitted Predictions table to display `[Full Season]` in the Category column (SDDREQ-174) with driver-team color indicators and remaining races.

7. **Documentation & Traceability**:
   - Published SDD Implementation Summary to Jama Set 9281 linked to Feature 10567 and all approved downstream requirements.
