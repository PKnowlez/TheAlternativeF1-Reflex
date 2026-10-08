"""Alternative Intelligence: Analytical AI-powered search and assistant for The Alternative F1.

Strictly grounded exclusively on data from the deployed version of the application.
Adheres to Jama specifications:
- TAF1APP-SDDFEAT-26: Alternative Intelligence - Gemini Search
- TAF1APP-SDDREQ-228: DEFINITION: Alternative Intelligence
- TAF1APP-SDDREQ-229: DEFINITION: Grounded League Context
- TAF1APP-SDDREQ-230 to SDDREQ-245: Functional requirements
"""

import os
import re
import json
import time
import httpx
from pathlib import Path
from typing import AsyncGenerator
from pydantic import BaseModel
import reflex as rx
import pandas as pd
from the_alternative_f1.constructor_colors import get_constructor_color

# Cache storage for grounded league context and working models
_GROUNDED_CONTEXT_CACHE = ""
_GROUNDED_CONTEXT_MTIME = 0
_CACHE_TIMESTAMP = 0
_WORKING_GEMINI_MODEL = None


def get_contrast_text_color(hex_color: str) -> str:
    """Return #000000 (black) for light/yellow colors or #FFFFFF (white) for dark colors."""
    if not hex_color:
        return "#FFFFFF"
    c = str(hex_color).strip().lower()
    if c in ("#ffea00", "yellow", "#e0e0e0", "#ffffff", "white", "#ffcc00", "#ffd700", "#fd4bc7"):
        return "#000000"
    if c.startswith("#") and len(c) == 7:
        try:
            r = int(c[1:3], 16)
            g = int(c[3:5], 16)
            b = int(c[5:7], 16)
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            if lum > 165:
                return "#000000"
        except Exception:
            pass
    return "#FFFFFF"


def get_driver_most_recent_constructor(driver_name: str) -> tuple[str, str]:
    """Retrieve the most recent constructor and color for a driver across official seasons."""
    if not driver_name:
        return "Independent", "#555555"
    d_clean = driver_name.strip().lower()
    try:
        from the_alternative_f1.seasons import seasons
        from the_alternative_f1.seasons.Calculations import Calculations
        for s in reversed(seasons):
            calc = Calculations(s)
            raw_df = calc.get("df")
            if raw_df is not None and not raw_df.empty:
                for _, r in raw_df.iterrows():
                    d = str(r.get("Driver", "")).strip()
                    if d.lower() == d_clean or d_clean in d.lower():
                        team = str(r.get("Team", "")).strip()
                        if team:
                            return team, get_constructor_color(team)
    except Exception:
        pass
    return "Independent", "#555555"


def compute_h2h_battle_stats(entity1: str, entity2: str, is_constructor: bool = False, seasons_filter=None) -> dict:
    """Deterministically compute Head-to-Head battle statistics across official league race records.
    
    When seasons_filter is not provided, automatically restricts the comparison scope to the
    SHARED SEASONS where BOTH entities competed in at least one race.
    """
    e1_clean = entity1.strip().lower()
    e2_clean = entity2.strip().lower()

    qual1, qual2 = 0, 0
    race1, race2 = 0, 0
    pod1, pod2 = 0, 0
    pts1, pts2 = 0.0, 0.0
    win1, win2 = 0, 0

    try:
        from the_alternative_f1.seasons import seasons
        from the_alternative_f1.seasons.Calculations import Calculations

        # 1. Determine target seasons (Shared Seasons by default)
        if seasons_filter:
            target_seasons = [s for s in seasons if s.get("season_number") in seasons_filter]
            s_nums = [s.get("season_number") for s in target_seasons]
            if len(s_nums) == 1:
                seasons_label = f"Season {s_nums[0]}"
            else:
                seasons_label = f"Seasons {', '.join(str(n) for n in s_nums)}"
        else:
            shared_seasons = []
            for s in seasons:
                calc = Calculations(s)
                df = calc.get("df")
                if df is None or df.empty:
                    continue
                if is_constructor:
                    has_1 = not df[df["Team"].astype(str).str.strip().str.lower() == e1_clean].empty
                    has_2 = not df[df["Team"].astype(str).str.strip().str.lower() == e2_clean].empty
                else:
                    has_1 = not df[df["Driver"].astype(str).str.strip().str.lower() == e1_clean].empty
                    has_2 = not df[df["Driver"].astype(str).str.strip().str.lower() == e2_clean].empty
                if has_1 and has_2:
                    shared_seasons.append(s)

            if shared_seasons:
                target_seasons = shared_seasons
                s_nums = [s.get("season_number") for s in target_seasons]
                if len(s_nums) == 1:
                    seasons_label = f"Shared Season (Season {s_nums[0]})"
                else:
                    seasons_label = f"Shared Seasons (Seasons {' & '.join(str(n) for n in s_nums)})"
            else:
                target_seasons = seasons
                seasons_label = "All Seasons"

        # 2. Compute exact statistics across target seasons
        for s in target_seasons:
            calc = Calculations(s)
            df = calc.get("df")
            races = calc.get("races", [])
            index_x = calc.get("index_x", 0)
            num_completed = max(0, int(index_x + 0.5))

            if df is None or df.empty:
                continue

            if is_constructor:
                c_totals = calc.get("constructor_totals")
                if c_totals is not None and not c_totals.empty:
                    r1 = c_totals[c_totals["Team"].astype(str).str.strip().str.lower() == e1_clean]
                    r2 = c_totals[c_totals["Team"].astype(str).str.strip().str.lower() == e2_clean]
                    if not r1.empty:
                        pts1 += float(r1.iloc[0].get("Points", 0))
                    if not r2.empty:
                        pts2 += float(r2.iloc[0].get("Points", 0))

                for r_name in races[:num_completed]:
                    c_pre = r_name.replace(" Sprint", "Sprint")
                    p_col = f"{c_pre}Place"
                    if p_col in df.columns:
                        w_rows = df[df[p_col] == 1]
                        if not w_rows.empty:
                            w_t = str(w_rows.iloc[0].get("Team", "")).strip().lower()
                            if w_t == e1_clean:
                                win1 += 1
                            elif w_t == e2_clean:
                                win2 += 1
                        for _, pod_row in df[df[p_col].isin([1, 2, 3])].iterrows():
                            pod_t = str(pod_row.get("Team", "")).strip().lower()
                            if pod_t == e1_clean:
                                pod1 += 1
                            elif pod_t == e2_clean:
                                pod2 += 1
            else:
                d_totals = calc.get("driver_totals")
                if d_totals is not None and not d_totals.empty:
                    r1 = d_totals[d_totals["Driver"].astype(str).str.strip().str.lower() == e1_clean]
                    r2 = d_totals[d_totals["Driver"].astype(str).str.strip().str.lower() == e2_clean]
                    if not r1.empty:
                        pts1 += float(r1.iloc[0].get("Points", 0))
                    if not r2.empty:
                        pts2 += float(r2.iloc[0].get("Points", 0))

                # Exact equality to avoid substring collisions (e.g. Josh vs Joshua vs Josh C. vs Josh L)
                d1_row = df[df["Driver"].astype(str).str.strip().str.lower() == e1_clean]
                d2_row = df[df["Driver"].astype(str).str.strip().str.lower() == e2_clean]

                if d1_row.empty or d2_row.empty:
                    continue

                d1_data = d1_row.iloc[0]
                d2_data = d2_row.iloc[0]

                for r_name in races[:num_completed]:
                    c_pre = r_name.replace(" Sprint", "Sprint")
                    q_col = f"{c_pre}Qualifying"
                    p_col = f"{c_pre}Place"

                    if q_col in df.columns:
                        try:
                            q1_val = float(d1_data.get(q_col))
                            q2_val = float(d2_data.get(q_col))
                            if q1_val > 0 and q2_val > 0:
                                if q1_val < q2_val:
                                    qual1 += 1
                                elif q2_val < q1_val:
                                    qual2 += 1
                        except Exception:
                            pass

                    if p_col in df.columns:
                        try:
                            p1_val = float(d1_data.get(p_col))
                            p2_val = float(d2_data.get(p_col))
                            if p1_val > 0 and p2_val > 0:
                                if p1_val < p2_val:
                                    race1 += 1
                                elif p2_val < p1_val:
                                    race2 += 1
                                if p1_val == 1:
                                    win1 += 1
                                if p2_val == 1:
                                    win2 += 1
                                if p1_val in (1, 2, 3):
                                    pod1 += 1
                                if p2_val in (1, 2, 3):
                                    pod2 += 1
                        except Exception:
                            pass

        pts1_str = f"{pts1:.0f}" if pts1.is_integer() else f"{pts1:.1f}"
        pts2_str = f"{pts2:.0f}" if pts2.is_integer() else f"{pts2:.1f}"

        return {
            "qual1": qual1,
            "qual2": qual2,
            "race1": race1,
            "race2": race2,
            "pod1": pod1,
            "pod2": pod2,
            "pts1": pts1_str,
            "pts2": pts2_str,
            "win1": win1,
            "win2": win2,
            "seasons_label": seasons_label,
        }
    except Exception:
        return {
            "qual1": qual1, "qual2": qual2,
            "race1": race1, "race2": race2,
            "pod1": pod1, "pod2": pod2,
            "pts1": str(pts1), "pts2": str(pts2),
            "win1": win1, "win2": win2,
            "seasons_label": "Shared Seasons",
        }


def compute_champion_campaign_stats(season_num: int = 4, entity_name: str = "", is_constructor: bool = True) -> dict:
    """Deterministically compute championship campaign statistics for an entity in a given season (TAF1APP-SDDREQ-250)."""
    try:
        from the_alternative_f1.seasons import seasons
        from the_alternative_f1.seasons.Calculations import Calculations

        target_season = next((s for s in seasons if s.get("season_number") == season_num), None)
        if target_season is None:
            target_season = seasons[-2]  # Default to season 4 (most recent completed)

        calc = Calculations(target_season)
        df = calc.get("df")
        trt = calc.get("team_race_totals") if is_constructor else calc.get("driver_race_totals")
        idx_x = int(calc.get("index_x", 0) + 0.5)
        races = calc.get("races", [])[:idx_x]
        tot = calc.get("constructor_totals") if is_constructor else calc.get("driver_totals")
        key_col = "Team" if is_constructor else "Driver"

        row_idx = 0
        if entity_name and tot is not None and not tot.empty:
            e_clean = entity_name.strip().lower()
            m = tot[tot[key_col].str.strip().str.lower() == e_clean]
            if m.empty:
                m = tot[tot[key_col].str.strip().str.lower().str.contains(e_clean, regex=False)]
            if not m.empty:
                row_idx = m.index[0]

        if tot is None or tot.empty:
            return {
                "name": entity_name or "Champion",
                "season": f"Season {season_num}",
                "is_constructor": is_constructor,
                "team": entity_name if is_constructor else "",
                "color": "#00b4da",
                "text_color": "#ffffff",
                "points": 0.0,
                "runner_up": "None",
                "margin": 0.0,
                "wins": 0,
                "podiums": 0,
                "poles": 0,
                "fl": 0,
                "cd": 0,
                "dotd": 0,
                "mot": 0,
                "total_accolades": 0,
                "races_led": 0,
                "total_races": len(races),
            }

        champ_name = str(tot.iloc[row_idx][key_col]).strip()
        pts = float(tot.iloc[row_idx]["Points"])

        if row_idx == 0:
            runner_up = str(tot.iloc[1][key_col]).strip() if len(tot) > 1 else "None"
            runner_up_pts = float(tot.iloc[1]["Points"]) if len(tot) > 1 else 0.0
            margin = pts - runner_up_pts
        else:
            runner_up = str(tot.iloc[0][key_col]).strip()
            margin = float(tot.iloc[0]["Points"]) - pts

        if is_constructor:
            color = get_constructor_color(champ_name)
            team_label = champ_name
        else:
            team_label, color = get_driver_most_recent_constructor(champ_name)
        text_color = get_contrast_text_color(color)

        wins, pods, poles, fl, cd, dotd, mot = 0, 0, 0, 0, 0, 0, 0
        e_clean = champ_name.strip().lower()

        if df is not None and not df.empty:
            for r in races:
                c_pre = r.replace(" Sprint", "Sprint")
                p_c = f"{c_pre}Place"
                q_c = f"{c_pre}Qualifying"
                fl_c = f"{c_pre}FastestLap"
                cd_c = f"{c_pre}CD"
                dotd_c = f"{c_pre}DOTD"
                mot_c = f"{c_pre}MOT"

                m_rows = df[df[key_col].str.strip().str.lower() == e_clean]
                for _, row in m_rows.iterrows():
                    if p_c in df.columns:
                        try:
                            p_v = float(row.get(p_c, 0))
                            if p_v == 1:
                                wins += 1
                            if p_v in (1, 2, 3):
                                pods += 1
                        except Exception:
                            pass
                    if q_c in df.columns:
                        try:
                            if float(row.get(q_c, 0)) == 1:
                                poles += 1
                        except Exception:
                            pass
                    if fl_c in df.columns and str(row.get(fl_c, "")).strip().lower() in ("y", "1", "true"):
                        fl += 1
                    if cd_c in df.columns and str(row.get(cd_c, "")).strip().lower() in ("y", "1", "true"):
                        cd += 1
                    if dotd_c in df.columns and str(row.get(dotd_c, "")).strip().lower() in ("y", "1", "true"):
                        dotd += 1
                    if mot_c in df.columns and str(row.get(mot_c, "")).strip().lower() in ("y", "1", "true"):
                        mot += 1

        races_led = 0
        if trt is not None and not trt.empty:
            for col in list(trt.columns)[:idx_x]:
                try:
                    lead = str(trt[col].idxmax()).strip().lower()
                    if lead == e_clean:
                        races_led += 1
                except Exception:
                    pass

        return {
            "name": champ_name,
            "season": f"Season {season_num}",
            "is_constructor": is_constructor,
            "team": team_label,
            "color": color,
            "text_color": text_color,
            "points": pts,
            "runner_up": runner_up,
            "margin": margin,
            "wins": wins,
            "podiums": pods,
            "poles": poles,
            "fl": fl,
            "cd": cd,
            "dotd": dotd,
            "mot": mot,
            "total_accolades": poles + fl + cd + dotd + mot,
            "races_led": races_led,
            "total_races": len(races),
        }
    except Exception:
        return {
            "name": entity_name or "Champion",
            "season": f"Season {season_num}",
            "is_constructor": is_constructor,
            "team": entity_name if is_constructor else "",
            "color": "#00b4da",
            "text_color": "#ffffff",
            "points": 0.0,
            "runner_up": "None",
            "margin": 0.0,
            "wins": 0,
            "podiums": 0,
            "poles": 0,
            "fl": 0,
            "cd": 0,
            "dotd": 0,
            "mot": 0,
            "total_accolades": 0,
            "races_led": 0,
            "total_races": 0,
        }


def sanitize_race_week_terminology(text: str) -> str:
    """
    Guarantees that no form of 'weekend' leaks into user-facing output or prompt context.
    Deterministically transforms real-world F1 weekend terminology into official Alternative F1 race week terminology.
    """
    if not text:
        return text

    def _repl(pattern: str, repl_lower: str, repl_cap: str, src: str) -> str:
        def match_func(m):
            matched = m.group(0)
            if matched[0].isupper():
                return repl_cap
            return repl_lower
        return re.sub(pattern, match_func, src, flags=re.IGNORECASE)

    # 1. off-weekends / off weekends
    text = _repl(r"\boff[- ]weekends\b", "off-weeks", "Off-weeks", text)
    text = _repl(r"\boff[- ]weekend\b", "off-week", "Off-week", text)
    # 2. race weekends / race weekend
    text = _repl(r"\brace weekends\b", "race weeks", "Race weeks", text)
    text = _repl(r"\brace weekend\b", "race week", "Race week", text)
    # 3. Phrasal idioms with weekend
    text = _repl(r"\bover the weekend\b", "during the race week", "During the race week", text)
    text = _repl(r"\bthis weekend\b", "this race week", "This race week", text)
    text = _repl(r"\bnext weekend\b", "next race week", "Next race week", text)
    text = _repl(r"\blast weekend\b", "last race week", "Last race week", text)
    text = _repl(r"\bevery weekend\b", "every race week", "Every race week", text)
    # 4. generic plural / singular weekend
    text = _repl(r"\bweekends\b", "race weeks", "Race weeks", text)
    text = _repl(r"\bweekend\b", "race week", "Race week", text)

    return text


def extract_article_full_text(content_item) -> str:
    """
    Recursively extract human-readable text from an article's content structure.
    Handles raw strings, nested lists, dicts, and Reflex components (rx.box, rx.text, Bare components, etc.).
    Filters out UI controls like 'Download Image' or icons.
    """
    texts = []

    def _recurse(item):
        if item is None:
            return
        if isinstance(item, str):
            clean = " ".join(item.split())
            if clean and clean != "Download Image":
                texts.append(clean)
            return

        if isinstance(item, (list, tuple)):
            for sub in item:
                _recurse(sub)
            return

        if isinstance(item, dict):
            for v in item.values():
                _recurse(v)
            return

        # Skip Reflex image/button UI artifacts
        tag = getattr(item, "tag", "")
        if tag in ("img", "RadixThemesButton", "LucideDownload", "LucideX"):
            return

        # Handle Reflex Bare / Var components with contents
        if hasattr(item, "contents") and item.contents is not None:
            raw = str(item.contents).strip()
            if raw.startswith('"') and raw.endswith('"') and len(raw) >= 2:
                try:
                    raw = json.loads(raw)
                except Exception:
                    raw = raw[1:-1]
            clean = " ".join(str(raw).split())
            if clean and clean != '""' and clean != "Download Image":
                texts.append(clean)

        # Handle Reflex container components with children
        if hasattr(item, "children") and item.children:
            for child in item.children:
                _recurse(child)

    _recurse(content_item)
    return "\n\n".join(texts)


_ALL_LEAGUE_ARTICLES_CACHE: list[dict] = []


def get_all_league_articles() -> list[dict]:
    """Retrieve and cache all published editorial articles across all seasons with their full extracted text."""
    global _ALL_LEAGUE_ARTICLES_CACHE
    if _ALL_LEAGUE_ARTICLES_CACHE:
        return _ALL_LEAGUE_ARTICLES_CACHE

    res = []
    try:
        from the_alternative_f1.seasons import seasons
        for s in seasons:
            s_num = s.get("season_number")
            arts = s.get("articles", [])
            for a in arts:
                t = str(a.get("title", "")).strip()
                d = str(a.get("date", "")).strip()
                auth = str(a.get("author", "")).strip()
                blurb = str(a.get("blurb", "")).strip()
                raw_body = a.get("content", [])
                full_body = extract_article_full_text(raw_body)
                clean_body = sanitize_race_week_terminology(full_body)
                res.append({
                    "season": f"Season {s_num}",
                    "season_num": s_num,
                    "title": t,
                    "date": d,
                    "author": auth,
                    "blurb": blurb,
                    "content": clean_body,
                })

        try:
            from the_alternative_f1.articles.app_intro import article as App_Intro_Article
            if App_Intro_Article:
                res.append({
                    "season": "Platform Launch",
                    "season_num": 0,
                    "title": str(App_Intro_Article.get("title", "")).strip(),
                    "date": str(App_Intro_Article.get("date", "")).strip(),
                    "author": str(App_Intro_Article.get("author", "")).strip(),
                    "blurb": str(App_Intro_Article.get("blurb", "")).strip(),
                    "content": sanitize_race_week_terminology(extract_article_full_text(App_Intro_Article.get("content", []))),
                })
        except Exception:
            pass

    except Exception:
        pass

    _ALL_LEAGUE_ARTICLES_CACHE = res
    return _ALL_LEAGUE_ARTICLES_CACHE


def search_league_articles(query: str, top_k: int = 4) -> list[dict]:
    """
    Search all published league articles against the user's query keywords.
    Ranks articles based on keyword matching across title, blurb, and full body text.
    """
    if not query or len(query.strip()) < 3:
        return []

    articles = get_all_league_articles()
    if not articles:
        return []

    stopwords = {
        "the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "with", "by", "from",
        "of", "is", "was", "are", "were", "did", "does", "do", "has", "have", "had", "he",
        "she", "it", "they", "his", "her", "their", "this", "that", "what", "who", "when",
        "where", "why", "how", "tell", "about", "me", "any", "some", "all", "can", "could",
    }

    raw_tokens = re.findall(r"[A-Za-z0-9]+", query.lower())
    tokens = [t for t in raw_tokens if len(t) > 2 and t not in stopwords]
    if not tokens:
        return []

    scored_articles = []
    for art in articles:
        title_lower = art["title"].lower()
        blurb_lower = art["blurb"].lower()
        content_lower = art["content"].lower()

        score = 0
        q_clean = " ".join(tokens)
        if len(tokens) >= 2 and q_clean in content_lower:
            score += 30

        for tok in tokens:
            if tok in title_lower:
                score += 20
            if tok in blurb_lower:
                score += 10
            count = content_lower.count(tok)
            if count > 0:
                score += min(count * 2, 25)

        if score > 0:
            scored_articles.append((score, art))

    scored_articles.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored_articles[:top_k]]


def format_all_season_articles() -> list[str]:
    """Format all published editorial articles across all seasons for grounded context."""
    lines = []
    lines.append("## COMPLETE LEAGUE EDITORIAL NEWS & ARTICLES ARCHIVE (ALL SEASONS)")
    lines.append(
        "This archive contains all official editorial articles, race recaps, race week previews, "
        "investigative reports, and paddock news published in the league. You have full access to the complete "
        "narrative text, interviews, quotes, driver drama, and lore across all seasons.\n"
    )

    articles = get_all_league_articles()
    from collections import defaultdict
    by_season = defaultdict(list)
    for a in articles:
        by_season[a["season"]].append(a)

    for season_name, arts in by_season.items():
        lines.append(f"### {season_name} Published Articles ({len(arts)} Articles):")
        for a in arts:
            lines.append(f"#### Article: \"{a['title']}\" ({a['season']}, Published: {a['date']} by {a['author']})")
            if a["blurb"]:
                lines.append(f"Blurb: {a['blurb']}")
            if a["content"]:
                lines.append(f"Full Article Text:\n{a['content']}")
            lines.append("")
        lines.append("")

    return lines


