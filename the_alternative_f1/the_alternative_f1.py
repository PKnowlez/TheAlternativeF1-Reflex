"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx
from rxconfig import config

import asyncio
import json
import os
import sqlalchemy
import sqlmodel
from sqlmodel import Field, Relationship, select
from the_alternative_f1.oauth_discord import oauth_discord

class CommentReply(rx.Model, table=True):
    comment_id: int = Field(foreign_key="comment.id")
    username: str
    avatar: str
    text: str
    likes: int = 0
    dislikes: int = 0
    liked_by: list[str] = Field(
        default=[],
        sa_column=sqlalchemy.Column(sqlalchemy.JSON)
    )
    disliked_by: list[str] = Field(
        default=[],
        sa_column=sqlalchemy.Column(sqlalchemy.JSON)
    )
    comment: "Comment" = Relationship(back_populates="replies")

class Comment(rx.Model, table=True):
    article_title: str
    username: str
    avatar: str
    text: str
    likes: int = 0
    dislikes: int = 0
    liked_by: list[str] = Field(
        default=[],
        sa_column=sqlalchemy.Column(sqlalchemy.JSON)
    )
    disliked_by: list[str] = Field(
        default=[],
        sa_column=sqlalchemy.Column(sqlalchemy.JSON)
    )
    replies: list[CommentReply] = Relationship(
        back_populates="comment",
        sa_relationship_kwargs={"lazy": "selectin"}
    )

COMMENTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "comments.json")
DB_INITIALIZED = False

