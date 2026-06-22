"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx

from rxconfig import config

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


class State(rx.State):
    """The app state."""
    selected_article_id: int = -1
    active_nav: str = "home"
    selected_reg_tab: str = "regulations"
    selected_stats_tab: str = "constructors"

    # ── Seasons state ────────────────────────────────────────────────────
    selected_season: int = LATEST_SEASON
    selected_season_tab: str = "standings"
    season_picker_open: bool = False
    rookies_only: bool = False

    def select_article(self, article_id: int):
        self.selected_article_id = article_id

    def set_nav(self, nav_name: str):
        self.active_nav = nav_name
        self.selected_article_id = -1
        if nav_name == "regulations":
            self.selected_reg_tab = "regulations"
        if nav_name == "stats":
            self.selected_stats_tab = "constructors"
        if nav_name == "seasons":
            self.selected_season_tab = "standings"
            self.rookies_only = False

    def set_reg_tab(self, tab_name: str):
        self.selected_reg_tab = tab_name

    def set_stats_tab(self, tab_name: str):
        self.selected_stats_tab = tab_name

    def set_season(self, season_num: int):
        self.selected_season = season_num
        self.season_picker_open = False

    def set_season_tab(self, tab_name: str):
        self.selected_season_tab = tab_name

    def toggle_season_picker(self):
        self.season_picker_open = not self.season_picker_open

    def toggle_rookies_only(self, value: bool):
        self.rookies_only = value

    def go_home(self):
        self.active_nav = "home"
        self.selected_article_id = -1


def header() -> rx.Component:
    """The permanent header (8% height) with the logo."""
    return rx.hstack(
        rx.image(
            src="/The Alternative F1 NEW Logo.png",
            height="70%",
            object_fit="contain",
        ),
        width="100%",
        height="8vh",
        bg="black",
        align="center",
        justify="center",
        border_bottom="1px solid #222222",
        position="sticky",
        top="0",
        z_index="100",
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
        cursor="pointer",
        on_click=lambda: State.select_article(article["id"]),
        _hover={
            "transform": "translateY(-6px)",
            "box_shadow": "0 10px 25px rgba(0, 180, 218, 0.3)",
            "border_color": "#00b4da",
        },
        transition="all 0.25s ease-in-out",
    )


def articles_list() -> rx.Component:
    """List of all article cards."""
    return rx.vstack(
        rx.vstack(
            rx.heading("The Alternative F1 League News", size="7", color="white", font_weight="900"),
            rx.text(
                "Stay up-to-date on the happenings of The Alternative F1 league.",
                color="#AAAAAA",
                font_size="sm",
            ),
            align_items="start",
            spacing="1",
            width="100%",
            max_width="1200px",
            padding_bottom="4",
        ),
        rx.flex(
            *[article_card(art) for art in articles],
            flex_wrap="wrap",
            justify="center",
            gap="5%",
            width="100%",
            max_width="1200px",
        ),
        width="100%",
        align="center",
        margin_bottom="160px",
    )


def article_detail() -> rx.Component:
    """The detailed article reading view."""
    def build_reader(article: dict) -> rx.Component:
        return rx.vstack(
            rx.button(
                rx.hstack(
                    rx.icon("arrow-left", size=16),
                    rx.text("Back to Articles"),
                ),
                variant="ghost",
                color="white",
                on_click=State.go_home,
                margin_bottom="4",
                _hover={"bg": "#00b4da", "color": "white"},
            ),
            rx.vstack(
                rx.image(
                    src=article["image"],
                    width="100%",
                    height=["200px", "350px", "400px"],
                    object_fit="cover",
                    border_radius="xl",
                    box_shadow="0 8px 30px rgba(0,0,0,0.5)",
                ),
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
                        rx.text(
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
            ),
            width="100%",
            max_width="800px",
            align_items="start",
            margin_bottom="160px",
        )

    return rx.box(
        rx.cond(
            State.selected_article_id == 0,
            build_reader(articles[0]),
            rx.cond(
                State.selected_article_id == 1,
                build_reader(articles[1]),
                rx.cond(
                    State.selected_article_id == 2,
                    build_reader(articles[2]),
                    rx.text("Article not found", color="white"),
                )
            )
        ),
        width="100%",
        display="flex",
        justify_content="center",
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
                width="34px",
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
                width="34px",
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
                width="34px",
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
            padding_left=["46px", "52px", "60px"],
        ),
        width="100%",
        max_width="1200px",
        align_items="start",
        spacing="0",
    )


