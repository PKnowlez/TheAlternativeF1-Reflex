import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Season 3 Historical Archive",
    "blurb": "This is the historical record of The Alternative's 3rd season (2024-2025).",
    "content": [
rx.text(
    r"""This is the historical record of The Alternative's 3rd season (2024-2025).""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.text(
    rx.text("Driver's Champion:", as_="span", font_weight="bold", font_style="italic"), " Nick - McLaren",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.text(
    rx.text("Constructor's Champion:", as_="span", font_weight="bold", font_style="italic"), " Alpine - Joshua & Eddie",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
    ],
    "image": "/Season3/Images/Trophy.png",
    "author": "System Administrator",
    "date": "February 20, 2025",
    "season": 3,
}