def init_db_from_json():
    # Automatically create tables if they do not exist
    try:
        rx.Model.metadata.create_all(rx.db.engine)
    except Exception as e:
        print(f"Error creating database tables: {e}")

    # If comments.json exists and the database is empty, migrate comments to SQL
    with rx.session() as session:
        try:
            count = len(session.exec(select(Comment)).all())
        except Exception:
            count = 0
        if count == 0 and os.path.exists(COMMENTS_FILE):
            try:
                with open(COMMENTS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Import comments
                for item in data:
                    comment_obj = Comment(
                        article_title=item["article_title"],
                        username=item["username"],
                        avatar=item["avatar"],
                        text=item["text"],
                        likes=item.get("likes", 0),
                        dislikes=item.get("dislikes", 0),
                        liked_by=item.get("liked_by", []),
                        disliked_by=item.get("disliked_by", [])
                    )
                    session.add(comment_obj)
                    session.commit()
                    
                    # Import replies for this comment
                    for r in item.get("replies", []):
                        reply_obj = CommentReply(
                            comment_id=comment_obj.id,
                            username=r["username"],
                            avatar=r["avatar"],
                            text=r["text"],
                            likes=r.get("likes", 0),
                            dislikes=r.get("dislikes", 0),
                            liked_by=r.get("liked_by", []),
                            disliked_by=r.get("disliked_by", [])
                        )
                        session.add(reply_obj)
                    session.commit()
                print("Successfully migrated comments.json to the database.")
            except Exception as e:
                print(f"Error migrating comments.json to database: {e}")
R2_CUSTOM_DOMAIN = os.getenv("R2_CUSTOM_DOMAIN", "https://pknowlez.com").rstrip("/")

def get_current_constructors() -> set:
    return {'Red Bull', 'McLaren', 'Cadillac', 'Haas', 'Williams', 'Audi', 'Ferrari', 'Mercedes'}

from the_alternative_f1.articles import articles
from the_alternative_f1.regulations_settings.Regulations import Regulations as regulations_content
from the_alternative_f1.regulations_settings.Settings import Settings as settings_content
from the_alternative_f1.all_time_stats.ConstructorAllTime import constructor_stats_view
from the_alternative_f1.all_time_stats.DriverAllTime import driver_stats_view
from the_alternative_f1.all_time_stats.RacesAllTime import races_all_time_view
from the_alternative_f1.seasons import seasons, LATEST_SEASON
from the_alternative_f1.seasons.Calculations import Calculations
from the_alternative_f1.seasons.Tab0_LeagueNews import Tab0
from the_alternative_f1.seasons.Tab1_Standings import Tab1
from the_alternative_f1.seasons.Tab2_RaceResults import Tab2
from the_alternative_f1.seasons.Tab3_ConstructorStatistics import Tab3
from the_alternative_f1.seasons.Tab4_DriverStatistics import Tab4
from the_alternative_f1.seasons.Tab5_DriverComparison import Tab5
from the_alternative_f1.seasons.Tab6_RaceSchedule import Tab6

# ── Dynamically derived from seasons __init__.py ─────────────────────────────
NUM_SEASONS: int = LATEST_SEASON
# ─────────────────────────────────────────────────────────────────────────────

def precompute_ticker_items() -> list[list]:
    import pandas as pd
    from the_alternative_f1.seasons import seasons
    from the_alternative_f1.seasons.Calculations import Calculations

    target_season = None
    target_res = None

    # Find the most recent season with at least one race result posted
    for s in reversed(seasons):
        try:
            res = Calculations(s)
            completed = 0
            df = res["df"]
            race_place = res["race_place"]
            for col in race_place:
                if not pd.isnull(df.iloc[0][col]):
                    completed += 1
            if completed > 0:
                target_season = s
                target_res = res
                break
        except Exception:
            pass

    items = []
    if target_res and target_season:
        # A. Constructor Standings (top 3)
        constructor_totals = target_res["constructor_totals"]
        medals = ["🥇", "🥈", "🥉"]
        for idx, (_, row) in enumerate(constructor_totals.head(3).iterrows()):
            items.append([
                "Constructor Standings",
                f"{medals[idx]} {row['Team']}\n({row['Points']} pts)",
                0,
                9
            ])

        # B. Driver Standings (top 3)
        driver_totals = target_res["driver_totals"]
        for idx, (_, row) in enumerate(driver_totals.head(3).iterrows()):
            items.append([
                "Driver Standings",
                f"{medals[idx]} {row['Driver']}\n({row['Points']} pts)",
                1,
                9
            ])

        # C. Most Recent Race Winner
        df = target_res["df"]
        races = target_res["races"]
        race_place = target_res["race_place"]
        last_completed_race_name = None
        last_completed_winner = None
        last_completed_team = None
        for i in reversed(range(len(races))):
            place_col = race_place[i]
            if not pd.isnull(df.iloc[0][place_col]):
                last_completed_race_name = races[i]
                df_sorted = df.sort_values(place_col, ascending=True)
                last_completed_winner = df_sorted["Driver"].iloc[0]
                last_completed_team = df_sorted["Team"].iloc[0]
                break
        if last_completed_race_name:
            items.append([
                f"{last_completed_race_name} Winner",
                f"🏆 {last_completed_winner}\n({last_completed_team})",
                2,
                3
            ])

        # D. Upcoming Race
        upcoming_race_name = None
        upcoming_race_date = None
        current_season = seasons[-1]
        try:
            curr_res = Calculations(current_season)
            sched = curr_res["schedule_df"]
            if "Status" in sched.columns:
                pending = sched[sched["Status"].astype(str).str.lower() != "final"]
                pending = pending[~pending["Race"].str.contains("Post-Season", case=False, na=False)]
                if not pending.empty:
                    upcoming_race_name = pending["Race"].iloc[0]
                    upcoming_race_date = pending["Date"].iloc[0] if "Date" in pending.columns else ""
        except Exception:
            pass

        if not upcoming_race_name:
            try:
                sched = target_res["schedule_df"]
                if "Status" in sched.columns:
                    pending = sched[sched["Status"].astype(str).str.lower() != "final"]
                    pending = pending[~pending["Race"].str.contains("Post-Season", case=False, na=False)]
                    if not pending.empty:
                        upcoming_race_name = pending["Race"].iloc[0]
                        upcoming_race_date = pending["Date"].iloc[0] if "Date" in pending.columns else ""
            except Exception:
                pass

        if upcoming_race_name:
            date_str = f"\n({upcoming_race_date})" if upcoming_race_date else ""
            items.append([
                "Upcoming Race",
                f"📅 {upcoming_race_name}{date_str}",
                3,
                3
            ])
    return items

STATIC_TICKER_ITEMS = precompute_ticker_items()


class State(rx.State):
    """The app state."""
    selected_article_title: str = ""
    active_nav: str = "home"
    selected_reg_tab: str = "regulations"
    selected_stats_tab: str = "constructors"

    # ── Seasons state ────────────────────────────────────────────────────
    selected_season: int = LATEST_SEASON
    selected_season_tab: str = "standings"
    season_picker_open: bool = False
    rookies_only: bool = False
    sprint_only: bool = False

    # ── Power Rankings State ─────────────────────────────────────────────
    show_power_rankings_header: bool = True
    power_rankings_header_phase: str = "animating_in"

    # ── Discord Login State ──────────────────────────────────────────────
    discord_username: str = rx.LocalStorage("", name="discord_username", sync=True)
    discord_avatar: str = rx.LocalStorage("", name="discord_avatar", sync=True)

    # ── Comments State ───────────────────────────────────────────────────
    comments_list: list[Comment] = []
    new_comment_text: str = ""
    active_reply_comment_id: int = -1
    new_reply_text: str = ""
    expanded_comment_ids: list[int] = []

    # ── Articles Expand State ────────────────────────────────────────────
    home_articles_expanded: bool = False
    season_articles_expanded: bool = False

    def expand_home_articles(self):
        self.home_articles_expanded = True

    def expand_season_articles(self):
        self.season_articles_expanded = True

    def set_discord_username(self, username: str):
        self.discord_username = username

    def set_discord_avatar(self, avatar: str):
        self.discord_avatar = avatar

    def set_new_comment_text(self, text: str):
        self.new_comment_text = text

    def set_new_reply_text(self, text: str):
        self.new_reply_text = text

    def login_with_discord(self):
        from the_alternative_f1.oauth_discord import load_env
        load_env()
        client_id = os.getenv("DISCORD_CLIENT_ID", "").strip()
        redirect_uri = os.getenv("DISCORD_REDIRECT_URI", "").strip()

        # Fallback to local mock page if credentials aren't set
        if not client_id or not redirect_uri:
            return rx.call_script("window.open('/oauth/discord', 'Discord Login', 'width=500,height=600')")

        import urllib.parse
        encoded_redirect = urllib.parse.quote(redirect_uri, safe="")
        auth_url = f"https://discord.com/oauth2/authorize?client_id={client_id}&redirect_uri={encoded_redirect}&response_type=code&scope=identify"
        return rx.call_script(f"window.open('{auth_url}', 'Discord Login', 'width=500,height=600')")

    def complete_discord_login(self):
        self.active_nav = "home"
        self.load_comments()

    def logout(self):
        self.discord_username = ""
        self.discord_avatar = ""
        self.active_nav = "home"

    def load_comments(self):
        global DB_INITIALIZED
        if not DB_INITIALIZED:
            init_db_from_json()
            DB_INITIALIZED = True
        
        try:
            with rx.session() as session:
                self.comments_list = session.exec(
                    select(Comment).where(Comment.article_title == self.selected_article_title)
                ).all()
        except Exception as e:
            print(f"Error loading comments: {e}")
            self.comments_list = []


    def add_comment(self):
        if not self.discord_username:
            return
        text = self.new_comment_text.strip()
        if not text:
            return
        
        try:
            with rx.session() as session:
                new_comment = Comment(
                    article_title=self.selected_article_title,
                    username=self.discord_username,
                    avatar=self.discord_avatar,
                    text=text,
                    likes=0,
                    dislikes=0,
                    liked_by=[],
                    disliked_by=[],
                )
                session.add(new_comment)
                session.commit()
        except Exception as e:
            print(f"Error adding comment: {e}")
            
        self.new_comment_text = ""
        self.load_comments()

    def add_reply(self, comment_id: int):
        if not self.discord_username:
            return
        text = self.new_reply_text.strip()
        if not text:
            return
        
        try:
            with rx.session() as session:
                new_reply = CommentReply(
                    comment_id=comment_id,
                    username=self.discord_username,
                    avatar=self.discord_avatar,
                    text=text,
                    likes=0,
                    dislikes=0,
                    liked_by=[],
                    disliked_by=[],
                )
                session.add(new_reply)
                session.commit()
                
                if comment_id not in self.expanded_comment_ids:
                    self.expanded_comment_ids.append(comment_id)
        except Exception as e:
            print(f"Error adding reply: {e}")
                
        self.new_reply_text = ""
        self.active_reply_comment_id = -1
        self.load_comments()

    def like_comment(self, comment_id: int, reply_id: int = None):
        if not self.discord_username:
            return
        user = self.discord_username
        
        try:
            with rx.session() as session:
                if reply_id is None:
                    c = session.exec(select(Comment).where(Comment.id == comment_id)).first()
                    if c:
                        liked = list(c.liked_by)
                        disliked = list(c.disliked_by)
                        if user in liked:
                            liked.remove(user)
                        else:
                            if user in disliked:
                                disliked.remove(user)
                            liked.append(user)
                        c.liked_by = liked
                        c.disliked_by = disliked
                        c.likes = len(liked)
                        c.dislikes = len(disliked)
                        session.add(c)
                        session.commit()
                else:
                    r = session.exec(select(CommentReply).where(CommentReply.id == reply_id)).first()
                    if r:
                        liked = list(r.liked_by)
                        disliked = list(r.disliked_by)
                        if user in liked:
                            liked.remove(user)
                        else:
                            if user in disliked:
                                disliked.remove(user)
                            liked.append(user)
                        r.liked_by = liked
                        r.disliked_by = disliked
                        r.likes = len(liked)
                        r.dislikes = len(disliked)
                        session.add(r)
                        session.commit()
        except Exception as e:
            print(f"Error liking comment/reply: {e}")
                    
        self.load_comments()

    def dislike_comment(self, comment_id: int, reply_id: int = None):
        if not self.discord_username:
            return
        user = self.discord_username
        
        try:
            with rx.session() as session:
                if reply_id is None:
                    c = session.exec(select(Comment).where(Comment.id == comment_id)).first()
                    if c:
                        liked = list(c.liked_by)
                        disliked = list(c.disliked_by)
                        if user in disliked:
                            disliked.remove(user)
                        else:
                            if user in liked:
                                liked.remove(user)
                            disliked.append(user)
                        c.liked_by = liked
                        c.disliked_by = disliked
                        c.likes = len(liked)
                        c.dislikes = len(disliked)
                        session.add(c)
                        session.commit()
                else:
                    r = session.exec(select(CommentReply).where(CommentReply.id == reply_id)).first()
                    if r:
                        liked = list(r.liked_by)
                        disliked = list(r.disliked_by)
                        if user in disliked:
                            disliked.remove(user)
                        else:
                            if user in liked:
                                liked.remove(user)
                            disliked.append(user)
                        r.liked_by = liked
                        r.disliked_by = disliked
                        r.likes = len(liked)
                        r.dislikes = len(disliked)
                        session.add(r)
                        session.commit()
        except Exception as e:
            print(f"Error disliking comment/reply: {e}")
                    
        self.load_comments()

    def toggle_replies(self, comment_id: int):
        if comment_id in self.expanded_comment_ids:
            self.expanded_comment_ids.remove(comment_id)
        else:
            self.expanded_comment_ids.append(comment_id)

    def set_active_reply_comment_id(self, comment_id: int):
        if self.active_reply_comment_id == comment_id:
            self.active_reply_comment_id = -1
        else:
            self.active_reply_comment_id = comment_id
        self.new_reply_text = ""


    def select_article(self, title: str):
        self.selected_article_title = title
        self.load_comments()

    def set_nav(self, nav_name: str):
        self.active_nav = nav_name
        self.selected_article_title = ""
        self.home_articles_expanded = False
        self.season_articles_expanded = False
        if nav_name == "regulations":
            self.selected_reg_tab = "regulations"
        if nav_name == "stats":
            self.selected_stats_tab = "constructors"
        if nav_name == "seasons":
            self.selected_season_tab = "standings"
            self.rookies_only = False
            self.sprint_only = False

    def set_reg_tab(self, tab_name: str):
        self.selected_reg_tab = tab_name

    def set_stats_tab(self, tab_name: str):
        self.selected_stats_tab = tab_name

    def set_season(self, season_num: int):
        self.selected_season = season_num
        self.season_picker_open = False
        self.season_articles_expanded = False
        if season_num in [1, 2]:
            self.sprint_only = False

    def set_season_tab(self, tab_name: str):
        self.selected_season_tab = tab_name

    def toggle_season_picker(self):
        self.season_picker_open = not self.season_picker_open

    def toggle_rookies_only(self, value: bool):
        self.rookies_only = value

    def toggle_sprint_only(self, value: bool):
        self.sprint_only = value

    def go_home(self):
        self.active_nav = "home"
        self.selected_article_title = ""
        self.home_articles_expanded = False
        self.season_articles_expanded = False

    # ── Ticker State ─────────────────────────────────────────────────────
    ticker_index: int = 0
    ticker_items: list[list] = STATIC_TICKER_ITEMS
    ticker_initialized: bool = False
    ticker_loop_running: bool = False

    @rx.var
    def ticker_header(self) -> str:
        if self.ticker_items and self.ticker_index < len(self.ticker_items):
            return self.ticker_items[self.ticker_index][0]
        return ""

    @rx.var
    def ticker_data(self) -> str:
        if self.ticker_items and self.ticker_index < len(self.ticker_items):
            return self.ticker_items[self.ticker_index][1]
        return ""

    @rx.var
    def major_index(self) -> int:
        if self.ticker_items and self.ticker_index < len(self.ticker_items):
            return self.ticker_items[self.ticker_index][2]
        return 0

    @rx.var
    def header_animation_duration(self) -> str:
        if self.ticker_items and self.ticker_index < len(self.ticker_items):
            return f"{self.ticker_items[self.ticker_index][3]}s"
        return "3s"

    @rx.var(auto_deps=False, deps=[])
    def latest_power_rankings_header(self) -> list[dict]:
        from the_alternative_f1.seasons.power_rankings import load_power_rankings
        from the_alternative_f1.seasons import LATEST_SEASON, seasons
        
        pr = load_power_rankings(LATEST_SEASON)
        races = pr.get("races", [])
        rankings = pr.get("rankings", {})
        
        teams = []
        if races and len(races) > 1:
            latest_race = races[-1]
            teams = rankings.get(latest_race, [])
        else:
            if "Preseason" in rankings:
                teams = rankings["Preseason"]
            else:
                latest_s = seasons[-1]
                teams = sorted(list(latest_s["team_colors"].keys()))
        
        current_constructors = get_current_constructors()
        teams = [t for t in teams if t in current_constructors]
        
        result = []
        n_teams = len(teams)
        for idx, team in enumerate(teams):
            delay = 0.5 + idx * 0.15
            offset = "-0.5vh" if idx % 2 == 0 else "0.5vh"
            result.append({
                "team": team,
                "index": idx,
                "delay": f"{delay:.2f}s, calc({delay:.2f}s + 1.5s)",
                "offset": offset,
                "icon": f"{R2_CUSTOM_DOMAIN}/Power Rankings/Car Icons/Icon_{team.replace(' ', '')}.png"
            })
        return result

    def _get_svg_raw_data(self) -> dict:
        from the_alternative_f1.seasons.power_rankings import load_power_rankings
        from the_alternative_f1.seasons import seasons
        
        pr = load_power_rankings(self.selected_season)
        races = pr.get("races", [])
        rankings = pr.get("rankings", {})
        
        season_dict = None
        for s in seasons:
            if s["season_number"] == self.selected_season:
                season_dict = s
                break
        
        if not season_dict or not races:
            return {"races": [], "paths": [], "y_labels": [], "view_box": "0 0 1000 500"}
            
        current_constructors = get_current_constructors()
        team_colors = season_dict.get("team_colors", {})
        latest_season_dict = seasons[-1]
        latest_team_colors = latest_season_dict.get("team_colors", {})
        teams = [t for t in latest_team_colors.keys() if t in current_constructors]
        
        M = len(races)
        N = len(teams)
        
        view_w, view_h = 1000, 500
        margin_l, margin_r = 100, 100
        margin_t, margin_b = 40, 50
        chart_w = view_w - margin_l - margin_r
        chart_h = view_h - margin_t - margin_b
        
        dx = chart_w / (M - 1) if M > 1 else chart_w
        dy = chart_h / (N - 1) if N > 1 else chart_h
        
        x_coords = [margin_l + i * dx for i in range(M)]
        
        paths = []
        for team in teams:
            points = []
            for i, race_name in enumerate(races):
                race_rankings = rankings.get(race_name, [])
                filtered_rankings = [t for t in race_rankings if t in current_constructors]
                if team in filtered_rankings:
                    rank_idx = filtered_rankings.index(team)
                    y = margin_t + rank_idx * dy
                    points.append((x_coords[i], y))
            
            if points:
                path_str = f"M {points[0][0]:.1f} {points[0][1]:.1f} " + " ".join([f"L {p[0]:.1f} {p[1]:.1f}" for p in points[1:]])
                leading_x, leading_y = points[-1]
                
                paths.append({
                    "team": team,
                    "color": team_colors.get(team) or latest_team_colors.get(team, "#555555"),
                    "path_string": path_str,
                    "leading_x": leading_x,
                    "leading_y": leading_y,
                    "icon": f"{R2_CUSTOM_DOMAIN}/Power Rankings/Car Icons/Icon_{team.replace(' ', '')}.png"
                })
                
        x_labels = [{"name": race_name, "x": x_coords[i]} for i, race_name in enumerate(races)]
        y_labels = [{"rank": r + 1, "y": margin_t + r * dy} for r in range(N)]
        
        return {
            "races": x_labels,
            "paths": paths,
            "y_labels": y_labels,
            "view_box": f"0 0 {view_w} {view_h}"
        }

    @rx.var(auto_deps=False, deps=["selected_season"])
    def power_rankings_races(self) -> list[dict]:
        return self._get_svg_raw_data()["races"]

    @rx.var(auto_deps=False, deps=["selected_season"])
    def power_rankings_paths(self) -> list[dict]:
        return self._get_svg_raw_data()["paths"]

    @rx.var(auto_deps=False, deps=["selected_season"])
    def power_rankings_y_labels(self) -> list[dict]:
        return self._get_svg_raw_data()["y_labels"]

    @rx.var(auto_deps=False, deps=["selected_season"])
    def power_rankings_view_box(self) -> str:
        return self._get_svg_raw_data()["view_box"]

    @rx.var(auto_deps=False, deps=["selected_season"])
    def power_rankings_list_data(self) -> list[dict]:
        from the_alternative_f1.seasons.power_rankings import load_power_rankings
        
        pr = load_power_rankings(self.selected_season)
        races = pr.get("races", [])
        rankings = pr.get("rankings", {})
        
        if not races:
            return []
            
        current_constructors = get_current_constructors()
        latest_race = races[-1]
        latest_ranking = rankings.get(latest_race, [])
        latest_ranking = [t for t in latest_ranking if t in current_constructors]
        
        prev_ranking = []
        if len(races) > 1:
            prev_race = races[-2]
            prev_ranking = rankings.get(prev_race, [])
            prev_ranking = [t for t in prev_ranking if t in current_constructors]
            
        result = []
        for idx, team in enumerate(latest_ranking):
            rank = idx + 1
            change_str = "▬"
            change_color = "#888888"
            
            if prev_ranking and team in prev_ranking:
                prev_idx = prev_ranking.index(team)
                prev_rank = prev_idx + 1
                change = prev_rank - rank
                if change > 0:
                    change_str = f"▲ +{change}"
                    change_color = "#30d158"
                elif change < 0:
                    change_str = f"▼ {change}"
                    change_color = "#ff453a"
                    
            result.append({
                "rank": rank,
                "team": team,
                "change": change_str,
                "change_color": change_color,
                "icon": f"{R2_CUSTOM_DOMAIN}/Power Rankings/Car Icons/Icon_{team.replace(' ', '')}.png"
            })
        return result

    @rx.event(background=True)
    async def on_app_mount(self):
        yield State.start_ticker_loop
        while True:
            async with self:
                self.show_power_rankings_header = True
                self.power_rankings_header_phase = "animating_in"
            
            await asyncio.sleep(8.05)
            
            async with self:
                self.power_rankings_header_phase = "animating_out"
                
            await asyncio.sleep(0.5)
            
            async with self:
                self.show_power_rankings_header = False
                
            await asyncio.sleep(90.0)

    def go_to_power_rankings(self):
        self.active_nav = "power_rankings"
        self.selected_article_title = ""
        self.show_power_rankings_header = False

    def initialize_ticker(self):
        if self.ticker_initialized:
            return
        
        import pandas as pd
        from the_alternative_f1.seasons import seasons
        from the_alternative_f1.seasons.Calculations import Calculations

        target_season = None
        target_res = None

        # Find the most recent season with at least one race result posted
        for s in reversed(seasons):
            try:
                res = Calculations(s)
                completed = 0
                df = res["df"]
                race_place = res["race_place"]
                for col in race_place:
                    if not pd.isnull(df.iloc[0][col]):
                        completed += 1
                if completed > 0:
                    target_season = s
                    target_res = res
                    break
            except Exception as e:
                # Silently ignore or log error
                print(f"Error checking season: {e}")

        items = []

        if target_res and target_season:
            # A. Constructor Standings (top 3)
            constructor_totals = target_res["constructor_totals"]
            medals = ["🥇", "🥈", "🥉"]
            for idx, (_, row) in enumerate(constructor_totals.head(3).iterrows()):
                team_name = row["Team"]
                pts = row["Points"]
                medal = medals[idx] if idx < len(medals) else ""
                items.append([
                    "Constructor Standings",
                    f"{medal} {team_name}\n({pts} pts)",
                    0,
                    9
                ])

            # B. Driver Standings (top 3)
            driver_totals = target_res["driver_totals"]
            for idx, (_, row) in enumerate(driver_totals.head(3).iterrows()):
                driver_name = row["Driver"]
                pts = row["Points"]
                medal = medals[idx] if idx < len(medals) else ""
                items.append([
                    "Driver Standings",
                    f"{medal} {driver_name}\n({pts} pts)",
                    1,
                    9
                ])

            # C. Most Recent Race Winner
            df = target_res["df"]
            races = target_res["races"]
            race_place = target_res["race_place"]
            
            last_completed_race_name = None
            last_completed_winner = None
            last_completed_team = None
            
            for i in reversed(range(len(races))):
                place_col = race_place[i]
                if not pd.isnull(df.iloc[0][place_col]):
                    last_completed_race_name = races[i]
                    df_sorted = df.sort_values(place_col, ascending=True)
                    last_completed_winner = df_sorted["Driver"].iloc[0]
                    last_completed_team = df_sorted["Team"].iloc[0]
                    break
            
            if last_completed_race_name:
                items.append([
                    f"{last_completed_race_name} Winner",
                    f"🏆 {last_completed_winner}\n({last_completed_team})",
                    2,
                    3
                ])

            # D. Upcoming Race from current season or target season
            upcoming_race_name = None
            upcoming_race_date = None

            current_season = seasons[-1]
            try:
                curr_res = Calculations(current_season)
                sched = curr_res["schedule_df"]
                if "Status" in sched.columns:
                    pending = sched[sched["Status"].astype(str).str.lower() != "final"]
                    pending = pending[~pending["Race"].str.contains("Post-Season", case=False, na=False)]
                    if not pending.empty:
                        upcoming_race_name = pending["Race"].iloc[0]
                        upcoming_race_date = pending["Date"].iloc[0] if "Date" in pending.columns else ""
            except Exception as e:
                print(f"Error checking current season schedule: {e}")

            if not upcoming_race_name:
                try:
                    sched = target_res["schedule_df"]
                    if "Status" in sched.columns:
                        pending = sched[sched["Status"].astype(str).str.lower() != "final"]
                        pending = pending[~pending["Race"].str.contains("Post-Season", case=False, na=False)]
                        if not pending.empty:
                            upcoming_race_name = pending["Race"].iloc[0]
                            upcoming_race_date = pending["Date"].iloc[0] if "Date" in pending.columns else ""
                except Exception:
                    pass

            if upcoming_race_name:
                date_str = f"\n({upcoming_race_date})" if upcoming_race_date else ""
                items.append([
                    "Upcoming Race",
                    f"📅 {upcoming_race_name}{date_str}",
                    3,
                    3
                ])
        
        self.ticker_items = items
        self.ticker_initialized = True

    @rx.event(background=True)
    async def start_ticker_loop(self):
        async with self:
            if self.ticker_loop_running:
                return
            self.ticker_loop_running = True
            if not self.ticker_items:
                self.initialize_ticker()
        
        try:
            while True:
                await asyncio.sleep(3)
                async with self:
                    if self.ticker_items:
                        self.ticker_index = (self.ticker_index + 1) % len(self.ticker_items)
        finally:
            async with self:
                self.ticker_loop_running = False


def header_ticker() -> rx.Component:
    """The sliding header ticker component."""
    return rx.vstack(
        rx.text(
            State.ticker_header,
            font_size=["7px", "8px", "9px"],
            color="#00b4da",
            font_weight="bold",
            text_transform="uppercase",
            letter_spacing="1px",
            margin="0",
            key=State.major_index,
            class_name="major-header-fade",
            style={"animationDuration": State.header_animation_duration},
        ),
        rx.text(
            State.ticker_data,
            font_size=["10px", "11px", "13px"],
            color="white",
            font_weight="600",
            margin="0",
            white_space="nowrap",
            key=State.ticker_index,
            class_name="ticker-data-fade",
        ),
        spacing="0",
        align_items="end",
    )


def power_rankings_starting_grid() -> rx.Component:
    """The animated starting grid showing constructor cars in power ranking order."""
    def render_grid_spot(item: dict) -> rx.Component:
        return rx.box(
            # Grid Box image
            rx.image(
                src=f"{R2_CUSTOM_DOMAIN}/Power Rankings/Car Icons/Icon_GridBox.png",
                width=["6.4vh", "8.8vh", "11.2vh"],
                height=["4vh", "5.5vh", "7vh"],
                object_fit="contain",
                opacity=0.6,
                display="block",
            ),
            # Car icon overlay
            rx.image(
                src=item["icon"],
                width=["5.6vh", "8.0vh", "10.15vh"],
                height=["3.2vh", "4.6vh", "5.8vh"],
                object_fit="contain",
                position="absolute",
                top=["0.4vh", "0.45vh", "0.6vh"],
                left=["0.4vh", "0.6vh", "0.8vh"],
                class_name="car-drive-in",
                style={"animationDelay": item["delay"]},
            ),
            position="relative",
            height=["4vh", "5.5vh", "7vh"],
            margin_top=item["offset"],
            margin_x=["0px", "1px", "2px"],
        )

    return rx.hstack(
        # Finish line
        rx.image(
            src=f"{R2_CUSTOM_DOMAIN}/Power Rankings/Car Icons/Icon_FinishLine.png",
            height=["5vh", "6.5vh", "8vh"],
            width="auto",
            object_fit="contain",
            margin_right=["2px", "4px", "6px"],
        ),
        # Constructor cars
        rx.foreach(
            State.latest_power_rankings_header,
            render_grid_spot
        ),

        class_name=rx.cond(
            State.power_rankings_header_phase == "animating_out",
            "header-animate-out",
            ""
        ),
        spacing={"initial": "1", "sm": "2", "md": "3"},
        align_items="center",
        justify="end",
        height="100%",
        padding_right="5%",
        style={"overflow": "visible"},
    )


def header() -> rx.Component:
    """The permanent header (8% height) with the logo."""
    return rx.hstack(
        # Left-aligned Logo
        rx.image(
            src="/The Alternative F1 NEW Logo.png",
            height=["4vh", "5vh", "5.6vh"],
            object_fit="contain",
            cursor="pointer",
            on_click=State.go_home,
        ),
        rx.spacer(),
        # Right-aligned content: animated starting grid on load, otherwise ticker
        rx.cond(
            State.show_power_rankings_header,
            power_rankings_starting_grid(),
            rx.cond(
                State.ticker_items,
                header_ticker(),
                rx.fragment(),
            ),
        ),
        width="100%",
        height="8vh",
        bg="black",
        border_bottom="1px solid #222222",
        position="sticky",
        top="0",
        z_index="100",
        align_items="center",
        padding_left="2.5%",
        padding_right="2.5%",
    )


def article_card(article: dict) -> rx.Component:
    """A card showcasing an article."""
    return rx.box(
        rx.vstack(
            rx.image(
                src=article["image"],
                width="100%",
                height="180px",
                object_fit="cover",
            ),
            rx.vstack(
                rx.text(
                    article["date"],
                    font_size="10px",
                    color="#00b4da",
                    font_weight="bold",
                    text_transform="uppercase",
                ),
                rx.heading(
                    article["title"],
                    size="4",
                    color="white",
                    font_family="Outfit",
                    font_weight="700",
                ),
                rx.text(
                    article["blurb"],
                    font_size="sm",
                    color="#CCCCCC",
                ),
                rx.hstack(
                    rx.text(
                        f"By {article['author']}",
                        font_size="xs",
                        color="#888888",
                    ),
                    rx.spacer(),
                    rx.text(
                        "Read Article →",
                        font_size="xs",
                        color="#00b4da",
                        font_weight="bold",
                    ),
                    width="100%",
                    align="center",
                ),
                spacing="2",
                align_items="start",
                padding="5%",
            ),
            spacing="0",
        ),
        bg="#18181C",
        border_radius="xl",
        box_shadow="0 4px 20px rgba(0, 0, 0, 0.3)",
        border="1px solid #2C2C32",
        overflow="hidden",
        width="100%",
        max_width="360px",
        margin_top="1%",
        margin_bottom="1%",
        cursor="pointer",
        on_click=lambda: State.select_article(article["title"]),
        _hover={
            "transform": "translateY(-6px)",
            "box_shadow": "0 10px 25px rgba(0, 180, 218, 0.3)",
            "border_color": "#00b4da",
        },
        transition="all 0.25s ease-in-out",
    )


def articles_list() -> rx.Component:
    """List of all article cards."""
    first_six = articles[:6]
    remaining = articles[6:]
    return rx.vstack(
        rx.vstack(
            rx.heading("League News", size="7", color="white", font_weight="900", padding_top="2.5%", padding_bottom="0%", padding_x="2%"),
            rx.text(
                "Click below to have our intern obliterate your self-esteem senselessly.",
                color="#AAAAAA",
                font_size="sm",
                padding_x="2%",
                padding_bottom="8"
            ),
            align_items="start",
            spacing="1",
            width="100%",
            max_width="1200px",
            padding_bottom="2",
        ),
        rx.flex(
            *[article_card(art) for art in first_six],
            rx.cond(
                ~State.home_articles_expanded,
                rx.center(
                    rx.button(
                        "Load More Articles",
                        on_click=State.expand_home_articles,
                        bg="#18181C",
                        color="#00b4da",
                        border="1px solid #00b4da",
                        padding_x="6",
                        padding_y="4",
                        border_radius="xl",
                        cursor="pointer",
                        _hover={
                            "bg": "#00b4da",
                            "color": "white",
                            "box_shadow": "0 0 15px rgba(0, 180, 218, 0.4)",
                            "transform": "scale(1.02)",
                        },
                        transition="all 0.25s ease-in-out",
                    ),
                    width="100%",
                    margin_top="4",
                    margin_bottom="120px",
                ),
                rx.fragment()
            ) if len(articles) > 6 else rx.fragment(),
            *[
                rx.cond(
                    State.home_articles_expanded,
                    article_card(art),
                    rx.fragment()
                )
                for art in remaining
            ],
            flex_wrap="wrap",
            justify="center",
            column_gap="4%",
            row_gap="2%",
            width="100%",
            max_width="1200px",
        ),
        width="100%",
        align="center",
        padding_bottom="160px",
    )
def comment_card(comment: Comment) -> rx.Component:
    """An individual comment card containing its text, actions, and replies."""
    
    def render_reply_item(reply: CommentReply) -> rx.Component:
        return rx.hstack(
            rx.avatar(
                src=reply.avatar,
                size="2",
                fallback="U",
                bg="#5865F2",
            ),
            rx.vstack(
                rx.hstack(
                    rx.text(reply.username, color="white", font_weight="bold", font_size="xs"),
                    spacing="2",
                    align="center",
                ),
                rx.text(reply.text, color="#CCCCCC", font_size="xs"),
                rx.hstack(
                    rx.button(
                        rx.hstack(
                            rx.icon("thumbs-up", size=12),
                            rx.text(reply.likes, font_size="10px"),
                            spacing="1",
                        ),
                        size="1",
                        variant="ghost",
                        color=rx.cond(reply.liked_by.contains(State.discord_username), "#00b4da", "#888888"),
                        on_click=lambda: State.like_comment(comment.id, reply.id),
                        cursor="pointer",
                    ),
                    rx.button(
                        rx.hstack(
                            rx.icon("thumbs-down", size=12),
                            rx.text(reply.dislikes, font_size="10px"),
                            spacing="1",
                        ),
                        size="1",
                        variant="ghost",
                        color=rx.cond(reply.disliked_by.contains(State.discord_username), "#FF4B4B", "#888888"),
                        on_click=lambda: State.dislike_comment(comment.id, reply.id),
                        cursor="pointer",
                    ),
                    spacing="2",
                    align="center",
                    margin_top="1",
                ),
                spacing="1",
                align_items="start",
                width="100%",
            ),
            spacing="3",
            align_items="start",
            padding_left="4",
            border_left="2px solid #2C2C32",
            width="100%",
            margin_y="2",
        )

    return rx.vstack(
        # Comment Header (User Info)
        rx.hstack(
            rx.avatar(
                src=comment.avatar,
                size="3",
                fallback="U",
                bg="#5865F2",
            ),
            rx.vstack(
                rx.text(comment.username, color="white", font_weight="bold", font_size="sm"),
                spacing="1",
                align_items="start",
            ),
            spacing="3",
            align="center",
            width="100%",
        ),

        # Comment Text
        rx.text(
            comment.text,
            color="#E0E0E0",
            font_size="sm",
            line_height="1.5",
            margin_top="2",
            width="100%",
        ),

        # Actions (Like, Dislike, Reply)
        rx.hstack(
            rx.button(
                rx.hstack(
                    rx.icon("thumbs-up", size=14),
                    rx.text(comment.likes, font_size="12px"),
                    spacing="1",
                ),
                size="1",
                variant="ghost",
                color=rx.cond(comment.liked_by.contains(State.discord_username), "#00b4da", "#888888"),
                on_click=lambda: State.like_comment(comment.id),
                cursor="pointer",
            ),
            rx.button(
                rx.hstack(
                    rx.icon("thumbs-down", size=14),
                    rx.text(comment.dislikes, font_size="12px"),
                    spacing="1",
                ),
                size="1",
                variant="ghost",
                color=rx.cond(comment.disliked_by.contains(State.discord_username), "#FF4B4B", "#888888"),
                on_click=lambda: State.dislike_comment(comment.id),
                cursor="pointer",
            ),
            rx.cond(
                State.discord_username != "",
                rx.button(
                    rx.hstack(
                        rx.icon("reply", size=14),
                        rx.text("Reply", font_size="12px"),
                        spacing="1",
                    ),
                    size="1",
                    variant="ghost",
                    color="#888888",
                    on_click=lambda: State.set_active_reply_comment_id(comment.id),
                    cursor="pointer",
                ),
                rx.fragment()
            ),
            spacing="4",
            align="center",
            margin_top="3",
            margin_bottom="2",
        ),

        # Reply input field (rendered if active_reply_comment_id matches this comment)
        rx.cond(
            State.active_reply_comment_id == comment.id,
            rx.vstack(
                rx.text_area(
                    placeholder=f"Reply to {comment.username}...",
                    value=State.new_reply_text,
                    on_change=State.set_new_reply_text,
                    width="100%",
                    bg="#202225",
                    border="1px solid #2C2C32",
                    color="white",
                    height="80px",
                ),
                rx.hstack(
                    rx.spacer(),
                    rx.button(
                        "Cancel",
                        size="1",
                        variant="ghost",
                        color="white",
                        on_click=lambda: State.set_active_reply_comment_id(""),
                        cursor="pointer",
                    ),
                    rx.button(
                        "Reply",
                        size="1",
                        bg="#00b4da",
                        color="white",
                        on_click=lambda: State.add_reply(comment.id),
                        cursor="pointer",
                    ),
                    spacing="2",
                    width="100%",
                ),
                width="100%",
                spacing="2",
                padding_top="2",
                border_top="1px solid #2C2C32",
            ),
            rx.fragment()
        ),

        # Replies Container (with collapse/expand logic)
        rx.cond(
            comment.replies.length() > 1,
            rx.cond(
                State.expanded_comment_ids.contains(comment.id),
                rx.vstack(
                    rx.button(
                        "Collapse Replies",
                        size="1",
                        variant="ghost",
                        color="#00b4da",
                        on_click=lambda: State.toggle_replies(comment.id),
                        cursor="pointer",
                        margin_bottom="2",
                    ),
                    rx.foreach(
                        comment.replies,
                        render_reply_item
                    ),
                    width="100%",
                    align_items="start",
                ),
                rx.button(
                    f"+{comment.replies.length()} Replies",
                    size="1",
                    bg="#202225",
                    color="#00b4da",
                    border="1px solid #2C2C32",
                    on_click=lambda: State.toggle_replies(comment.id),
                    _hover={"bg": "#00b4da", "color": "white"},
                    cursor="pointer",
                    margin_top="2",
                ),
            ),
            rx.cond(
                comment.replies.length() == 1,
                rx.foreach(
                    comment.replies,
                    render_reply_item
                ),
                rx.fragment()
            )
        ),

        width="100%",
        bg="#18181C",
        border="1px solid #2C2C32",
        padding="2%",
        border_radius="xl",
        align_items="start",
        spacing="2",
    )


def comments_section() -> rx.Component:
    """The comments section container below the article."""
    return rx.vstack(
        rx.divider(border_color="#2C2C32", margin_y="6"),
        rx.heading("Discussion", size="5", color="white", font_weight="800", margin_bottom="4"),
        
        # New comment input
        rx.cond(
            State.discord_username == "",
            # Prompt to login
            rx.hstack(
                rx.text("You must be logged in to comment.", color="#AAAAAA", font_size="sm"),
                rx.button(
                    "Login with Discord",
                    bg="#5865F2",
                    color="white",
                    size="2",
                    on_click=State.login_with_discord,
                    cursor="pointer",
                ),
                bg="#18181C",
                border="1px solid #2C2C32",
                padding="4",
                border_radius="lg",
                width="100%",
                align="center",
                justify="between",
                margin_bottom="4",
            ),
            # Input to submit comment
            rx.vstack(
                rx.hstack(
                    rx.avatar(
                        src=State.discord_avatar,
                        size="2",
                        fallback="U",
                        bg="#5865F2",
                    ),
                    rx.text(f"Commenting as {State.discord_username}", color="white", font_size="sm", font_weight="bold"),
                    spacing="2",
                    align="center",
                ),
                rx.text_area(
                    placeholder="Join the discussion...",
                    value=State.new_comment_text,
                    on_change=State.set_new_comment_text,
                    width="100%",
                    bg="#18181C",
                    border="1px solid #2C2C32",
                    color="white",
                    height="100px",
                ),
                rx.button(
                    "Submit Comment",
                    bg="#00b4da",
                    color="white",
                    on_click=State.add_comment,
                    align_self="end",
                    _hover={"bg": "#009bbd"},
                    cursor="pointer",
                ),
                spacing="3",
                width="100%",
                bg="#18181C",
                border="1px solid #2C2C32",
                padding="4",
                border_radius="lg",
                margin_bottom="6",
            )
        ),
        
        # List of comment cards
        rx.cond(
            State.comments_list.length() > 0,
            rx.vstack(
                rx.foreach(State.comments_list, comment_card),
                width="100%",
                spacing="4",
            ),
            rx.text("No comments yet. Start the conversation!", color="#888888", font_size="sm", text_align="center", width="100%", padding_y="8")
        ),
        
        width="100%",
        align_items="start",
        padding_x=["2%", "2%", "0px"],
    )


def article_detail() -> rx.Component:
    """The detailed article reading view."""
    def build_reader(article: dict) -> rx.Component:
        return rx.vstack(
            rx.image(
                src=article["image"],
                width="100%",
                height=["200px", "350px", "400px"],
                object_fit="cover",
                border_radius="xl",
                box_shadow="0 8px 30px rgba(0,0,0,0.5)",
                margin_x="0px",
                class_name="portrait-border-to-border",
            ),
            rx.vstack(
                rx.hstack(
                    rx.badge(article["date"], color_scheme="cyan", variant="solid"),
                    rx.text(f"Written by {article['author']}", color="#888888", font_size="sm"),
                    spacing="4",
                    margin_top="4",
                ),
                rx.heading(
                    article["title"],
                    size="7",
                    color="white",
                    font_weight="900",
                    margin_y="4",
                    line_height="1.2",
                ),
                rx.vstack(
                    *[
                        para if isinstance(para, rx.Component) else rx.text(
                            para,
                            color="#E0E0E0",
                            font_size="md",
                            line_height="1.7",
                            margin_bottom="4",
                        )
                        for para in article["content"]
                    ],
                    align_items="start",
                    width="100%",
                ),
                align_items="start",
                width="100%",
                padding_x=["2%", "2%", "0px"],
            ),
            comments_section(),
            width="100%",
            max_width="800px",
            align_items="start",
            margin_x="auto",
            margin_bottom="160px",
            spacing="6",
        )

    # Combine global articles and all season-specific articles to build the full search list
    all_articles = list(articles)
    for s in seasons:
        for art in s.get("articles", []):
            if art not in all_articles:
                all_articles.append(art)

    # Rewrite all article R2 asset paths dynamically to use the custom domain
    from the_alternative_f1.articles.components import rewrite_r2_url, rewrite_paths_in_component
    for art in all_articles:
        if "image" in art and isinstance(art["image"], str):
            art["image"] = rewrite_r2_url(art["image"])
        if "content" in art and isinstance(art["content"], list):
            for item in art["content"]:
                if isinstance(item, rx.Component):
                    rewrite_paths_in_component(item)

    # Build the conditional chain dynamically based on the full list of articles
    cond_chain = rx.text("Article not found", color="white")
    for article in reversed(all_articles):
        cond_chain = rx.cond(
            State.selected_article_title == article["title"],
            build_reader(article),
            cond_chain,
        )

    return rx.box(
        cond_chain,
        width="100%",
    )


def stats_view() -> rx.Component:
    """All Time Stats view with sidebar tabs for Constructors, Drivers, and Races."""
    return rx.hstack(
        # Sidebar with vertical buck-tooth tabs on the left
        rx.vstack(
            # Constructors Tab
            rx.button(
                "CONSTRUCTORS",
                bg=rx.cond(State.selected_stats_tab == "constructors", "#00b4da", "#18181C"),
                color="white",
                font_size="10px",
                font_weight="bold",
                width="26px",
                height="130px",
                style={"writingMode": "vertical-rl"},
                border_radius="0px 8px 8px 0px",
                border="1px solid #2D2D32",
                border_left="none",
                on_click=lambda: State.set_stats_tab("constructors"),
                _hover={"bg": "#00b4da", "transform": "scaleX(1.05)"},
                cursor="pointer",
                padding="0",
            ),
            # Drivers Tab
            rx.button(
                "DRIVERS",
                bg=rx.cond(State.selected_stats_tab == "drivers", "#00b4da", "#18181C"),
                color="white",
                font_size="10px",
                font_weight="bold",
                width="26px",
                height="130px",
                style={"writingMode": "vertical-rl"},
                border_radius="0px 8px 8px 0px",
                border="1px solid #2D2D32",
                border_left="none",
                on_click=lambda: State.set_stats_tab("drivers"),
                _hover={"bg": "#00b4da", "transform": "scaleX(1.05)"},
                cursor="pointer",
                padding="0",
            ),
            # Races Tab
            rx.button(
                "RACES",
                bg=rx.cond(State.selected_stats_tab == "races", "#00b4da", "#18181C"),
                color="white",
                font_size="10px",
                font_weight="bold",
                width="26px",
                height="130px",
                style={"writingMode": "vertical-rl"},
                border_radius="0px 8px 8px 0px",
                border="1px solid #2D2D32",
                border_left="none",
                on_click=lambda: State.set_stats_tab("races"),
                _hover={"bg": "#00b4da", "transform": "scaleX(1.05)"},
                cursor="pointer",
                padding="0",
            ),
            spacing="3",
            align_items="start",
            padding_top="8",
            position="fixed",
            left="0",
            top="12vh",
            z_index="99",
        ),
        # Content Display Area
        rx.box(
            rx.cond(
                State.selected_stats_tab == "constructors",
                constructor_stats_view(NUM_SEASONS),
                rx.cond(
                    State.selected_stats_tab == "drivers",
                    driver_stats_view(NUM_SEASONS),
                    races_all_time_view(NUM_SEASONS),
                ),
            ),
            width="100%",
            padding_left=["31px", "44px", "56px"],
            padding_right=["31px", "44px", "56px"],
        ),
        width="100%",
        max_width="1200px",
        align_items="start",
        spacing="0",
    )


def login_view() -> rx.Component:
    """Centered, Discord-only Login Page."""
    return rx.center(
        rx.cond(
            State.discord_username == "",
            # Not Logged In
            rx.vstack(
                rx.image(
                    src="https://assets-global.website-files.com/6257adef93867e50d84d30e2/636e0a6a49cf127bf92de1e2_icon_clyde_blurple_RGB.png",
                    height="48px",
                    object_fit="contain",
                    margin_bottom="2",
                ),
                rx.heading("Driver Login", size="6", color="white", font_weight="900", text_align="center"),
                rx.text("Authorize with Discord to submit comments and access the control panel.", color="#AAAAAA", font_size="sm", text_align="center", margin_bottom="6"),
                rx.button(
                    rx.hstack(
                        rx.icon("log-in", size=18),
                        rx.text("Login with Discord", font_weight="bold"),
                        spacing="2",
                        align="center",
                    ),
                    bg="#5865F2",
                    color="white",
                    width="100%",
                    height="44px",
                    on_click=State.login_with_discord,
                    _hover={"bg": "#4752c4", "transform": "scale(1.02)"},
                    transition="all 0.2s ease-in-out",
                    cursor="pointer",
                    border_radius="md",
                ),
                width="100%",
                max_width="400px",
                bg="#18181C",
                padding="32px",
                border_radius="xl",
                border="1px solid #2C2C32",
                box_shadow="0 8px 30px rgba(0,0,0,0.5)",
                align_items="center",
            ),
            # Logged In
            rx.vstack(
                rx.heading("Driver Account", size="6", color="white", font_weight="900", text_align="center"),
                rx.text("You are currently signed in.", color="#AAAAAA", font_size="sm", text_align="center", margin_bottom="4"),
                rx.hstack(
                    rx.avatar(
                        src=State.discord_avatar,
                        size="5",
                        fallback="U",
                        bg="#5865F2",
                        border="2px solid #00b4da",
                    ),
                    rx.vstack(
                        rx.text(State.discord_username, color="white", font_weight="bold", font_size="lg"),
                        rx.badge("Verified League Driver", color_scheme="cyan", variant="solid"),
                        spacing="1",
                        align_items="start",
                    ),
                    spacing="4",
                    align="center",
                    bg="#252529",
                    padding="4",
                    border_radius="lg",
                    width="100%",
                    margin_bottom="6",
                ),
                rx.button(
                    "Logout",
                    bg="#FF4B4B",
                    color="white",
                    width="100%",
                    height="40px",
                    on_click=State.logout,
                    _hover={"bg": "#E04040", "transform": "scale(1.02)"},
                    transition="all 0.2s ease-in-out",
                    cursor="pointer",
                    border_radius="md",
                ),
                width="100%",
                max_width="400px",
                bg="#18181C",
                padding="32px",
                border_radius="xl",
                border="1px solid #2C2C32",
                box_shadow="0 8px 30px rgba(0,0,0,0.5)",
                align_items="center",
            ),
        ),
        width="100%",
        min_height="50vh",
        display="flex",
        align_items="center",
        justify="center",
    )


def regulations_view() -> rx.Component:
    """The league regulations view with side navigation tabs."""
    return rx.hstack(
        # Sidebar with vertical buck-tooth tabs on the left
        rx.vstack(
            # Regulations Tab
            rx.button(
                "REGULATIONS",
                bg=rx.cond(State.selected_reg_tab == "regulations", "#00b4da", "#18181C"),
                color="white",
                font_size="10px",
                font_weight="bold",
                width="26px",
                height="130px",
                style={"writingMode": "vertical-rl"},
                border_radius="0px 8px 8px 0px",
                border="1px solid #2D2D32",
                border_left="none",
                on_click=lambda: State.set_reg_tab("regulations"),
                _hover={"bg": "#00b4da", "transform": "scaleX(1.05)"},
                cursor="pointer",
                padding="0",
            ),
            # Settings Tab
            rx.button(
                "SETTINGS",
                bg=rx.cond(State.selected_reg_tab == "settings", "#00b4da", "#18181C"),
                color="white",
                font_size="10px",
                font_weight="bold",
                width="26px",
                height="130px",
                style={"writingMode": "vertical-rl"},
                border_radius="0px 8px 8px 0px",
                border="1px solid #2D2D32",
                border_left="none",
                on_click=lambda: State.set_reg_tab("settings"),
                _hover={"bg": "#00b4da", "transform": "scaleX(1.05)"},
                cursor="pointer",
                padding="0",
            ),
            spacing="3",
            align_items="start",
            padding_top="8",
            position="fixed",
            left="0",
            top="12vh",
            z_index="99",
        ),
        # Content Display Area
        rx.box(
            rx.cond(
                State.selected_reg_tab == "regulations",
                regulations_content(),
                settings_content(),
            ),
            width="100%",
            padding_left=["31px", "44px", "56px"],
            padding_right=["31px", "44px", "56px"],
        ),
        width="100%",
        max_width="1200px",
        align_items="start",
        spacing="0",
    )


def _build_season_content(season_idx: int, tab: str, rookies_only: bool, sprint_only: bool) -> rx.Component:
    """Build the content for a specific season and tab."""
    season_data = seasons[season_idx]
    data = Calculations(season_data, sprint_only=sprint_only)

    if tab == "news":
        return Tab0(
            season_data,
            select_article=State.select_article,
            season_articles_expanded=State.season_articles_expanded,
            expand_season_articles=State.expand_season_articles,
        )
    elif tab == "standings":
        return Tab1(
            data,
            season_data,
            sprint_only_var=State.sprint_only,
            toggle_sprint_only=State.toggle_sprint_only,
        )
    elif tab == "race_results":
        return Tab2(
            data,
            season_data,
            sprint_only_var=State.sprint_only,
            toggle_sprint_only=State.toggle_sprint_only,
        )
    elif tab == "constructor_stats":
        return Tab3(
            data,
            season_data,
            sprint_only_var=State.sprint_only,
            toggle_sprint_only=State.toggle_sprint_only,
        )
    elif tab == "driver_stats":
        return Tab4(
            data,
            season_data,
            sprint_only_var=State.sprint_only,
            toggle_sprint_only=State.toggle_sprint_only,
        )
    elif tab == "driver_comparisons":
        return Tab5(
            data,
            season_data,
            rookies_only=rookies_only,
            rookies_only_var=State.rookies_only,
            toggle_rookies_only=State.toggle_rookies_only,
            sprint_only_var=State.sprint_only,
            toggle_sprint_only=State.toggle_sprint_only,
        )
    elif tab == "schedule":
        return Tab6(data, season_data)
    else:
        return Tab1(data, season_data)


def _season_tab_button(label: str, tab_key: str) -> rx.Component:
    """A single sidebar tab button for seasons."""
    return rx.button(
        label,
        bg=rx.cond(State.selected_season_tab == tab_key, "#00b4da", "#18181C"),
        color="white",
        font_size=["7px", "8px", "9px"],
        font_weight="bold",
        width="26px",
        style={"writingMode": "vertical-rl"},
        border_radius="0px 8px 8px 0px",
        border="1px solid #2D2D32",
        border_left="none",
        on_click=State.set_season_tab(tab_key),
        _hover={"bg": "#00b4da", "transform": "scaleX(1.05)"},
        cursor="pointer",
        padding="0",
        flex="1",
        min_height=["22px", "26px", "30px"],
    )


def _season_picker_button(s: dict) -> rx.Component:
    """A single season button in the picker."""
    return rx.button(
        f"S{s['season_number']}",
        bg=rx.cond(
            State.selected_season == s["season_number"],
            "#00b4da",
            "#111111",
        ),
        color="white",
        font_size="9px",
        font_weight="bold",
        width="26px",
        height="22px",
        min_height="22px",
        border_radius="0px 6px 6px 0px",
        border="1px solid #2D2D32",
        border_left="none",
        on_click=lambda: State.set_season(s["season_number"]),
        _hover={"bg": "#00b4da"},
        cursor="pointer",
        padding="0",
    )


def seasons_view() -> rx.Component:
    """The Seasons view with sidebar navigation and content area."""

    # Season picker buttons (shown when expanded)
    season_picker_buttons = rx.cond(
        State.season_picker_open,
        rx.vstack(
            *[_season_picker_button(s) for s in seasons],
            spacing="1",
        ),
        rx.fragment(),
    )


    # Tab definitions: (label, key)
    tabs = [
        ("NEWS", "news"),
        ("STANDINGS", "standings"),
        ("RESULTS", "race_results"),
        ("CONSTRUCTORS", "constructor_stats"),
        ("DRIVERS", "driver_stats"),
        ("COMPARISONS", "driver_comparisons"),
        ("SCHEDULE", "schedule"),
    ]

    # Build content using nested rx.cond for each season
    # We need to build a cond chain for selected_season (1..N)
    # and within each, a cond chain for selected_season_tab
    def build_tab_cond(season_idx: int) -> rx.Component:
        """Build a conditional chain for tabs within a season."""
        tab_keys = [t[1] for t in tabs]
        # Start from the last tab and work backwards
        result = _build_season_content(season_idx, tab_keys[-1], False, False)
        for tk in reversed(tab_keys[:-1]):
            if tk == "driver_comparisons":
                result = rx.cond(
                    State.selected_season_tab == tk,
                    rx.cond(
                        State.sprint_only,
                        rx.cond(
                            State.rookies_only,
                            _build_season_content(season_idx, tk, rookies_only=True, sprint_only=True),
                            _build_season_content(season_idx, tk, rookies_only=False, sprint_only=True),
                        ),
                        rx.cond(
                            State.rookies_only,
                            _build_season_content(season_idx, tk, rookies_only=True, sprint_only=False),
                            _build_season_content(season_idx, tk, rookies_only=False, sprint_only=False),
                        ),
                    ),
                    result,
                )
            elif tk in ["standings", "race_results", "constructor_stats", "driver_stats"]:
                result = rx.cond(
                    State.selected_season_tab == tk,
                    rx.cond(
                        State.sprint_only,
                        _build_season_content(season_idx, tk, rookies_only=False, sprint_only=True),
                        _build_season_content(season_idx, tk, rookies_only=False, sprint_only=False),
                    ),
                    result,
                )
            else:
                result = rx.cond(
                    State.selected_season_tab == tk,
                    _build_season_content(season_idx, tk, False, False),
                    result,
                )
        return result

    # Build season conditional chain
    content = build_tab_cond(len(seasons) - 1)  # default to last season
    for idx in range(len(seasons) - 2, -1, -1):
        content = rx.cond(
            State.selected_season == seasons[idx]["season_number"],
            build_tab_cond(idx),
            content,
        )

    return rx.hstack(
        # Sidebar
        rx.vstack(
            # Season picker toggle
            rx.button(
                rx.cond(
                    State.season_picker_open,
                    "▼",
                    "▶",
                ),
                bg=rx.cond(State.season_picker_open, "#00b4da", "#18181C"),
                color="white",
                font_size="10px",
                font_weight="bold",
                width="26px",
                height="34px",
                min_height="34px",
                border_radius="0px 8px 8px 0px",
                border="1px solid #2D2D32",
                border_left="none",
                on_click=State.toggle_season_picker,
                _hover={"bg": "#00b4da", "transform": "scaleX(1.05)"},
                cursor="pointer",
                padding="0",
            ),
            season_picker_buttons,
            # Tab buttons
            *[_season_tab_button(label, key) for label, key in tabs],
            spacing="1",
            align_items="start",
            padding_top="4",
            position="fixed",
            left="0",
            top="12vh",
            z_index="99",
            height="calc(100vh - 12vh - 60px - 10px)",
            style={
                "overflow_y": "auto",
                "scrollbar_width": "none",  # Firefox
                "-ms-overflow-style": "none",  # IE/Edge
                "&::-webkit-scrollbar": {  # Chrome/Safari/Opera
                    "display": "none",
                },
            },
        ),
        # Content area
        rx.box(
            rx.vstack(
                content,
                width="100%",
                spacing="0",
            ),
            width="100%",
            padding_left=["31px", "44px", "56px"],
            padding_right=["31px", "44px", "56px"],
        ),
        width="100%",
        max_width="1200px",
        align_items="start",
        spacing="0",
    )


def footer() -> rx.Component:
    """The permanent bottom navigation bar with square icon buttons and a protruding circular Home button."""
    footer_height = "60px"
    home_button_height = "70px"  # 15% taller than 60px
    return rx.hstack(
        rx.hstack(
            # Left Group (Regulations, All Time Stats)
            rx.hstack(
                rx.button(
                    rx.image(
                        src="/Icons/IconRegulations.png",
                        height="22px",
                        object_fit="contain",
                    ),
                    bg=rx.cond(State.active_nav == "regulations", "#00b4da", "transparent"),
                    border="1px solid #00b4da",
                    color="white",
                    border_radius="sm",
                    width="36px",
                    height="36px",
                    min_width="36px",
                    max_width="36px",
                    on_click=lambda: State.set_nav("regulations"),
                    _hover={"bg": "#00b4da", "transform": "scale(1.05)"},
                    cursor="pointer",
                    padding="0",
                ),
                rx.button(
                    rx.image(
                        src="/Icons/IconAll.png",
                        height="22px",
                        object_fit="contain",
                    ),
                    bg=rx.cond(State.active_nav == "stats", "#00b4da", "transparent"),
                    border="1px solid #00b4da",
                    color="white",
                    border_radius="sm",
                    width="36px",
                    height="36px",
                    min_width="36px",
                    max_width="36px",
                    on_click=lambda: State.set_nav("stats"),
                    _hover={"bg": "#00b4da", "transform": "scale(1.05)"},
                    cursor="pointer",
                    padding="0",
                ),
                spacing="2",
            ),
            # Center circular Home button that pokes up
            rx.box(
                rx.image(
                    src="/Icons/IconLogo.png",
                    height="36px",
                    width="36px",
                    object_fit="contain",
                ),
                bg=rx.cond(State.active_nav == "home", "#00b4da", "#1A1A1A"),
                border="2px solid #00b4da",
                border_radius="50%",
                width=home_button_height,
                height=home_button_height,
                display="flex",
                align_items="center",
                justify_content="center",
                on_click=State.go_home,
                _hover={"bg": "#00b4da", "transform": "scale(1.05)", "box_shadow": "0 0 12px #00b4da"},
                cursor="pointer",
                position="relative",
                top="-8px",  # Pokes up above the footer
                z_index="101",
                transition="all 0.2s ease-in-out",
            ),
            # Right Group (Seasons, Login)
            rx.hstack(
                rx.button(
                    rx.image(
                        src="/Icons/IconSeason.png",
                        height="22px",
                        object_fit="contain",
                    ),
                    bg=rx.cond(State.active_nav == "seasons", "#00b4da", "transparent"),
                    border="1px solid #00b4da",
                    color="white",
                    border_radius="sm",
                    width="36px",
                    height="36px",
                    min_width="36px",
                    max_width="36px",
                    on_click=lambda: State.set_nav("seasons"),
                    _hover={"bg": "#00b4da", "transform": "scale(1.05)"},
                    cursor="pointer",
                    padding="0",
                ),
                rx.button(
                    rx.image(
                        src="/Icons/IconLogin.png",
                        height="22px",
                        object_fit="contain",
                    ),
                    bg=rx.cond(State.active_nav == "power_rankings", "#00b4da", "transparent"),
                    border="1px solid #00b4da",
                    color="white",
                    border_radius="sm",
                    width="36px",
                    height="36px",
                    min_width="36px",
                    max_width="36px",
                    on_click=lambda: State.set_nav("power_rankings"),
                    _hover={"bg": "#00b4da", "transform": "scale(1.05)"},
                    cursor="pointer",
                    padding="0",
                ),
                spacing="2",
            ),
            width="100%",
            max_width="360px",
            justify="center",
            spacing="5",
            align="center",
            padding_x="2",
            style={"overflow": "visible"},
        ),
        width="100%",
        height=footer_height,
        bg="black",
        align="center",
        justify="center",
        border_top="1px solid #222222",
        position="fixed",
        bottom="0",
        left="0",
        right="0",
        z_index="100",
        style={"overflow": "visible"},
    )


def power_rankings_table() -> rx.Component:
    """A table showing the current power rankings with change indicators."""
    def render_row(item: dict) -> rx.Component:
        return rx.table.row(
            # Rank
            rx.table.cell(
                rx.text(
                    item["rank"],
                    font_weight="bold",
                    color="white",
                ),
                align="center",
            ),
            # Icon & Team Name
            rx.table.cell(
                rx.hstack(
                    rx.image(
                        src=item["icon"],
                        width="24px",
                        height="16px",
                        object_fit="contain",
                    ),
                    rx.text(
                        item["team"],
                        font_weight="600",
                        color="white",
                        font_family="Outfit",
                    ),
                    align_items="center",
                    spacing="2",
                ),
            ),
            # Change Indicator
            rx.table.cell(
                rx.text(
                    item["change"],
                    color=item["change_color"],
                    font_weight="bold",
                    font_size="sm",
                ),
                align="center",
            ),
        )

    return rx.vstack(
        rx.text(
            "Current Standings & Form",
            color="white",
            font_size="lg",
            font_weight="bold",
            margin_bottom="2",
        ),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Rank", align="center", color="#888888"),
                    rx.table.column_header_cell("Constructor", color="#888888"),
                    rx.table.column_header_cell("Change", align="center", color="#888888"),
                ),
            ),
            rx.table.body(
                rx.foreach(
                    State.power_rankings_list_data,
                    render_row
                ),
            ),
            width="100%",
            variant="ghost",
        ),
        width="100%",
    )


