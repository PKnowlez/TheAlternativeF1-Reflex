"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx

from rxconfig import config

from the_alternative_f1.articles import articles
from the_alternative_f1.regulations_settings.Regulations import Regulations as regulations_content
from the_alternative_f1.regulations_settings.Settings import Settings as settings_content


class State(rx.State):
    """The app state."""
    selected_article_id: int = -1
    active_nav: str = "home"
    selected_reg_tab: str = "regulations"

    def select_article(self, article_id: int):
        self.selected_article_id = article_id

    def set_nav(self, nav_name: str):
        self.active_nav = nav_name
        self.selected_article_id = -1
        if nav_name == "regulations":
            self.selected_reg_tab = "regulations"

    def set_reg_tab(self, tab_name: str):
        self.selected_reg_tab = tab_name

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
            "box_shadow": "0 10px 25px rgba(225, 6, 0, 0.2)",
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


def schedule_view() -> rx.Component:
    """Mock schedule view."""
    races = [
        {"gp": "Bahrain Grand Prix", "date": "March 5-7", "track": "Sakhir", "status": "Completed"},
        {"gp": "Saudi Arabian Grand Prix", "date": "March 19-21", "track": "Jeddah Corniche", "status": "Completed"},
        {"gp": "Australian Grand Prix", "date": "April 2-4", "track": "Albert Park", "status": "Upcoming"},
        {"gp": "Azerbaijan Grand Prix", "date": "April 28-30", "track": "Baku City Circuit", "status": "Upcoming"},
    ]
    return rx.vstack(
        rx.heading("Race Schedule 2026", size="6", color="white", font_weight="900", margin_bottom="4"),
        rx.vstack(
            *[
                rx.hstack(
                    rx.box(
                        bg=rx.cond(race["status"] == "Completed", "#333333", "#00b4da"),
                        width="12px",
                        height="12px",
                        border_radius="full",
                    ),
                    rx.vstack(
                        rx.heading(race["gp"], size="3", color="white"),
                        rx.text(f"{race['track']} • {race['date']}", color="#AAAAAA", font_size="sm"),
                        align_items="start",
                    ),
                    rx.spacer(),
                    rx.badge(
                        race["status"],
                        color_scheme=rx.cond(race["status"] == "Completed", "gray", "cyan"),
                        variant="solid",
                    ),
                    width="100%",
                    bg="#18181C",
                    padding="4",
                    border_radius="lg",
                    border="1px solid #2C2C32",
                    align="center",
                )
                for race in races
            ],
            spacing="3",
            width="100%",
        ),
        width="100%",
        max_width="700px",
    )


def standings_view() -> rx.Component:
    """Mock standings view."""
    drivers = [
        {"pos": "1", "driver": "Max Verstappen", "team": "Red Bull Racing", "points": "258"},
        {"pos": "2", "driver": "Lando Norris", "team": "McLaren", "points": "220"},
        {"pos": "3", "driver": "Charles Leclerc", "team": "Ferrari", "points": "185"},
        {"pos": "4", "driver": "Oscar Piastri", "team": "McLaren", "points": "162"},
        {"pos": "5", "driver": "Carlos Sainz", "team": "Ferrari", "points": "145"},
    ]
    return rx.vstack(
        rx.heading("Driver Standings", size="6", color="white", font_weight="900", margin_bottom="4"),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Pos", color="#00b4da"),
                    rx.table.column_header_cell("Driver", color="#00b4da"),
                    rx.table.column_header_cell("Team", color="#00b4da"),
                    rx.table.column_header_cell("Points", color="#00b4da", justify="end"),
                )
            ),
            rx.table.body(
                *[
                    rx.table.row(
                        rx.table.row_header_cell(d["pos"], color="white", font_weight="bold"),
                        rx.table.cell(d["driver"], color="white"),
                        rx.table.cell(d["team"], color="#AAAAAA"),
                        rx.table.cell(d["points"], color="white", justify="end", font_weight="bold"),
                    )
                    for d in drivers
                ]
            ),
            width="100%",
            variant="ghost",
        ),
        width="100%",
        max_width="700px",
        bg="#18181C",
        padding="6",
        border_radius="xl",
        border="1px solid #2C2C32",
    )