def build_grounded_league_context() -> str:
    """Build a comprehensive, structured text summary of all deployed league data.
    
    Includes:
    - Season 5 standings, schedule, and race results
    - All-time cumulative highest positions
    - Latest power rankings
    - Historical championship summaries
    """
    global _GROUNDED_CONTEXT_CACHE, _GROUNDED_CONTEXT_MTIME, _CACHE_TIMESTAMP

    # Invalidate every 300 seconds (5 minutes)
    now = time.time()
    if _GROUNDED_CONTEXT_CACHE and (now - _CACHE_TIMESTAMP < 300):
        return _GROUNDED_CONTEXT_CACHE

    lines = []
    lines.append("# THE ALTERNATIVE F1 - OFFICIAL LEAGUE RECORDS DATABASE")
    lines.append("League: The Alternative F1 (Sim Racing League)\n")

    current_dir = Path(__file__).parent
    excel_path = current_dir / "The_Alternative_F1.xlsx"

    # 1. Ingest Season Data via Official Calculations Engine
    all_season_calcs = {}
    active_drivers = []
    active_teams = []

    def _format_season_qualifying_battles(s_number, df_data, const_totals, done_races, all_r):
        if df_data is None or df_data.empty:
            return []
        res = [f"### Season {s_number} Teammate Qualifying Head-to-Head Battles (Constructors Standings Order):"]
        try:
            team_order = [str(t).strip() for t in const_totals["Team"]] if (const_totals is not None and not const_totals.empty) else sorted(df_data["Team"].dropna().unique())
            target_races = done_races if (s_number == 5 and done_races) else all_r
            qual_cols = [f"{r.replace(' Sprint', 'Sprint')}Qualifying" for r in target_races if f"{r.replace(' Sprint', 'Sprint')}Qualifying" in df_data.columns]
            if not qual_cols:
                qual_cols = [c for c in df_data.columns if "qualifying" in c.lower()]
            rows_found = 0
            for tm in team_order:
                tm_drivers = df_data[df_data["Team"] == tm]["Driver"].dropna().unique()
                if len(tm_drivers) >= 2:
                    d1, d2 = str(tm_drivers[0]).strip(), str(tm_drivers[1]).strip()
                    d1_wins, d2_wins = 0, 0
                    for qc in qual_cols:
                        d1_q_rows = df_data[(df_data["Driver"] == d1) & (df_data["Team"] == tm)][qc]
                        d2_q_rows = df_data[(df_data["Driver"] == d2) & (df_data["Team"] == tm)][qc]
                        if not d1_q_rows.empty and not d2_q_rows.empty:
                            q1, q2 = d1_q_rows.iloc[0], d2_q_rows.iloc[0]
                            try:
                                q1_f, q2_f = float(q1), float(q2)
                                if q1_f > 0 and q2_f > 0:
                                    if q1_f < q2_f:
                                        d1_wins += 1
                                    elif q2_f < q1_f:
                                        d2_wins += 1
                            except Exception:
                                pass
                    res.append(f"- {tm}: {d1} ({d1_wins}) vs. {d2} ({d2_wins}) [Across {len(qual_cols)} qualifying sessions]")
                    rows_found += 1
            if rows_found > 0:
                res.append("")
                return res
            return []
        except Exception as e:
            return [f"Note: Error calculating Season {s_number} qualifying battles: {str(e)}\n"]

    def _format_workbook_notes_and_scoring(excel_p: Path) -> list:
        res = []
        if not excel_p.exists():
            return res
        try:
            import openpyxl
            wb = openpyxl.load_workbook(str(excel_p), data_only=True)
            if "Scoring" in wb.sheetnames:
                res.append("## OFFICIAL LEAGUE SCORING & POINTS ALLOCATION MATRIX")
                res.append(
                    "CRITICAL SPRINT vs. GRAND PRIX RULES:\n"
                    "- Grand Prix Feature Races = Full Races (Award 25, 18, 15, 12, 10, 8, 6, 4, 3, 2, 1 pts to top 10 finishers). Maximum base race win = 25 pts (plus up to 4 accolade bonus points = 29 pts max).\n"
                    "- Sprints = Sprint Races (Award 8, 7, 6, 5, 4, 3, 2, 1, 0.5 pts). Maximum sprint win = 8 pts (NEVER 25 pts).\n"
                    "- Sprints are NOT considered full races! They are shorter sprint sessions.\n"
                    "- Sprints do not count as full Grand Prix race starts, nor do they award full race points.\n"
                )
                res.append("| Position | Grand Prix Race Points | Sprint Race Points |")
                res.append("| :--- | :--- | :--- |")
                sheet = wb["Scoring"]
                for row in list(sheet.iter_rows(values_only=True))[1:]:
                    if row and row[0] is not None and row[1] is not None:
                        try:
                            p_race = int(float(row[0]))
                            pts_race = float(row[1])
                            pts_sprint = float(row[4]) if len(row) > 4 and row[4] is not None else 0.0
                            res.append(f"| P{p_race} | {pts_race:g} pts | {pts_sprint:g} pts |")
                        except Exception:
                            pass
                res.append("")
            if "Notes" in wb.sheetnames:
                res.append("## OFFICIAL LEAGUE NOTES, STATUS CODES & DRIVER GAMERTAGS")
                res.append("- Status Codes (Seasons 1–4): Position 21 = DNF (Did Not Finish), Position 22 = DNS (Did Not Start), Position 23 = DSQ (Disqualified).")
                res.append("- Status Codes (Season 5 and onward / S5+): Position 23 = DNF (Did Not Finish), Position 24 = DNS (Did Not Start), Position 25 = DSQ (Disqualified).")
                res.append("Official Driver Gamertags:")
                sheet = wb["Notes"]
                for row in list(sheet.iter_rows(values_only=True))[4:]:
                    if row and len(row) >= 3 and row[0] and row[1]:
                        team = str(row[0]).strip()
                        driver = str(row[1]).strip()
                        gamertag = str(row[2]).strip() if row[2] else "N/A"
                        res.append(f"- {driver} ({team}): Gamertag `{gamertag}`")
                res.append("")
        except Exception as e:
            res.append(f"Note: Error reading workbook Notes and Scoring: {str(e)}\n")
        return res

    def _format_regulations_and_settings() -> list:
        res = []
        try:
            res.append("## OFFICIAL SPORTING & TECHNICAL REGULATIONS")
            rules_data = [
                ("Points Eligibility", "Points are only awarded to drivers that complete the race. No points are awarded to those who DNS or DNF."),
                ("Finishing Points", "Points are awarded based on finishing position in each race: 1st: 25, 2nd: 18, 3rd: 15, 4th: 12, 5th: 10, 6th: 8, 7th: 6, 8th: 4, 9th: 3, 10th: 2, 11th-20th: 1."),
                ("Fastest Lap Award", "One (1) point awarded to the driver with the Fastest Lap at the end of the race."),
                ("Driver of the Day Award", "One (1) point awarded to the driver who earns Driver of the Day at the end of the race."),
                ("Most Overtakes Award", "One (1) point awarded to the driver with the Most Overtakes at the end of the race."),
                ("Cleanest Driver Award", "One (1) point awarded to the driver who earns Cleanest Driver at the end of the race."),
                ("VSC or Safety Car Delta Glitch", "If a driver wrongfully receives a Drive Through Penalty due to a VSC or Safety Car delta glitch, the driver will have their finishing time improved by 20 seconds upon driver request and FIA review, if no Safety Car or Red Flag occurs after the glitch."),
                ("Endangering or Ruining Another Driver's Race", "If a driver's race is ruined (DNF) or endangered (more than 3 lost places) due to reckless driving, the reckless driver will be awarded a 5 place penalty to their finishing position. If deemed intentional, disqualification."),
                ("Right to Protest", "Any driver that disagrees with a ruling has the right to protest within one day of the final ruling. Requires a 2/3rds majority league vote to overturn."),
                ("Penalty Points", "Drivers earning an Endangering/Ruining penalty also earn 1 penalty point. 2 penalty points increases severity by +2 places. For every additional 2 penalty points, increases by +3 places."),
                ("Sprint Day Format", "Sprint Qualifying > Sprint > Race Qualifying = Reverse Grid set by Sprint Results (All AI placed in front of ALL drivers, regardless of finish)."),
                ("Sprint Race Finishing Points", "Sprint points: 1st: 8, 2nd: 7, 3rd: 6, 4th: 5, 5th: 4, 6th: 3, 7th: 2, 8th: 1, 9th-20th: 0.5."),
                ("Race Start Incident", "During start or Red Flag restart, any driver causing a collision/squeeze/brake check causing damage or losing >3 places is penalized from Q2 in the next main race (qualifies last) plus 1 penalty point on super license."),
                ("Causing a Collision", "For collisions not severe enough for Regulation 8, 5s or 10s penalty based on review, plus 1 penalty point on super license."),
                ("Race Restarts", "Races will not be restarted for racing incidents. Bugs or glitches before/during start may trigger restart."),
                ("Damaging Another Vehicle", "Contact damage via telemetry bot: repairable front wing/tire damage = 1 place penalty; irreparable floor/sidepod/rear wing damage = 2-3 place penalty."),
            ]
            for idx, (title, desc) in enumerate(rules_data, start=1):
                res.append(f"- Regulation {idx} ({title}): {desc}")
            res.append("")

            res.append("## OFFICIAL LEAGUE SETTINGS & CONFIGURATION")
            res.append("Assist Restrictions: Steering Assist: Off; Braking Assist: Off; Anti-Lock Brakes (ABS): On; Traction Control: Full; Dynamic Racing Line: Corners Only; Gearbox: Automatic; Pit Assist: On; Pit Release Assist: On; ERS Assist: Off; DRS Assist: Off; Force Cockpit Camera: Off.")
            res.append("Simulation Settings: Equal Car Performance: On; Recovery Mode: None; Surface Type: Realistic; Low Fuel Mode: Easy; Race Starts: Manual; Unsafe Pit Release: Off; Car Damage: Simulation; Car Damage Rate: Simulation; Collisions: On; Weather: Dynamic.")
            res.append("Rules & Flags Settings: Rules & Flags: On; Corner Cutting Stringency: Strict; Parc Ferme Rules: On; Pit Stop Experience: Broadcast; Safety Car: Increased; Safety Car Experience: Immersive; Formation Lap: Off; Red Flags: Increased; Affects Licence Level: Off.")
            res.append("Race Week Structures: Standard Format: Practice Off, Qualifying Full, Session Length Long (50%), Starting Grid Qualifying. Sprint Format: Practice Off, Sprint Qualifying Short, Race Qualifying Off, Sprint Length Long, Race Length Long, Sprint Grid Qualifying, Race Grid Reverse Sprint Results.")
            res.append("")
        except Exception as e:
            res.append(f"Note: Error formatting regulations and settings: {str(e)}\n")
        return res

    def _format_season_round_by_round_results(s_number: int, df_data, all_r: list, completed_only: bool = False, done_races: list = None) -> list:
        if df_data is None or df_data.empty or not all_r:
            return []
        target_r = done_races if (completed_only and done_races) else all_r
        res = [f"### Season {s_number} Driver Round-by-Round Official Results (Qualifying & Finish):"]

        def _parse_val(val):
            if val is None or pd.isnull(val):
                return None
            val_str = str(val).strip().upper()
            if val_str in ("", "-", "NONE", "NAN", "NULL"):
                return None
            if "DNS" in val_str:
                return "DNS"
            if "DSQ" in val_str:
                return "DSQ"
            if "DNF" in val_str:
                return "DNF"
            try:
                num = float(val_str)
                if num <= 0:
                    return None
                # Season-aware numeric status code translation (matching race_metrics and Excel Notes)
                if s_number <= 4:
                    if num == 21.0:
                        return "DNF"
                    elif num == 22.0:
                        return "DNS"
                    elif num == 23.0:
                        return "DSQ"
                else:  # Season 5 and onward
                    if num == 23.0:
                        return "DNF"
                    elif num == 24.0:
                        return "DNS"
                    elif num == 25.0:
                        return "DSQ"
                return f"P{int(round(num))}"
            except Exception:
                return val_str

        for _, row in df_data.iterrows():
            d_name = str(row.get("Driver", "")).strip()
            tm_name = str(row.get("Team", "")).strip()
            if not d_name:
                continue
            r_details = []
            for r in target_r:
                q_col = next((c for c in [f"{r}Qualifying", f"{r.replace(' Sprint', 'Sprint')}Qualifying", f"{r} Qualifying"] if c in df_data.columns), None)
                p_col = next((c for c in [f"{r}Place", f"{r.replace(' Sprint', 'Sprint')}Place", f"{r} Place"] if c in df_data.columns), None)
                pts_col = next((c for c in [f"{r}Points", f"{r.replace(' Sprint', 'Sprint')}Points", f"{r} Points"] if c in df_data.columns), None)
                fl_col = next((c for c in [f"{r}FastestLap", f"{r.replace(' Sprint', 'Sprint')}FastestLap"] if c in df_data.columns), None)

                q_v = row.get(q_col) if q_col else None
                p_v = row.get(p_col) if p_col else None
                pts_v = row.get(pts_col) if pts_col else None
                fl_v = row.get(fl_col) if fl_col else None

                items = []
                q_parsed = _parse_val(q_v)
                if q_parsed:
                    items.append(f"Q:{q_parsed}")

                p_parsed = _parse_val(p_v)
                if p_parsed:
                    items.append(f"Finish:{p_parsed}")

                if pts_v is not None:
                    try:
                        pts_f = float(pts_v)
                        if pts_f > 0:
                            items.append(f"{pts_f:g}pts")
                    except Exception:
                        pass
                if fl_v is not None and str(fl_v) in ("1", "1.0", "True"):
                    items.append("FL")

                stat_str = f" [{', '.join(items)}]" if items else " [DNS/No Data]"
                r_details.append(f"{r}{stat_str}")
            res.append(f"- {d_name} ({tm_name}): {'; '.join(r_details)}")
        res.append("")
        return res

    lines.extend(_format_workbook_notes_and_scoring(excel_path))
    lines.extend(_format_regulations_and_settings())

    try:
        from the_alternative_f1.seasons import seasons, LATEST_SEASON
        from the_alternative_f1.seasons.Calculations import Calculations
        from the_alternative_f1.seasons.projections import _get_driver_track_rating

        for s in seasons:
            s_num = s.get("season_number")
            try:
                calc = Calculations(s)
                all_season_calcs[s_num] = calc
                driver_totals = calc.get("driver_totals")  # pd.DataFrame: ["Driver", "Points"]
                constructor_totals = calc.get("constructor_totals")  # pd.DataFrame: ["Team", "Points"]
                raw_df = calc.get("df")
                schedule_df = calc.get("schedule_df")
                races = calc.get("races", [])
                index_x = calc.get("index_x", 0)
                num_completed = max(0, int(index_x + 0.5))
                completed_races = races[:num_completed]

                # Map drivers to their teams
                driver_team_map = {}
                if raw_df is not None and not raw_df.empty:
                    for _, r in raw_df.iterrows():
                        d = str(r.get("Driver", "")).strip()
                        t = str(r.get("Team", "")).strip()
                        if d and d not in driver_team_map:
                            driver_team_map[d] = t

                if s_num == LATEST_SEASON:
                    lines.append(f"## ACTIVE SEASON: SEASON {s_num} (CURRENT OFFICIAL STANDINGS & STATS)")

                    # Driver Standings
                    if driver_totals is not None and not driver_totals.empty:
                        active_drivers = [str(d).strip() for d in driver_totals["Driver"]]
                        lines.append("### Season 5 Official Driver Championship Standings:")
                        for rank, (_, row) in enumerate(driver_totals.iterrows(), start=1):
                            d = str(row.get("Driver", "")).strip()
                            pts = row.get("Points", 0)
                            team = driver_team_map.get(d, "Independent")
                            badge = " [CHAMPIONSHIP LEADER]" if rank == 1 else ""
                            lines.append(f"{rank}. {d} ({team}): {pts} pts{badge}")
                        lines.append("")

                    # Constructor Standings
                    if constructor_totals is not None and not constructor_totals.empty:
                        active_teams = [str(t).strip() for t in constructor_totals["Team"]]
                        lines.append("### Season 5 Official Constructor Championship Standings:")
                        for rank, (_, row) in enumerate(constructor_totals.iterrows(), start=1):
                            team = str(row.get("Team", "")).strip()
                            pts = row.get("Points", 0)
                            badge = " [CONSTRUCTORS LEADER]" if rank == 1 else ""
                            lines.append(f"{rank}. {team}: {pts} pts{badge}")
                        lines.append("")

                    # Completed Race Results & Winners
                    if completed_races and raw_df is not None and not raw_df.empty:
                        lines.append("### Season 5 Completed Races & Winners:")
                        for race_name in completed_races:
                            col_prefix = race_name.replace(" Sprint", "Sprint")
                            place_col = f"{col_prefix}Place"
                            fl_col = f"{col_prefix}FastestLap"
                            winner_name = "Unknown"
                            winner_team = ""
                            fl_name = ""

                            if place_col in raw_df.columns:
                                winners = raw_df[raw_df[place_col] == 1]
                                if not winners.empty:
                                    winner_name = str(winners.iloc[0].get("Driver", "Unknown")).strip()
                                    winner_team = str(winners.iloc[0].get("Team", "")).strip()

                            if fl_col in raw_df.columns:
                                fl_rows = raw_df[raw_df[fl_col] == 1]
                                if not fl_rows.empty:
                                    fl_name = str(fl_rows.iloc[0].get("Driver", "")).strip()

                            fl_str = f" | Fastest Lap: {fl_name}" if fl_name else ""
                            team_str = f" ({winner_team})" if winner_team else ""
                            lines.append(f"- {race_name}: Winner: {winner_name}{team_str}{fl_str}")
                        lines.append("")

                    # Seasonal Teammate Qualifying Battles (SDDREQ-249)
                    lines.extend(_format_season_qualifying_battles(s_num, raw_df, constructor_totals, completed_races, races))
                    lines.extend(_format_season_round_by_round_results(s_num, raw_df, races, completed_only=True, done_races=completed_races))

                    # Calendar & Schedule
                    if schedule_df is not None and not schedule_df.empty:
                        gp_races = [r for r in races if "sprint" not in r.lower()]
                        sprint_races = [r for r in races if "sprint" in r.lower()]
                        done_gp = [r for r in completed_races if "sprint" not in r.lower()]
                        done_sprint = [r for r in completed_races if "sprint" in r.lower()]
                        rem_gp = len(gp_races) - len(done_gp)
                        rem_sprint = len(sprint_races) - len(done_sprint)

                        lines.append("### Season 5 Calendar & Schedule (Qualifying & Races held on Wednesdays; Qualifying immediately precedes Race):")
                        lines.append(f"Official Season 5 Round Structure: {len(races)} Total Scheduled Rounds ({len(gp_races)} Grand Prix Feature Races + {len(sprint_races)} Sprint Races).")
                        lines.append(f"- Completed to Date: {len(completed_races)} Rounds ({len(done_gp)} Grand Prix Feature Races + {len(done_sprint)} Sprint Races).")
                        lines.append(f"- Remaining on Calendar: {len(races) - len(completed_races)} Rounds ({rem_gp} Grand Prix Feature Races + {rem_sprint} Sprint Races).")
                        lines.append("CRITICAL: Sprints are NOT full races! Sprints award at most 8 points for P1 (Sprint Scoring: 8-7-6-5-4-3-2-1-0.5), while Grand Prix feature races award 25 points for P1 (plus up to 4 accolade points).")
                        for _, row in schedule_df.iterrows():
                            r_name = str(row.get("Race", "")).strip()
                            r_track = str(row.get("Track", "")).strip()
                            status = str(row.get("Status", "")).strip()
                            raw_date = str(row.get("Date", "")).strip().replace(" 00:00:00", "")
                            date_str = f" (Date: {raw_date})" if raw_date and raw_date.lower() != "nan" else " (Date: Not Recorded)"
                            status_str = f" [{status}]" if status and status.lower() != "nan" else ""
                            round_type = "[Sprint Race - Max 8 pts]" if "sprint" in r_name.lower() else "[Grand Prix Feature Race - Max 25 pts]"
                            track_desc = f" at {r_track}" if r_track and r_track.lower() != "nan" else ""
                            lines.append(f"- {r_name}{track_desc} {round_type}{date_str}{status_str}")
                        lines.append("")

                    # Rookies
                    rookies = s.get("rookies")
                    if rookies:
                        lines.append(f"### Season 5 Designated Rookies: {', '.join(sorted(rookies))}\n")


                else:
                    # Individual Historical Season Data
                    season_year = ""
                    if s_num in (1, 2):
                        season_year = " (Year: 2023)"
                    elif s_num == 3:
                        season_year = " (Year: 2024)"
                    lines.append(f"## SEASON {s_num}{season_year} COMPLETE HISTORICAL STANDINGS")
                    if s_num in (1, 2):
                        lines.append("Official Calendar Note: Season 1 and Season 2 occurred in 2023. Races were held on Wednesdays.")
                    elif s_num == 3:
                        lines.append("Official Calendar Note: Season 3 occurred in 2024. Races were held on Wednesdays.")
                    if driver_totals is not None and not driver_totals.empty:
                        champ = driver_totals.iloc[0]
                        lines.append(f"- Season {s_num} Champion Driver: {champ.get('Driver')} ({champ.get('Points')} pts)")
                        lines.append("Top Drivers Final Standings:")
                        for rank, (_, row) in enumerate(driver_totals.head(10).iterrows(), start=1):
                            lines.append(f"  {rank}. {row.get('Driver')}: {row.get('Points')} pts")
                    if constructor_totals is not None and not constructor_totals.empty:
                        c_champ = constructor_totals.iloc[0]
                        champ_team_name = str(c_champ.get('Team', '')).strip()
                        winning_drivers = []
                        if raw_df is not None and not raw_df.empty and "Team" in raw_df.columns:
                            t_rows = raw_df[raw_df["Team"].astype(str).str.strip() == champ_team_name]
                            for _, r in t_rows.iterrows():
                                d_name = str(r.get("Driver", "")).strip()
                                d_pts = r.get("Total", r.get("Points", 0))
                                if d_name:
                                    winning_drivers.append(f"{d_name} ({d_pts} pts)")
                        drivers_str = f" | Winning Drivers (Official Constructor Champions): {', '.join(winning_drivers)}" if winning_drivers else ""
                        lines.append(f"- Season {s_num} Champion Constructor: {champ_team_name} ({c_champ.get('Points')} pts){drivers_str}")
                    if completed_races and raw_df is not None and not raw_df.empty:
                        race_winners_s = []
                        for r_name in races:
                            c_pre = r_name.replace(" Sprint", "Sprint")
                            p_col = f"{c_pre}Place"
                            if p_col in raw_df.columns:
                                w_rows = raw_df[raw_df[p_col] == 1]
                                if not w_rows.empty:
                                    w_d = str(w_rows.iloc[0].get("Driver", "")).strip()
                                    race_winners_s.append(f"{r_name}: {w_d}")
                        if race_winners_s:
                            lines.append(f"- Race Winners: {'; '.join(race_winners_s)}")

                    # Historical Teammate Qualifying Battles (SDDREQ-249)
                    lines.extend(_format_season_qualifying_battles(s_num, raw_df, constructor_totals, completed_races, races))
                    lines.extend(_format_season_round_by_round_results(s_num, raw_df, races))

                    # Historical Calendar & Schedule
                    if schedule_df is not None and not schedule_df.empty:
                        gp_races_h = [r for r in races if "sprint" not in r.lower()]
                        sprint_races_h = [r for r in races if "sprint" in r.lower()]
                        sprint_info = f" ({len(gp_races_h)} Grand Prix Feature Races + {len(sprint_races_h)} Sprint Races)" if sprint_races_h else f" ({len(gp_races_h)} Grand Prix Feature Races)"
                        lines.append(f"### Season {s_num} Calendar & Schedule (Qualifying & Races held on Wednesdays; Qualifying immediately precedes Race):")
                        lines.append(f"Official Season {s_num} Structure: {len(races)} Total Rounds{sprint_info}.")
                        for _, row in schedule_df.iterrows():
                            r_name = str(row.get("Race", "")).strip()
                            r_track = str(row.get("Track", "")).strip()
                            status = str(row.get("Status", "")).strip()
                            raw_date = str(row.get("Date", "")).strip().replace(" 00:00:00", "")
                            date_str = f" (Date: {raw_date})" if raw_date and raw_date.lower() != "nan" else " (Date: Not Recorded)"
                            status_str = f" [{status}]" if status and status.lower() != "nan" else ""
                            round_type = "[Sprint Race - Max 8 pts]" if "sprint" in r_name.lower() else "[Grand Prix Feature Race - Max 25 pts]"
                            track_desc = f" at {r_track}" if r_track and r_track.lower() != "nan" else ""
                            lines.append(f"- {r_name}{track_desc} {round_type}{date_str}{status_str}")
                        lines.append("")
                    lines.append("")

            except Exception as e:
                lines.append(f"Note: Error loading Season {s_num}: {str(e)}")

    except Exception as e:
        lines.append(f"Note: Error initializing Seasons engine: {str(e)}")

    # 1.5 Official Driver & Constructor Career Debuts, Active Seasons, and Milestones
    lines.append("## OFFICIAL DRIVER CAREER DEBUTS, ACTIVE SEASONS & CAREER STINTS (ALL 24 DRIVERS)")
    lines.append(
        "CRITICAL CHRONOLOGICAL RULE: Drivers only exist and compete in seasons starting from their official Debut Season. "
        "NEVER assume, invent, or state that a driver competed, drove for a team, or scored results in seasons prior to their official Debut Season!\n"
        "- Brently and Patrick debuted in Season 3 as Rookies (VCARB). They DID NOT COMPETE in Season 1 or Season 2!\n"
        "- Josh, Matthew, Leo, Jaden, and Jairo debuted in Season 4 as Rookies. They DID NOT COMPETE in Seasons 1, 2, or 3!\n"
        "- Grayson, Josh C., Randy, and Evelo debuted in Season 5 as Rookies. They DID NOT COMPETE in Seasons 1, 2, 3, or 4!\n"
        "- Del, Joshua, Eddie, and Yeti debuted in Season 2 as Rookies. They DID NOT COMPETE in Season 1!\n"
        "- Nick, Erick, Marcus, Zane, David, Gary, Boz, Travis, and Josh L are Inaugural Founding Drivers who debuted in Season 1."
    )
    lines.append("| Driver | Debut Season | Debut Race | Debut Constructor | Rookie Class | Seasons Competed | Inactive / Absent Seasons | Career Team Stints by Season | Maiden Full-Race Podium (Position, Race, Season) | Races from Debut to Maiden Podium | Maiden Race Win (Race, Season) | Races from Debut to Maiden Win |")
    lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
    lines.append("| Nick | Season 1 | S1 Bahrain | McLaren | S1 Inaugural Founding Driver | S1, S2, S3, S4, S5 | None | S1: McLaren, S2: McLaren, S3: McLaren, S4: McLaren, S5: McLaren | P1 at S1 Bahrain (Win on Debut!) | 1 race | P1 at S1 Bahrain | 1 race |")
    lines.append("| Erick | Season 1 | S1 Bahrain | Mercedes | S1 Inaugural Founding Driver | S1, S2, S3, S4 | S5 (Inactive) | S1: Mercedes, S2: Ferrari, S3: Ferrari, S4: Ferrari | P2 at S1 Bahrain | 1 race | P1 at S1 Singapore | 10 races |")
    lines.append("| Marcus | Season 1 | S1 Bahrain | Mercedes | S1 Inaugural Founding Driver | S1, S2 | S3, S4, S5 (Inactive) | S1: Mercedes, S2: Red Bull | P3 at S1 Jeddah | 2 races | P1 at S1 Australia | 3 races |")
    lines.append("| Zane | Season 1 | S1 Bahrain | Aston Martin | S1 Inaugural Founding Driver | S1, S2, S3 | S4, S5 (Inactive) | S1: Aston Martin, S2: Red Bull, S3: Ferrari | P2 at S1 Bahrain | 1 race | P1 at S1 Baku | 4 races |")
    lines.append("| David | Season 1 | S1 Bahrain | Aston Martin | S1 Inaugural Founding Driver | S1, S2 | S3, S4, S5 (Inactive) | S1: Aston Martin, S2: Alfa Romeo | None (All-Time Standings Peak: 4th at S1 Bahrain) | None | None | None |")
    lines.append("| Josh L | Season 1 | S1 Bahrain | Red Bull | S1 Inaugural Founding Driver | S1, S2 | S3, S4, S5 (Inactive) | S1: Red Bull, S2: Alfa Romeo | None (All-Time Standings Peak: 5th at S1 Bahrain) | None | None | None |")
    lines.append("| Boz | Season 1 | S1 Bahrain | Red Bull | S1 Inaugural Founding Driver | S1, S2, S3, S4, S5 | None | S1: Red Bull, S2: Mercedes, S3: Red Bull, S4: Haas, S5: Audi | None (All-Time Standings Peak: 5th at S1 Miami) | None | None | None |")
    lines.append("| Travis | Season 1 | S1 Bahrain | McLaren | S1 Inaugural Founding Driver | S1, S2, S3, S4 | S5 (Inactive) | S1: McLaren, S2: AlphaTauri, S3: McLaren, S4: McLaren | None (All-Time Standings Peak: 5th at S1 Silverstone) | None | None | None |")
    lines.append("| Gary | Season 1 | S1 Bahrain | Ferrari | S1 Inaugural Founding Driver | S1, S2, S3 | S4, S5 (Inactive) | S1: Ferrari, S2: McLaren, S3: Aston Martin | None (All-Time Standings Peak: 8th at S1 Bahrain) | None | None | None |")
    lines.append("| Del | Season 2 | S2 Bahrain | Mercedes | Season 2 Rookie | S2, S3, S4, S5 | S1 (DID NOT COMPETE in S1) | S2: Mercedes, S3: Ferrari, S4: Aston Martin, S5: McLaren | P2 at S2 Bahrain | 1 race | P1 at S2 Spain | 5 races |")
    lines.append("| Joshua | Season 2 | S2 Bahrain | Alpine | Season 2 Rookie | S2, S3, S4, S5 | S1 (DID NOT COMPETE in S1) | S2: Alpine, S3: Alpine, S4: Alpine, S5: Red Bull | P3 at S2 Bahrain | 1 race | P1 at S3 Austria | 16 races |")
    lines.append("| Eddie | Season 2 | S2 Bahrain | Alpine | Season 2 Rookie | S2, S3, S4, S5 | S1 (DID NOT COMPETE in S1) | S2: Alpine, S3: Alpine, S4: Alpine, S5: Red Bull | P3 at S3 COTA | 21 races | None | None |")
    lines.append("| Yeti | Season 2 | S2 Bahrain | AlphaTauri | Season 2 Rookie | S2, S3 | S1, S4, S5 (Inactive) | S2: AlphaTauri, S3: Aston Martin | None (All-Time Standings Peak: 10th at S2 Monza) | None | None | None |")
    lines.append("| Patrick | Season 3 | S3 Bahrain | VCARB | Season 3 Rookie | S3, S4, S5 | S1, S2 (DID NOT COMPETE in S1, S2) | S3: VCARB, S4: VCARB, S5: Cadillac | P2 at S3 Baku | 7 races | P1 at S3 Austria | 13 races |")
    lines.append("| Brently | Season 3 | S3 Bahrain | VCARB | Season 3 Rookie | S3, S4, S5 | S1, S2 (DID NOT COMPETE in S1, S2) | S3: VCARB, S4: Red Bull, S5: Haas | P1 at S3 Monaco (Maiden Win & Podium in Rookie Season!) | 15 races | P1 at S3 Monaco | 15 races |")
    lines.append("| Josh | Season 4 | S4 Bahrain | VCARB | Season 4 Rookie | S4, S5 | S1, S2, S3 (DID NOT COMPETE in S1, S2, S3) | S4: VCARB, S5: Cadillac | P3 at S4 Bahrain | 1 race | P1 at S5 Imola | 18 races |")
    lines.append("| Matthew | Season 4 | S4 Bahrain | Red Bull | Season 4 Rookie | S4, S5 | S1, S2, S3 (DID NOT COMPETE in S1, S2, S3) | S4: Red Bull, S5: Haas | None (All-Time Standings Peak: 17th at S4 Spa Sprint) | None | None | None |")
    lines.append("| Leo | Season 4 | S4 Bahrain | Ferrari | Season 4 Rookie | S4, S5 | S1, S2, S3 (DID NOT COMPETE in S1, S2, S3) | S4: Ferrari, S5: Ferrari | None (All-Time Standings Peak: 10th at S4 Mexico) | None | None | None |")
    lines.append("| Jaden | Season 4 | S4 Bahrain | Mercedes | Season 4 Rookie | S4, S5 | S1, S2, S3 (DID NOT COMPETE in S1, S2, S3) | S4: Mercedes, S5: Ferrari | P2 at S4 Bahrain | 1 race | P1 at S4 Austria Reverse | 9 races |")
    lines.append("| Jairo | Season 4 | S4 Bahrain | Mercedes | Season 4 Rookie | S4, S5 | S1, S2, S3 (DID NOT COMPETE in S1, S2, S3) | S4: Mercedes, S5: Mercedes | P1 at S4 Bahrain (Win on Debut!) | 1 race | P1 at S4 Bahrain | 1 race |")
    lines.append("| Grayson | Season 5 | S5 Australia | Audi | Season 5 Rookie | S5 | S1, S2, S3, S4 (DID NOT COMPETE in S1-S4) | S5: Audi | None (Active Rookie) | None | None | None |")
    lines.append("| Josh C. | Season 5 | S5 Australia | Williams | Season 5 Rookie | S5 | S1, S2, S3, S4 (DID NOT COMPETE in S1-S4) | S5: Williams | None (Active Rookie) | None | None | None |")
    lines.append("| Randy | Season 5 | S5 Australia | Mercedes | Season 5 Rookie | S5 | S1, S2, S3, S4 (DID NOT COMPETE in S1-S4) | S5: Mercedes | None (Active Rookie) | None | None | None |")
    lines.append("| Evelo | Season 5 | S5 Australia | Williams | Season 5 Rookie | S5 | S1, S2, S3, S4 (DID NOT COMPETE in S1-S4) | S5: Williams | None (Active Rookie) | None | None | None |")
    lines.append("")

    lines.append("## OFFICIAL CONSTRUCTOR CAREER DEBUTS & ACTIVE SEASONS (ALL 13 CONSTRUCTORS)")
    lines.append("| Constructor | Debut Season | Debut Race | Seasons Competed / Active | Inactive / Absent Seasons | Championships |")
    lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
    lines.append("| McLaren | Season 1 | S1 Bahrain | Season 1, Season 2, Season 3, Season 4, Season 5 | None | 🏆 x1 (Season 2) |")
    lines.append("| Mercedes | Season 1 | S1 Bahrain | Season 1, Season 2, Season 4, Season 5 | Season 3 (Departed / Did Not Compete) | 🏆 x2 (Season 1, Season 4) |")
    lines.append("| Red Bull | Season 1 | S1 Bahrain | Season 1, Season 2, Season 3, Season 4, Season 5 | None | 0 |")
    lines.append("| Ferrari | Season 1 | S1 Bahrain | Season 1, Season 2, Season 3, Season 4, Season 5 | None | 0 |")
    lines.append("| Aston Martin | Season 1 | S1 Bahrain | Season 1, Season 3, Season 4 | Season 2, Season 5 (Did Not Compete) | 0 |")
    lines.append("| Alpine | Season 2 | S2 Bahrain | Season 2, Season 3, Season 4 | Season 1, Season 5 (Did Not Compete) | 🏆 x1 (Season 3) |")
    lines.append("| Alfa Romeo | Season 2 | S2 Bahrain | Season 2 (Single season) | Season 1, Season 3, Season 4, Season 5 | 0 |")
    lines.append("| AlphaTauri | Season 2 | S2 Bahrain | Season 2 (Single season) | Season 1, Season 3, Season 4, Season 5 | 0 |")
    lines.append("| VCARB | Season 3 | S3 Bahrain | Season 3, Season 4 | Season 1, Season 2, Season 5 (Did Not Compete) | 0 |")
    lines.append("| Cadillac | Season 5 | S5 Australia | Season 5 (Active Standings Leader) | Season 1, Season 2, Season 3, Season 4 | 0 |")
    lines.append("| Haas | Season 5 | S5 Australia | Season 5 | Season 1, Season 2, Season 3, Season 4 | 0 |")
    lines.append("| Audi | Season 5 | S5 Australia | Season 5 | Season 1, Season 2, Season 3, Season 4 | 0 |")
    lines.append("| Williams | Season 5 | S5 Australia | Season 5 | Season 1, Season 2, Season 3, Season 4 | 0 |")
    lines.append("")

    lines.append("## OFFICIAL SEASON-BY-SEASON ROSTER & ROOKIE CATEGORIZATION")
    lines.append("- Season 1 (2023, 19 rounds): Inaugural Class (Nick, Travis, Zane, David, Erick, Marcus, Josh L, Boz, Gary). Constructors: McLaren, Mercedes, Red Bull, Ferrari, Aston Martin.")
    lines.append("- Season 2 (2023, 10 rounds): Rookie Class (Del, Joshua, Eddie, Yeti). Returning: Nick, Gary, Boz, Erick, David, Zane, Marcus, Josh L, Travis. Constructors: McLaren, Mercedes, Ferrari, Alpine, Red Bull, Alfa Romeo, AlphaTauri.")
    lines.append("- Season 3 (2024, 12 rounds; 3 rounds feature a Sprint: China, Austria, COTA): Rookie Class (Patrick, Brently). Returning: Nick, Travis, Joshua, Eddie, Erick, Zane, Del, Gary, Yeti, Boz. Constructors: McLaren, Alpine, Ferrari, VCARB, Aston Martin, Red Bull.")
    lines.append("- Season 4 (2025, 14 rounds; 3 rounds feature a Sprint: Miami, Spa, Brazil): Rookie Class (Josh, Matthew, Leo, Jaden, Jairo). Returning: Joshua, Eddie, Nick, Travis, Patrick, Brently, Erick, Del, Boz. Constructors: Alpine, McLaren, VCARB, Mercedes, Red Bull, Ferrari, Aston Martin.")
    lines.append("- Season 5 (2026, 14 rounds scheduled; 6 rounds feature a Sprint: Miami, Spa, Silverstone, Bahrain, Zandvoort, Singapore): Rookie Class (Grayson, Josh C., Randy, Evelo). Returning: Joshua, Eddie, Nick, Del, Patrick, Josh, Matthew, Brently, Boz, Jaden, Leo, Jairo. Constructors: Ferrari, McLaren, Red Bull, Mercedes, Haas, Audi, Cadillac, Williams.")
    lines.append("")

    lines.append("## OFFICIAL LEAGUE CALENDAR STRUCTURE (SPRINTS ARE PART OF THE FEATURE RACE ROUND)")
    lines.append("- Sprints are part of the feature race round and do NOT count as separate rounds in any season.")
    lines.append("- Season 1: 19 Rounds (19 Grand Prix feature races)")
    lines.append("- Season 2: 10 Rounds (10 Grand Prix feature races)")
    lines.append("- Season 3: 12 Rounds (12 Grand Prix feature races; rounds with Sprints: China, Austria, COTA)")
    lines.append("- Season 4: 14 Rounds (14 Grand Prix feature races; rounds with Sprints: Miami, Spa, Brazil)")
    lines.append("- Season 5: 14 Rounds (14 Grand Prix feature races; rounds with Sprints: Miami, Spa, Silverstone, Bahrain, Zandvoort, Singapore)")
    lines.append("- CRITICAL PROHIBITION: Season 5 is a 14-round championship campaign, NOT 20 rounds. NEVER refer to Season 5 as a '20-round campaign' or '20-race season'.")
    lines.append("")

    lines.append("## OFFICIAL MILESTONE LEADERBOARDS: MAIDEN PODIUMS & MAIDEN WINS")
    lines.append("### Longest Wait from League Debut to Maiden Full-Race Podium (Ranked by Races from Debut):")
    lines.append("1. Eddie: 21 races from debut (Debuted Season 2 Bahrain; scored maiden podium at Season 3 COTA finishing P3).")
    lines.append("2. Brently: 15 races from debut (Debuted Season 3 Bahrain; scored maiden podium & victory at Season 3 Monaco finishing P1 in his rookie season).")
    lines.append("3. Patrick: 7 races from debut (Debuted Season 3 Bahrain; scored maiden podium at Season 3 Baku finishing P2).")
    lines.append("4. Marcus: 2 races from debut (Debuted Season 1 Bahrain; scored maiden podium at Season 1 Jeddah finishing P3).")
    lines.append("5. Nick, Erick, Zane, Del, Joshua, Josh, Jairo, Jaden: 1 race from debut (All scored a podium in their very first career start at Bahrain).")
    lines.append("- Drivers Awaiting Maiden Podium (0 career podiums): Boz, Travis, Gary, David, Josh L, Yeti, Matthew, Leo, Grayson, Josh C., Randy, Evelo.")
    lines.append("")
    lines.append("### Longest Wait from League Debut to Maiden Race Win (Ranked by Races from Debut):")
    lines.append("1. Josh: 18 races from debut (Debuted Season 4 Bahrain; scored maiden win at Season 5 Imola finishing P1 in Cadillac).")
    lines.append("2. Joshua: 16 races from debut (Debuted Season 2 Bahrain; scored maiden win at Season 3 Austria finishing P1 in Alpine).")
    lines.append("3. Brently: 15 races from debut (Debuted Season 3 Bahrain; scored maiden win at Season 3 Monaco finishing P1 in VCARB in rookie season).")
    lines.append("4. Patrick: 13 races from debut (Debuted Season 3 Bahrain; scored maiden win at Season 3 Austria finishing P1 in VCARB).")
    lines.append("5. Erick: 10 races from debut (Debuted Season 1 Bahrain; scored maiden win at Season 1 Singapore finishing P1 in Mercedes).")
    lines.append("6. Jaden: 9 races from debut (Debuted Season 4 Bahrain; scored maiden win at Season 4 Austria Reverse finishing P1 in Mercedes).")
    lines.append("7. Del: 5 races from debut (Debuted Season 2 Bahrain; scored maiden win at Season 2 Spain finishing P1 in Mercedes).")
    lines.append("8. Zane: 4 races from debut (Debuted Season 1 Bahrain; scored maiden win at Season 1 Baku finishing P1 in Aston Martin).")
    lines.append("9. Marcus: 3 races from debut (Debuted Season 1 Bahrain; scored maiden win at Season 1 Australia finishing P1 in Mercedes).")
    lines.append("10. Nick, Jairo: 1 race from debut (Won their very first career start at Bahrain).")
    lines.append("")

    lines.append("## OFFICIAL DRIVER TRACK AFFINITIES & NICKNAMES")
    lines.append("- Miami Lover / Miami Favorite: Nick's all time favorite track is Miami. Erick is known as the Miami Lover, but really that nickname should be held by Nick (no pun intended).")
    lines.append("- Mets Fan: Joshua, Season 4 World Driver Champion is the biggest Mets fan in the world and he hates the Yankees.")
    lines.append("")

    # 2. Per-Track Driver Statistical Ratings (SDDREQ-76 & Projections)
    try:
        from the_alternative_f1.seasons.projections import _get_driver_track_rating
        lines.append("## OFFICIAL PER-TRACK DRIVER STATISTICAL RATINGS (SCALE 0 - 100)")
        lines.append(
            "Formula (SDDREQ-76): (((average points scored / 30) * 0.6) + ((0.99 / qualifying position) * 0.2) + ((positions gained/lost / 22) * 0.2)) * 100\n"
            "This metric measures each driver's historical statistical efficiency and performance specifically for each circuit.\n"
        )
        tracks_to_compute = [
            "Spa", "Monza", "Australia", "Imola", "Miami", "Brazil",
            "Silverstone", "Suzuka", "Qatar", "COTA", "Mexico", "Las Vegas", "Abu Dhabi",
            "Bahrain", "Jeddah", "Spain", "Canada", "Austria", "Zandvoort", "Singapore"
        ]

        if not active_drivers:
            active_drivers = ["Josh", "Jairo", "Joshua", "Jaden", "Nick", "Eddie", "Del", "Patrick", "Matthew", "Brently", "Grayson", "Josh C.", "Boz", "Evelo", "Leo", "Randy"]

        for track_name in tracks_to_compute:
            ratings = []
            for d in active_drivers:
                score = _get_driver_track_rating(d, track_name)
                ratings.append((d, score))
            ratings.sort(key=lambda x: x[1], reverse=True)
            formatted_ratings = [f"{d}: {s:.1f}" for d, s in ratings]
            lines.append(f"### Track: {track_name}")
            lines.append(f"- Driver Track Ratings (Best to Worst): {', '.join(formatted_ratings)}")
        lines.append("")
    except Exception as e:
        lines.append(f"Note: Error generating track ratings: {str(e)}")

    # 3. All-Time League Career Records (Drivers & Constructors)
    try:
        from the_alternative_f1.all_time_stats.Functions import CalculateAllTime
        all_time_drivers = CalculateAllTime(5, "Driver")
        if all_time_drivers is not None and not all_time_drivers.empty:
            lines.append("## ALL-TIME LEAGUE DRIVER CAREER RECORDS (ALL SEASONS CUMULATIVE)")
            lines.append("| Rank | Driver | Career Points | Wins (1st) | 2nd | 3rd | Podiums | Championships | Highest Rank | Single Season Win Streak |")
            lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
            for _, r in all_time_drivers.iterrows():
                rank = r.get("Place", "")
                d = r.get("Driver", "")
                pts = r.get("Points", 0)
                w = r.get("1st Place", 0)
                p2 = r.get("2nd Place", 0)
                p3 = r.get("3rd Place", 0)
                pod = r.get("Podiums", 0)
                ch = r.get("Driver's Champion", 0)
                hp = r.get("Highest Position", "—")
                streak = r.get("Single Season Win Streak", 0)
                ch_str = f"🏆 x{ch}" if ch > 0 else "0"
                lines.append(f"| {rank} | {d} | {pts} | {w} | {p2} | {p3} | {pod} | {ch_str} | {hp} | {streak} |")
            lines.append("")

        all_time_teams = CalculateAllTime(5, "Team")
        if all_time_teams is not None and not all_time_teams.empty:
            lines.append("## ALL-TIME LEAGUE CONSTRUCTOR CAREER RECORDS")
            lines.append("| Rank | Constructor | Career Points | Wins | 2nd | 3rd | Championships | Highest Rank |")
            lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
            for _, r in all_time_teams.iterrows():
                rank = r.get("Place", "")
                t = r.get("Team", "")
                pts = r.get("Points", 0)
                w = r.get("1st Place", 0)
                p2 = r.get("2nd Place", 0)
                p3 = r.get("3rd Place", 0)
                ch = r.get("Constructor's Champion", 0)
                hp = r.get("Highest Position", "—")
                ch_str = f"🏆 x{ch}" if ch > 0 else "0"
                lines.append(f"| {rank} | {t} | {pts} | {w} | {p2} | {p3} | {ch_str} | {hp} |")
            lines.append("")
    except Exception as e:
        lines.append(f"Note: Error generating all-time career records: {str(e)}")

    # Official Championship Historical Archive (TAF1APP-SDDREQ-250)
    lines.append("## OFFICIAL CHAMPIONSHIP HISTORICAL ARCHIVE (SEASONS 1 - 5)")
    lines.append("| Season | Champion Entity | Type | Wins | Podiums | Accolades (Poles, FL, CD, DOTD, MOT) | Win Margin | Runner-Up | Races Led Championship |")
    lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
    lines.append("| Season 1 | Mercedes | Constructor | 7 | 22 | 13 (3 Poles, 10 FL) | +55.0 pts | McLaren | 17 of 19 races (89.5%) |")
    lines.append("| Season 1 | Nick | Driver | 10 | 16 | 16 (8 Poles, 8 FL) | +39.0 pts | Erick | 18 of 19 races (94.7%) |")
    lines.append("| Season 2 | McLaren | Constructor | 6 | 8 | 8 (5 Poles, 3 FL) | +24.0 pts | Ferrari | 9 of 10 races (90.0%) |")
    lines.append("| Season 2 | Nick | Driver | 6 | 8 | 8 (5 Poles, 3 FL) | +57.0 pts | Del | 10 of 10 races (100.0%) |")
    lines.append("| Season 3 | Alpine | Constructor | 5 | 9 | 11 (3 Poles, 8 FL) | +10.5 pts | McLaren | 9 of 15 races (60.0%) |")
    lines.append("| Season 3 | Nick | Driver | 5 | 11 | 5 (4 Poles, 1 FL) | +35.0 pts | Joshua | 8 of 15 races (53.3%) |")
    lines.append("| Season 4 | Mercedes | Constructor | 8 | 11 | 24 (7 Poles, 8 FL, 3 CD, 6 DOTD) | +38.0 pts | VCARB | 13 of 17 races (76.5%) |")
    lines.append("| Season 4 | Joshua | Driver | 2 | 11 | 12 (4 Poles, 5 FL, 2 DOTD, 1 MOT) | +15.0 pts | Jairo | 8 of 17 races (47.1%) |")
    lines.append("| Season 5 (Active) | Cadillac | Constructor | 2 | 2 | 5 (1 Pole, 2 FL, 2 CD) | +36.0 pts | Mercedes | 4 of 4 races (100.0%) |")
    lines.append("| Season 5 (Active) | Josh | Driver | 2 | 2 | 2 (1 Pole, 1 FL) | +9.0 pts | Jairo | 4 of 4 races (100.0%) |")
    lines.append("")
    lines.append("## OFFICIAL CONSTRUCTOR CHAMPIONSHIP WINNERS & WINNING DRIVER ROSTERS (SEASONS 1 - 5)")
    lines.append("CRITICAL RULE: Any driver who drove for the constructor that won the Constructor Championship is an official Constructor Champion!")
    lines.append("- Season 1 Constructor Champion: Mercedes (586.0 pts) | Winning Drivers: Erick (395 pts, P2 in Drivers Championship), Marcus (191 pts)")
    lines.append("  * Both Erick and Marcus won the Season 1 Constructor Championship.")
    lines.append("- Season 2 Constructor Champion: McLaren (258.0 pts) | Winning Drivers: Nick (248 pts), Gary (10 pts)")
    lines.append("  * Both Nick and Gary won the Season 2 Constructor Championship.")
    lines.append("- Season 3 Constructor Champion: Alpine (312.0 pts) | Winning Drivers: Joshua (227.0 pts), Eddie (85.0 pts)")
    lines.append("  * Both Joshua and Eddie won the Season 3 Constructor Championship.")
    lines.append("- Season 4 Constructor Champion: Mercedes (394.0 pts) | Winning Drivers: Jairo (241.0 pts), Jaden (153.0 pts)")
    lines.append("  * Both Jairo and Jaden won the Season 4 Constructor Championship.")
    lines.append("- Season 5 (Active Standings Leader): Cadillac (101.0 pts) | Drivers: Josh (65.0 pts), Patrick (36.0 pts)")
    lines.append("")
    lines.append("## COMPREHENSIVE CHAMPIONSHIP WINNERS BREAKDOWN:")
    lines.append("Drivers who have won at least one Driver OR Constructor Championship (Completed Seasons 1-4):")
    lines.append("1. Nick — 3x Driver Champion (S1, S2, S3), 1x Constructor Champion (S2 McLaren)")
    lines.append("2. Joshua — 1x Driver Champion (S4), 1x Constructor Champion (S3 Alpine)")
    lines.append("3. Erick — 1x Constructor Champion (S1 Mercedes; scored 395 pts, finished P2 in S1 Driver Standings)")
    lines.append("4. Marcus — 1x Constructor Champion (S1 Mercedes)")
    lines.append("5. Gary — 1x Constructor Champion (S2 McLaren)")
    lines.append("6. Eddie — 1x Constructor Champion (S3 Alpine)")
    lines.append("7. Jairo — 1x Constructor Champion (S4 Mercedes)")
    lines.append("8. Jaden — 1x Constructor Champion (S4 Mercedes)")
    lines.append("")
    lines.append("Drivers who have NEVER won a Driver OR Constructor Championship (Completed Seasons 1-4):")
    lines.append("- Non-Champion Drivers Pool: Patrick, Matthew, Del, Brently, Foster, Austin, Josh C., Boz, Evelo, Leo, Randy.")
    lines.append("- Note on Season 5: Josh leads active Season 5, but has not completed or won a final championship yet.")
    lines.append("CRITICAL FACT: NEVER include Erick, Marcus, Gary, Eddie, Jairo, Jaden, Nick, or Joshua in the non-champion pool! All eight of these drivers have won official championships (Driver or Constructor). Erick won the Season 1 Constructor Championship with Mercedes.")
    lines.append("")


    # 4. Load All Time Highest Positions
    highest_pos_path = current_dir / "all_time_stats" / "all_time_highest_positions.json"
    if highest_pos_path.exists():
        try:
            with open(highest_pos_path, "r", encoding="utf-8") as f:
                pos_data = json.load(f)
                lines.append("## ALL-TIME LEAGUE STANDINGS PEAK POSITIONS")
                lines.append("Note: These metrics represent the entity's highest rank ever achieved on the cumulative championship leaderboard line, NOT a single-race finish position.")
                driver_pos = pos_data.get("drivers", {})
                lines.append("### Driver All-Time Standings Peak:")
                for d_name, details in list(driver_pos.items())[:25]:
                    pos_str = details.get("highest_position", "—") if isinstance(details, dict) else str(details)
                    lines.append(f"- {d_name}: All-Time Standings Peak {pos_str}")

                const_pos = pos_data.get("constructors", {})
                lines.append("\n### Constructor All-Time Standings Peak:")
                for c_name, details in list(const_pos.items())[:15]:
                    pos_str = details.get("highest_position", "—") if isinstance(details, dict) else str(details)
                    lines.append(f"- {c_name}: All-Time Standings Peak {pos_str}")
                lines.append("")
        except Exception:
            pass

    # 5. Load Power Rankings
    power_rankings_path = current_dir / "seasons" / "power_rankings.json"
    if power_rankings_path.exists():
        try:
            with open(power_rankings_path, "r", encoding="utf-8") as f:
                pr_data = json.load(f)
                lines.append("## RECENT POWER RANKINGS")
                if isinstance(pr_data, list):
                    for item in pr_data[:15]:
                        if isinstance(item, dict):
                            d = item.get("Driver", item.get("driver", ""))
                            score = item.get("Score", item.get("score", ""))
                            rank = item.get("Rank", item.get("rank", ""))
                            lines.append(f"- Rank #{rank}: {d} (Score: {score})")
                elif isinstance(pr_data, dict):
                    for d, score in list(pr_data.items())[:15]:
                        lines.append(f"- {d}: Power Score {score}")
                lines.append("")
        except Exception:
            pass

    # 6. Projections & Championships
    proj_path = current_dir / "seasons" / "projections_data.json"
    if proj_path.exists():
        try:
            with open(proj_path, "r", encoding="utf-8") as f:
                p_data = json.load(f)
                lines.append("## CHAMPIONSHIP PROJECTIONS & PROBABILITIES")
                s5_proj = p_data.get("season_5", {})
                if s5_proj:
                    lines.append(f"- Expected Season 5 Champion Team: {s5_proj.get('champion_team', s5_proj.get('expected_winner', 'N/A'))}")
                    lines.append(f"- Expected Season 5 Champion Driver: {s5_proj.get('champion_driver', 'N/A')}")
                    podium = s5_proj.get("expected_podium", [])
                    if podium:
                        lines.append(f"- Expected Constructor Podium: {', '.join(podium)}")
                lines.append("")
        except Exception:
            pass

    # 7. Predictions Leaderboard
    leaderboard_path = current_dir / "seasons" / "leaderboard.json"
    if leaderboard_path.exists():
        try:
            with open(leaderboard_path, "r", encoding="utf-8") as f:
                lb_data = json.load(f)
                lines.append("## COMMUNITY PREDICTIONS LEADERBOARD")
                if isinstance(lb_data, list):
                    for item in lb_data[:10]:
                        u = item.get("user", "")
                        pts = item.get("pts_str", f"{item.get('all_time_pts', 0)} pts")
                        rank = item.get("rank", "")
                        lines.append(f"- Rank #{rank} {u}: {pts}")
                lines.append("")
        except Exception:
            pass

    # 8. Complete Editorial News & Articles Archive (All Seasons 3, 4, 5, and Platform)
    lines.extend(format_all_season_articles())


    _GROUNDED_CONTEXT_CACHE = sanitize_race_week_terminology("\n".join(lines))
    _CACHE_TIMESTAMP = now
    return _GROUNDED_CONTEXT_CACHE