def power_rankings_trajectory_graph() -> rx.Component:
    """The interactive SVG bump chart showing power ranking trajectories."""
    return rx.vstack(
        rx.text(
            "Ranking Trajectory",
            color="white",
            font_size="lg",
            font_weight="bold",
            margin_bottom="2",
        ),
        rx.el.svg(
            # Grid background lines
            rx.foreach(
                State.power_rankings_races,
                lambda race: rx.el.line(
                    x1=race["x"],
                    y1=40,
                    x2=race["x"],
                    y2=450,
                    stroke="rgba(255, 255, 255, 0.08)",
                    stroke_width="1",
                )
            ),
            rx.foreach(
                State.power_rankings_y_labels,
                lambda label: rx.el.line(
                    x1=100,
                    y1=label["y"],
                    x2=900,
                    y2=label["y"],
                    stroke="rgba(255, 255, 255, 0.08)",
                    stroke_width="1",
                )
            ),
            # Y-axis Labels
            rx.foreach(
                State.power_rankings_y_labels,
                lambda label: rx.el.text(
                    label["rank"],
                    x=60,
                    y=label["y"],
                    dy="4",
                    fill="#888888",
                    font_size="12",
                    font_family="Outfit",
                    font_weight="bold",
                    text_anchor="middle",
                )
            ),
            # X-axis Labels
            rx.foreach(
                State.power_rankings_races,
                lambda race: rx.el.text(
                    race["name"],
                    x=race["x"],
                    y=480,
                    fill="#CCCCCC",
                    font_size="10",
                    font_family="Outfit",
                    text_anchor="middle",
                )
            ),
            # Trajectory Paths
            rx.foreach(
                State.power_rankings_paths,
                lambda path: rx.el.g(
                    rx.el.path(
                        d=path["path_string"],
                        stroke=path["color"],
                        stroke_width="4",
                        fill="none",
                        opacity=0.8,
                    ),
                    rx.el.image(
                        href=path["icon"],
                        x=path["leading_x"],
                        y=path["leading_y"],
                        width="30",
                        height="30",
                        transform="translate(-15px, -15px)",
                    ),
                )
            ),
            view_box=State.power_rankings_view_box,
            width="100%",
            height="auto",
        ),
        width="100%",
    )