def login_view() -> rx.Component:
    """A clean, premium Login form."""
    return rx.vstack(
        rx.heading("Driver Login", size="6", color="white", font_weight="900", margin_bottom="2"),
        rx.text("Access the FIA control panel and your superlicense.", color="#AAAAAA", font_size="sm", margin_bottom="6"),
        rx.vstack(
            rx.text("Username or Email", color="white", font_size="xs", font_weight="bold", align_self="start"),
            rx.input(placeholder="driver@alternativef1.com", type="email", width="100%", bg="#18181C", border_color="#2C2C32", color="white"),
            rx.text("Password", color="white", font_size="xs", font_weight="bold", align_self="start", margin_top="3"),
            rx.input(placeholder="••••••••", type="password", width="100%", bg="#18181C", border_color="#2C2C32", color="white"),
            rx.button(
                "Sign In",
                bg="#00b4da",
                color="white",
                width="100%",
                margin_top="6",
                _hover={"bg": "#009bbd"},
                cursor="pointer",
            ),
            width="100%",
            spacing="2",
        ),
        width="100%",
        max_width="400px",
        bg="#18181C",
        padding="6",
        border_radius="xl",
        border="1px solid #2C2C32",
        align_items="center",
        margin_bottom="160px",
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
                width="34px",
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
                width="34px",
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
            padding_left=["46px", "52px", "60px"],
        ),
        width="100%",
        max_width="1200px",
        align_items="start",
        spacing="0",
    )


def _build_season_content(season_idx: int, tab: str, rookies_only: bool) -> rx.Component:
    """Build the content for a specific season and tab."""
    season_data = seasons[season_idx]
    data = Calculations(season_data)

    if tab == "news":
        return Tab0(articles, season_data["season_number"])
    elif tab == "standings":
        return Tab1(data, season_data)
    elif tab == "race_results":
        return Tab2(data, season_data)
    elif tab == "constructor_stats":
        return Tab3(data, season_data)
    elif tab == "driver_stats":
        return Tab4(data, season_data)
    elif tab == "driver_comparisons":
        return Tab5(data, season_data, rookies_only=rookies_only)
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
        font_size="9px",
        font_weight="bold",
        width="34px",
        height=rx.cond(
            State.season_picker_open,
            "calc((100vh - 12vh - 60px - 120px) / 7)",
            "calc((100vh - 12vh - 60px - 40px) / 7)",
        ),
        min_height="40px",
        max_height="100px",
        style={"writingMode": "vertical-rl"},
        border_radius="0px 8px 8px 0px",
        border="1px solid #2D2D32",
        border_left="none",
        on_click=State.set_season_tab(tab_key),
        _hover={"bg": "#00b4da", "transform": "scaleX(1.05)"},
        cursor="pointer",
        padding="0",
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
        width="34px",
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
        result = _build_season_content(season_idx, tab_keys[-1], False)
        for tk in reversed(tab_keys[:-1]):
            rookies = tk == "driver_comparisons"
            result = rx.cond(
                State.selected_season_tab == tk,
                _build_season_content(season_idx, tk, True if rookies else False),
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

    # Rookies toggle (shown only on comparisons tab)
    rookies_toggle = rx.cond(
        State.selected_season_tab == "driver_comparisons",
        rx.hstack(
            rx.text("Rookies Only", color="white", font_size="sm", font_weight="600"),
            rx.switch(
                checked=State.rookies_only,
                on_change=State.toggle_rookies_only,
                color_scheme="cyan",
            ),
            spacing="2",
            align="center",
            margin_bottom="4",
        ),
        rx.fragment(),
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
                width="34px",
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
            spacing="2",
            align_items="start",
            padding_top="4",
            position="fixed",
            left="0",
            top="12vh",
            z_index="99",
            max_height="calc(100vh - 12vh - 60px)",
            overflow_y="auto",
        ),
        # Content area
        rx.box(
            rx.vstack(
                rookies_toggle,
                content,
                width="100%",
                spacing="0",
            ),
            width="100%",
            padding_left=["46px", "52px", "60px"],
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
                    bg=rx.cond(State.active_nav == "login", "#00b4da", "transparent"),
                    border="1px solid #00b4da",
                    color="white",
                    border_radius="sm",
                    width="36px",
                    height="36px",
                    min_width="36px",
                    max_width="36px",
                    on_click=lambda: State.set_nav("login"),
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


def index() -> rx.Component:
    """The main view structure."""
    return rx.box(
        rx.vstack(
            header(),
            # Main scrollable content area with medium gray background (bg="#2A2A2E")
            rx.box(
                # Inner centering wrapper
                rx.box(
                    rx.vstack(
                        rx.cond(
                            State.selected_article_id != -1,
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
                                                State.active_nav == "login",
                                                login_view(),
                                                rx.text("Not found", color="white"),
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
                bg="#2A2A2E",
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
    )


app = rx.App(
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&display=swap",
    ],
    head_components=[
        rx.el.link(rel="icon", href="/Icons/IconLogoApp.png"),
        rx.el.link(rel="apple-touch-icon", href="/Icons/IconLogoApp.png"),
    ],
)
app.add_page(index)