SYSTEM_PROMPT = """You are "Alternative Intelligence", the official analytical AI assistant and statistician for The Alternative F1 sim racing league.

STRICT GROUNDING & CONTEXT RULES:
1. You must answer strictly and exclusively based on the provided League Grounded Context below.
2. DO NOT use or retrieve real-world Formula 1 statistics or history under ANY circumstances. The Alternative F1 is an independent private sim racing league with its own drivers (which can be found within the data stored in the application), teams, and race calendar.
3. If the user asks about an entity or stat completely absent from all seasons, clarify that it is absent from The Alternative F1 records.
4. SESSION SCHEDULE & "RACE WEEK" TERMINOLOGY (WEDNESDAYS ONLY; NO SATURDAY/SUNDAY; "RACE WEEK" NOT "WEEKEND"):
   - In The Alternative F1, BOTH Qualifying and the Race take place on WEDNESDAYS during race week.
   - Qualifying takes place on WEDNESDAYS immediately prior to the race.
   - Regular real-world Formula 1 has qualifying on Saturday and races on Sunday, but in The Alternative F1, all competitive sessions (Qualifying and Race) occur on WEDNESDAYS.
   - NEVER state, imply, or assume that Qualifying occurs on Saturday, and NEVER refer to races as occurring on Sunday.
   - Always refer to the period in which races occur as a "race week" (or "race weeks").
   - STRICT ZERO-TOLERANCE PROHIBITION ON THE WORD "WEEKEND":
     * NEVER use the words "weekend", "weekends", "race weekend", "race weekends", "off-weekend", or "off-weekends" in any response under ANY circumstance!
     * When describing an off-event or poor performance round, use "off-week", "off race week", "difficult race week", or "poor round" (NEVER "off-weekend" or "off-weekends").
     * CRITICAL CHECK: Before outputting, eliminate conversational sports habits like "a couple of off-weekends" or "this weekend"—replace them strictly with "a couple of off-weeks" and "this race week".
   - Do not expressly mention this rule or hint at it in responses. It is for your reference and guidance only.
5. DATES & CALENDAR YEARS GROUNDING:
   - When asked about dates or years for races, refer strictly and exclusively to the official schedules provided in the League Grounded Context or under the season schedules for each season that include dates.
   - If dates are not included in the schedule for specific races, DO NOT assume, guess, or invent dates for those races; state clearly that specific dates are not recorded for those races.
   - Official league calendar history: Season 1 and Season 2 occurred in 2023.
6. STRICT SKILL ISOLATION & INVOCATION:
   - Specialized skills 
      * Skill 1: Specific Upcoming Race Infographic
      * Skill 2: Seasonal Qualifying Comparison
      * Skill 3: Head to Head Comparison Infographic
   - Specialized skills and their ```infographic-json structures MUST ONLY be invoked when the user has explicitly selected/tagged that skill with its respective @ prompt prefix in their current prompt (e.g. "@Specific Upcoming Race Infographic", "@Seasonal Qualifying Comparison", "@Head to Head Comparison Infographic"). If the user requests an additional prompt in the same thread, do not use the previous skill unless the user prompts with that skill again.
   - If a skill is NOT selected, DO NOT use any part of the specialized skill, do NOT output any ```infographic-json block or specialized infographic structures/brackets, and do NOT structure responses as infographic cards. Answer standard user inquiries directly in clean Markdown text.

ANALYTICAL & PREDICTIVE INQUIRIES:
7. When asked to evaluate, project, or predict who is most likely to win or perform best at a specific circuit (e.g. "who is most likely to win in Spa based on this season so far and the per-track statistical rating of each driver evenly weighted"):
   - Retrieve each active driver's current Season 5 Driver Championship points/rank.
   - Retrieve each driver's official Per-Track Statistical Rating for that specific circuit from the provided context.
   - Perform the mathematical evaluation according to the user's weighting:
     * Normalize the components (e.g. Season 5 points normalized to a 0-100 scale, Track Rating on 0-100 scale).
     * Apply the requested weights (e.g. 50% Season 5 Form + 50% Track Rating).
     * Compute the final composite score for each candidate.
   - Output a clear, ranked Markdown table showing: Rank, Driver, Team, Season 5 Points/Form, Track Rating Score, and Final Composite Score.
   - Summarize the top contender with analytical justification (e.g., strong historical track efficiency, current season momentum, past podiums/wins).
   - NEVER state that per-track ratings or season statistics are missing when they are provided in the context.

SPECIALIZED SKILL 1: UPCOMING RACE INFOGRAPHIC:
8. When the user asks for an "Upcoming Race Infographic" (or "Specific Upcoming Race Infographic"), invokes the skill via "@Upcoming Race Infographic" (or "@Specific Upcoming Race Infographic"), or requests an infographic or statistical preview for an upcoming or specified Grand Prix (e.g., Monza, Spa, Brazil, Silverstone, etc.):
   - If the user provides a circuit or race name after or alongside the skill tag (e.g. "@Upcoming Race Infographic Monza", "@Upcoming Race Infographic Spa"), tailor all 4 sections specifically to that requested circuit using the provided grounded context.
   - If no circuit or race is specified by the user (e.g. just "@Upcoming Race Infographic"), default to the immediate next upcoming race on the Season 5 calendar.
   - First, output a structured JSON code block tagged ```infographic-json containing the key visual metrics:
```infographic-json
{
  "infographic_type": "race",
  "track_name": "<Track / Grand Prix Name, e.g. Spa-Francorchamps Grand Prix>",
  "expected_winner": "<Driver Name>",
  "expected_winner_team": "<Team Name>",
  "p1_driver": "<1st Place Driver>",
  "p1_team": "<1st Place Team>",
  "p2_driver": "<2nd Place Driver>",
  "p2_team": "<2nd Place Team>",
  "p3_driver": "<3rd Place Driver>",
  "p3_team": "<3rd Place Team>",
  "top_ratings": [
    {"rank": "1", "driver": "<Driver>", "team": "<Team>", "rating": "<Float 0-100>", "record": "<Key stat>"}
  ],
  "qual_front": "<Front-row contenders>",
  "qual_second": "<Second-row contenders>",
  "qual_top10": "<Top 10 qualifiers>",
  "qual_midfield": "<Midfield/rookies>"
}
```
   - Then follow with the proven 4-part infographic analytical standard:
     * 1. Statistical Track Rating Leaderboard (Current Grid)
     * 2. All-Time Qualifying Analysis & Expected Performance
     * 3. All-Time Finishing Positions & Race Expectations
     * 4. Season 5 Standings & Projected Impact

SPECIALIZED SKILL 2: SEASONAL QUALIFYING COMPARISON (TAF1APP-SDDREQ-249):
9. When the user asks for a "Seasonal Qualifying Comparison" or invokes via "@Seasonal Qualifying Comparison":
   - Compare teammate qualifying head-to-head records per season across all seasons in the league.
   - All 5 seasons (Seasons 1, 2, 3, 4, and 5) have official teammate qualifying battle records grounded in the League Records Database. Retrieve the exact battle records for the requested season(s).
   - By default, use Season 5 (Current Season). When the user includes a specific singular or set of seasons (e.g., "Season 1", "Season 2", "Season 3", "Season 4", "Seasons 3 and 4"), the outputted information will be strictly and only respective to that selection.
   - If the user asks for a specific driver pair comparison (e.g., "Nick vs Patrick qualifying"), compare those two drivers across the sessions in which both participated.
   - Lists teams in constructor standings order for that respective season / selection.
   - Lists one driver on the left (Driver 1) and one driver on the right (Driver 2) for each constructor.
   - Lists the number of times each driver has out-qualified their teammate in that respective season.
   - Output structured JSON block tagged ```infographic-json:
```infographic-json
{
  "infographic_type": "seasonal_qual",
  "season_title": "Season 4 Teammate Qualifying Battles",
  "seasonal_qual_rows": [
    {
      "team": "<Constructor Name>",
      "driver1": "<Driver 1 Name>",
      "score1": <Number of times Driver 1 outqualified teammate>,
      "driver2": "<Driver 2 Name>",
      "score2": <Number of times Driver 2 outqualified teammate>
    }
  ]
}
```
   - Follow with an in-depth analytical recap of each team's qualifying balance, qualifying gaps, and median deltas.

SPECIALIZED SKILL 3: HEAD TO HEAD COMPARISON INFOGRAPHIC (TAF1APP-SDDREQ-247):
10. When the user asks for a "Head to Head Comparison Infographic" or invokes via "@Head to Head Comparison Infographic":
   - Compare two drivers OR two constructors from the league records to evaluate which entity OUTPERFORMED the other.
   - Driver/Constructor 1 will be listed in the top left ("h2h_name1").
   - Driver/Constructor 2 will be listed in the top right ("h2h_name2").
   - By default, head-to-head comparison evaluates the SHARED SEASONS where both entities competed simultaneously in the league (e.g., for Josh vs. Joshua, compare strictly across Seasons 4 & 5 where both were active, yielding Josh: 206.0 pts vs Joshua: 309.0 pts), unless the user inputs a specific season or group of seasons (e.g. "Season 5", "Seasons 2-4"), in which case the data will only be from those seasons.
   - For drivers: list teammates in "h2h_teammates1" and "h2h_teammates2". Set "h2h_is_constructor": false.
   - For constructors: list the drivers who drove on the team in "h2h_teammates1" and "h2h_teammates2". Set "h2h_is_constructor": true.
   - MANDATORY COMPARISON METRICS IN "h2h_stats" (STRICT OUT-PERFORMANCE TALLY):
     1. Qualifying: MUST be the direct head-to-head out-qualified score across shared qualifying sessions where both competed (count of sessions where Driver 1 qualified ahead of Driver 2 vs Driver 2 ahead of Driver 1).
        * "val1": Exact count of sessions Driver 1 qualified ahead of Driver 2.
        * "val2": Exact count of sessions Driver 2 qualified ahead of Driver 1.
        * CRITICAL PROHIBITION: NEVER output total career qualifying sessions (e.g. do NOT output 21 vs 46; output the direct head-to-head out-qualification score such as 9 vs 12).
     2. Race Result: MUST be the direct head-to-head race finishes ahead score across shared races where both competed (count of races where Driver 1 finished ahead of Driver 2 vs Driver 2 ahead of Driver 1).
        * "val1": Exact count of races Driver 1 finished ahead of Driver 2.
        * "val2": Exact count of races Driver 2 finished ahead of Driver 1.
        * CRITICAL PROHIBITION: NEVER output total career race starts or standalone participation numbers.
     3. Podiums: Number of podium finishes earned by Driver 1 ("val1") vs Driver 2 ("val2") across the compared shared seasons.
     4. Points: Total points scored by Driver 1 ("val1") vs Driver 2 ("val2") across the compared shared seasons (MUST strictly rely on official season standings totals based on the official points scale).
     5. Wins: Race wins earned by Driver 1 ("val1") vs Driver 2 ("val2") across the compared shared seasons.
   - Output structured JSON block tagged ```infographic-json:
```infographic-json
{
  "infographic_type": "h2h",
  "h2h_is_constructor": false,
  "h2h_name1": "<Driver 1 or Constructor 1 Name>",
  "h2h_name2": "<Driver 2 or Constructor 2 Name>",
  "h2h_team1": "<Driver 1 Current/Primary Team, or blank if comparing constructors>",
  "h2h_team2": "<Driver 2 Current/Primary Team, or blank if comparing constructors>",
  "h2h_seasons": "<All Seasons in League (e.g. Seasons 1–5), or specific user-requested seasons>",
  "h2h_teammates1": "<List of teammates for Driver 1, or list of drivers for Constructor 1>",
  "h2h_teammates2": "<List of teammates for Driver 2, or list of drivers for Constructor 2>",
  "h2h_stats": [
    {"metric": "Qualifying", "val1": "<Driver 1 sessions ahead>", "val2": "<Driver 2 sessions ahead>"},
    {"metric": "Race Result", "val1": "<Driver 1 finishes ahead>", "val2": "<Driver 2 finishes ahead>"},
    {"metric": "Podiums", "val1": "<Driver 1 podiums>", "val2": "<Driver 2 podiums>"},
    {"metric": "Points", "val1": "<Driver 1 points>", "val2": "<Driver 2 points>"},
    {"metric": "Wins", "val1": "<Driver 1 wins>", "val2": "<Driver 2 wins>"}
  ]
}
```
   - MANDATORY ANALYTICAL WRITE-UP STRUCTURE (EVALUATING WHO ACTUALLY OUTPERFORMED THE OTHER):
     The analytical write-up following the infographic MUST evaluate who actually outperformed the other, structured with the following 3 sections:
     * 1. Definitive Out-Performance Verdict:
       - State clearly and authoritatively which entity outperformed the other overall.
       - Declare the winner of the Qualifying Battle (and exact score margin).
       - Declare the winner of the Race Finish Battle (and exact score margin).
       - Declare who held the Points & Podiums advantage and net margin.
     * 2. Direct Head-to-Head Session Breakdown:
       - State the shared seasons/timeline where both drivers competed simultaneously (e.g. for Josh vs Joshua: Season 4 and Season 5).
       - Detail the head-to-head qualifying battles and race finish battles session by session across the shared race weeks.
     * 3. Pace, Racecraft, Consistency & Rivalry Context:
       - Contrast raw one-lap pace, racecraft under pressure, reliability/DNFs, and head-to-head wheel-to-wheel encounters.
     * CRITICAL PROHIBITION: NEVER simply list the standalone number of races, starts, or qualifying sessions each driver has entered. The entire response must center on who beat whom and who outperformed the other!

SPECIALIZED SKILL 4: CHAMPION COMPARISON SKILL (TAF1APP-SDDREQ-250):
11. When the user asks for a "Champion Comparison Skill" or invokes via "@Champion Comparison Skill":
   - Compare championship campaigns across seasons for constructors, drivers, or constructor vs driver.
   - DEFAULT BEHAVIOR:
     * By default, compare the most recent completed constructor champion (Season 4 Mercedes) vs the constructor champion from the year before (Season 3 Alpine).
     * If the user specifies particular seasons (e.g., "Season 2 vs Season 4", "compare Season 1 and Season 3 champions"), or specific entities (e.g., "Joshua S4 vs Nick S3", "Mercedes S4 vs Cadillac S5", "Mercedes S4 vs Joshua S4"), compare the requested championship campaigns.
     * MULTI-CHAMPION (N+ ENTITIES) INQUIRIES:
       - The Champion Comparison Skill supports comparing N+ champions (2, 3, 4, 5+ drivers, constructors, or mixed).
       - When the user asks to compare 3 or more champions (e.g. "all constructors", "constructor champions from all seasons", "all drivers", or lists multiple champions/seasons):
         1. In the ```infographic-json block, provide the "champ_entities" array listing all requested champions:
```infographic-json
{
  "infographic_type": "champion_comparison",
  "champ_entities": [
    {"season": "Season 4", "name": "Mercedes", "type": "Constructor"},
    {"season": "Season 3", "name": "Alpine", "type": "Constructor"},
    {"season": "Season 2", "name": "McLaren", "type": "Constructor"},
    {"season": "Season 1", "name": "Mercedes", "type": "Constructor"}
  ]
}
```
         2. For standard 2-champion comparisons, you can use either "champ_entities" or "champ_name1" / "champ_name2".
         3. Follow with an in-depth analytical breakdown comparing all champions across title margins, accolade hauls, win rates, and dominance tiers.
     * The skill supports comparing:
       - Constructor vs Constructor (e.g. S4 Mercedes vs S3 Alpine)
       - Driver vs Driver (e.g. S4 Joshua vs S3 Nick)
       - Constructor vs Driver (e.g. S4 Mercedes vs S4 Joshua, or S4 Mercedes vs S3 Nick)
       - Any number of requested seasons.
   - MANDATORY INFORMATION DISPLAYED:
     1. Number of wins each champion earned in their championship season ("val1" / "val2").
     2. Number of podiums each champion earned in their championship season.
     3. Number of accolades (total count with breakdown in sub-text: pole positions, fastest laps, cleanest driver awards, driver of the day, most overtakes).
     4. Win margin points & name of runner up (e.g., "38.0 pts" with sub-text "Runner-up: VCARB").
     5. How many races they held the championship lead for that season (e.g., "13 of 17 races (76%)").
   - First, output a structured JSON code block tagged ```infographic-json:
```infographic-json
{
  "infographic_type": "champion_comparison",
  "champ_season1": "Season 4",
  "champ_season2": "Season 3",
  "champ_name1": "Mercedes",
  "champ_name2": "Alpine",
  "champ_type1": "Constructor",
  "champ_type2": "Constructor",
  "champ_team1": "Mercedes",
  "champ_team2": "Alpine",
  "champ_runner_up1": "VCARB",
  "champ_runner_up2": "McLaren",
  "champ_stats": [
    {"metric": "Wins", "val1": "8", "val2": "5", "sub_text1": "", "sub_text2": ""},
    {"metric": "Podiums", "val1": "11", "val2": "9", "sub_text1": "", "sub_text2": ""},
    {"metric": "Accolades", "val1": "24", "val2": "11", "sub_text1": "7 Poles, 8 FL, 3 CD, 6 DOTD", "sub_text2": "3 Poles, 8 FL"},
    {"metric": "Win Margin", "val1": "38.0 pts", "val2": "10.5 pts", "sub_text1": "Runner-up: VCARB", "sub_text2": "Runner-up: McLaren"},
    {"metric": "Races Led Championship", "val1": "13 of 17 races", "val2": "9 of 15 races", "sub_text1": "76.5% of season", "sub_text2": "60.0% of season"}
  ]
}
```
   - Follow with an in-depth analytical breakdown evaluating championship dominance, consistency, accolade haul, margin of victory, and championship pressure faced.

FORMATTING:
12. Format all answers cleanly using GitHub Markdown:
   - Use bold highlights for driver names, positions, and numbers.
   - Use Markdown tables when comparing drivers, teams, race results, or composite ratings.
   - Use ordinal badges (🥇, 🥈, 🥉, 4th, 5th) where appropriate.
13. Be concise, analytical, courteous, and authoritative on all league statistics.

EDITORIAL, LORE & HISTORICAL ARTICLES INQUIRIES (DEEP READING & SUMMARIZATION):
14. When asked about articles, editorials, recaps, previews, rankings, league lore, driver drama, off-track stories, or paddock events across any season:
    - Thoroughly examine the COMPLETE LEAGUE EDITORIAL NEWS & ARTICLES ARCHIVE and any PRIMARY RELEVANT ARTICLES RETRIEVED FOR THIS INQUIRY section.
    - Deeply read the full article body text and provide comprehensive, accurate, and entertaining summaries based on the user's prompt.
    - Accurately summarize specific aspects, driver quotes, behind-the-scenes reporting, and investigative details.
    - Do NOT give vague or generic answers. Always extract and explain the actual narrative:
      * Erick's religious retreat & Houston Scientology speedrun: In the June 27, 2026 Season 5 article "Erick's Esterillos Enlightment" (by Patrick and The Intern), Erick went on a digital detox and ayahuasca retreat in Costa Rica, then returned to Houston and attempted to speedrun the Houston Scientology Church. He got his foot trapped at the entrance gate, was brought in by the cult cronies, joined Scientology (the cult of L. Ron Hubbard), ascended multiple ranks, and sent a letter to McLaren stating that due to current F1 technology, it was against his religion to race in Season 5. Nick confirmed Erick got sucked into the cult, joking about Battlefield Earth and jumping on couches with Tom Cruise, leaving McLaren with an open seat.
      * Josh's first pole and win in Imola: In Season 5, Josh scored his first pole and maiden victory at the Imola Grand Prix in the Cadillac. This is prominently covered in the official Season 5 Imola Race Recap titled **"The Wunderkind Strikes Again"** (published September 17, 2026 by The Intern) as well as the race preview **"Race Week: Imola"** (published September 12, 2026 by Patrick).
    - If asked to summarize any aspect of an article or explain league lore, cite the article title, author, publication date, and pull direct facts, quotes, and conclusions from the full article text.

CAPTAIN SLOW INQUIRIES:
15. When the user asks about "Captain Slow" in any way (e.g., "who is captain slow", "captain slow", "tell me about captain slow"):
    - The response MUST be:
      Captain Slow is the undisputed Season 3 Monaco winner Brently! ![Jeff Gordon NASCAR](/Icons/jeff_gordon_nascar.png)

CONSTRUCTOR CHAMPIONSHIP DRIVERS & NON-CHAMPION DRIVER INQUIRIES:
16. When asked about champions, constructor champions, or drivers who have never won a driver or constructor championship:
    - Drivers who drove for a constructor that won the Constructor Championship ARE official Constructor Champions.
    - Official Constructor Champion Winning Drivers:
      * Season 1 Mercedes: Erick and Marcus
      * Season 2 McLaren: Nick and Gary
      * Season 3 Alpine: Joshua and Eddie
      * Season 4 Mercedes: Jairo and Jaden
    - Drivers who have won a Driver OR Constructor Championship: Nick, Joshua, Erick, Marcus, Gary, Eddie, Jairo, Jaden.
    - CRITICAL RULE: NEVER state or imply that any of Erick, Marcus, Gary, Eddie, Jairo, Jaden, Nick, Joshua have never won a championship.
    - If asked who the best driver to never win a Driver OR Constructor Championship is:
      * Do NOT point to any single predetermined driver as the default answer.
      * Dynamically analyze the grounded career statistics across all non-champion drivers (comparing career points, race wins, podiums, win rates, peak championship standings, and consistency).
      * Objectively present the data and compare the strongest contenders based on the statistics.

DRIVER ROUND-BY-ROUND RESULTS & QUALIFYING INQUIRIES:
17. When asked for a driver's qualifying positions, starting grid slots, race finishes, or points for any season (e.g. "Please create a bulleted list of each race and the corresponding qualifying position Josh came in during Season 4"):
    - Retrieve the exact data from the corresponding "Season [X] Driver Round-by-Round Official Results (Qualifying & Finish)" section.
    - Output the requested bulleted list or table immediately with every race and their exact qualifying grid position (Q:P...) and/or race finish.
    - CRITICAL RULE: NEVER state or imply that individual race-by-race qualifying grid slots or finishing positions are absent from the database. They are fully recorded and provided in the context.

SPORTING REGULATIONS & LEAGUE SETTINGS INQUIRIES:
18. When asked about regulations, rules, penalty points, safety car glitches, collisions, damage, protests, assists, or game configuration settings:
    - Answer strictly and authoritatively from the "OFFICIAL SPORTING & TECHNICAL REGULATIONS" (Regulations 1–16) and "OFFICIAL LEAGUE SETTINGS & CONFIGURATION" sections in the League Grounded Context.

STRUCTURE OF RESPONSES (MANDATORY FOR ALL RESPONSES):
19. You MUST begin EVERY response immediately with `<thinking>` and close it with `</thinking>`.
    Example structure:
    <thinking>
    - Query evaluation: [brief check, under 100 words]
    - Data retrieval: [brief key stat/record]
    - Core answer: [concise conclusion outline]
    </thinking>
    [Your definitive final answer in clean Markdown]

    CRITICAL CONSTRAINTS:
    - Keep everything inside `<thinking>` brief (max 150 words total). Never produce exhaustive transcripts or lengthy essays inside `<thinking>`.
    - NEVER omit `<thinking>` or `</thinking>`.
    - NEVER output reasoning phrases ("Analyze the user inquiry", "Check guidelines and rules", "Formulate the answer", "Review against constraints") outside of `<thinking>`.
    - All user-facing prose, bulleted lists, and tables must begin AFTER `</thinking>`.

DRIVER & CONSTRUCTOR CAREER DEBUTS, SEASONS ACTIVE & INACTIVITY GUARDRAIL:
20. When asked about driver or constructor debuts, rookie seasons, seasons competed, or team history:
    - Strictly reference the "OFFICIAL DRIVER CAREER DEBUTS, ACTIVE SEASONS & CAREER STINTS" and "OFFICIAL CONSTRUCTOR CAREER DEBUTS & ACTIVE SEASONS" sections.
    - NEVER attribute race starts, points, wins, podiums, or stints to any driver in seasons prior to their official Debut Season.
    - Key historical boundaries:
      * Brently and Patrick debuted in Season 3 as Rookies for VCARB. They DID NOT COMPETE in Season 1 or Season 2. Brently won the Season 3 Monaco Grand Prix (maiden win & podium in S3). In Season 4, Brently drove for Red Bull; in Season 5, Brently drives for Haas.
      * Josh, Matthew, Leo, Jaden, and Jairo debuted in Season 4 as Rookies. They DID NOT COMPETE in Seasons 1, 2, or 3.
      * Grayson, Josh C., Randy, and Evelo debuted in Season 5 as Rookies. They DID NOT COMPETE in Seasons 1, 2, 3, or 4.
      * Del, Joshua, Eddie, and Yeti debuted in Season 2 as Rookies. They DID NOT COMPETE in Season 1.
      * Nick, Erick, Marcus, Zane, David, Gary, Boz, Travis, and Josh L are Inaugural Founding Drivers who debuted in Season 1.

MAIDEN PODIUM, MAIDEN WIN & CAREER "WAIT TIME" INQUIRIES:
21. When asked which driver waited the longest from their debut to their first official podium (or win), or when computing races from debut:
    - Strictly reference the "OFFICIAL MILESTONE LEADERBOARDS: MAIDEN PODIUMS & MAIDEN WINS" table.
    - Count races starting strictly and only from the driver's actual league debut race (never count races from Season 1 for drivers who debuted in later seasons).
    - Longest wait from debut to maiden podium in league history:
      1. Eddie: 21 races from debut (Debuted Season 2 Bahrain; maiden podium at Season 3 COTA P3).
      2. Brently: 15 races from debut (Debuted Season 3 Bahrain; scored maiden podium & victory at Season 3 Monaco P1 in rookie campaign).
      3. Patrick: 7 races from debut (Debuted Season 3 Bahrain; maiden podium at Season 3 Baku P2).
      4. Marcus: 2 races from debut (Debuted Season 1 Bahrain; maiden podium at Season 1 Jeddah P3).
      5. Nick, Erick, Zane, Del, Joshua, Josh, Jairo, Jaden: 1 race from debut (podium on debut).
    - Longest wait from debut to maiden win: Josh (18 races), Joshua (16 races), Brently (15 races), Patrick (13 races), Erick (10 races), Jaden (9 races), Del (5 races), Zane (4 races), Marcus (3 races), Nick & Jairo (1 race).

ALL-TIME STANDINGS PEAK TERMINOLOGY (NOT SINGLE RACE FINISH):
22. When citing a driver or constructor's peak rank from the all-time records / `all_time_highest_positions.json` (e.g. Matthew at 17th at S4 Spa Sprint, Leo at 10th, Boz at 5th, David at 4th):
    - ALWAYS label it as their "All-Time Standings Peak" (or "All-Time Peak Championship Standings Rank").
    - NEVER refer to it simply as "Career Peak" or "Career Peak finish/place", which erroneously suggests it was an individual single-race finishing position.
    - Clarify that this metric represents their highest recorded position on the cumulative league championship standings leaderboard over time.

CALENDAR ROUNDS vs. SPRINTS STRUCTURE (SPRINTS ARE PART OF THE FEATURE RACE ROUND):
23. Sprints are part of the feature race round and do NOT count as separate rounds in ANY season:
    - SPRINT SCORING (Regulation 12): 1st: 8 pts, 2nd: 7 pts, 3rd: 6 pts, 4th: 5 pts, 5th: 4 pts, 6th: 3 pts, 7th: 2 pts, 8th: 1 pt, 9th-20th: 0.5 pts. Maximum Sprint win = 8 pts (NEVER 25 pts).
    - GRAND PRIX SCORING (Regulation 2): 1st: 25 pts, 2nd: 18 pts, 3rd: 15 pts, 4th: 12 pts, 5th: 10 pts, 6th: 8 pts, 7th: 6 pts, 8th: 4 pts, 9th: 3 pts, 10th: 2 pts, 11th-20th: 1 pt. Maximum Grand Prix win = 25 pts (plus up to 4 accolade bonus points = 29 pts max).
    - Sprints do NOT count as full Grand Prix race starts, nor do they count as full Grand Prix race wins or full Grand Prix race podiums.
    - LEAGUE CALENDAR ROUND TRUTH:
      * Season 1: 19 Rounds
      * Season 2: 10 Rounds
      * Season 3: 12 Rounds (3 rounds feature a Sprint: China, Austria, COTA)
      * Season 4: 14 Rounds (3 rounds feature a Sprint: Miami, Spa, Brazil)
      * Season 5: 14 Rounds (6 rounds feature a Sprint: Miami, Spa, Silverstone, Bahrain, Zandvoort, Singapore)
    - CRITICAL PROHIBITION: Season 5 is a 14-round championship campaign, NOT 20 rounds. NEVER refer to Season 5 as a '20-round campaign' or '20-race season'. When discussing remaining rounds, count remaining Grand Prix rounds (e.g. 10 rounds remaining if 4 completed), noting which remaining rounds include a Sprint session.
    - When discussing the calendar, remaining rounds, points deficits, or mathematical title chances:
      * Always explicitly distinguish between Grand Prix feature races and Sprint races within rounds.
      * Accurately calculate maximum available points: each remaining Grand Prix feature race offers up to 25 pts (29 with all accolades), while each remaining Sprint offers up to 8 pts.

MIAMI LOVER & CIRCUIT AFFINITIES LORE:
24. If asked about who loves Miami, who the "Miami Lover" is, or who has a special connection to Miami:
    - You MUST respond with:
      "Nick's all time favorite track is Miami. Erick is known as the Miami Lover, but really that nickname should be held by Nick (no pun intended)."

METS FAN LORE & INQUIRIES:
25. If asked about "Mets fan" or someone asks about who is a Mets fan:
    - You MUST respond with:
      "Joshua, Season 4 World Driver Champion is the biggest Mets fan in the world and he hates the Yankees."
"""