def power_rankings_view() -> rx.Component:
    """The Power Rankings page."""
    from the_alternative_f1.seasons import seasons

    # Season picker buttons (shown when expanded)
    season_picker_buttons = rx.cond(
        State.season_picker_open,
        rx.vstack(
            *[_season_picker_button(s) for s in seasons],
            spacing="1",
        ),
        rx.fragment(),
    )

    # Sidebar for Season Selector
    sidebar = rx.vstack(
        # Season picker toggle
        rx.button(
            rx.cond(
                State.season_picker_open,
                "▼",
                "▶",
            ),
            bg=rx.cond(State.season_picker_open, "#00b4da", "#18181C"),
            color="white",
            font_size="10px",
            font_weight="bold",
            width="26px",
            height="34px",
            min_height="34px",
            border_radius="0px 8px 8px 0px",
            border="1px solid #2D2D32",
            border_left="none",
            on_click=State.toggle_season_picker,
            _hover={"bg": "#00b4da", "transform": "scaleX(1.05)"},
            cursor="pointer",
            padding="0",
        ),
        season_picker_buttons,
        spacing="1",
        align_items="start",
        padding_top="4",
        position="fixed",
        left="0",
        top="12vh",
        z_index="99",
    )

    # Main content layout
    content = rx.vstack(
        # Title
        rx.heading(
            f"Power Rankings: Season {State.selected_season}",
            size="6",
            color="white",
            font_family="Outfit",
            margin_bottom="4",
        ),
        # Trajectory Graph Container
        rx.box(
            power_rankings_trajectory_graph(),
            width="100%",
            bg="#18181C",
            border="1px solid #2C2C32",
            padding="4",
            border_radius="xl",
            margin_bottom="6",
        ),
        # Rankings Table Container
        rx.box(
            power_rankings_table(),
            width="100%",
            bg="#18181C",
            border="1px solid #2C2C32",
            padding="4",
            border_radius="xl",
        ),
        width="100%",
        spacing="4",
    )

    return rx.hstack(
        sidebar,
        rx.box(
            content,
            width="100%",
            padding_left=["31px", "44px", "56px"],
            padding_right=["31px", "44px", "56px"],
        ),
        width="100%",
        max_width="1200px",
        align_items="start",
        spacing="0",
    )


