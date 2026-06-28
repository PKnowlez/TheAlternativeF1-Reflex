"""Tab 0 — League News (Reflex).

Displays articles from the homepage that match the selected season.
"""

import reflex as rx


def Tab0(season_data: dict, select_article = None, season_articles_expanded = None, expand_season_articles = None) -> rx.Component:
    """Render season-specific news articles.

    Parameters
    ----------
    season_data : dict
        The season config dict from season_N.py.
    """
    season_number = season_data["season_number"]
    configured_articles = season_data.get("articles", [])

    # Filter and keep only articles whose 'season' matches the season_number
    season_articles = [a for a in configured_articles if a.get("season") == season_number]

    if not season_articles:
        return rx.vstack(
            rx.heading(
                f"Season {season_number} News",
                size="6",
                color="white",
                font_weight="900",
                padding_y="2.5%",
                padding_x="2%",
            ),
            rx.box(
                rx.vstack(
                    rx.icon("newspaper", size=48, color="#555555"),
                    rx.text(
                        "No news for this season yet.",
                        color="#888888",
                        font_size="md",
                    ),
                    spacing="4",
                    align="center",
                    padding_y="12",
                ),
                width="100%",
                bg="#18181C",
                border_radius="xl",
                border="1px solid #2C2C32",
            ),
            width="100%",
            align_items="start",
            spacing="4",
        )

    # Render matching article cards
    def news_card(article: dict) -> rx.Component:
        return rx.box(
            rx.vstack(
                rx.image(
                    src=article.get("image", ""),
                    width="100%",
                    height="180px",
                    object_fit="cover",
                ),
                rx.vstack(
                    rx.text(
                        article.get("date", ""),
                        font_size="10px",
                        color="#00b4da",
                        font_weight="bold",
                        text_transform="uppercase",
                    ),
                    rx.heading(
                        article.get("title", ""),
                        size="4",
                        color="white",
                        font_family="Outfit",
                        font_weight="700",
                    ),
                    rx.text(
                        article.get("blurb", ""),
                        font_size="sm",
                        color="#CCCCCC",
                    ),
                    rx.hstack(
                        rx.text(
                            f"By {article.get('author', '')}",
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
            margin_top="2%",
            margin_bottom="2%",
            cursor="pointer",
            on_click=lambda: select_article(article["title"]) if select_article is not None else None,
            _hover={
                "transform": "translateY(-6px)",
                "box_shadow": "0 10px 25px rgba(0, 180, 218, 0.3)",
                "border_color": "#00b4da",
            },
            transition="all 0.25s ease-in-out",
        )

    first_six = season_articles[:6]
    remaining = season_articles[6:]

    return rx.vstack(
        rx.vstack(
            rx.heading(
                f"Season {season_number} News",
                size="6",
                color="white",
                font_weight="900",
                padding_y="2.5%",
                padding_x="2%",
            ),
            align_items="start",
            width="100%",
            max_width="1200px",
            padding_bottom="4",
        ),
        rx.flex(
            *[news_card(a) for a in first_six],
            rx.cond(
                ~season_articles_expanded,
                rx.center(
                    rx.button(
                        "Load More Articles",
                        on_click=expand_season_articles,
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
            ) if len(season_articles) > 6 else rx.fragment(),
            *[
                rx.cond(
                    season_articles_expanded,
                    news_card(a),
                    rx.fragment()
                )
                for a in remaining
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
        spacing="4",
    )