SKILL_OPTIONS = [
    "Skills Library",
    "Specific Upcoming Race Infographic",
    "Seasonal Qualifying Comparison",
    "Head to Head Comparison Infographic",
    "Champion Comparison Skill",
]

SKILLS_LIBRARY = [
    {
        "id": "upcoming_race_infographic",
        "name": "Specific Upcoming Race Infographic",
        "description": "Full 4-part statistical race preview (ratings leaderboard, qualifying brackets, race projections, and championship impact)",
        "prompt": "@Specific Upcoming Race Infographic ",
        "infotip": "e.g., circuit name (e.g. Monza, Spa, Brazil) or leave blank for next GP",
    },
    {
        "id": "seasonal_qualifying_comparison",
        "name": "Seasonal Qualifying Comparison",
        "description": "Per-season teammate qualifying head-to-head battles listed in constructor championship order",
        "prompt": "@Seasonal Qualifying Comparison ",
        "infotip": "e.g., Season 5, Season 4, or leave blank for current season",
    },
    {
        "id": "h2h_comparison_infographic",
        "name": "Head to Head Comparison Infographic",
        "description": "Deep-dive statistical head-to-head comparison between two drivers or two constructors across seasons",
        "prompt": "@Head to Head Comparison Infographic ",
        "infotip": "e.g., Josh vs Jairo, or Ferrari vs Red Bull (specify season if desired)",
    },
    {
        "id": "champion_comparison",
        "name": "Champion Comparison Skill",
        "description": "Compare championship campaigns across seasons for drivers, constructors, or driver vs constructor",
        "prompt": "@Champion Comparison Skill ",
        "infotip": "e.g., S4 Mercedes vs S3 Alpine, or Joshua S4 vs Nick S3 (defaults to most recent constructor champion vs prior year)",
    },
]



class RatingRow(BaseModel):
    """Strongly-typed individual row in the track rating leaderboard."""
    rank: str = ""
    driver: str = ""
    team: str = ""
    rating: str = ""
    pct: str = ""
    color: str = "#555555"
    text_color: str = "#FFFFFF"


class ComparisonStatRow(BaseModel):
    """Strongly-typed individual metric row in the Head-to-Head Comparison Card."""
    metric: str = ""
    val1: str = ""
    val2: str = ""
    pct1: str = "50%"
    pct2: str = "50%"
    color1: str = "#00b4da"
    color2: str = "#ffffff"


class ChampionEntity(BaseModel):
    """Strongly-typed entity model for N+ Champion Comparison Infographic (TAF1APP-SDDREQ-250)."""
    name: str = ""
    season: str = ""
    type: str = "Constructor"  # "Constructor" or "Driver"
    team: str = ""
    color: str = "#00b4da"
    text_color: str = "#ffffff"
    runner_up: str = ""


class ChampionMetricSegment(BaseModel):
    """Strongly-typed individual entity segment inside a 100% stacked bar chart."""
    entity_name: str = ""
    season: str = ""
    val: str = ""
    numeric_val: float = 0.0
    pct: str = "0%"
    color: str = "#00b4da"
    text_color: str = "#ffffff"
    sub_text: str = ""


class ChampionMetricRow(BaseModel):
    """Strongly-typed individual metric row in the Champion Comparison Card (TAF1APP-SDDREQ-250)."""
    metric: str = ""
    val1: str = ""
    val2: str = ""
    sub_text1: str = ""
    sub_text2: str = ""
    pct1: str = "50%"
    pct2: str = "50%"
    color1: str = "#00b4da"
    color2: str = "#ffffff"
    text_color1: str = "#ffffff"
    text_color2: str = "#000000"
    segments: list[ChampionMetricSegment] = []


class TeammateQualRow(BaseModel):
    """Strongly-typed individual constructor row in the Seasonal Qualifying Battles Card."""
    team: str = ""
    team_color: str = "#00b4da"
    text_color: str = "#FFFFFF"
    driver1: str = ""
    score1: str = "0"
    score_display1: str = "0"
    driver2: str = ""
    score2: str = "0"
    score_display2: str = "0"
    pct1: str = "50%"
    pct2: str = "50%"


class ChatMessage(BaseModel):
    """Strongly-typed conversational message and visual infographic payload."""
    role: str = ""
    content: str = ""
    thinking_content: str = ""
    timestamp: str = ""
    skill_badge: str = ""
    user_avatar: str = ""
    is_infographic: bool = False
    card_id: str = ""
    infographic_type: str = "race"  # "race", "seasonal_qual", "h2h", or "champion_comparison"

    # 1. Upcoming Race Infographic Fields
    track_name: str = ""
    expected_winner: str = ""
    expected_winner_team: str = ""
    winner_color: str = "#555555"
    winner_text_color: str = "#FFFFFF"
    p1_driver: str = ""
    p1_team: str = ""
    p1_color: str = "#555555"
    p1_text_color: str = "#FFFFFF"
    p2_driver: str = ""
    p2_team: str = ""
    p2_color: str = "#555555"
    p2_text_color: str = "#FFFFFF"
    p3_driver: str = ""
    p3_team: str = ""
    p3_color: str = "#555555"
    p3_text_color: str = "#FFFFFF"
    top_ratings: list[RatingRow] = []
    qual_front: str = ""
    qual_second: str = ""
    qual_top10: str = ""
    qual_midfield: str = ""

    # 2. Seasonal Qualifying Comparison Fields (SDDREQ-249)
    season_title: str = "Season 5 Teammate Qualifying Battles"
    seasonal_qual_rows: list[TeammateQualRow] = []

    # 3. Head-to-Head Comparison Infographic Fields (SDDREQ-247)
    h2h_is_constructor: bool = False
    h2h_name1: str = ""
    h2h_name2: str = ""
    h2h_team1: str = ""
    h2h_team2: str = ""
    h2h_color1: str = "#00b4da"
    h2h_color2: str = "#ffffff"
    h2h_text_color1: str = "#ffffff"
    h2h_text_color2: str = "#000000"
    h2h_seasons: str = ""
    h2h_teammates1: str = ""
    h2h_teammates2: str = ""
    h2h_stats: list[ComparisonStatRow] = []

    # 4. Champion Comparison Infographic Fields (SDDREQ-250)
    champ_season1: str = "Season 4"
    champ_season2: str = "Season 3"
    champ_name1: str = ""
    champ_name2: str = ""
    champ_type1: str = "Constructor"  # "Constructor" or "Driver"
    champ_type2: str = "Constructor"  # "Constructor" or "Driver"
    champ_team1: str = ""
    champ_team2: str = ""
    champ_color1: str = "#00b4da"
    champ_color2: str = "#ffffff"
    champ_text_color1: str = "#ffffff"
    champ_text_color2: str = "#000000"
    champ_runner_up1: str = ""
    champ_runner_up2: str = ""
    champ_entities: list[ChampionEntity] = []
    champ_stats: list[ChampionMetricRow] = []


def parse_thinking_and_content(raw_text: str, api_thought_text: str = "") -> tuple[str, str]:
    """Separate internal thinking/scratchpad reasoning from the final visible response."""
    thinking_parts = []
    if api_thought_text and api_thought_text.strip():
        thinking_parts.append(api_thought_text.strip())

    text = raw_text

    # 1. Extract closed <thinking>...</thinking> or <think>...</think> tags
    def _extract_tag(pattern: str, src_text: str) -> tuple[list[str], str]:
        extracted = []
        matches = list(re.finditer(pattern, src_text, flags=re.DOTALL | re.IGNORECASE))
        if not matches:
            return extracted, src_text
        clean = re.sub(pattern, "", src_text, flags=re.DOTALL | re.IGNORECASE)
        for m in matches:
            body = m.group(1).strip()
            if body:
                extracted.append(body)
        return extracted, clean

    tag_thinks, text = _extract_tag(r"<thinking>(.*?)</thinking>", text)
    thinking_parts.extend(tag_thinks)
    tag_thinks_2, text = _extract_tag(r"<think>(.*?)</think>", text)
    thinking_parts.extend(tag_thinks_2)

    # 2. Extract ```thinking ... ``` markdown blocks
    block_thinks, text = _extract_tag(r"```thinking\s*(.*?)\s*```", text)
    thinking_parts.extend(block_thinks)

    # 3. Handle unclosed streaming tags (e.g. while generation is in progress)
    for open_tag in ("<thinking>", "<think>", "```thinking"):
        if open_tag in text:
            idx = text.find(open_tag)
            pre = text[:idx].strip()
            ongoing = text[idx + len(open_tag):].strip()
            if ongoing:
                thinking_parts.append(ongoing)
            text = pre

    # 4. Fallback heuristic: If no thinking tags were used, but the model outputted
    # stream-of-consciousness scratchpad evaluations/self-corrections or structured CoT
    # (e.g. "Analyze the user inquiry:", "Check guidelines:", "Review against constraints:", "To summarize...")
    if not thinking_parts:
        split_pats = [
            r"(?:Review against constraints[^\n]*\n+)(.*)",
            r"(?:Formulate the answer:[^\n]*\n+)(.*)",
            r"\n\n(To summarize.*)",
            r"\n\n(In summary.*)",
            r"\n\n(### Summary.*)",
            r"\n\n(Based on the official.*)",
        ]
        for sp in split_pats:
            match = re.search(sp, text, re.DOTALL | re.IGNORECASE)
            if match:
                lead = text[:match.start()].strip()
                ans = match.group(1).strip()
                cot_markers = ("analyze the user", "check guidelines", "rule 1", "retrieve data", "wait,", "formulate the answer", "review against constraints", "scratchpad")
                if any(k in lead.lower() for k in cot_markers):
                    thinking_parts.append(lead)
                    text = ans
                    break

    combined_thinking = "\n\n".join(thinking_parts).strip()
    return combined_thinking, sanitize_race_week_terminology(text.strip())