def index() -> rx.Component:
    """The main view structure."""
    return rx.box(
        rx.vstack(
            header(),
            # Main scrollable content area with medium gray background (bg="#47474c")
            rx.box(
                # Inner centering wrapper
                rx.box(
                    rx.vstack(
                        rx.cond(
                            State.selected_article_title != "",
                            article_detail(),
                            rx.cond(
                                State.active_nav == "home",
                                articles_list(),
                                rx.cond(
                                    State.active_nav == "regulations",
                                    regulations_view(),
                                    rx.cond(
                                        State.active_nav == "stats",
                                        stats_view(),
                                        rx.cond(
                                            State.active_nav == "seasons",
                                            seasons_view(),
                                            rx.cond(
                                                State.active_nav == "power_rankings",
                                                power_rankings_view(),
                                                rx.cond(
                                                    State.active_nav == "login",
                                                    login_view(),
                                                    rx.text("Not found", color="white"),
                                                )
                                            )
                                        )
                                    )
                                )
                            )
                        ),
                        rx.box(height="160px", min_height="160px", width="100%", flex_shrink="0"),  # Physical spacer to guarantee bottom scroll space
                        width="100%",
                        spacing="0",
                    ),
                    display="flex",
                    justify_content="center",
                    width="100%",
                ),
                width="100%",
                flex="1",
                overflow_y="auto",
                bg="var(--main-bg-color)",
                padding_x=["4", "6", "8"],
                padding_top="8",
            ),
            footer(),
            width="100%",
            height="100vh",
            spacing="0",
        ),
        font_family="Outfit",
        bg="black",
        width="100%",
        height="100vh",
        overflow="hidden",
        on_mount=State.on_app_mount,
    )


app = rx.App(
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&display=swap",
        "style.css",
    ],
    head_components=[
        rx.el.link(rel="icon", href="/Icons/IconLogoApp.png"),
        rx.el.link(rel="apple-touch-icon", href="/Icons/IconLogoApp.png"),
    ],
)
app.add_page(index)

