import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Australia Recap: A Rumble Down Under",
    "blurb": "Season 3 news article: Australia Recap: A Rumble Down Under.",
    "content": [
rx.vstack(
    rx.text("Australia Start", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/thealternativef1-cloudflare/Season3/Images/Australia_Start.png",
        width="100%",
        max_width="400px",
        border_radius="md",
        box_shadow="0 4px 12px rgba(0,0,0,0.4)"
    ),
    align_items="center",
    width="100%",
    margin_y="4",
),
rx.vstack(
    rx.text("Australia Race Collage", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/thealternativef1-cloudflare/Season3/Images/Australia_Collage.png",
        width="100%",
        max_width="400px",
        border_radius="md",
        box_shadow="0 4px 12px rgba(0,0,0,0.4)"
    ),
    align_items="center",
    width="100%",
    margin_y="4",
),
rx.vstack(
    rx.text("Australia Side Shot", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/thealternativef1-cloudflare/Season3/Images/Australia_Side_Shot.png",
        width="100%",
        max_width="400px",
        border_radius="md",
        box_shadow="0 4px 12px rgba(0,0,0,0.4)"
    ),
    align_items="center",
    width="100%",
    margin_y="4",
),
    ],
    "image": "/thealternativef1-cloudflare/Season3/Images/Australia_Start.png",
    "author": "Patrick Knowles with credit Erick & Nick",
    "date": "December 11, 2024",
    "season": 3,
}
