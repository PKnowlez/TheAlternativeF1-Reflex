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


def stats_view() -> rx.Component:
    """All Time Stats view."""
    stats_data = [
        {"metric": "Most Championship Titles", "holder": "Max Verstappen", "value": "4"},
        {"metric": "Most Race Wins", "holder": "Lando Norris", "value": "32"},
        {"metric": "Most Pole Positions", "holder": "Charles Leclerc", "value": "41"},
        {"metric": "Most Podiums", "holder": "Max Verstappen", "value": "98"},
        {"metric": "Most Fastest Laps", "holder": "Oscar Piastri", "value": "18"},
    ]
    return rx.vstack(
        rx.heading("All Time League Stats", size="6", color="white", font_weight="900", margin_bottom="4"),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Metric", color="#00b4da"),
                    rx.table.column_header_cell("Record Holder", color="#00b4da"),
                    rx.table.column_header_cell("Value", color="#00b4da", justify="end"),
                )
            ),
            rx.table.body(
                *[
                    rx.table.row(
                        rx.table.cell(item["metric"], color="white", font_weight="bold"),
                        rx.table.cell(item["holder"], color="#CCCCCC"),
                        rx.table.cell(item["value"], color="#00b4da", justify="end", font_weight="bold"),
                    )
                    for item in stats_data
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


def seasons_view() -> rx.Component:
    """Historical Seasons view."""
    seasons_data = [
        {"season": "Season 2025", "champion": "Max Verstappen", "constructor": "Red Bull Racing", "status": "Completed"},
        {"season": "Season 2024", "champion": "Lando Norris", "constructor": "McLaren", "status": "Completed"},
        {"season": "Season 2023", "champion": "Max Verstappen", "constructor": "Red Bull Racing", "status": "Completed"},
        {"season": "Season 2026", "champion": "TBD", "constructor": "TBD", "status": "Active"},
    ]
    return rx.vstack(
        rx.heading("League Seasons History", size="6", color="white", font_weight="900", margin_bottom="4"),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Season", color="#00b4da"),
                    rx.table.column_header_cell("Driver Champion", color="#00b4da"),
                    rx.table.column_header_cell("Constructor Champion", color="#00b4da"),
                    rx.table.column_header_cell("Status", color="#00b4da", justify="end"),
                )
            ),
            rx.table.body(
                *[
                    rx.table.row(
                        rx.table.cell(item["season"], color="white", font_weight="bold"),
                        rx.table.cell(item["champion"], color="#CCCCCC"),
                        rx.table.cell(item["constructor"], color="#CCCCCC"),
                        rx.table.cell(
                            rx.badge(item["status"], color_scheme=rx.cond(item["status"] == "Completed", "gray", "cyan"), variant="solid"),
                            justify="end"
                        ),
                    )
                    for item in seasons_data
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
            # Left Grid (Regulations, All Time Stats) - flex="1"
            rx.grid(
                rx.button(
                    "Regulations",
                    bg=rx.cond(State.active_nav == "regulations", "#00b4da", "transparent"),
                    border="1px solid #00b4da",
                    color="white",
                    font_size="xs",
                    font_weight="600",
                    border_radius="sm",
                    width="100%",
                    height="32px",
                    on_click=lambda: State.set_nav("regulations"),
                    _hover={"bg": "#00b4da", "transform": "scale(1.02)"},
                    cursor="pointer",
                ),
                rx.button(
                    "All Time Stats",
                    bg=rx.cond(State.active_nav == "stats", "#00b4da", "transparent"),
                    border="1px solid #00b4da",
                    color="white",
                    font_size="xs",
                    font_weight="600",
                    border_radius="sm",
                    width="100%",
                    height="32px",
                    on_click=lambda: State.set_nav("stats"),
                    _hover={"bg": "#00b4da", "transform": "scale(1.02)"},
                    cursor="pointer",
                ),
                columns="2",
                spacing="2",
                flex="1",
            ),
            # Center circular Home button
            rx.box(
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
                padding_x="3",
            ),
            # Right Grid (Seasons, Login) - flex="1"
            rx.grid(
                rx.button(
                    "Seasons",
                    bg=rx.cond(State.active_nav == "seasons", "#00b4da", "transparent"),
                    border="1px solid #00b4da",
                    color="white",
                    font_size="xs",
                    font_weight="600",
                    border_radius="sm",
                    width="100%",
                    height="32px",
                    on_click=lambda: State.set_nav("seasons"),
                    _hover={"bg": "#00b4da", "transform": "scale(1.02)"},
                    cursor="pointer",
                ),
                rx.button(
                    "Login",
                    bg=rx.cond(State.active_nav == "login", "#00b4da", "transparent"),
                    border="1px solid #00b4da",
                    color="white",
                    font_size="xs",
                    font_weight="600",
                    border_radius="sm",
                    width="100%",
                    height="32px",
                    on_click=lambda: State.set_nav("login"),
                    _hover={"bg": "#00b4da", "transform": "scale(1.02)"},
                    cursor="pointer",
                ),
                columns="2",
                spacing="2",
                flex="1",
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
        position="fixed",
        bottom="0",
        left="0",
        right="0",
        z_index="100",
    )


def index() -> rx.Component:
    """The main view structure."""
    return rx.box(
        rx.vstack(
            header(),
            # Main scrollable content area with medium gray background (bg="#2A2A2E")
            rx.box(
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
                    width="100%",
                    padding_bottom="100px",  # Push content above the fixed footer
                ),
                width="100%",
                flex="1",
                overflow_y="auto",
                bg="#2A2A2E",
                padding_x=["4", "6", "8"],
                padding_top="8",
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

