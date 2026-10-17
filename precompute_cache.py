"""Precompute and serialize all static data and analytical calculations locally.

Run this script on your local computer before running 'reflex deploy'.
It generates and serializes:
  - calculations_cache.pickle (Season 1-5 Calculations, race totals, driver totals)
  - detailed_cache.pickle (Detailed driver and constructor career records & positions)
  - power_rankings.json (Pre-calculated power rankings)
  - predictions.json (Predictions market data)
  - leaderboard.json (Fantasy leaderboard points)
  - grounded_deep_stats.json (Structured AI league grounding context)

This completely eliminates the 10-minute server startup calculation on Reflex Cloud,
allowing the deployed app to boot and hydrate in milliseconds.
"""

import sys
import os
import time
from pathlib import Path

def main():
    start_time = time.time()
    print("=" * 70)
    print("STARTING LOCAL LEAGUE DATA PRECOMPUTATION & CACHING")
    print("=" * 70)

    # 1. Warm up season calculations
    print("\n[1/5] Calculating Season Results (Seasons 1-5)...")
    t0 = time.time()
    from the_alternative_f1.seasons import seasons
    from the_alternative_f1.seasons.Calculations import Calculations, save_calculations_cache, _calculations_cache
    for s in seasons:
        Calculations(s, sprint_only=False)
        Calculations(s, sprint_only=True)
    save_calculations_cache()
    calc_path = Path("the_alternative_f1/seasons/calculations_cache.pickle")
    calc_size = calc_path.stat().st_size // 1024 if calc_path.exists() else 0
    print(f"  -> Saved calculations_cache.pickle ({calc_size} KB) in {time.time() - t0:.2f}s")

    # 2. Warm up all-time detailed statistics
    print("\n[2/5] Calculating All-Time Detailed Driver & Constructor Metrics...")
    t0 = time.time()
    from the_alternative_f1.all_time_stats.DetailedAllTime import (
        get_entity_lists,
        compute_entity_detailed_metrics,
        save_detailed_cache,
    )
    drivers, teams = get_entity_lists(len(seasons))
    for d in drivers:
        compute_entity_detailed_metrics(len(seasons), "Driver", d)
    for t in teams:
        compute_entity_detailed_metrics(len(seasons), "Constructor", t)
    save_detailed_cache()
    det_path = Path("the_alternative_f1/all_time_stats/detailed_cache.pickle")
    det_size = det_path.stat().st_size // 1024 if det_path.exists() else 0
    print(f"  -> Saved detailed_cache.pickle ({det_size} KB) in {time.time() - t0:.2f}s")

    # 3. Precompute Power Rankings, Projections & Predictions
    print("\n[3/5] Syncing Power Rankings, Predictions, and Projections...")
    t0 = time.time()
    from the_alternative_f1.the_alternative_f1 import (
        precompute_all_power_rankings,
        precompute_all_season_projections,
        precompute_all_predictions,
        precompute_leaderboard_cache,
    )
    precompute_all_power_rankings(force=True)
    precompute_all_season_projections()
    precompute_all_predictions()
    precompute_leaderboard_cache(force=True)
    print(f"  -> JSON state datasets synced in {time.time() - t0:.2f}s")

    # 4. Map Data & Teammate Networks
    print("\n[4/5] Precomputing Map & Teammate Network Visualizations...")
    t0 = time.time()
    from the_alternative_f1.all_time_stats.MapAllTime import precompute_all_map_data
    from the_alternative_f1.all_time_stats.SummaryAllTime import precompute_summary_data
    from the_alternative_f1.all_time_stats.TeammateNetwork import build_teammate_network_data
    from the_alternative_f1.all_time_stats.Functions import get_all_time_highest_positions, CalculateAllTime, PointTotals
    precompute_all_map_data()
    precompute_summary_data(num_seasons=len(seasons))
    build_teammate_network_data()
    get_all_time_highest_positions(num_seasons=len(seasons))
    CalculateAllTime(len(seasons), "Driver")
    CalculateAllTime(len(seasons), "Team")
    for s_idx in range(1, len(seasons) + 1):
        PointTotals(s_idx)
    print(f"  -> Maps and historical matrices compiled in {time.time() - t0:.2f}s")

    # 5. Grounded Intelligence Context
    print("\n[5/5] Re-compiling Alternative Intelligence Grounded Context...")
    t0 = time.time()
    from the_alternative_f1.alternative_intelligence import reload_grounded_league_context
    reload_grounded_league_context()
    print(f"  -> Grounded deep stats and context compiled in {time.time() - t0:.2f}s")

    total_time = time.time() - start_time
    print("\n" + "=" * 70)
    print(f"SUCCESS: Precomputed cache ready for deployment in {total_time:.2f} seconds.")
    print("You can now safely run: reflex deploy")
    print("=" * 70)

if __name__ == "__main__":
    main()
