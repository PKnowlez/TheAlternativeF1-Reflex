import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Race Week - Australia",
    "blurb": "Season 3 news article: Race Week - Australia.",
    "content": [
rx.vstack(
    rx.text("Albert Park Circuit Map", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/Season3/Images/Australia_Circuit.png",
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
    "image": "/Season3/Images/Australia_Circuit.png",
    "author": "System Administrator",
    "date": "February 20, 2025",
    "season": 3,
}