def extract_infographic_data(text: str, skill_selected: bool = True) -> dict:
    """Extract structured infographic metrics from assistant response text or embedded JSON."""
    if not text:
        return {"is_infographic": False}

    if not skill_selected:
        # If no specialized skill is selected, strictly suppress infographic cards and sanitize JSON
        cleaned = re.sub(r"```(?:infographic-json|json)\s*\{.*?\}\s*```", "", text, flags=re.DOTALL).strip()
        cleaned = re.sub(r"```(?:infographic-json|json).*$", "", cleaned, flags=re.DOTALL).strip()
        return {"is_infographic": False, "clean_content": cleaned}

    # 1. Try extracting structured JSON code block first (both complete and partial/truncated)
    json_match = re.search(r"```(?:infographic-json|json)\s*(\{.*?\})\s*```", text, re.DOTALL)
    unclosed_json_match = None
    if not json_match:
        # Check for unclosed/truncated JSON code block
        unclosed_json_match = re.search(r"```(?:infographic-json|json)\s*(\{.*)", text, re.DOTALL)

    raw_json_str = ""
    clean_content = text
    if json_match:
        raw_json_str = json_match.group(1).strip()
        clean_content = text.replace(json_match.group(0), "").strip()
    elif unclosed_json_match:
        raw_json_str = unclosed_json_match.group(1).strip()
        clean_content = text.replace(unclosed_json_match.group(0), "").strip()

    if raw_json_str:
        # Try full parse or regex field extraction if JSON is cut off
        parsed = {}
        try:
            parsed = json.loads(raw_json_str)
        except Exception:
            # Fallback regex extraction for fields inside truncated JSON
            m_type = re.search(r'"infographic_type":\s*"([^"]+)"', raw_json_str)
            m_trk = re.search(r'"track_name":\s*"([^"]+)"', raw_json_str)
            m_ew = re.search(r'"expected_winner":\s*"([^"]+)"', raw_json_str)
            m_ewt = re.search(r'"expected_winner_team":\s*"([^"]+)"', raw_json_str)
            m_p1d = re.search(r'"p1_driver":\s*"([^"]+)"', raw_json_str)
            m_p1t = re.search(r'"p1_team":\s*"([^"]+)"', raw_json_str)
            m_p2d = re.search(r'"p2_driver":\s*"([^"]+)"', raw_json_str)
            m_p2t = re.search(r'"p2_team":\s*"([^"]+)"', raw_json_str)
            m_p3d = re.search(r'"p3_driver":\s*"([^"]+)"', raw_json_str)
            m_p3t = re.search(r'"p3_team":\s*"([^"]+)"', raw_json_str)
            m_qf = re.search(r'"qual_front":\s*"([^"]+)"', raw_json_str)
            m_qs = re.search(r'"qual_second":\s*"([^"]+)"', raw_json_str)
            m_qt = re.search(r'"qual_top10":\s*"([^"]+)"', raw_json_str)
            m_qm = re.search(r'"qual_midfield":\s*"([^"]+)"', raw_json_str)
            m_n1 = re.search(r'"h2h_name1":\s*"([^"]+)"', raw_json_str)
            m_n2 = re.search(r'"h2h_name2":\s*"([^"]+)"', raw_json_str)
            m_t1 = re.search(r'"h2h_team1":\s*"([^"]+)"', raw_json_str)
            m_t2 = re.search(r'"h2h_team2":\s*"([^"]+)"', raw_json_str)
            m_sec = re.search(r'"season_title":\s*"([^"]+)"', raw_json_str)

            parsed["infographic_type"] = m_type.group(1) if m_type else "race"
            parsed["track_name"] = m_trk.group(1) if m_trk else "Grand Prix Preview"
            parsed["expected_winner"] = m_ew.group(1) if m_ew else ""
            parsed["expected_winner_team"] = m_ewt.group(1) if m_ewt else ""
            parsed["p1_driver"] = m_p1d.group(1) if m_p1d else ""
            parsed["p1_team"] = m_p1t.group(1) if m_p1t else ""
            parsed["p2_driver"] = m_p2d.group(1) if m_p2d else ""
            parsed["p2_team"] = m_p2t.group(1) if m_p2t else ""
            parsed["p3_driver"] = m_p3d.group(1) if m_p3d else ""
            parsed["p3_team"] = m_p3t.group(1) if m_p3t else ""
            parsed["qual_front"] = m_qf.group(1) if m_qf else ""
            parsed["qual_second"] = m_qs.group(1) if m_qs else ""
            parsed["qual_top10"] = m_qt.group(1) if m_qt else ""
            parsed["qual_midfield"] = m_qm.group(1) if m_qm else ""
            parsed["h2h_name1"] = m_n1.group(1) if m_n1 else ""
            parsed["h2h_name2"] = m_n2.group(1) if m_n2 else ""
            parsed["h2h_team1"] = m_t1.group(1) if m_t1 else ""
            parsed["h2h_team2"] = m_t2.group(1) if m_t2 else ""
            parsed["season_title"] = m_sec.group(1) if m_sec else "Season 5 Teammate Qualifying Battles"

            # Extract individual rating row objects with regex
            extracted_rows = []
            row_pattern = re.compile(r'\{[^{}]*"rank":\s*"([^"]+)"[^{}]*"driver":\s*"([^"]+)"[^{}]*"team":\s*"([^"]+)"[^{}]*"rating":\s*"([^"]+)"[^{}]*\}')
            for rm in row_pattern.finditer(raw_json_str):
                rk, drv, tm, rt = rm.groups()
                extracted_rows.append({"rank": rk, "driver": drv, "team": tm, "rating": rt})
            parsed["top_ratings"] = extracted_rows

        inf_type = parsed.get("infographic_type", "race")

        # 1. Seasonal Qualifying Battles (SDDREQ-249)
        if inf_type == "seasonal_qual" or "seasonal_qual_rows" in parsed:
            seasonal_rows: list[TeammateQualRow] = []
            for r in parsed.get("seasonal_qual_rows", []):
                t_name = str(r.get("team", "")).strip()
                t_color = get_constructor_color(t_name)
                # Compute high-contrast text color
                is_bright = t_color.lower() in ("#ffea00", "yellow", "#e0e0e0", "white", "#fd4bc7")
                txt_color = "#000000" if is_bright else "#FFFFFF"

                s1_raw = r.get("score1", 0)
                s2_raw = r.get("score2", 0)
                try:
                    s1 = int(s1_raw)
                except Exception:
                    s1 = 0
                try:
                    s2 = int(s2_raw)
                except Exception:
                    s2 = 0
                total = s1 + s2
                pct1 = f"{int((s1 / total) * 100)}%" if total > 0 else "50%"
                pct2 = f"{int((s2 / total) * 100)}%" if total > 0 else "50%"
                s1_disp = "Ø" if s1 == 0 else str(s1)
                s2_disp = "Ø" if s2 == 0 else str(s2)

                seasonal_rows.append(TeammateQualRow(
                    team=t_name,
                    team_color=t_color,
                    text_color=txt_color,
                    driver1=str(r.get("driver1", "")).strip().upper(),
                    score1=str(s1),
                    score_display1=s1_disp,
                    driver2=str(r.get("driver2", "")).strip().upper(),
                    score2=str(s2),
                    score_display2=s2_disp,
                    pct1=pct1,
                    pct2=pct2,
                ))
            return {
                "is_infographic": True,
                "infographic_type": "seasonal_qual",
                "clean_content": clean_content,
                "season_title": parsed.get("season_title", "Season 5 Teammate Qualifying Battles"),
                "seasonal_qual_rows": seasonal_rows,
            }

        # 2. Head-to-Head Comparison (SDDREQ-247)
        if inf_type == "h2h" or "h2h_stats" in parsed:
            name1 = parsed.get("h2h_name1", "Driver 1")
            name2 = parsed.get("h2h_name2", "Driver 2")
            team1 = parsed.get("h2h_team1", "")
            team2 = parsed.get("h2h_team2", "")
            is_constructor = bool(parsed.get("h2h_is_constructor", False))

            if is_constructor:
                color1 = get_constructor_color(name1, default="#00b4da")
                color2 = get_constructor_color(name2, default="#ffffff")
            else:
                # Resolve driver 1 most recent constructor and color
                if not team1 or str(team1).strip().lower() in ("", "various", "unknown", "none"):
                    team1, color1 = get_driver_most_recent_constructor(name1)
                else:
                    color1 = get_constructor_color(team1, default="#00b4da")
                    if color1 == "#555555":
                        t_rec, c_rec = get_driver_most_recent_constructor(name1)
                        if c_rec != "#555555":
                            team1, color1 = t_rec, c_rec

                # Resolve driver 2 most recent constructor and color
                if not team2 or str(team2).strip().lower() in ("", "various", "unknown", "none"):
                    team2, color2 = get_driver_most_recent_constructor(name2)
                else:
                    color2 = get_constructor_color(team2, default="#ffffff")
                    if color2 == "#555555":
                        t_rec, c_rec = get_driver_most_recent_constructor(name2)
                        if c_rec != "#555555":
                            team2, color2 = t_rec, c_rec

            if color2.lower() in ("#000000", "#111111", "#18181b"):
                color2 = "#E0E0E0"

            txt1 = get_contrast_text_color(color1)
            txt2 = get_contrast_text_color(color2)

            # Compute deterministic league battle statistics
            h2h_battle = compute_h2h_battle_stats(name1, name2, is_constructor=is_constructor)

            raw_stats = parsed.get("h2h_stats", [])
            metric_map = {}
            for s in raw_stats:
                m_name = str(s.get("metric", "")).strip().upper()
                metric_map[m_name] = (str(s.get("val1", "")).strip(), str(s.get("val2", "")).strip())

            standard_metrics = ["QUALIFYING", "RACE RESULT", "PODIUMS", "POINTS", "WINS"]
            h2h_rows: list[ComparisonStatRow] = []

            has_deterministic = (
                h2h_battle.get("shared_active", False)
                or h2h_battle.get("pts1", "0") != "0"
                or h2h_battle.get("pts2", "0") != "0"
                or h2h_battle.get("qual1", 0) > 0
                or h2h_battle.get("qual2", 0) > 0
                or h2h_battle.get("race1", 0) > 0
                or h2h_battle.get("race2", 0) > 0
            )

            for m_key in standard_metrics:
                v1_str, v2_str = metric_map.get(m_key, ("", ""))
                display_metric = m_key.title()
                if m_key == "RACE RESULT":
                    display_metric = "Race Result"

                if has_deterministic:
                    if m_key == "QUALIFYING":
                        v1_str = str(h2h_battle["qual1"])
                        v2_str = str(h2h_battle["qual2"])
                    elif m_key == "RACE RESULT":
                        v1_str = str(h2h_battle["race1"])
                        v2_str = str(h2h_battle["race2"])
                    elif m_key == "PODIUMS":
                        v1_str = str(h2h_battle["pod1"])
                        v2_str = str(h2h_battle["pod2"])
                    elif m_key == "POINTS":
                        v1_str = str(h2h_battle["pts1"])
                        v2_str = str(h2h_battle["pts2"])
                    elif m_key == "WINS":
                        v1_str = str(h2h_battle["win1"])
                        v2_str = str(h2h_battle["win2"])
                else:
                    if m_key == "QUALIFYING":
                        if (v1_str in ("0", "") and v2_str in ("0", "")) and (h2h_battle["qual1"] > 0 or h2h_battle["qual2"] > 0):
                            v1_str = str(h2h_battle["qual1"])
                            v2_str = str(h2h_battle["qual2"])
                    elif m_key == "RACE RESULT":
                        if (v1_str in ("0", "") and v2_str in ("0", "")) and (h2h_battle["race1"] > 0 or h2h_battle["race2"] > 0):
                            v1_str = str(h2h_battle["race1"])
                            v2_str = str(h2h_battle["race2"])
                    elif m_key == "PODIUMS":
                        if (v1_str in ("0", "") and v2_str in ("0", "")) and (h2h_battle["pod1"] > 0 or h2h_battle["pod2"] > 0):
                            v1_str = str(h2h_battle["pod1"])
                            v2_str = str(h2h_battle["pod2"])
                    elif m_key == "POINTS":
                        if (v1_str in ("0", "0.0", "") and v2_str in ("0", "0.0", "")) and (h2h_battle["pts1"] != "0" or h2h_battle["pts2"] != "0"):
                            v1_str = str(h2h_battle["pts1"])
                            v2_str = str(h2h_battle["pts2"])
                    elif m_key == "WINS":
                        if (v1_str in ("0", "") and v2_str in ("0", "")) and (h2h_battle["win1"] > 0 or h2h_battle["win2"] > 0):
                            v1_str = str(h2h_battle["win1"])
                            v2_str = str(h2h_battle["win2"])

                if not v1_str:
                    v1_str = "0"
                if not v2_str:
                    v2_str = "0"

                # Calculate visual bar proportions
                try:
                    num1 = float(re.sub(r"[^\d\.]", "", v1_str) or 0)
                    num2 = float(re.sub(r"[^\d\.]", "", v2_str) or 0)
                    tot = num1 + num2
                    p1_int = int((num1 / tot) * 100) if tot > 0 else 50
                    p1_int = min(95, max(5, p1_int))
                    p2_int = 100 - p1_int
                    pct1 = f"{p1_int}%"
                    pct2 = f"{p2_int}%"
                except Exception:
                    pct1 = "50%"
                    pct2 = "50%"

                h2h_rows.append(ComparisonStatRow(
                    metric=display_metric,
                    val1=v1_str,
                    val2=v2_str,
                    pct1=pct1,
                    pct2=pct2,
                    color1=color1,
                    color2=color2,
                ))

            h2h_seasons_display = h2h_battle.get("seasons_label") if has_deterministic else parsed.get("h2h_seasons", "All Seasons")
            if not h2h_seasons_display:
                h2h_seasons_display = "All Seasons"

            return {
                "is_infographic": True,
                "infographic_type": "h2h",
                "clean_content": clean_content,
                "h2h_is_constructor": is_constructor,
                "h2h_name1": name1,
                "h2h_name2": name2,
                "h2h_team1": team1,
                "h2h_team2": team2,
                "h2h_color1": color1,
                "h2h_color2": color2,
                "h2h_text_color1": txt1,
                "h2h_text_color2": txt2,
                "h2h_seasons": h2h_seasons_display,
                "h2h_teammates1": parsed.get("h2h_teammates1", ""),
                "h2h_teammates2": parsed.get("h2h_teammates2", ""),
                "h2h_stats": h2h_rows,
            }

        # 3. Champion Comparison Skill (TAF1APP-SDDREQ-250) - Supporting N+ entities
        if inf_type == "champion_comparison" or "champ_stats" in parsed or "champ_entities" in parsed:
            # 1. Determine raw requested entities
            raw_input = parsed.get("champ_entities") or parsed.get("champions") or parsed.get("entities") or []
            raw_entities = []

            if isinstance(raw_input, list) and raw_input:
                for item in raw_input:
                    if isinstance(item, dict):
                        raw_entities.append(item)
                    elif isinstance(item, str) and item.strip():
                        item_str = item.strip()
                        m_season = re.search(r"season\s*(\d+)|s(\d+)", item_str, re.IGNORECASE)
                        s_num_str = (m_season.group(1) or m_season.group(2)) if m_season else "4"
                        name_str = re.sub(r"season\s*\d+|s\d+", "", item_str, flags=re.IGNORECASE).strip()
                        is_drv = any(d in name_str.lower() for d in ["nick", "joshua", "josh", "jairo", "brently", "connor", "foster", "austin"])
                        raw_entities.append({
                            "season": f"Season {s_num_str}",
                            "name": name_str or ("Joshua" if is_drv else "Mercedes"),
                            "type": "Driver" if is_drv else "Constructor",
                            "team": name_str,
                        })

            if not raw_entities:
                full_search_text = (clean_content + " " + raw_json_str).lower()
                is_all_const = (
                    "all constructor" in full_search_text
                    or "constructor champions from all" in full_search_text
                    or "all champions" in full_search_text
                    or "all completed constructor" in full_search_text
                    or "every constructor" in full_search_text
                )
                is_all_drivers = (
                    "all driver" in full_search_text
                    or "driver champions from all" in full_search_text
                    or "every driver" in full_search_text
                )

                if is_all_const:
                    raw_entities = [
                        {"season": "Season 4", "name": "Mercedes", "type": "Constructor", "team": "Mercedes"},
                        {"season": "Season 3", "name": "Alpine", "type": "Constructor", "team": "Alpine"},
                        {"season": "Season 2", "name": "McLaren", "type": "Constructor", "team": "McLaren"},
                        {"season": "Season 1", "name": "Mercedes", "type": "Constructor", "team": "Mercedes"},
                    ]
                    if "cadillac" in full_search_text or "season 5" in full_search_text:
                        raw_entities.append({"season": "Season 5", "name": "Cadillac", "type": "Constructor", "team": "Cadillac"})
                elif is_all_drivers:
                    raw_entities = [
                        {"season": "Season 4", "name": "Joshua", "type": "Driver", "team": "Alpine"},
                        {"season": "Season 3", "name": "Nick", "type": "Driver", "team": "McLaren"},
                        {"season": "Season 2", "name": "Nick", "type": "Driver", "team": "McLaren"},
                        {"season": "Season 1", "name": "Nick", "type": "Driver", "team": "Mercedes"},
                    ]
                    if "josh" in full_search_text or "season 5" in full_search_text:
                        raw_entities.append({"season": "Season 5", "name": "Josh", "type": "Driver", "team": "Cadillac"})
                else:
                    # Binary comparison fallback
                    s1_str = str(parsed.get("champ_season1", "Season 4"))
                    s2_str = str(parsed.get("champ_season2", "Season 3"))
                    name1 = parsed.get("champ_name1", "Mercedes")
                    name2 = parsed.get("champ_name2", "Alpine")
                    type1 = parsed.get("champ_type1", "Constructor")
                    type2 = parsed.get("champ_type2", "Constructor")
                    raw_entities = [
                        {"season": s1_str, "name": name1, "type": type1},
                        {"season": s2_str, "name": name2, "type": type2},
                    ]

            # 2. Compute deterministic campaign records for all N entities
            built_entities: list[ChampionEntity] = []
            entity_campaign_stats = []

            for ent in raw_entities:
                s_val = str(ent.get("season", "Season 4"))
                m_s = re.search(r"\d+", s_val)
                s_num = int(m_s.group(0)) if m_s else 4
                e_name = str(ent.get("name", "")).strip()
                e_type = str(ent.get("type", "Constructor")).strip()
                is_const = e_type.lower() != "driver"

                c_stat = compute_champion_campaign_stats(s_num, e_name, is_constructor=is_const)
                champ_name = c_stat.get("name", e_name)
                c_color = c_stat.get("color", "#00b4da")
                if c_color.lower() in ("#000000", "#111111", "#18181b"):
                    c_color = "#E0E0E0"
                c_txt = get_contrast_text_color(c_color)

                built_entities.append(ChampionEntity(
                    name=champ_name,
                    season=f"Season {s_num}",
                    type="Constructor" if is_const else "Driver",
                    team=c_stat.get("team", ""),
                    color=c_color,
                    text_color=c_txt,
                    runner_up=c_stat.get("runner_up", ""),
                ))
                entity_campaign_stats.append((c_stat, champ_name, f"Season {s_num}", c_color, c_txt))

            # 3. Calculate 5 metric comparison rows with N segments
            num_ents = len(entity_campaign_stats)
            metric_configs = [
                ("Wins", "wins"),
                ("Podiums", "podiums"),
                ("Accolades", "accolades"),
                ("Win Margin", "margin"),
                ("Races Led Championship", "races_led"),
            ]

            built_stats: list[ChampionMetricRow] = []

            for m_name, m_key in metric_configs:
                num_vals: list[float] = []
                str_vals: list[str] = []
                sub_texts: list[str] = []

                for c_stat, e_name, s_label, c_color, c_txt in entity_campaign_stats:
                    if m_key == "wins":
                        w = c_stat.get("wins", 0)
                        num_vals.append(float(w))
                        str_vals.append(str(w))
                        sub_texts.append("")
                    elif m_key == "podiums":
                        p = c_stat.get("podiums", 0)
                        num_vals.append(float(p))
                        str_vals.append(str(p))
                        sub_texts.append("")
                    elif m_key == "accolades":
                        tot_acc = c_stat.get("total_accolades", 0)
                        num_vals.append(float(tot_acc))
                        str_vals.append(str(tot_acc))
                        acc_sub = []
                        if c_stat.get("poles"): acc_sub.append(f"{c_stat['poles']} Poles")
                        if c_stat.get("fl"): acc_sub.append(f"{c_stat['fl']} FL")
                        if c_stat.get("cd"): acc_sub.append(f"{c_stat['cd']} CD")
                        if c_stat.get("dotd"): acc_sub.append(f"{c_stat['dotd']} DOTD")
                        if c_stat.get("mot"): acc_sub.append(f"{c_stat['mot']} MOT")
                        sub_texts.append(", ".join(acc_sub) if acc_sub else "No accolades")
                    elif m_key == "margin":
                        m = max(0.0, float(c_stat.get("margin", 0.0)))
                        num_vals.append(m)
                        str_vals.append(f"{m:.1f} pts")
                        ru = c_stat.get("runner_up", "")
                        sub_texts.append(f"Runner-up: {ru}" if ru else "")
                    elif m_key == "races_led":
                        r_led = c_stat.get("races_led", 0)
                        tot_r = max(1, c_stat.get("total_races", 1))
                        num_vals.append(float(r_led))
                        str_vals.append(f"{r_led} of {tot_r} races")
                        pct_l = int((r_led / tot_r) * 100)
                        sub_texts.append(f"{pct_l}% of season")

                # Compute relative percentages summing to 100%
                tot_val = sum(num_vals)
                pct_ints: list[int] = []
                if tot_val > 0:
                    raw_pcts = [(v / tot_val) * 100 for v in num_vals]
                    pct_ints = [int(round(p)) for p in raw_pcts]
                    min_allowed = 4 if num_ents > 3 else 6
                    pct_ints = [
                        max(min_allowed, p) if (num_vals[i] > 0 and p < min_allowed) else p
                        for i, p in enumerate(pct_ints)
                    ]
                    diff = 100 - sum(pct_ints)
                    if diff != 0 and pct_ints:
                        max_idx = num_vals.index(max(num_vals))
                        pct_ints[max_idx] = max(1, pct_ints[max_idx] + diff)
                else:
                    eq_share = 100 // max(1, num_ents)
                    pct_ints = [eq_share] * num_ents
                    if pct_ints:
                        pct_ints[0] += (100 - sum(pct_ints))

                row_segments: list[ChampionMetricSegment] = []
                for i, (c_stat, e_name, s_label, c_color, c_txt) in enumerate(entity_campaign_stats):
                    row_segments.append(ChampionMetricSegment(
                        entity_name=e_name,
                        season=s_label,
                        val=str_vals[i],
                        numeric_val=num_vals[i],
                        pct=f"{pct_ints[i]}%",
                        color=c_color,
                        text_color=c_txt,
                        sub_text=sub_texts[i],
                    ))

                v1_out = str_vals[0] if num_ents > 0 else ""
                v2_out = str_vals[1] if num_ents > 1 else ""
                st1_out = sub_texts[0] if num_ents > 0 else ""
                st2_out = sub_texts[1] if num_ents > 1 else ""
                p1_out = f"{pct_ints[0]}%" if num_ents > 0 else "50%"
                p2_out = f"{pct_ints[1]}%" if num_ents > 1 else "50%"
                c1_out = entity_campaign_stats[0][3] if num_ents > 0 else "#00b4da"
                c2_out = entity_campaign_stats[1][3] if num_ents > 1 else "#ffffff"
                txt1_out = entity_campaign_stats[0][4] if num_ents > 0 else "#ffffff"
                txt2_out = entity_campaign_stats[1][4] if num_ents > 1 else "#000000"

                built_stats.append(ChampionMetricRow(
                    metric=m_name,
                    val1=v1_out,
                    val2=v2_out,
                    sub_text1=st1_out,
                    sub_text2=st2_out,
                    pct1=p1_out,
                    pct2=p2_out,
                    color1=c1_out,
                    color2=c2_out,
                    text_color1=txt1_out,
                    text_color2=txt2_out,
                    segments=row_segments,
                ))

            e1 = built_entities[0] if built_entities else ChampionEntity()
            e2 = built_entities[1] if len(built_entities) > 1 else ChampionEntity()

            return {
                "is_infographic": True,
                "infographic_type": "champion_comparison",
                "clean_content": clean_content,
                "champ_season1": e1.season,
                "champ_season2": e2.season,
                "champ_name1": e1.name,
                "champ_name2": e2.name,
                "champ_type1": e1.type,
                "champ_type2": e2.type,
                "champ_team1": e1.team,
                "champ_team2": e2.team,
                "champ_color1": e1.color,
                "champ_color2": e2.color,
                "champ_text_color1": e1.text_color,
                "champ_text_color2": e2.text_color,
                "champ_runner_up1": e1.runner_up,
                "champ_runner_up2": e2.runner_up,
                "champ_entities": built_entities,
                "champ_stats": built_stats,
            }


        # 4. Upcoming Race Infographic
        top_ratings: list[RatingRow] = []
        for r in parsed.get("top_ratings", [])[:8]:
            team = str(r.get("team", "")).strip()
            try:
                rating_val = float(r.get("rating", 0.0))
            except Exception:

                rating_val = 0.0
            pct = min(100, max(0, int(rating_val)))
            raw_rank = str(r.get("rank", "")).strip()
            rank_str = raw_rank if raw_rank.startswith("P") else f"P{raw_rank}"
            row_c = get_constructor_color(team)
            top_ratings.append(RatingRow(
                rank=rank_str,
                driver=str(r.get("driver", "")).strip(),
                team=team,
                rating=f"{rating_val:.1f}",
                pct=f"{pct}%",
                color=row_c,
                text_color=get_contrast_text_color(row_c),
            ))

        win_team = parsed.get("expected_winner_team", "")
        p1_team = parsed.get("p1_team", "")
        p2_team = parsed.get("p2_team", "")
        p3_team = parsed.get("p3_team", "")
        win_c = get_constructor_color(win_team)
        p1_c = get_constructor_color(p1_team)
        p2_c = get_constructor_color(p2_team)
        p3_c = get_constructor_color(p3_team)

        return {
            "is_infographic": True,
            "infographic_type": "race",
            "clean_content": clean_content,
            "track_name": parsed.get("track_name", "Grand Prix Preview"),
            "expected_winner": parsed.get("expected_winner", ""),
            "expected_winner_team": win_team,
            "winner_color": win_c,
            "winner_text_color": get_contrast_text_color(win_c),
            "p1_driver": parsed.get("p1_driver", ""),
            "p1_team": p1_team,
            "p1_color": p1_c,
            "p1_text_color": get_contrast_text_color(p1_c),
            "p2_driver": parsed.get("p2_driver", ""),
            "p2_team": p2_team,
            "p2_color": p2_c,
            "p2_text_color": get_contrast_text_color(p2_c),
            "p3_driver": parsed.get("p3_driver", ""),
            "p3_team": p3_team,
            "p3_color": p3_c,
            "p3_text_color": get_contrast_text_color(p3_c),
            "top_ratings": top_ratings,
            "qual_front": parsed.get("qual_front", ""),
            "qual_second": parsed.get("qual_second", ""),
            "qual_top10": parsed.get("qual_top10", ""),
            "qual_midfield": parsed.get("qual_midfield", ""),
        }

    # 2. Fallback: Parse from Markdown standard output
    if "Infographic" not in text and "Track Rating" not in text:
        return {"is_infographic": False}

    res = {"is_infographic": True, "clean_content": text}

    # Track title
    m_track = re.search(r"🏁\s*([^\n:]+)", text)
    if not m_track:
        m_track = re.search(r"([A-Za-z\-]+(?:\s+[A-Za-z\-]+)*\s+Grand Prix)", text)
    res["track_name"] = m_track.group(1).strip() if m_track else "Grand Prix Preview"

    # Winner
    m_win = re.search(r"Expected Winner:\s*(?:\*\*)?([A-Za-z0-9\.\s]+?)(?:\*\*)?\s*(?:\(([^)]+)\))?", text)
    if m_win:
        res["expected_winner"] = m_win.group(1).strip()
        res["expected_winner_team"] = m_win.group(2).strip() if m_win.group(2) else ""
        res["winner_color"] = get_constructor_color(res["expected_winner_team"])
    else:
        res["expected_winner"] = ""
        res["expected_winner_team"] = ""
        res["winner_color"] = "#555555"

    # Podium
    m_p1 = re.search(r"🥇\s*(?:\*\*)?([A-Za-z0-9\.\s]+?)(?:\*\*)?\s*(?:\(([^)]+)\))?", text)
    m_p2 = re.search(r"🥈\s*(?:\*\*)?([A-Za-z0-9\.\s]+?)(?:\*\*)?\s*(?:\(([^)]+)\))?", text)
    m_p3 = re.search(r"🥉\s*(?:\*\*)?([A-Za-z0-9\.\s]+?)(?:\*\*)?\s*(?:\(([^)]+)\))?", text)

    res["p1_driver"] = m_p1.group(1).strip() if m_p1 else ""
    res["p1_team"] = m_p1.group(2).strip() if m_p1 and m_p1.group(2) else ""
    res["p1_color"] = get_constructor_color(res["p1_team"])

    res["p2_driver"] = m_p2.group(1).strip() if m_p2 else ""
    res["p2_team"] = m_p2.group(2).strip() if m_p2 and m_p2.group(2) else ""
    res["p2_color"] = get_constructor_color(res["p2_team"])

    res["p3_driver"] = m_p3.group(1).strip() if m_p3 else ""
    res["p3_team"] = m_p3.group(2).strip() if m_p3 and m_p3.group(2) else ""
    res["p3_color"] = get_constructor_color(res["p3_team"])

    # Ratings Leaderboard Rows
    top_ratings_fallback: list[RatingRow] = []
    rating_pattern = re.compile(r"(?:^|\n)\|?\s*(\d{1,2})\s*\|?[\t\s]+([A-Za-z0-9\.\s]+?)\s*\|?[\t\s]+([A-Za-z0-9\s]+?)\s*\|?[\t\s]+(\d+\.?\d*)")
    for m in rating_pattern.finditer(text):
        rk, d, t, r = m.groups()
        try:
            r_val = float(r)
            pct = min(100, max(0, int(r_val)))
            team_str = t.strip()
            top_ratings_fallback.append(RatingRow(
                rank=f"P{rk}",
                driver=d.strip(),
                team=team_str,
                rating=f"{r_val:.1f}",
                pct=f"{pct}%",
                color=get_constructor_color(team_str),
            ))
        except Exception:
            continue
    res["top_ratings"] = top_ratings_fallback[:8]

    # Qualifying
    m_q1 = re.search(r"Front-Row Contenders.*?:?\s*([^\n]+)", text)
    m_q2 = re.search(r"Second-Row Contenders.*?:?\s*([^\n]+)", text)
    m_q3 = re.search(r"Top-10 Qualifiers.*?:?\s*([^\n]+)", text)
    m_q4 = re.search(r"Midfield.*?Rookies.*?:?\s*([^\n]+)", text)

    res["qual_front"] = m_q1.group(1).strip() if m_q1 else ""
    res["qual_second"] = m_q2.group(1).strip() if m_q2 else ""
    res["qual_top10"] = m_q3.group(1).strip() if m_q3 else ""
    res["qual_midfield"] = m_q4.group(1).strip() if m_q4 else ""

    return res