def teams_view() -> rx.Component:
    """Mock teams view."""
    teams_data = [
        {"name": "Red Bull Racing", "color": "#0600EF", "drivers": "M. Verstappen / L. Lawson"},
        {"name": "Ferrari", "color": "#EF1A2D", "drivers": "C. Leclerc / L. Hamilton"},
        {"name": "McLaren", "color": "#FF8700", "drivers": "L. Norris / O. Piastri"},
        {"name": "Mercedes", "color": "#00A19B", "drivers": "G. Russell / K. Antonelli"},
    ]
    return rx.vstack(
        rx.heading("Constructor Teams", size="6", color="white", font_weight="900", margin_bottom="4"),
        rx.grid(
            *[
                rx.vstack(
                    rx.box(width="100%", height="6px", bg=team["color"], border_radius="full"),
                    rx.heading(team["name"], size="4", color="white"),
                    rx.text(team["drivers"], color="#AAAAAA", font_size="sm"),
                    bg="#18181C",
                    padding="5",
                    border_radius="xl",
                    border="1px solid #2C2C32",
                    align_items="start",
                    spacing="2",
                    width="100%",
                    _hover={"transform": "translateY(-4px)", "border_color": team["color"]},
                    transition="all 0.2s ease-in-out",
                )
                for team in teams_data
            ],
            columns="2",
            spacing="4",
            width="100%",
        ),
        width="100%",
        max_width="750px",
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


def footer() -> rx.Component:
    """The permanent bottom navigation bar (8% height) with rect and circular buttons."""
    return rx.hstack(
        rx.hstack(
            # Left rectangle buttons
            rx.hstack(
                rx.button(
                    "Regulations",
                    bg=rx.cond(State.active_nav == "regulations", "#00b4da", "transparent"),
                    border="1px solid #00b4da",
                    color="white",
                    font_size="xs",
                    font_weight="600",
                    border_radius="sm",
                    padding_x="3",
                    padding_y="1.5",
                    on_click=lambda: State.set_nav("regulations"),
                    _hover={"bg": "#00b4da", "transform": "scale(1.05)"},
                    cursor="pointer",
                ),
                rx.button(
                    "Schedule",
                    bg=rx.cond(State.active_nav == "schedule", "#00b4da", "transparent"),
                    border="1px solid #00b4da",
                    color="white",
                    font_size="xs",
                    font_weight="600",
                    border_radius="sm",
                    padding_x="3",
                    padding_y="1.5",
                    on_click=lambda: State.set_nav("schedule"),
                    _hover={"bg": "#00b4da", "transform": "scale(1.05)"},
                    cursor="pointer",
                ),
                spacing="2",
            ),
            # Center circular home button
            rx.button(
                rx.icon("home", size=18),
                bg=rx.cond(State.active_nav == "home", "#00b4da", "#1A1A1A"),
                border="2px solid #00b4da",
                border_radius="full",
                width="44px",
                height="44px",
                color="white",
                on_click=State.go_home,
                _hover={"bg": "#00b4da", "transform": "scale(1.1)", "box_shadow": "0 0 10px #00b4da"},
                cursor="pointer",
            ),
            # Right rectangle buttons
            rx.hstack(
                rx.button(
                    "Standings",
                    bg=rx.cond(State.active_nav == "standings", "#00b4da", "transparent"),
                    border="1px solid #00b4da",
                    color="white",
                    font_size="xs",
                    font_weight="600",
                    border_radius="sm",
                    padding_x="3",
                    padding_y="1.5",
                    on_click=lambda: State.set_nav("standings"),
                    _hover={"bg": "#00b4da", "transform": "scale(1.05)"},
                    cursor="pointer",
                ),
                rx.button(
                    "Teams",
                    bg=rx.cond(State.active_nav == "teams", "#00b4da", "transparent"),
                    border="1px solid #00b4da",
                    color="white",
                    font_size="xs",
                    font_weight="600",
                    border_radius="sm",
                    padding_x="3",
                    padding_y="1.5",
                    on_click=lambda: State.set_nav("teams"),
                    _hover={"bg": "#00b4da", "transform": "scale(1.05)"},
                    cursor="pointer",
                ),
                spacing="2",
            ),
            width="100%",
            max_width="600px",
            justify="between",
            align="center",
            padding_x="4",
        ),
        width="100%",
        height="8vh",
        bg="black",
        align="center",
        justify="center",
        border_top="1px solid #222222",
        position="sticky",
        bottom="0",
        z_index="100",
    )


def index() -> rx.Component:
    """The main view structure."""
    return rx.box(
        rx.vstack(
            header(),
            # Main scrollable content area with medium gray background (bg="#2A2A2E")
            rx.box(
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
                                State.active_nav == "schedule",
                                schedule_view(),
                                rx.cond(
                                    State.active_nav == "standings",
                                    standings_view(),
                                    rx.cond(
                                        State.active_nav == "teams",
                                        teams_view(),
                                        rx.text("Not found", color="white"),
                                    )
                                )
                            )
                        )
                    )
                ),
                width="100%",
                flex="1",
                overflow_y="auto",
                bg="#2A2A2E",
                padding_x=["4", "6", "8"],
                padding_y="8",
                display="flex",
                justify_content="center",
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
)
app.add_page(index)

