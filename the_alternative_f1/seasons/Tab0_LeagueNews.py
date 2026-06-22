"""Tab 0 — League News (Reflex).

Displays articles from the homepage that match the selected season.
"""

import reflex as rx


def Tab0(articles: list, season_number: int) -> rx.Component:
    """Render season-specific news articles.

    Parameters
    ----------
    articles : list[dict]
        The full articles list (each dict has an optional ``season`` key).
    season_number : int
        The currently selected season number.
    """
    # Filter articles that belong to this season
    season_articles = [a for a in articles if a.get("season") == season_number]

    if not season_articles:
        return rx.vstack(
            rx.heading(
                f"Season {season_number} News",
                size="6",
                color="white",
                font_weight="900",
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
                    height="160px",
                    object_fit="cover",
                    border_radius="lg lg 0 0",
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
                    rx.text(
                        f"By {article.get('author', '')}",
                        font_size="xs",
                        color="#888888",
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
        )

    return rx.vstack(
        rx.heading(
            f"Season {season_number} News",
            size="6",
            color="white",
            font_weight="900",
        ),
        rx.flex(
            *[news_card(a) for a in season_articles],
            flex_wrap="wrap",
            justify="center",
            gap="5%",
            width="100%",
        ),
        width="100%",
        align_items="start",
        spacing="4",
    )