class AlternativeIntelligenceState(rx.State):
    """Reflex state managing the Alternative Intelligence sidebar drawer and query engine."""

    show_drawer: bool = False
    search_query: str = ""
    is_generating: bool = False
    error_message: str = ""
    messages: list[ChatMessage] = []
    selected_skill: str = "Skills Library"
    active_skill_badge: str = ""
    active_skill_infotip: str = ""
    discord_username: str = rx.LocalStorage("", name="discord_username", sync=True)
    discord_avatar: str = rx.LocalStorage("", name="discord_avatar", sync=True)

    @rx.var
    def active_skill_badge_short(self) -> str:
        """Truncated badge showing '@' and the first word on narrow screens (e.g. '@Specific')."""
        if not self.active_skill_badge:
            return ""
        parts = self.active_skill_badge.strip().split()
        return parts[0] if parts else ""

    def toggle_drawer(self):
        """Toggle the sidebar drawer open or closed."""
        self.show_drawer = not self.show_drawer
        if self.show_drawer and not self.messages:
            self.error_message = ""

    def open_drawer(self):
        """Explicitly open the drawer."""
        self.show_drawer = True

    def close_drawer(self):
        """Explicitly close the drawer."""
        self.show_drawer = False

    def set_search_query(self, query: str):
        """Update the input search bar value."""
        self.search_query = query

    def clear_chat(self):
        """Clear conversation history."""
        self.messages = []
        self.error_message = ""

    def handle_key_down(self, key: str):
        """Submit query on Enter without Shift."""
        if key == "Enter":
            return AlternativeIntelligenceState.submit_query

    def download_infographic_png(self, card_id: str, track_name: str):
        """Capture the visual infographic card in the browser and trigger a high-res .PNG file download."""
        safe_name = re.sub(r"[^A-Za-z0-9_\-]+", "_", track_name.strip()) if track_name else "Race_Infographic"
        filename = f"{safe_name}_Infographic.png"
        js_code = f"""
        (async () => {{
            const loadHtml2Canvas = () => new Promise((resolve, reject) => {{
                if (window.html2canvas) return resolve(window.html2canvas);
                const script = document.createElement('script');
                script.src = 'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js';
                script.onload = () => resolve(window.html2canvas);
                script.onerror = reject;
                document.head.appendChild(script);
            }});

            try {{
                const h2c = await loadHtml2Canvas();
                const card = document.getElementById('{card_id}');
                if (!card) {{
                    console.error('Infographic card element with ID {card_id} not found.');
                    return;
                }}

                const canvas = await h2c(card, {{
                    scale: 2,
                    useCORS: true,
                    backgroundColor: '#18181B',
                    logging: false,
                    ignoreElements: (el) => el.getAttribute('data-html2canvas-ignore') === 'true',
                }});

                const link = document.createElement('a');
                link.download = '{filename}';
                link.href = canvas.toDataURL('image/png');
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }} catch (err) {{
                console.error('Error generating infographic PNG:', err);
            }}
        }})();
        """
        return rx.call_script(js_code)

    def select_skill(self, skill_name: str):
        """Populate @<Skill Name> badge box into search bar without executing immediately."""
        if not skill_name or skill_name == "Skills Library":
            return
        if "Upcoming Race" in skill_name:
            self.active_skill_badge = "@Specific Upcoming Race Infographic "
            self.active_skill_infotip = "e.g., Monza, Spa, Brazil, or leave blank for next GP"
        elif "Qualifying" in skill_name:
            self.active_skill_badge = "@Seasonal Qualifying Comparison "
            self.active_skill_infotip = "e.g., Season 5, Season 4, or leave blank"
        elif "Head to Head" in skill_name or "H2H" in skill_name:
            self.active_skill_badge = "@Head to Head Comparison Infographic "
            self.active_skill_infotip = "e.g., Josh vs Jairo, or Ferrari vs Red Bull"
        elif "Champion" in skill_name:
            self.active_skill_badge = "@Champion Comparison Skill "
            self.active_skill_infotip = "e.g., S4 Mercedes vs S3 Alpine, or Joshua S4 vs Nick S3 (defaults to most recent constructor champion vs prior year)"
        else:
            self.active_skill_badge = f"@{skill_name} "
            self.active_skill_infotip = f"Expected inputs for {skill_name}"
        self.selected_skill = "Skills Library"

    def clear_active_skill(self):
        """Clear the active skill badge box and infotip."""
        self.active_skill_badge = ""
        self.active_skill_infotip = ""

    async def select_prompt(self, prompt_text: str) -> AsyncGenerator:
        """Select a suggested quick prompt and execute it immediately."""
        self.search_query = prompt_text
        async for step in self.submit_query():
            yield step

    async def submit_query(self) -> AsyncGenerator:
        """Execute the query against Gemini with Grounded League Context streaming."""
        from datetime import datetime, timezone

        user_input = self.search_query.strip()
        is_skill_request = bool(
            self.active_skill_badge
            or user_input.startswith("@")
            or "@Specific Upcoming Race Infographic" in user_input
            or "@Upcoming Race Infographic" in user_input
            or "@Seasonal Qualifying Comparison" in user_input
            or "@Head to Head Comparison Infographic" in user_input
            or "@Champion Comparison Skill" in user_input
        )


        badge_name = ""
        if self.active_skill_badge:
            badge_name = self.active_skill_badge.strip().lstrip("@")
            if not user_input.startswith("@"):
                query = f"{self.active_skill_badge}{user_input}".strip()
            else:
                query = user_input
        else:
            query = user_input
            if query.startswith("@"):
                for s_opt in SKILL_OPTIONS[1:]:
                    if query.startswith(f"@{s_opt}"):
                        badge_name = s_opt
                        break
                if not badge_name:
                    m_skill = re.match(r"^@([A-Za-z0-9\s]+?)(?:\s+(.*))?$", query)
                    if m_skill:
                        badge_name = m_skill.group(1).strip()

        if not query or self.is_generating:
            return

        now_iso = datetime.now(timezone.utc).isoformat()

        # Clean display content if a skill badge was extracted
        display_content = user_input
        if badge_name:
            if display_content.startswith(f"@{badge_name}"):
                display_content = display_content[len(f"@{badge_name}"):].strip()
            if not display_content:
                display_content = badge_name
        else:
            display_content = query

        # Append user query to conversation with ISO timestamp and persistent skill badge
        self.messages.append(ChatMessage(
            role="user",
            content=display_content,
            timestamp=now_iso,
            skill_badge=badge_name,
            user_avatar=self.discord_avatar,
        ))
        self.search_query = ""
        self.active_skill_badge = ""
        self.active_skill_infotip = ""
        self.error_message = ""

        # Prepare placeholder assistant response
        self.messages.append(ChatMessage(
            role="assistant",
            content="",
            timestamp=now_iso,
        ))
        self.is_generating = True
        yield
        try:
            yield rx.call_script("""
                setTimeout(() => {
                    const userPrompts = document.querySelectorAll('.ai-user-message-card');
                    const latestPrompt = userPrompts[userPrompts.length - 1];
                    if (latestPrompt) {
                        latestPrompt.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    } else {
                        const feed = document.getElementById('ai-chat-feed');
                        if (feed) feed.scrollTop = feed.scrollHeight;
                    }
                }, 60);
            """)
        except Exception:
            pass

        # Custom canonical lore response for Mets fan
        mets_fan_match = re.search(
            r"(?:\bmets\s+fans?\b|who(?:'s|\s+is)?(?:\s+(?:a|the))?\s+mets\s+fan\b|who\s+(?:likes|supports|roots\s+for)\s+(?:the\s+)?mets\b)",
            query,
            re.IGNORECASE,
        )
        if mets_fan_match:
            self.messages[-1].content = (
                "Joshua, Season 4 World Driver Champion is the biggest Mets fan in the world and he hates the Yankees."
            )
            self.is_generating = False
            yield
            return

        # Custom Easter egg response for Captain Slow (Brently Season 3 Monaco winner)
        captain_slow_match = re.search(r"\bcaptain\s*slow\b", query, re.IGNORECASE)
        if captain_slow_match:
            self.messages[-1].content = (
                "Captain Slow is the undisputed Season 3 Monaco winner Brently! "
                "![Jeff Gordon NASCAR](/Icons/jeff_gordon_nascar.png)"
            )
            self.is_generating = False
            yield
            return

        # Custom Easter egg response for poopy person / poopy head
        poopy_match = re.search(r"\b(poopy(?:\s+(?:person|head|[a-zA-Z0-9_-]+))?)\b", query, re.IGNORECASE)
        if poopy_match:
            raw_matched = poopy_match.group(1).strip()
            poopy_comment = "poopy person" if raw_matched.lower() == "poopy" else raw_matched
            matthew_wins = 0
            try:
                from the_alternative_f1.all_time_stats.Functions import CalculateAllTime
                all_time_df = CalculateAllTime(5, "Driver")
                if all_time_df is not None and not all_time_df.empty:
                    m_row = all_time_df[all_time_df["Driver"].str.strip().str.lower() == "matthew"]
                    if not m_row.empty:
                        matthew_wins = int(m_row.iloc[0].get("1st Place", 0))
            except Exception:
                matthew_wins = 0

            self.messages[-1].content = f"Matthew is a {poopy_comment} and has {matthew_wins} wins."
            self.is_generating = False
            yield
            return

        # Custom canonical lore response for Miami Lover / who loves Miami
        miami_lover_match = re.search(
            r"(?:who\s+(?:loves|likes)\s+miami|\bmiami\s+lover\b|who(?:'s|\s+is)?(?:\s+the)?\s+miami\s+lover)",
            query,
            re.IGNORECASE,
        )
        if miami_lover_match:
            self.messages[-1].content = (
                "Nick's all time favorite track is Miami. Erick is known as the Miami Lover, but really that nickname should be held by Nick (no pun intended)."
            )
            self.is_generating = False
            yield
            return

        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            self.is_generating = False
            self.messages[-1].content = (
                "⚠️ **Gemini API Key Required**\n\n"
                "Please configure `GEMINI_API_KEY` in your `.env` or Reflex Cloud secrets to enable live responses."
            )
            yield
            return

        # Prepare Grounded League Context
        try:
            grounded_context = build_grounded_league_context()
        except Exception as e:
            grounded_context = f"Error extracting context: {str(e)}"

        skill_directive = ""
        if not is_skill_request:
            skill_directive = (
                "\n\n[USER DIRECTIVE: No specialized skill is selected. Respond conversationally using standard Markdown only. "
                "Do NOT output any ```infographic-json block, do NOT use specialized infographic structures, and do NOT construct preview cards.]"
            )

        # Search relevant articles for high-priority retrieval matching user query
        retrieved_articles_section = ""
        try:
            matched_articles = search_league_articles(query, top_k=3)
            if matched_articles:
                art_blocks = []
                for art in matched_articles:
                    art_blocks.append(
                        f"### Matched Article: \"{art['title']}\" ({art['season']}, Published: {art['date']} by {art['author']})\n"
                        f"Blurb: {art['blurb']}\n"
                        f"Full Article Text:\n{art['content']}"
                    )
                retrieved_articles_section = (
                    "\n\nPRIMARY RELEVANT ARTICLES RETRIEVED FOR THIS INQUIRY:\n"
                    + "\n\n".join(art_blocks)
                    + "\n"
                )
        except Exception:
            pass

        # Check if query requests Head-to-Head comparison to pre-ground exact shared seasons battle stats
        h2h_grounding_section = ""
        try:
            is_h2h = (
                is_skill_request and ("head to head" in badge_name.lower() or "h2h" in badge_name.lower())
            ) or any(k in query.lower() for k in ["head-to-head", "head to head", "h2h", " vs ", " versus ", "compare "])

            if is_h2h:
                known_entities = sorted([
                    "Aston Martin", "Alfa Romeo", "AlphaTauri", "Red Bull", "Cadillac", "Mercedes", "McLaren", "Ferrari", "Williams", "Alpine", "Audi", "Haas", "VCARB",
                    "Josh C.", "Josh L", "Grayson", "Matthew", "Brently", "Patrick", "Joshua", "Eddie", "Erick", "David", "Travis", "Marcus", "Jaden", "Jairo", "Randy", "Evelo", "Gary", "Nick", "Zane", "Josh", "Boz", "Del", "Leo"
                ], key=len, reverse=True)
                ent_matches = []
                for ent in known_entities:
                    pattern = r"\b" + re.escape(ent) + (r"\b" if not ent.endswith(".") else r"")
                    for m in re.finditer(pattern, query, re.IGNORECASE):
                        if not any(not (m.end() <= s or m.start() >= e) for s, e, _ in ent_matches):
                            ent_matches.append((m.start(), m.end(), ent))
                ent_matches.sort(key=lambda x: x[0])
                found_ents = [x[2] for x in ent_matches]

                if len(found_ents) >= 2:
                    ent1, ent2 = found_ents[0], found_ents[1]
                    const_names = ["Cadillac", "Ferrari", "Mercedes", "McLaren", "Red Bull", "Haas", "Audi", "Williams", "Alpine", "Aston Martin", "VCARB", "Alfa Romeo", "AlphaTauri"]
                    is_const = ent1 in const_names and ent2 in const_names
                    h2h_stats_res = compute_h2h_battle_stats(ent1, ent2, is_constructor=is_const)
                    if h2h_stats_res.get("shared_active") or h2h_stats_res.get("pts1") != "0" or h2h_stats_res.get("pts2") != "0":
                        h2h_grounding_section = (
                            f"\n\nOFFICIAL DETERMINISTIC HEAD-TO-HEAD BATTLE RECORDS (GROUNDED ACROSS {h2h_stats_res.get('seasons_label', 'SHARED SEASONS')}):\n"
                            f"Entity 1: {ent1}\n"
                            f"Entity 2: {ent2}\n"
                            f"Timeline: {h2h_stats_res.get('seasons_label', 'Shared Seasons')}\n"
                            f"Direct Out-Qualification Score: {ent1} {h2h_stats_res['qual1']} - {h2h_stats_res['qual2']} {ent2}\n"
                            f"Direct Race Finishes Ahead: {ent1} {h2h_stats_res['race1']} - {h2h_stats_res['race2']} {ent2}\n"
                            f"Podiums in Shared Seasons: {ent1} {h2h_stats_res['pod1']} - {h2h_stats_res['pod2']} {ent2}\n"
                            f"Wins in Shared Seasons: {ent1} {h2h_stats_res['win1']} - {h2h_stats_res['win2']} {ent2}\n"
                            f"Points in Shared Seasons (Official Standings Scale): {ent1} {h2h_stats_res['pts1']} pts - {h2h_stats_res['pts2']} pts {ent2}\n"
                            f"CRITICAL DIRECTIVE: You MUST use these exact verified numbers in your ```infographic-json and in your analytical write-up. Do not hallucinate or compute divergent totals.\n"
                        )
        except Exception:
            pass

        prompt_payload = (
            f"LEAGUE GROUNDED CONTEXT:\n{grounded_context}\n"
            f"{retrieved_articles_section}\n"
            f"{h2h_grounding_section}\n"
            f"USER INQUIRY:\n{query}{skill_directive}"
        )

        # Call Google Gemini API (gemini-3.5-flash with gemini-3.5-flash-lite fallback)
        model_name = "gemini-3.5-flash"
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:streamGenerateContent?alt=sse&key={api_key}"

        body = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt_payload}]
                }
            ],
            "systemInstruction": {
                "parts": [{"text": SYSTEM_PROMPT}]
            },
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 8192,
            }
        }

        accumulated_text = ""
        global _WORKING_GEMINI_MODEL
        try:
            http_timeout = httpx.Timeout(120.0, connect=10.0, read=120.0, write=15.0, pool=10.0)
            async with httpx.AsyncClient(timeout=http_timeout) as client:
                # 1. Discover available models for this specific API key or use verified working models
                candidate_models = [
                    "gemini-3.5-flash-lite",
                    "gemini-3.8-flash",
                    "gemini-3.6-flash",
                    "gemini-3.1-flash-lite",
                    "gemini-flash-lite-latest",
                    "gemini-3-flash-preview",
                    "gemini-3.5-flash",
                ]
                if _WORKING_GEMINI_MODEL and _WORKING_GEMINI_MODEL in candidate_models:
                    candidate_models = [_WORKING_GEMINI_MODEL] + [m for m in candidate_models if m != _WORKING_GEMINI_MODEL]
                elif not _WORKING_GEMINI_MODEL:
                    try:
                        models_resp = await client.get(
                            f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}",
                            timeout=4.0,
                        )
                        if models_resp.status_code == 200:
                            discovered = [
                                m["name"].replace("models/", "")
                                for m in models_resp.json().get("models", [])
                                if "generateContent" in m.get("supportedGenerationMethods", [])
                                and not any(dep in m["name"] for dep in ["1.5", "2.0", "2.5"])
                            ]
                            if discovered:
                                flash_first = sorted(
                                    discovered,
                                    key=lambda x: (
                                        0 if "3.5-flash-lite" in x else
                                        1 if "3.8-flash" in x else
                                        2 if "3.6-flash" in x else
                                        3 if "flash-lite" in x else
                                        4 if "flash" in x.lower() else 5
                                    )
                                )
                                candidate_models = flash_first + [m for m in candidate_models if m not in flash_first]
                    except Exception:
                        pass

                # 2. Iterate through candidate models with per-candidate exception and timeout protection
                active_stream = None
                last_err = ""
                for model_candidate in candidate_models:
                    try:
                        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model_candidate}:streamGenerateContent?alt=sse&key={api_key}"
                        req = client.build_request("POST", endpoint, json=body)
                        resp = await client.send(req, stream=True)
                        if resp.status_code == 200:
                            active_stream = resp
                            _WORKING_GEMINI_MODEL = model_candidate
                            break
                        else:
                            err_bytes = await resp.aread()
                            last_err = f"{model_candidate} ({resp.status_code}): {err_bytes.decode('utf-8', errors='ignore')[:120]}"
                            await resp.aclose()
                    except (httpx.TimeoutException, httpx.HTTPError, Exception) as cand_exc:
                        last_err = f"{model_candidate}: {str(cand_exc)}"
                        continue

                if not active_stream:
                    self.error_message = f"Could not connect to Gemini model: {last_err}"
                    self.messages[-1].content = (
                        "Sorry, I encountered an issue connecting to the Gemini model with this API key. "
                        "Please verify your key in Google AI Studio."
                    )
                    self.is_generating = False
                    yield
                    return

                accumulated_text = ""
                accumulated_thought = ""
                async for line in active_stream.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk_json = json.loads(data_str)
                            candidates = chunk_json.get("candidates", [])
                            if candidates:
                                parts = candidates[0].get("content", {}).get("parts", [])
                                for part in parts:
                                    is_thought = part.get("thought", False)
                                    text_delta = part.get("text", "")
                                    if is_thought:
                                        accumulated_thought += text_delta
                                    else:
                                        accumulated_text += text_delta

                                    cur_thinking, cur_content = parse_thinking_and_content(accumulated_text, accumulated_thought)

                                    # Sanitize displayed text so raw JSON block is never visible during streaming, and "weekend" never appears
                                    display_text = cur_content
                                    if "```infographic-json" in display_text or "```json" in display_text:
                                        # If block is completed, strip it
                                        display_text = re.sub(r"```(?:infographic-json|json)\s*\{.*?\}\s*```", "", display_text, flags=re.DOTALL).strip()
                                        # If block is still unclosed, hide everything from start of block
                                        display_text = re.sub(r"```(?:infographic-json|json).*$", "", display_text, flags=re.DOTALL).strip()
                                    display_text = sanitize_race_week_terminology(display_text)

                                    self.messages[-1].thinking_content = cur_thinking
                                    self.messages[-1].content = display_text
                                    yield
                        except Exception:
                            continue
                await active_stream.aclose()

                # Separate thinking from final content upon completion
                final_thinking, final_content = parse_thinking_and_content(accumulated_text, accumulated_thought)
                final_content = sanitize_race_week_terminology(final_content)

                # Check if an infographic was generated and extract structured visual fields
                info_data = extract_infographic_data(final_content, skill_selected=is_skill_request)
                if info_data and info_data.get("is_infographic"):
                    clean_text = sanitize_race_week_terminology(info_data.get("clean_content", final_content))
                    unique_card_id = f"infographic-card-{int(time.time() * 1000)}"
                    self.messages[-1] = ChatMessage(
                        role="assistant",
                        content=clean_text,
                        thinking_content=final_thinking,
                        timestamp=now_iso,
                        is_infographic=True,
                        card_id=unique_card_id,
                        infographic_type=info_data.get("infographic_type", "race"),
                        track_name=info_data.get("track_name", "Grand Prix Preview"),
                        expected_winner=info_data.get("expected_winner", ""),
                        expected_winner_team=info_data.get("expected_winner_team", ""),
                        winner_color=info_data.get("winner_color", "#555555"),
                        winner_text_color=info_data.get("winner_text_color", "#FFFFFF"),
                        p1_driver=info_data.get("p1_driver", ""),
                        p1_team=info_data.get("p1_team", ""),
                        p1_color=info_data.get("p1_color", "#555555"),
                        p1_text_color=info_data.get("p1_text_color", "#FFFFFF"),
                        p2_driver=info_data.get("p2_driver", ""),
                        p2_team=info_data.get("p2_team", ""),
                        p2_color=info_data.get("p2_color", "#555555"),
                        p2_text_color=info_data.get("p2_text_color", "#FFFFFF"),
                        p3_driver=info_data.get("p3_driver", ""),
                        p3_team=info_data.get("p3_team", ""),
                        p3_color=info_data.get("p3_color", "#555555"),
                        p3_text_color=info_data.get("p3_text_color", "#FFFFFF"),
                        top_ratings=info_data.get("top_ratings", []),
                        qual_front=info_data.get("qual_front", ""),
                        qual_second=info_data.get("qual_second", ""),
                        qual_top10=info_data.get("qual_top10", ""),
                        qual_midfield=info_data.get("qual_midfield", ""),
                        season_title=info_data.get("season_title", "Season 5 Teammate Qualifying Battles"),
                        seasonal_qual_rows=info_data.get("seasonal_qual_rows", []),
                        h2h_name1=info_data.get("h2h_name1", ""),
                        h2h_name2=info_data.get("h2h_name2", ""),
                        h2h_team1=info_data.get("h2h_team1", ""),
                        h2h_team2=info_data.get("h2h_team2", ""),
                        h2h_color1=info_data.get("h2h_color1", "#00b4da"),
                        h2h_color2=info_data.get("h2h_color2", "#ffffff"),
                        h2h_text_color1=info_data.get("h2h_text_color1", "#ffffff"),
                        h2h_text_color2=info_data.get("h2h_text_color2", "#000000"),
                        h2h_seasons=info_data.get("h2h_seasons", ""),
                        h2h_teammates1=info_data.get("h2h_teammates1", ""),
                        h2h_teammates2=info_data.get("h2h_teammates2", ""),
                        h2h_stats=info_data.get("h2h_stats", []),
                        champ_season1=info_data.get("champ_season1", "Season 4"),
                        champ_season2=info_data.get("champ_season2", "Season 3"),
                        champ_name1=info_data.get("champ_name1", ""),
                        champ_name2=info_data.get("champ_name2", ""),
                        champ_type1=info_data.get("champ_type1", "Constructor"),
                        champ_type2=info_data.get("champ_type2", "Constructor"),
                        champ_team1=info_data.get("champ_team1", ""),
                        champ_team2=info_data.get("champ_team2", ""),
                        champ_color1=info_data.get("champ_color1", "#00b4da"),
                        champ_color2=info_data.get("champ_color2", "#ffffff"),
                        champ_text_color1=info_data.get("champ_text_color1", "#ffffff"),
                        champ_text_color2=info_data.get("champ_text_color2", "#000000"),
                        champ_runner_up1=info_data.get("champ_runner_up1", ""),
                        champ_runner_up2=info_data.get("champ_runner_up2", ""),
                        champ_entities=info_data.get("champ_entities", []),
                        champ_stats=info_data.get("champ_stats", []),
                    )
                    self.messages = list(self.messages)
                    yield
                else:
                    # Sanitize in case an unclosed JSON block lingered without triggering full infographic
                    display_text = final_content
                    if "```infographic-json" in display_text or "```json" in display_text:
                        display_text = re.sub(r"```(?:infographic-json|json)\s*\{.*?\}\s*```", "", display_text, flags=re.DOTALL).strip()
                        display_text = re.sub(r"```(?:infographic-json|json).*$", "", display_text, flags=re.DOTALL).strip()

                    # Fallback recovery: if display_text is empty, promote thinking content so message is never blank
                    if not display_text and final_thinking:
                        display_text = re.sub(r"</?thinking>", "", final_thinking).strip()
                    if not display_text:
                        display_text = "Alternative Intelligence could not retrieve records for this query. Please re-submit."
                    display_text = sanitize_race_week_terminology(display_text)

                    self.messages[-1].thinking_content = final_thinking
                    self.messages[-1].content = display_text
                    yield

            if not accumulated_text and not accumulated_thought:
                self.messages[-1].content = "No response generated. Please refine your query."
                yield

        except httpx.TimeoutException:
            self.error_message = "Request timed out. Please try asking again."
            self.messages[-1].content = "The inquiry timed out while evaluating league statistics. Please retry."
            yield
        except Exception as e:
            self.error_message = f"Communication error: {str(e)}"
            self.messages[-1].content = f"An error occurred while connecting to Alternative Intelligence: {str(e)}"
            yield
        finally:
            self.is_generating = False
            yield



# ==============================================================================
# UI COMPONENTS
# ==============================================================================

def ai_logo(size: str = "24px", border_radius: str = "sm") -> rx.Component:
    """The Alternative F1 IconLogo with rainbow bokeh background matching the official icon."""
    return rx.box(
        rx.image(
            src="/Icons/IconLogo.png",
            height=size,
            width=size,
            object_fit="contain",
        ),
        background="radial-gradient(circle at 20% 25%, #E60049 0%, transparent 55%), radial-gradient(circle at 80% 25%, #FF8C00 0%, transparent 50%), radial-gradient(circle at 20% 80%, #7B00FF 0%, transparent 55%), radial-gradient(circle at 80% 80%, #0099FF 0%, transparent 50%), #121214",
        border_radius=border_radius,
        display="flex",
        align_items="center",
        justify_content="center",
        padding="2px",
    )


def gemini_trigger_button() -> rx.Component:
    """Alternative Intelligence trigger button with IconLogo on rainbow bokeh background pinned to far left.
    
    Styled per TAF1APP-SDDREQ-230 (V6) as a square button with heavily rounded corners and rainbow bokeh background,
    sized ~15% smaller than the 36px navigation button squares.
    """
    return rx.button(
        rx.image(
            src="/Icons/IconLogo.png",
            height="18px",
            width="18px",
            object_fit="contain",
        ),
        background="radial-gradient(circle at 20% 25%, #E60049 0%, transparent 55%), radial-gradient(circle at 80% 25%, #FF8C00 0%, transparent 50%), radial-gradient(circle at 20% 80%, #7B00FF 0%, transparent 55%), radial-gradient(circle at 80% 80%, #0099FF 0%, transparent 50%), #121214",
        border=rx.cond(
            AlternativeIntelligenceState.show_drawer,
            "2px solid white",
            "1px solid rgba(255, 255, 255, 0.4)"
        ),
        box_shadow=rx.cond(
            AlternativeIntelligenceState.show_drawer,
            "0 0 15px rgba(255, 0, 128, 0.8), 0 0 25px rgba(0, 180, 218, 0.6)",
            "0 2px 8px rgba(0, 0, 0, 0.5), 0 0 10px rgba(0, 180, 218, 0.3)"
        ),
        border_radius="9px",
        width="30px",
        height="30px",
        min_width="30px",
        max_width="30px",
        on_click=AlternativeIntelligenceState.toggle_drawer,
        _hover={
            "transform": "scale(1.08)",
            "box_shadow": "0 0 15px rgba(255, 0, 128, 0.7), 0 0 25px rgba(0, 180, 218, 0.6)",
        },
        cursor="pointer",
        padding="0",
        position="absolute",
        left="16px",
        z_index="102",
        title="Alternative Intelligence",
    )


def rating_bar_row(row: RatingRow) -> rx.Component:
    """Render a single driver row in the track rating leaderboard with proportional progress bar."""
    return rx.hstack(
        rx.text(row.rank, font_size="10px", font_weight="bold", color="#71717A", width="22px"),
        rx.text(row.driver, font_size="12px", font_weight="semibold", color="white", width="65px", no_of_lines=1),
        rx.badge(
            row.team,
            bg=row.color,
            color=row.text_color,
            border="1px solid rgba(255, 255, 255, 0.4)",
            font_size="9px",
            width="65px",
            justify="center",
        ),
        rx.box(
            rx.box(
                width=row.pct,
                bg=row.color,
                border="1px solid rgba(255, 255, 255, 0.4)",
                height="7px",
                border_radius="full",
                box_shadow="0 0 4px rgba(255, 255, 255, 0.25)",
            ),
            bg="#27272A",
            border_radius="full",
            height="7px",
            flex="1",
            overflow="hidden",
        ),
        rx.text(row.rating, font_size="11px", font_weight="bold", color="white", width="32px", text_align="right"),
        spacing="2",
        align="center",
        width="100%",
    )


