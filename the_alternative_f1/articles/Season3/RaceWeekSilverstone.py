import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Race Week - Silverstone",
    "blurb": "Season 3 news article: Race Week - Silverstone.",
    "content": [
rx.vstack(
    rx.text("Season Trophy", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/thealternativef1-cloudflare/Season3/Images/Trophy.png",
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
    "image": "/thealternativef1-cloudflare/Season3/Images/Trophy.png",
    "author": "Patrick Knowles",
    "date": "December 1, 2024",
    "season": 3,
}