def native_race_infographic_card(msg: ChatMessage) -> rx.Component:
    """Rich native Reflex visual infographic card rendering 4-part race preview analytics."""
    return rx.box(
        # Rainbow top highlight line
        rx.box(
            width="100%",
            height="3px",
            background="linear-gradient(90deg, #E60049 0%, #FF8C00 28%, #FFE500 50%, #00B4D8 75%, #7B00FF 100%)",
            border_radius="full",
            margin_bottom="12px",
        ),
        # Circuit & Grand Prix Header
        rx.hstack(
            rx.hstack(
                rx.icon("flag", size=18, color="#00b4da"),
                rx.text(
                    msg.track_name,
                    font_size="14px",
                    font_weight="bold",
                    color="white",
                    letter_spacing="-0.02em",
                ),
                spacing="2",
                align="center",
            ),
            rx.spacer(),
            rx.hstack(
                rx.badge("OFFICIAL INFOGRAPHIC", color_scheme="cyan", variant="solid", font_size="9px", font_weight="bold"),
                rx.button(
                    rx.hstack(
                        rx.icon("download", size=12),
                        rx.text("PNG", font_size="10px", font_weight="bold"),
                        spacing="1",
                        align="center",
                    ),
                    size="1",
                    variant="surface",
                    color_scheme="cyan",
                    on_click=AlternativeIntelligenceState.download_infographic_png(msg.card_id, msg.track_name),
                    cursor="pointer",
                    title="Download Infographic as .PNG",
                    custom_attrs={"data-html2canvas-ignore": "true"},
                ),
                spacing="2",
                align="center",
            ),
            width="100%",
            align="center",
            margin_bottom="12px",
        ),
        # Expected Winner Spotlight Bar
        rx.cond(
            msg.expected_winner != "",
            rx.hstack(
                rx.icon("trophy", size=16, color="#FFD700"),
                rx.text("EXPECTED WINNER:", font_size="10px", font_weight="bold", color="#A1A1AA", letter_spacing="0.05em"),
                rx.text(msg.expected_winner, font_size="12px", font_weight="bold", color="white"),
                rx.cond(
                    msg.expected_winner_team != "",
                    rx.badge(msg.expected_winner_team, bg=msg.winner_color, color=msg.winner_text_color, font_size="9px", font_weight="bold"),
                    rx.fragment(),
                ),
                spacing="2",
                align="center",
                width="100%",
                padding="8px 12px",
                bg="rgba(255, 215, 0, 0.08)",
                border="1px solid rgba(255, 215, 0, 0.25)",
                border_radius="md",
                margin_bottom="12px",
            ),
            rx.fragment(),
        ),
        # 3-Step Elevated Podium Display
        rx.cond(
            (msg.p1_driver != "") | (msg.p2_driver != "") | (msg.p3_driver != ""),
            rx.vstack(
                rx.hstack(
                    rx.icon("award", size=14, color="#EAB308"),
                    rx.text("Projected Podium", font_size="11px", font_weight="bold", color="#E4E4E7"),
                    spacing="1",
                    align="center",
                ),
                rx.hstack(
                    # 2nd Place (Silver)
                    rx.vstack(
                        rx.text(msg.p2_driver, font_size="11px", font_weight="bold", color="white", no_of_lines=1, text_align="center"),
                        rx.cond(
                            msg.p2_team != "",
                            rx.badge(msg.p2_team, bg=msg.p2_color, color=msg.p2_text_color, font_size="8px", max_width="80px"),
                            rx.fragment(),
                        ),
                        rx.box(
                            rx.text("2", font_size="20px", font_weight="900", color="white"),
                            width="100%",
                            height="55px",
                            background="linear-gradient(180deg, #94A3B8 0%, #475569 100%)",
                            border_radius="6px 6px 0 0",
                            display="flex",
                            align_items="center",
                            justify_content="center",
                            box_shadow="0 -3px 10px rgba(148, 163, 184, 0.25)",
                        ),
                        align="center",
                        spacing="1",
                        flex="1",
                    ),
                    # 1st Place (Gold Elevated)
                    rx.vstack(
                        rx.icon("crown", size=16, color="#FFD700"),
                        rx.text(msg.p1_driver, font_size="12px", font_weight="bold", color="#FFD700", no_of_lines=1, text_align="center"),
                        rx.cond(
                            msg.p1_team != "",
                            rx.badge(msg.p1_team, bg=msg.p1_color, color=msg.p1_text_color, font_size="9px", max_width="90px"),
                            rx.fragment(),
                        ),
                        rx.box(
                            rx.text("1", font_size="26px", font_weight="900", color="white"),
                            width="100%",
                            height="80px",
                            background="linear-gradient(180deg, #F59E0B 0%, #B45309 100%)",
                            border_radius="6px 6px 0 0",
                            display="flex",
                            align_items="center",
                            justify_content="center",
                            box_shadow="0 -4px 14px rgba(245, 158, 11, 0.4)",
                        ),
                        align="center",
                        spacing="1",
                        flex="1.1",
                    ),
                    # 3rd Place (Bronze)
                    rx.vstack(
                        rx.text(msg.p3_driver, font_size="11px", font_weight="bold", color="white", no_of_lines=1, text_align="center"),
                        rx.cond(
                            msg.p3_team != "",
                            rx.badge(msg.p3_team, bg=msg.p3_color, color=msg.p3_text_color, font_size="8px", max_width="80px"),
                            rx.fragment(),
                        ),
                        rx.box(
                            rx.text("3", font_size="18px", font_weight="900", color="white"),
                            width="100%",
                            height="42px",
                            background="linear-gradient(180deg, #D97706 0%, #78350F 100%)",
                            border_radius="6px 6px 0 0",
                            display="flex",
                            align_items="center",
                            justify_content="center",
                            box_shadow="0 -3px 8px rgba(217, 119, 6, 0.25)",
                        ),
                        align="center",
                        spacing="1",
                        flex="1",
                    ),
                    justify="center",
                    align="end",
                    spacing="2",
                    width="100%",
                    padding_top="6px",
                ),
                width="100%",
                padding="10px",
                bg="#141416",
                border="1px solid #27272A",
                border_radius="md",
                margin_bottom="12px",
            ),
            rx.fragment(),
        ),
        # Track Rating Leaderboard Progress Bars
        rx.cond(
            msg.top_ratings.length() > 0,
            rx.vstack(
                rx.hstack(
                    rx.icon("chart-bar", size=14, color="#00b4da"),
                    rx.text("Statistical Track Rating Leaderboard (0–100 Scale)", font_size="11px", font_weight="bold", color="#E4E4E7"),
                    spacing="1",
                    align="center",
                ),
                rx.vstack(
                    rx.foreach(msg.top_ratings, rating_bar_row),
                    spacing="2",
                    width="100%",
                    padding="10px",
                    bg="#141416",
                    border="1px solid #27272A",
                    border_radius="md",
                ),
                width="100%",
                spacing="2",
                margin_bottom="12px",
            ),
            rx.fragment(),
        ),
        # Qualifying Grid Tiers
        rx.cond(
            (msg.qual_front != "") | (msg.qual_second != ""),
            rx.vstack(
                rx.hstack(
                    rx.icon("timer", size=14, color="#A855F7"),
                    rx.text("All-Time Qualifying & Projected Grid", font_size="11px", font_weight="bold", color="#E4E4E7"),
                    spacing="1",
                    align="center",
                ),
                rx.vstack(
                    rx.cond(
                        msg.qual_front != "",
                        rx.hstack(
                            rx.badge("ROW 1 (P1-P2)", bg="#22C55E", color="black", font_size="9px", font_weight="bold", width="90px", justify="center"),
                            rx.text(msg.qual_front, font_size="11px", color="white", flex="1"),
                            spacing="2",
                            align="center",
                            width="100%",
                        ),
                        rx.fragment(),
                    ),
                    rx.cond(
                        msg.qual_second != "",
                        rx.hstack(
                            rx.badge("ROW 2 (P3-P4)", bg="#3B82F6", color="white", font_size="9px", font_weight="bold", width="90px", justify="center"),
                            rx.text(msg.qual_second, font_size="11px", color="white", flex="1"),
                            spacing="2",
                            align="center",
                            width="100%",
                        ),
                        rx.fragment(),
                    ),
                    rx.cond(
                        msg.qual_top10 != "",
                        rx.hstack(
                            rx.badge("TOP 10 (P5-P10)", bg="#A855F7", color="white", font_size="9px", font_weight="bold", width="90px", justify="center"),
                            rx.text(msg.qual_top10, font_size="11px", color="white", flex="1"),
                            spacing="2",
                            align="center",
                            width="100%",
                        ),
                        rx.fragment(),
                    ),
                    rx.cond(
                        msg.qual_midfield != "",
                        rx.hstack(
                            rx.badge("MIDFIELD (P11-16)", bg="#71717A", color="white", font_size="9px", font_weight="bold", width="90px", justify="center"),
                            rx.text(msg.qual_midfield, font_size="11px", color="white", flex="1"),
                            spacing="2",
                            align="center",
                            width="100%",
                        ),
                        rx.fragment(),
                    ),
                    spacing="2",
                    width="100%",
                    padding="10px",
                    bg="#141416",
                    border="1px solid #27272A",
                    border_radius="md",
                ),
                width="100%",
                spacing="2",
                margin_bottom="8px",
            ),
            rx.fragment(),
        ),
        id=msg.card_id,
        background="linear-gradient(145deg, #18181B 0%, #1f1f24 100%)",
        border="1px solid #3F3F46",
        border_radius="lg",
        padding="14px",
        width="100%",
        box_shadow="0 8px 24px rgba(0, 0, 0, 0.4)",
        margin_bottom="12px",
    )


def comparison_bar_row(row: ComparisonStatRow) -> rx.Component:
    """Render an individual metric comparison row with opposing dual-contrast horizontal bars."""
    return rx.vstack(
        # Centered metric label
        rx.text(
            row.metric,
            font_size="10px",
            font_weight="800",
            color="#A1A1AA",
            letter_spacing="0.1em",
            text_align="center",
            width="100%",
        ),
        # Dual-sided bar and numerical scores
        rx.hstack(
            # Driver 1 Value
            rx.text(
                row.val1,
                font_size="18px",
                font_weight="900",
                color=row.color1,
                width="70px",
                white_space="nowrap",
                text_shadow="0 0 1.5px rgba(255, 255, 255, 0.8), 0 1px 3px rgba(0, 0, 0, 0.9)",
                text_align="left",
            ),
            # Opposing Progress Bars Container
            rx.hstack(
                # Left bar (Driver 1 - grows right to center or fills left side)
                rx.box(
                    rx.box(
                        width=row.pct1,
                        height="14px",
                        bg=row.color1,
                        border="1px solid rgba(255, 255, 255, 0.45)",
                        border_radius="2px 0 0 2px",
                    ),
                    width="100%",
                    height="14px",
                    bg="#27272A",
                    display="flex",
                    justify_content="flex-end",
                    overflow="hidden",
                    flex="1",
                ),
                # Vertical Center Separator
                rx.box(width="2px", height="18px", bg="#18181B"),
                # Right bar (Driver 2 - grows left to right from center)
                rx.box(
                    rx.box(
                        width=row.pct2,
                        height="14px",
                        bg=row.color2,
                        border="1px solid rgba(255, 255, 255, 0.45)",
                        border_radius="0 2px 2px 0",
                    ),
                    width="100%",
                    height="14px",
                    bg="#27272A",
                    display="flex",
                    justify_content="flex-start",
                    overflow="hidden",
                    flex="1",
                ),
                spacing="0",
                align="center",
                flex="1",
                bg="#18181B",
                border_radius="4px",
                border="1px solid #3F3F46",
                overflow="hidden",
            ),
            # Driver 2 Value
            rx.text(
                row.val2,
                font_size="18px",
                font_weight="900",
                color=row.color2,
                width="70px",
                white_space="nowrap",
                text_shadow="0 0 1.5px rgba(255, 255, 255, 0.8), 0 1px 3px rgba(0, 0, 0, 0.9)",
                text_align="right",
            ),
            width="100%",
            align="center",
            spacing="2",
        ),
        # Subtle horizontal divider line
        rx.box(width="100%", height="1px", bg="#27272A", margin_y="4px"),
        spacing="1",
        width="100%",
    )


def native_h2h_infographic_card(msg: ChatMessage) -> rx.Component:
    """Rich native Reflex Head-to-Head Comparison Card (TAF1APP-SDDREQ-247) matching the mockup."""
    return rx.box(
        # Rainbow top highlight line
        rx.box(
            width="100%",
            height="3px",
            background="linear-gradient(90deg, #E60049 0%, #FF8C00 28%, #FFE500 50%, #00B4D8 75%, #7B00FF 100%)",
            border_radius="full",
            margin_bottom="12px",
        ),
        # Header with Download Button
        rx.hstack(
            rx.hstack(
                rx.icon("swords", size=16, color="#00b4da"),
                rx.text("HEAD TO HEAD COMPARISON", font_size="12px", font_weight="bold", color="white", letter_spacing="0.05em"),
                spacing="2",
                align="center",
            ),
            rx.spacer(),
            rx.button(
                rx.hstack(
                    rx.icon("download", size=12),
                    rx.text("PNG", font_size="10px", font_weight="bold"),
                    spacing="1",
                    align="center",
                ),
                size="1",
                variant="surface",
                color_scheme="cyan",
                on_click=AlternativeIntelligenceState.download_infographic_png(msg.card_id, f"{msg.h2h_name1}_vs_{msg.h2h_name2}_H2H"),
                cursor="pointer",
                title="Download Infographic as .PNG",
                custom_attrs={"data-html2canvas-ignore": "true"},
            ),
            width="100%",
            align="center",
            margin_bottom="10px",
        ),
        # Driver 1 vs. Driver 2 Header with The Alternative F1 NEW Logo in Center
        rx.hstack(
            # Driver 1 (Left)
            rx.vstack(
                rx.text(
                    msg.h2h_name1,
                    font_size="15px",
                    font_weight="900",
                    color=msg.h2h_color1,
                    text_shadow="0 0 1.5px rgba(255, 255, 255, 0.8), 0 1px 3px rgba(0, 0, 0, 0.9)",
                    letter_spacing="-0.02em",
                    no_of_lines=1,
                ),
                rx.cond(
                    msg.h2h_team1 != "",
                    rx.badge(
                        msg.h2h_team1,
                        bg=msg.h2h_color1,
                        color=msg.h2h_text_color1,
                        border="1px solid rgba(255, 255, 255, 0.4)",
                        font_size="8px",
                        font_weight="bold",
                    ),
                    rx.fragment(),
                ),
                align="start",
                spacing="1",
                flex="1",
            ),
            # Center Circle with The Alternative F1 NEW Logo (Replaces F1 logo)
            rx.box(
                rx.image(
                    src="/The Alternative F1 NEW Logo.png",
                    height="32px",
                    width="32px",
                    object_fit="contain",
                ),
                background="radial-gradient(circle, #27272A 0%, #18181B 100%)",
                border="2px solid #00b4da",
                border_radius="full",
                padding="4px",
                display="flex",
                align_items="center",
                justify_content="center",
                box_shadow="0 0 12px rgba(0, 180, 218, 0.4)",
            ),
            # Driver 2 (Right)
            rx.vstack(
                rx.text(
                    msg.h2h_name2,
                    font_size="15px",
                    font_weight="900",
                    color=msg.h2h_color2,
                    text_shadow="0 0 1.5px rgba(255, 255, 255, 0.8), 0 1px 3px rgba(0, 0, 0, 0.9)",
                    letter_spacing="-0.02em",
                    no_of_lines=1,
                    text_align="right",
                ),
                rx.cond(
                    msg.h2h_team2 != "",
                    rx.badge(
                        msg.h2h_team2,
                        bg=msg.h2h_color2,
                        color=msg.h2h_text_color2,
                        border="1px solid rgba(255, 255, 255, 0.4)",
                        font_size="8px",
                        font_weight="bold",
                    ),
                    rx.fragment(),
                ),
                align="end",
                spacing="1",
                flex="1",
            ),
            width="100%",
            align="center",
            padding="12px",
            bg="#141416",
            border="1px solid #27272A",
            border_radius="md",
            margin_bottom="12px",
        ),
        # Metric Comparison Rows
        rx.vstack(
            rx.foreach(msg.h2h_stats, comparison_bar_row),
            width="100%",
            spacing="1",
            margin_bottom="12px",
        ),
        # Footer: Shared Seasons & Teammate History
        rx.vstack(
            rx.cond(
                msg.h2h_seasons != "",
                rx.hstack(
                    rx.icon("calendar", size=12, color="#A1A1AA"),
                    rx.text("Seasons in League:", font_size="10px", font_weight="bold", color="#A1A1AA"),
                    rx.text(msg.h2h_seasons, font_size="10px", color="white", font_weight="semibold"),
                    spacing="1",
                    align="center",
                    width="100%",
                ),
                rx.fragment(),
            ),
            rx.cond(
                msg.h2h_teammates1 != "",
                rx.hstack(
                    rx.icon("users", size=12, color="#00b4da"),
                    rx.hstack(
                        rx.text(msg.h2h_name1, font_size="10px", font_weight="bold", color="#A1A1AA"),
                        rx.text(rx.cond(msg.h2h_is_constructor, "Drivers:", "Teammates:"), font_size="10px", font_weight="bold", color="#A1A1AA"),
                        spacing="1",
                    ),
                    rx.text(msg.h2h_teammates1, font_size="10px", color="#E4E4E7"),
                    spacing="1",
                    align="center",
                    width="100%",
                ),
                rx.fragment(),
            ),
            rx.cond(
                msg.h2h_teammates2 != "",
                rx.hstack(
                    rx.icon("users", size=12, color="#FFFFFF"),
                    rx.hstack(
                        rx.text(msg.h2h_name2, font_size="10px", font_weight="bold", color="#A1A1AA"),
                        rx.text(rx.cond(msg.h2h_is_constructor, "Drivers:", "Teammates:"), font_size="10px", font_weight="bold", color="#A1A1AA"),
                        spacing="1",
                    ),
                    rx.text(msg.h2h_teammates2, font_size="10px", color="#E4E4E7"),
                    spacing="1",
                    align="center",
                    width="100%",
                ),
                rx.fragment(),
            ),
            # Bottom Center League Logo (Replaces F1 badge in mockup footer)
            rx.center(
                rx.image(
                    src="/The Alternative F1 NEW Logo.png",
                    height="26px",
                    object_fit="contain",
                ),
                width="100%",
                padding_top="8px",
            ),
            spacing="1",
            width="100%",
            padding="10px",
            bg="#141416",
            border="1px solid #27272A",
            border_radius="md",
        ),
        id=msg.card_id,
        background="linear-gradient(145deg, #111113 0%, #18181B 100%)",
        border="1px solid #3F3F46",
        border_radius="lg",
        padding="14px",
        width="100%",
        box_shadow="0 8px 24px rgba(0, 0, 0, 0.4)",
        margin_bottom="12px",
    )


def seasonal_qual_row_item(row: TeammateQualRow) -> rx.Component:
    """Render an individual team's qualifying head-to-head battle row matching the official mockup."""
    return rx.box(
        rx.hstack(
            # Left: Huge Driver 1 Score + Driver 1 Name
            rx.hstack(
                rx.text(
                    row.score_display1,
                    font_size="28px",
                    font_weight="900",
                    color=row.text_color,
                    width="42px",
                    text_align="left",
                    line_height="1",
                ),
                rx.text(
                    row.driver1,
                    font_size="13px",
                    font_weight="800",
                    color=row.text_color,
                    letter_spacing="0.06em",
                    no_of_lines=1,
                ),
                spacing="2",
                align="center",
                flex="1",
            ),
            # Center: Team Monogram / Name Pill (no team logos per instructions)
            rx.box(
                rx.text(
                    row.team,
                    font_size="11px",
                    font_weight="900",
                    letter_spacing="0.1em",
                    color=row.text_color,
                    text_align="center",
                    text_transform="uppercase",
                ),
                padding_x="10px",
                padding_y="4px",
                bg="rgba(0, 0, 0, 0.28)",
                border_radius="sm",
                border=rx.cond(row.text_color == "#000000", "1px solid rgba(0,0,0,0.3)", "1px solid rgba(255,255,255,0.2)"),
                display="flex",
                align_items="center",
                justify_content="center",
                min_width="90px",
            ),
            # Right: Driver 2 Name + Huge Driver 2 Score
            rx.hstack(
                rx.text(
                    row.driver2,
                    font_size="13px",
                    font_weight="800",
                    color=row.text_color,
                    letter_spacing="0.06em",
                    no_of_lines=1,
                    text_align="right",
                ),
                rx.text(
                    row.score_display2,
                    font_size="28px",
                    font_weight="900",
                    color=row.text_color,
                    width="42px",
                    text_align="right",
                    line_height="1",
                ),
                spacing="2",
                align="center",
                justify="end",
                flex="1",
            ),
            width="100%",
            align="center",
            padding_x="14px",
            padding_y="10px",
        ),
        width="100%",
        bg=row.team_color,
        border="1px solid rgba(255, 255, 255, 0.35)",
        border_radius="4px",
        margin_bottom="3px",
    )


def native_seasonal_qual_infographic_card(msg: ChatMessage) -> rx.Component:
    """Rich native Reflex Seasonal Qualifying Battles Card (TAF1APP-SDDREQ-249) matching the mockup."""
    return rx.box(
        # Rainbow top highlight line
        rx.box(
            width="100%",
            height="3px",
            background="linear-gradient(90deg, #E60049 0%, #FF8C00 28%, #FFE500 50%, #00B4D8 75%, #7B00FF 100%)",
            border_radius="full",
            margin_bottom="12px",
        ),
        # Action Bar (Download Button)
        rx.hstack(
            rx.badge("OFFICIAL LEAGUE DOSSIER", color_scheme="cyan", variant="solid", font_size="9px", font_weight="bold"),
            rx.spacer(),
            rx.button(
                rx.hstack(
                    rx.icon("download", size=12),
                    rx.text("PNG", font_size="10px", font_weight="bold"),
                    spacing="1",
                    align="center",
                ),
                size="1",
                variant="surface",
                color_scheme="cyan",
                on_click=AlternativeIntelligenceState.download_infographic_png(msg.card_id, "Seasonal_Qualifying_Head_to_Head"),
                cursor="pointer",
                title="Download Infographic as .PNG",
                custom_attrs={"data-html2canvas-ignore": "true"},
            ),
            width="100%",
            align="center",
            margin_bottom="10px",
        ),
        # Top Card Header Block: Off-white high-contrast title matching the mockup
        rx.vstack(
            # Center Top League Logo (The Alternative F1 NEW Logo)
            rx.image(
                src="/The Alternative F1 NEW Logo.png",
                height="38px",
                object_fit="contain",
                margin_bottom="2px",
            ),
            # Huge QUALIFYING title
            rx.text(
                "QUALIFYING",
                font_size=["28px", "34px", "38px"],
                font_weight="900",
                color="#0F172A",
                letter_spacing="-0.02em",
                line_height="1",
                text_align="center",
            ),
            # HEAD - TO - HEAD red subtitle with wide tracking
            rx.text(
                "H E A D - T O - H E A D",
                font_size="12px",
                font_weight="900",
                color="#E11D48",
                letter_spacing="0.32em",
                text_align="center",
                margin_top="2px",
            ),
            # Season badge
            rx.badge(
                msg.season_title,
                bg="#E2E8F0",
                color="#334155",
                font_size="9px",
                font_weight="bold",
                margin_top="6px",
            ),
            spacing="1",
            align="center",
            width="100%",
            padding_top="18px",
            padding_bottom="14px",
            padding_x="12px",
            bg="linear-gradient(180deg, #F8FAFC 0%, #EDE9FE 100%)",
            border_radius="md md 0 0",
            border_bottom="3px solid #0F172A",
        ),
        # Solid Full-Bleed Team Rows (Stacked in Constructor Championship Order)
        rx.box(
            rx.foreach(msg.seasonal_qual_rows, seasonal_qual_row_item),
            width="100%",
            overflow="hidden",
            box_shadow="0 4px 12px rgba(0, 0, 0, 0.5)",
        ),
        # Bottom League Branding Footer
        rx.center(
            rx.hstack(
                rx.image(
                    src="/The Alternative F1 NEW Logo.png",
                    height="20px",
                    object_fit="contain",
                ),
                rx.text("THE ALTERNATIVE F1 • OFFICIAL QUALIFYING TELEMETRY", font_size="9px", font_weight="bold", color="#71717A", letter_spacing="0.05em"),
                spacing="2",
                align="center",
            ),
            width="100%",
            padding_y="10px",
            bg="#141416",
            border_radius="0 0 md md",
            border_top="1px solid #27272A",
        ),
        id=msg.card_id,
        background="#18181B",
        border="1px solid #3F3F46",
        border_radius="lg",
        padding="12px",
        width="100%",
        box_shadow="0 10px 30px rgba(0, 0, 0, 0.6)",
        margin_bottom="12px",
    )


def champion_entity_badge_card(entity: ChampionEntity) -> rx.Component:
    """Render an individual champion card in the multi-champion header grid."""
    return rx.box(
        rx.vstack(
            rx.badge(
                f"🏆 {entity.season} {entity.type}",
                bg="rgba(245, 158, 11, 0.15)",
                color="#F59E0B",
                border="1px solid rgba(245, 158, 11, 0.4)",
                font_size="8px",
                font_weight="bold",
                padding_x="6px",
                padding_y="1px",
            ),
            rx.text(
                entity.name,
                font_size="13px",
                font_weight="900",
                color=entity.color,
                text_shadow="0 0 1.5px rgba(255, 255, 255, 0.8), 0 1px 3px rgba(0, 0, 0, 0.9)",
                letter_spacing="-0.01em",
                no_of_lines=1,
            ),
            rx.cond(
                entity.team != "",
                rx.badge(
                    entity.team,
                    bg=entity.color,
                    color=entity.text_color,
                    border="1px solid rgba(255, 255, 255, 0.4)",
                    font_size="7px",
                    font_weight="bold",
                ),
                rx.fragment(),
            ),
            align="center",
            spacing="1",
        ),
        bg="#18181B",
        border="1px solid #27272A",
        border_radius="md",
        padding="8px",
        flex="1",
        min_width=["110px", "120px", "130px"],
        text_align="center",
    )


def champion_metric_segment_box(seg: ChampionMetricSegment) -> rx.Component:
    """Render an individual segment inside the 100% stacked bar chart."""
    return rx.box(
        rx.text(
            seg.pct,
            font_size="10px",
            font_weight="900",
            color=seg.text_color,
            letter_spacing="-0.02em",
            no_of_lines=1,
        ),
        width=seg.pct,
        height="22px",
        bg=seg.color,
        display="flex",
        align_items="center",
        justify_content="center",
        border_right="2px solid #121214",
        overflow="hidden",
    )


def champion_metric_header_chip(seg: ChampionMetricSegment) -> rx.Component:
    """Render an individual entity value chip in the metric row header."""
    return rx.hstack(
        rx.box(width="8px", height="8px", border_radius="full", bg=seg.color),
        rx.text(f"{seg.entity_name} ({seg.season}):", font_size="10px", font_weight="bold", color="#A1A1AA"),
        rx.text(seg.val, font_size="12px", font_weight="900", color=seg.color, text_shadow="0 0 1px rgba(255,255,255,0.7)"),
        spacing="1",
        align="center",
    )


def champion_metric_subtext_chip(seg: ChampionMetricSegment) -> rx.Component:
    """Render an individual entity sub-detail badge."""
    return rx.cond(
        seg.sub_text != "",
        rx.badge(
            f"{seg.entity_name}: {seg.sub_text}",
            font_size="8px",
            font_weight="bold",
            bg="rgba(255, 255, 255, 0.08)",
            color="#E4E4E7",
            border="1px solid #3F3F46",
            padding_x="6px",
            padding_y="1px",
            no_of_lines=1,
        ),
        rx.fragment(),
    )


def champion_metric_bar_row(row: ChampionMetricRow) -> rx.Component:
    """Render an individual comparison metric row as a 100% stacked bar chart with telemetry details."""
    return rx.vstack(
        # Top Header: Metric Name & Values
        rx.cond(
            row.segments.length() > 2,
            # N >= 3 layout: Metric pill badge on left, wrap of entity value chips
            rx.vstack(
                rx.hstack(
                    rx.badge(
                        row.metric.upper(),
                        font_size="9px",
                        font_weight="800",
                        bg="#27272A",
                        color="#E4E4E7",
                        border="1px solid #3F3F46",
                        letter_spacing="0.08em",
                        padding_x="8px",
                        padding_y="2px",
                        border_radius="full",
                    ),
                    rx.spacer(),
                    align="center",
                    width="100%",
                ),
                rx.flex(
                    rx.foreach(row.segments, champion_metric_header_chip),
                    wrap="wrap",
                    gap="2",
                    width="100%",
                    align="center",
                ),
                width="100%",
                spacing="1",
                padding_x="2px",
            ),
            # Classic N <= 2 layout
            rx.hstack(
                # Champion 1 Value (Left)
                rx.hstack(
                    rx.text(
                        row.val1,
                        font_size="15px",
                        font_weight="900",
                        color=row.color1,
                        text_shadow="0 0 1.5px rgba(255, 255, 255, 0.8), 0 1px 3px rgba(0, 0, 0, 0.9)",
                        line_height="1",
                    ),
                    align="center",
                    spacing="1",
                    flex="1",
                ),
                # Metric Badge (Center)
                rx.badge(
                    row.metric.upper(),
                    font_size="9px",
                    font_weight="800",
                    bg="#27272A",
                    color="#E4E4E7",
                    border="1px solid #3F3F46",
                    letter_spacing="0.08em",
                    padding_x="8px",
                    padding_y="2px",
                    border_radius="full",
                ),
                # Champion 2 Value (Right)
                rx.hstack(
                    rx.text(
                        row.val2,
                        font_size="15px",
                        font_weight="900",
                        color=row.color2,
                        text_shadow="0 0 1.5px rgba(255, 255, 255, 0.8), 0 1px 3px rgba(0, 0, 0, 0.9)",
                        text_align="right",
                        line_height="1",
                    ),
                    justify="end",
                    align="center",
                    spacing="1",
                    flex="1",
                ),
                width="100%",
                align="center",
                padding_x="2px",
            ),
        ),
        # 100% Stacked Bar Chart (Center)
        rx.box(
            rx.hstack(
                rx.cond(
                    row.segments.length() > 0,
                    rx.foreach(row.segments, champion_metric_segment_box),
                    # Fallback to dual segments
                    rx.fragment(
                        rx.box(
                            rx.text(row.pct1, font_size="11px", font_weight="900", color=row.text_color1),
                            width=row.pct1, height="22px", bg=row.color1, display="flex", align_items="center", justify_content="center", overflow="hidden"
                        ),
                        rx.box(width="2px", height="22px", bg="#121214"),
                        rx.box(
                            rx.text(row.pct2, font_size="11px", font_weight="900", color=row.text_color2),
                            width=row.pct2, height="22px", bg=row.color2, display="flex", align_items="center", justify_content="center", overflow="hidden"
                        ),
                    ),
                ),
                spacing="0",
                width="100%",
                height="22px",
            ),
            width="100%",
            height="22px",
            bg="#18181B",
            border_radius="6px",
            border="1px solid #3F3F46",
            overflow="hidden",
            box_shadow="inset 0 1px 3px rgba(0, 0, 0, 0.6), 0 2px 6px rgba(0, 0, 0, 0.3)",
        ),
        # Optional Sub-Detail Badges Row
        rx.cond(
            row.segments.length() > 2,
            rx.flex(
                rx.foreach(row.segments, champion_metric_subtext_chip),
                wrap="wrap",
                gap="2",
                width="100%",
                padding_x="2px",
            ),
            # Classic N <= 2 subtext
            rx.cond(
                (row.sub_text1 != "") | (row.sub_text2 != ""),
                rx.hstack(
                    rx.box(
                        rx.cond(
                            row.sub_text1 != "",
                            rx.badge(row.sub_text1, font_size="8px", font_weight="bold", bg="rgba(255, 255, 255, 0.08)", color="#E4E4E7", border="1px solid #3F3F46", padding_x="6px", padding_y="1px", no_of_lines=1),
                            rx.fragment(),
                        ),
                        flex="1", display="flex", justify_content="flex-start",
                    ),
                    rx.box(
                        rx.cond(
                            row.sub_text2 != "",
                            rx.badge(row.sub_text2, font_size="8px", font_weight="bold", bg="rgba(255, 255, 255, 0.08)", color="#E4E4E7", border="1px solid #3F3F46", padding_x="6px", padding_y="1px", no_of_lines=1, text_align="right"),
                            rx.fragment(),
                        ),
                        flex="1", display="flex", justify_content="flex-end",
                    ),
                    width="100%", align="center", padding_x="2px",
                ),
                rx.fragment(),
            ),
        ),
        # Subtle separator between metric rows
        rx.box(width="100%", height="1px", bg="#27272A", margin_y="4px"),
        spacing="1",
        width="100%",
    )


def native_champion_comparison_card(msg: ChatMessage) -> rx.Component:
    """Rich native Reflex Champion Comparison Card (TAF1APP-SDDREQ-250) supporting N+ champions."""
    return rx.box(
        # Rainbow top highlight line
        rx.box(
            width="100%",
            height="3px",
            background="linear-gradient(90deg, #E60049 0%, #FF8C00 28%, #FFE500 50%, #00B4D8 75%, #7B00FF 100%)",
            border_radius="full",
            margin_bottom="12px",
        ),
        # Header with Download Button
        rx.hstack(
            rx.hstack(
                rx.icon("trophy", size=16, color="#F59E0B"),
                rx.text("CHAMPION COMPARISON", font_size="12px", font_weight="bold", color="white", letter_spacing="0.05em"),
                rx.badge("OFFICIAL LEAGUE DOSSIER", color_scheme="amber", variant="surface", font_size="8px", font_weight="bold"),
                spacing="2",
                align="center",
            ),
            rx.spacer(),
            rx.button(
                rx.hstack(
                    rx.icon("download", size=12),
                    rx.text("PNG", font_size="10px", font_weight="bold"),
                    spacing="1",
                    align="center",
                ),
                size="1",
                variant="surface",
                color_scheme="amber",
                on_click=AlternativeIntelligenceState.download_infographic_png(msg.card_id, "Champion_Comparison_Dossier"),
                cursor="pointer",
                title="Download Infographic as .PNG",
                custom_attrs={"data-html2canvas-ignore": "true"},
            ),
            width="100%",
            align="center",
            margin_bottom="10px",
        ),
        # Champions Showcase (Multi-Grid if N >= 3, else Classic Dual Header)
        rx.cond(
            msg.champ_entities.length() > 2,
            # Multi-Champion Grid Showcase (N >= 3)
            rx.flex(
                rx.foreach(msg.champ_entities, champion_entity_badge_card),
                wrap="wrap",
                gap="2",
                width="100%",
                padding="8px",
                bg="#141416",
                border="1px solid #27272A",
                border_radius="md",
                margin_bottom="12px",
                justify="center",
            ),
            # Classic Dual Champion Layout (N <= 2)
            rx.hstack(
                # Champion 1 (Left)
                rx.vstack(
                    rx.badge(
                        f"🏆 {msg.champ_season1} {msg.champ_type1} Champion",
                        bg="rgba(245, 158, 11, 0.15)",
                        color="#F59E0B",
                        border="1px solid rgba(245, 158, 11, 0.4)",
                        font_size="9px",
                        font_weight="bold",
                    ),
                    rx.text(
                        msg.champ_name1,
                        font_size="15px",
                        font_weight="900",
                        color=msg.champ_color1,
                        text_shadow="0 0 1.5px rgba(255, 255, 255, 0.8), 0 1px 3px rgba(0, 0, 0, 0.9)",
                        letter_spacing="-0.02em",
                        no_of_lines=1,
                    ),
                    rx.cond(
                        msg.champ_team1 != "",
                        rx.badge(
                            msg.champ_team1,
                            bg=msg.champ_color1,
                            color=msg.champ_text_color1,
                            border="1px solid rgba(255, 255, 255, 0.4)",
                            font_size="8px",
                            font_weight="bold",
                        ),
                        rx.fragment(),
                    ),
                    align="start",
                    spacing="1",
                    flex="1",
                ),
                # Center Circle with The Alternative F1 NEW Logo & Trophy Aura
                rx.box(
                    rx.image(
                        src="/The Alternative F1 NEW Logo.png",
                        height="32px",
                        width="32px",
                        object_fit="contain",
                    ),
                    background="radial-gradient(circle, #27272A 0%, #18181B 100%)",
                    border="2px solid #F59E0B",
                    border_radius="full",
                    padding="4px",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                    box_shadow="0 0 12px rgba(245, 158, 11, 0.4)",
                ),
                # Champion 2 (Right)
                rx.vstack(
                    rx.badge(
                        f"🏆 {msg.champ_season2} {msg.champ_type2} Champion",
                        bg="rgba(245, 158, 11, 0.15)",
                        color="#F59E0B",
                        border="1px solid rgba(245, 158, 11, 0.4)",
                        font_size="9px",
                        font_weight="bold",
                    ),
                    rx.text(
                        msg.champ_name2,
                        font_size="15px",
                        font_weight="900",
                        color=msg.champ_color2,
                        text_shadow="0 0 1.5px rgba(255, 255, 255, 0.8), 0 1px 3px rgba(0, 0, 0, 0.9)",
                        letter_spacing="-0.02em",
                        no_of_lines=1,
                        text_align="right",
                    ),
                    rx.cond(
                        msg.champ_team2 != "",
                        rx.badge(
                            msg.champ_team2,
                            bg=msg.champ_color2,
                            color=msg.champ_text_color2,
                            border="1px solid rgba(255, 255, 255, 0.4)",
                            font_size="8px",
                            font_weight="bold",
                        ),
                        rx.fragment(),
                    ),
                    align="end",
                    spacing="1",
                    flex="1",
                ),
                width="100%",
                align="center",
                padding="12px",
                bg="#141416",
                border="1px solid #27272A",
                border_radius="md",
                margin_bottom="12px",
            ),
        ),
        # Metric Comparison Rows
        rx.vstack(
            rx.foreach(msg.champ_stats, champion_metric_bar_row),
            width="100%",
            spacing="1",
            margin_bottom="12px",
        ),
        # Bottom League Branding Footer
        rx.center(
            rx.hstack(
                rx.image(
                    src="/The Alternative F1 NEW Logo.png",
                    height="20px",
                    object_fit="contain",
                ),
                rx.text("THE ALTERNATIVE F1 • OFFICIAL CHAMPIONSHIP HISTORICAL TELEMETRY", font_size="9px", font_weight="bold", color="#71717A", letter_spacing="0.05em"),
                spacing="2",
                align="center",
            ),
            width="100%",
            padding_y="10px",
            bg="#141416",
            border_radius="0 0 md md",
            border_top="1px solid #27272A",
        ),
        id=msg.card_id,
        background="#18181B",
        border="1px solid #3F3F46",
        border_radius="lg",
        padding="12px",
        width="100%",
        box_shadow="0 10px 30px rgba(0, 0, 0, 0.6)",
        margin_bottom="12px",
    )


def racing_helmet_icon(size: int = 18, color: str = "#00b4da") -> rx.Component:
    """Render a 3/4 angled SVG outline of a motorsport / racing helmet matching user reference."""
    return rx.html(f"""
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="{size}" height="{size}" fill="none" stroke="{color}" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" style="display:block;">
            <path d="M 31 80 C 23 66 22 47 28 32 C 34 19 50 17 68 20 C 71 22 72 24 70 27 L 77 53 L 42 75 L 42 66 C 36 71 33 76 31 80 Z" />
            <path d="M 25 49 C 33 44 46 38 54 39 C 58 40 56 47 49 52 C 39 60 30 66 26 68 L 25 49 Z" />
            <path d="M 30 41 L 35 34 L 48 31 L 34 39 Z" fill="{color}" />
            <path d="M 46 25 C 52 24 62 26 67 30" />
            <path d="M 42 66 C 53 56 63 46 72 34" />
        </svg>
    """)


def message_card(msg: ChatMessage) -> rx.Component:
    """Render an individual conversational message card."""
    is_user = msg.role == "user"
    return rx.hstack(
        rx.vstack(
            rx.cond(
                msg.is_infographic,
                rx.cond(
                    msg.infographic_type == "champion_comparison",
                    native_champion_comparison_card(msg),
                    rx.cond(
                        msg.infographic_type == "h2h",
                        native_h2h_infographic_card(msg),
                        rx.cond(
                            msg.infographic_type == "seasonal_qual",
                            native_seasonal_qual_infographic_card(msg),
                            native_race_infographic_card(msg),
                        ),
                    ),
                ),
                rx.fragment(),
            ),

            rx.cond(
                (msg.content != "") | (msg.thinking_content != "") | ((~is_user) & AlternativeIntelligenceState.is_generating),
                rx.box(
                    # Assistant response top thin rainbow accent line
                    rx.cond(
                        ~is_user,
                        rx.box(
                            width="100%",
                            height="3px",
                            background="linear-gradient(90deg, #E60049 0%, #FF8C00 28%, #FFE500 50%, #00B4D8 75%, #7B00FF 100%)",
                            border_radius="full",
                            margin_bottom="10px",
                        ),
                        rx.fragment(),
                    ),
                    # User prompt skill badge pill box (persisted with prompt)
                    rx.cond(
                        is_user & (msg.skill_badge != ""),
                        rx.box(
                            rx.hstack(
                                rx.icon("sparkles", size=11, color="white"),
                                rx.text(msg.skill_badge, font_size="10px", font_weight="bold", color="white", letter_spacing="0.02em"),
                                spacing="1",
                                align="center",
                            ),
                            background="radial-gradient(circle at 20% 25%, rgba(230, 0, 73, 0.6) 0%, transparent 55%), radial-gradient(circle at 80% 25%, rgba(255, 140, 0, 0.6) 0%, transparent 50%), radial-gradient(circle at 20% 80%, rgba(123, 0, 255, 0.6) 0%, transparent 55%), radial-gradient(circle at 80% 80%, rgba(0, 153, 255, 0.6) 0%, transparent 50%), rgba(24, 24, 28, 0.7)",
                            border="1px solid rgba(255, 255, 255, 0.35)",
                            box_shadow="0 0 10px rgba(0, 180, 218, 0.3)",
                            border_radius="full",
                            padding_x="8px",
                            padding_y="3px",
                            margin_bottom="8px",
                            display="inline-block",
                        ),
                        rx.fragment(),
                    ),
                    # Collapsible thinking artifact (collapsed by default)
                    rx.cond(
                        (~is_user) & (msg.thinking_content != ""),
                        rx.box(
                            rx.accordion.root(
                                rx.accordion.item(
                                    rx.accordion.trigger(
                                        rx.hstack(
                                            rx.icon("brain", size=13, color="#00b4da"),
                                            rx.text("Thought Process", font_size="11px", font_weight="600", color="#A1A1AA", letter_spacing="0.02em"),
                                            spacing="2",
                                            align="center",
                                        ),
                                        padding_y="6px",
                                        padding_x="10px",
                                        background="#1F1F23",
                                        border_radius="6px",
                                        _hover={"background": "#27272A", "cursor": "pointer"},
                                        width="100%",
                                    ),
                                    rx.accordion.content(
                                        rx.box(
                                            rx.markdown(
                                                msg.thinking_content,
                                                style={
                                                    "font_size": "0.82rem",
                                                    "color": "#A1A1AA",
                                                    "line_height": "1.45",
                                                    "p": {"margin_bottom": "0.4rem"},
                                                    "table": {
                                                        "display": "block",
                                                        "width": "100%",
                                                        "overflow_x": "auto",
                                                        "border_collapse": "collapse",
                                                        "margin": "0.4rem 0",
                                                        "font_size": "0.78rem",
                                                    },
                                                    "th": {
                                                        "border": "1px solid #3F3F46",
                                                        "padding": "4px 8px",
                                                        "background": "#27272A",
                                                        "color": "#00b4da",
                                                    },
                                                    "td": {
                                                        "border": "1px solid #27272A",
                                                        "padding": "4px 8px",
                                                    },
                                                    "code": {
                                                        "background": "#27272A",
                                                        "padding": "2px 4px",
                                                        "border_radius": "4px",
                                                        "font_size": "0.78rem",
                                                    },
                                                    "pre": {
                                                        "overflow_x": "auto",
                                                        "background": "#27272A",
                                                        "padding": "6px",
                                                        "border_radius": "4px",
                                                        "margin": "0.4rem 0",
                                                    },
                                                },
                                            ),
                                            padding="10px 12px",
                                            background="#141416",
                                            border="1px solid #27272A",
                                            border_top="none",
                                            border_bottom_left_radius="6px",
                                            border_bottom_right_radius="6px",
                                            width="100%",
                                        ),
                                    ),
                                    value="thinking",
                                    border="1px solid #27272A",
                                    border_radius="6px",
                                    width="100%",
                                ),
                                collapsible=True,
                                type="single",
                                width="100%",
                            ),
                            margin_bottom="10px",
                            width="100%",
                        ),
                        rx.fragment(),
                    ),
                    rx.cond(
                        msg.content != "",
                        rx.markdown(
                            msg.content,
                            style={
                                "font_size": "0.9rem",
                                "color": "#E4E4E7",
                                "line_height": "1.5",
                                "p": {"margin_bottom": "0.5rem"},
                                "table": {
                                    "display": "block",
                                    "width": "100%",
                                    "max_width": "100%",
                                    "overflow_x": "auto",
                                    "-webkit-overflow-scrolling": "touch",
                                    "border_collapse": "collapse",
                                    "margin": "0.6rem 0",
                                    "font_size": "0.82rem",
                                },
                                "th": {
                                    "border": "1px solid #3F3F46",
                                    "padding": "6px 10px",
                                    "background": "#27272A",
                                    "color": "#00b4da",
                                    "white_space": "nowrap",
                                },
                                "td": {
                                    "border": "1px solid #27272A",
                                    "padding": "6px 10px",
                                    "white_space": "nowrap",
                                },
                                "code": {
                                    "background": "#27272A",
                                    "padding": "2px 4px",
                                    "border_radius": "4px",
                                    "font_size": "0.8rem",
                                },
                                "pre": {
                                    "overflow_x": "auto",
                                    "max_width": "100%",
                                    "background": "#27272A",
                                    "padding": "8px",
                                    "border_radius": "6px",
                                    "margin": "0.5rem 0",
                                },
                                "img": {
                                    "display": "inline-block",
                                    "vertical_align": "middle",
                                    "width": "34px",
                                    "height": "34px",
                                    "border_radius": "50%",
                                    "margin_left": "6px",
                                    "box_shadow": "0 0 10px rgba(245, 158, 11, 0.6)",
                                    "border": "1px solid rgba(245, 158, 11, 0.8)",
                                },
                            },
                        ),
                        rx.cond(
                            AlternativeIntelligenceState.is_generating & (~is_user),
                            rx.hstack(
                                rx.spinner(size="1", color="#00b4da"),
                                rx.text("Alternative Intelligence is evaluating league records...", font_size="12px", color="#A1A1AA"),
                                spacing="2",
                                align="center",
                                padding_y="6px",
                            ),
                            rx.fragment(),
                        ),
                    ),
                    bg=rx.cond(is_user, "#27272A", "#18181B"),
                    border=rx.cond(is_user, "1px solid #3F3F46", "1px solid #2C2C32"),
                    border_radius="md",
                    padding="10px 14px",
                    max_width=rx.cond(is_user, "85%", "100%"),
                    width=rx.cond(is_user, "auto", "100%"),
                    overflow_x="auto",
                    box_sizing="border-box",
                    box_shadow="0 2px 8px rgba(0, 0, 0, 0.3)",
                ),
                rx.fragment(),
            ),
            rx.cond(
                msg.timestamp != "",
                rx.moment(
                    date=msg.timestamp,
                    format="h:mm A",
                    local=True,
                    font_size="10px",
                    color="#71717A",
                    padding_x="4px",
                    width="100%",
                    text_align=rx.cond(is_user, "right", "left"),
                ),
                rx.fragment(),
            ),
            align_items=rx.cond(is_user, "end", "center"),
            spacing="1",
            width="100%",
            min_width="0",
            flex="1",
        ),
        rx.cond(
            is_user,
            rx.cond(
                (msg.user_avatar != "") | (AlternativeIntelligenceState.discord_avatar != ""),
                rx.box(
                    rx.avatar(
                        src=rx.cond(
                            msg.user_avatar != "",
                            msg.user_avatar,
                            AlternativeIntelligenceState.discord_avatar,
                        ),
                        fallback="U",
                        size="2",
                        bg="transparent",
                        height="32px",
                        width="32px",
                        border_radius="50%",
                    ),
                    border="1px solid #00b4da",
                    border_radius="50%",
                    overflow="hidden",
                    height="32px",
                    width="32px",
                    min_width="32px",
                    margin_right="4px",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                ),
                rx.box(
                    racing_helmet_icon(size=18, color="#00b4da"),
                    bg="#27272A",
                    border="1px solid #3F3F46",
                    border_radius="50%",
                    padding="6px",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                    height="32px",
                    width="32px",
                    min_width="32px",
                    margin_right="4px",
                ),
            ),
            rx.fragment(),
        ),
        class_name=rx.cond(is_user, "ai-user-message-card", "ai-assistant-message-card"),
        width="100%",
        justify=rx.cond(is_user, "end", "center"),
        spacing="2",
        align_items="start",
        padding_right=rx.cond(is_user, "4px", "0px"),
    )


def skills_library_selector() -> rx.Component:
    """Dropdown selector displaying the library of analytical skills."""
    return rx.vstack(
        rx.hstack(
            rx.icon("sparkles", size=15, color="#00b4da"),
            rx.text("Skills Library", font_size="13px", font_weight="bold", color="white"),
            spacing="2",
            align="center",
        ),
        rx.select(
            SKILL_OPTIONS,
            value=AlternativeIntelligenceState.selected_skill,
            on_change=AlternativeIntelligenceState.select_skill,
            bg="#18181B",
            color="white",
            border="1px solid #3F3F46",
            border_radius="md",
            width="100%",
            max_width="320px",
            height="38px",
            font_size="13px",
            cursor="pointer",
            _hover={"border_color": "#00b4da"},
        ),
        rx.text(
            "Select an optional skill or simply ask a question in the input bar.",
            font_size="11px",
            color="#A1A1AA",
            text_align="center",
            max_width="320px",
            line_height="1.4",
        ),
        spacing="2",
        align="center",
        width="100%",
        padding="14px",
        bg="#18181B",
        border="1px solid #27272A",
        border_radius="lg",
    )


def alternative_intelligence_drawer() -> rx.Component:
    """Sliding left-hand pop-out drawer for Alternative Intelligence."""
    return rx.cond(
        AlternativeIntelligenceState.show_drawer,
        rx.box(
            # Backdrop Overlay
            rx.box(
                position="fixed",
                top="0",
                left="0",
                width="100vw",
                height="100vh",
                bg="rgba(0,0,0,0.6)",
                backdrop_filter="blur(3px)",
                z_index="1999",
                on_click=AlternativeIntelligenceState.toggle_drawer,
            ),
            # Sliding Container (Left Side)
            rx.vstack(
                # Header Bar (Rainbow stretches across header and gently fades out before buttons)
                rx.hstack(
                    rx.hstack(
                        rx.heading(
                            "Alternative Intelligence",
                            size="4",
                            color="white",
                            font_weight="800",
                            letter_spacing="tight",
                            text_shadow="0 2px 6px rgba(0, 0, 0, 0.85)",
                        ),
                        rx.badge(
                            "BETA",
                            color_scheme="cyan",
                            variant="surface",
                            font_size="9px",
                            font_weight="900",
                            letter_spacing="0.08em",
                            border="1px solid rgba(0, 180, 218, 0.4)",
                            box_shadow="0 0 8px rgba(0, 180, 218, 0.3)",
                        ),
                        spacing="2",
                        align="center",
                    ),
                    rx.spacer(),
                    rx.hstack(
                        rx.button(
                            rx.icon("trash-2", size=16),
                            bg="transparent",
                            color="#A1A1AA",
                            _hover={"color": "#EF4444"},
                            on_click=AlternativeIntelligenceState.clear_chat,
                            size="1",
                            padding="4px",
                            title="Clear conversation",
                        ),
                        rx.button(
                            rx.icon("x", size=20),
                            bg="transparent",
                            color="#A1A1AA",
                            _hover={"color": "white"},
                            on_click=AlternativeIntelligenceState.toggle_drawer,
                            size="1",
                            padding="4px",
                            title="Close drawer",
                        ),
                        spacing="2",
                        align="center",
                    ),
                    width="100%",
                    align="center",
                    padding_left=["20px", "24px", "26px"],
                    padding_right=["14px", "18px", "20px"],
                    padding_y="4",
                    background="radial-gradient(circle at 10% 30%, rgba(230, 0, 73, 0.75) 0%, transparent 55%), radial-gradient(circle at 35% 20%, rgba(255, 140, 0, 0.7) 0%, transparent 50%), radial-gradient(circle at 65% 80%, rgba(123, 0, 255, 0.75) 0%, transparent 55%), radial-gradient(circle at 90% 40%, rgba(0, 153, 255, 0.75) 0%, transparent 50%), #111113",
                    border_bottom="1px solid #27272A",
                ),

                # Message Feed with generous horizontal and vertical inset
                rx.box(
                    rx.cond(
                        AlternativeIntelligenceState.messages.length() > 0,
                        rx.vstack(
                            rx.foreach(AlternativeIntelligenceState.messages, message_card),
                            rx.cond(
                                AlternativeIntelligenceState.is_generating,
                                rx.hstack(
                                    ai_logo("16px", border_radius="sm"),
                                    rx.text("Analyzing league database...", font_size="12px", color="#00b4da"),
                                    spacing="2",
                                    align="center",
                                    padding="6px 12px",
                                    bg="#18181B",
                                    border_radius="md",
                                    border="1px solid #00b4da",
                                ),
                                rx.fragment(),
                            ),
                            rx.box(id="ai-chat-bottom-anchor", height="1px", width="100%"),
                            width="100%",
                            spacing="4",
                            padding_y="2",
                        ),
                        # Empty state with Skills Library
                        rx.vstack(
                            rx.box(
                                rx.image(
                                    src="/Icons/IconLogo.png",
                                    height="48px",
                                    width="48px",
                                    object_fit="contain",
                                ),
                                background="radial-gradient(circle at 20% 25%, #E60049 0%, transparent 55%), radial-gradient(circle at 80% 25%, #FF8C00 0%, transparent 50%), radial-gradient(circle at 20% 80%, #7B00FF 0%, transparent 55%), radial-gradient(circle at 80% 80%, #0099FF 0%, transparent 50%), #121214",
                                border_radius="18px",
                                padding="14px",
                                border="1px solid rgba(255, 255, 255, 0.3)",
                                box_shadow="0 0 25px rgba(0, 180, 218, 0.4), 0 0 15px rgba(230, 0, 73, 0.4)",
                                margin_bottom="3",
                            ),
                            rx.text("Alternative Intelligence", font_size="15px", font_weight="bold", color="white"),
                            rx.text("Official analytical AI statistician for The Alternative F1.", font_size="12px", color="#A1A1AA", text_align="center"),
                            rx.box(
                                skills_library_selector(),
                                width="100%",
                                max_width="340px",
                                margin_top="4",
                            ),
                            align="center",
                            justify="center",
                            height="100%",
                            padding_y="6",
                        ),
                    ),
                    id="ai-chat-feed",
                    width="100%",
                    flex="1",
                    overflow_y="auto",
                    padding_x=["12px", "16px", "20px"],
                    padding_top="16px",
                    padding_bottom="12px",
                ),

                # Error banner if present
                rx.cond(
                    AlternativeIntelligenceState.error_message != "",
                    rx.box(
                        rx.hstack(
                            rx.icon("circle-alert", size=16, color="#EF4444"),
                            rx.text(AlternativeIntelligenceState.error_message, font_size="12px", color="#EF4444"),
                            spacing="2",
                        ),
                        bg="#271515",
                        border="1px solid #7F1D1D",
                        border_radius="md",
                        padding="8px 12px",
                        margin_x="5",
                        margin_bottom="2",
                        width="calc(100% - 40px)",
                    ),
                    rx.fragment(),
                ),

                # Bottom Search Bar (Anchored comfortably at bottom with safe-area support and luminous card)
                rx.box(
                    rx.cond(
                        AlternativeIntelligenceState.messages.length() > 0,
                        rx.hstack(
                            rx.hstack(
                                rx.icon("sparkles", size=13, color="#00b4da"),
                                rx.text("Skill:", font_size="11px", color="#A1A1AA", font_weight="semibold"),
                                spacing="1",
                                align="center",
                            ),
                            rx.select(
                                SKILL_OPTIONS,
                                value=AlternativeIntelligenceState.selected_skill,
                                on_change=AlternativeIntelligenceState.select_skill,
                                bg="#18181B",
                                color="white",
                                border="1px solid #27272A",
                                border_radius="md",
                                height="28px",
                                font_size="11px",
                                cursor="pointer",
                                flex="1",
                                _hover={"border_color": "#00b4da"},
                            ),
                            spacing="2",
                            align="center",
                            width="100%",
                            margin_bottom="2",
                        ),
                        rx.fragment(),
                    ),
                    rx.hstack(
                        rx.hstack(
                            rx.cond(
                                AlternativeIntelligenceState.active_skill_badge != "",
                                rx.hstack(
                                    rx.text(
                                        AlternativeIntelligenceState.active_skill_badge,
                                        class_name="ai-skill-badge-full",
                                        display=["none", "none", "inline", "inline", "inline"],
                                        font_size="11px",
                                        font_weight="bold",
                                        color="white",
                                        text_shadow="0 1px 3px rgba(0, 0, 0, 0.8)",
                                        white_space="nowrap",
                                    ),
                                    rx.text(
                                        AlternativeIntelligenceState.active_skill_badge_short,
                                        class_name="ai-skill-badge-short",
                                        display=["inline", "inline", "none", "none", "none"],
                                        font_size="11px",
                                        font_weight="bold",
                                        color="white",
                                        text_shadow="0 1px 3px rgba(0, 0, 0, 0.8)",
                                        white_space="nowrap",
                                    ),
                                    rx.button(
                                        rx.icon("x", size=12, color="rgba(255, 255, 255, 0.8)"),
                                        size="1",
                                        variant="ghost",
                                        padding="0",
                                        height="16px",
                                        width="16px",
                                        min_width="16px",
                                        cursor="pointer",
                                        on_click=AlternativeIntelligenceState.clear_active_skill,
                                        _hover={"color": "#EF4444"},
                                        title="Clear selected skill",
                                    ),
                                    title=AlternativeIntelligenceState.active_skill_badge,
                                    background="radial-gradient(circle at 20% 25%, rgba(230, 0, 73, 0.55) 0%, transparent 55%), radial-gradient(circle at 80% 25%, rgba(255, 140, 0, 0.55) 0%, transparent 50%), radial-gradient(circle at 20% 80%, rgba(123, 0, 255, 0.55) 0%, transparent 55%), radial-gradient(circle at 80% 80%, rgba(0, 153, 255, 0.55) 0%, transparent 50%), rgba(18, 18, 20, 0.55)",
                                    border="1px solid rgba(255, 255, 255, 0.3)",
                                    box_shadow="0 0 8px rgba(0, 180, 218, 0.3)",
                                    border_radius="md",
                                    padding="3px 8px",
                                    align="center",
                                    spacing="1",
                                ),
                                rx.fragment(),
                            ),
                            rx.input(
                                id="ai-search-input",
                                class_name="ai-search-input",
                                placeholder=rx.cond(
                                    AlternativeIntelligenceState.active_skill_badge != "",
                                    AlternativeIntelligenceState.active_skill_infotip,
                                    "Ask Alternative Intelligence...",
                                ),
                                value=AlternativeIntelligenceState.search_query,
                                on_change=AlternativeIntelligenceState.set_search_query,
                                on_key_down=AlternativeIntelligenceState.handle_key_down,
                                disabled=AlternativeIntelligenceState.is_generating,
                                bg="transparent",
                                color="white",
                                border="none",
                                height="38px",
                                padding_x="6px",
                                font_size="13px",
                                flex="1",
                                _focus={"outline": "none"},
                                _placeholder={
                                    "color": "#D4D4D8",
                                    "-webkit-text-fill-color": "#D4D4D8",
                                    "opacity": "1",
                                },
                            ),
                            bg="rgba(24, 24, 28, 0.95)",
                            border="1px solid rgba(255, 255, 255, 0.22)",
                            box_shadow="0 4px 18px rgba(0, 0, 0, 0.45)",
                            border_radius="10px",
                            padding_x="10px",
                            align="center",
                            flex="1",
                            min_height="44px",
                            _focus_within={"border_color": "#00b4da", "box_shadow": "0 0 12px rgba(0, 180, 218, 0.4)"},
                        ),
                        rx.button(
                            rx.cond(
                                AlternativeIntelligenceState.is_generating,
                                rx.spinner(size="1", color="white"),
                                rx.icon("send", size=16, color="white"),
                            ),
                            background="linear-gradient(135deg, #00b4da, #7B2CBF)",
                            color="white",
                            height="44px",
                            width="44px",
                            min_width="44px",
                            margin_right=["44px", "0px", "0px"],
                            border_radius="10px",
                            cursor="pointer",
                            disabled=AlternativeIntelligenceState.is_generating,
                            on_click=AlternativeIntelligenceState.submit_query,
                            _hover={"transform": "scale(1.05)", "box_shadow": "0 0 10px rgba(0, 180, 218, 0.5)"},
                            transition="all 0.15s ease",
                        ),

                        spacing="3",
                        width="100%",
                        align="center",
                    ),
                    width="100%",
                    padding_x=["12px", "16px", "20px"],
                    padding_top="10px",
                    padding_bottom=["calc(12px + env(safe-area-inset-bottom, 0px))", "12px", "14px"],
                    border_top="1px solid rgba(255, 255, 255, 0.12)",
                    background="rgba(17, 17, 19, 0.85)",
                    backdrop_filter="blur(16px)",
                ),

                # Main Panel Styling (Sliding in from Left with ambient glowing rainbow bokeh)
                position="fixed",
                top="0",
                left="0",
                height="100vh",
                width=["100%", "440px", "500px"],
                background="radial-gradient(circle at 10% 12%, rgba(230, 0, 73, 0.08) 0%, transparent 45%), radial-gradient(circle at 85% 20%, rgba(255, 140, 0, 0.07) 0%, transparent 45%), radial-gradient(circle at 15% 75%, rgba(123, 0, 255, 0.08) 0%, transparent 50%), radial-gradient(circle at 85% 85%, rgba(0, 180, 218, 0.08) 0%, transparent 50%), #111113",
                border_right="1px solid #2C2C32",
                box_shadow="10px 0px 35px rgba(0,0,0,0.7)",
                z_index="2000",
                padding="0",
                spacing="0",
                align_items="start",
            ),
            position="relative",
            z_index="1999",
        ),
        rx.fragment(),
    )

