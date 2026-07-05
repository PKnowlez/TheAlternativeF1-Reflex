import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Congratulations Nick",
    "blurb": "The team at McLaren wants to express our sincerest congratulations to our champion.",
    "content": [
rx.vstack(
    rx.text("Congratulations Nick WDC Graphic", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/thealternativef1-cloudflare/Season3/Images/Nick_Championship.png",
        width="100%",
        max_width="400px",
        border_radius="md",
        box_shadow="0 4px 12px rgba(0,0,0,0.4)"
    ),
    align_items="center",
    width="100%",
    margin_y="4",
),
rx.text(
    r"""The team at McLaren wants to express our sincerest congratulations to our champion. Nick’s commitment to this team, to the league, and to the sport have shown through as he battled from behind and overtook his competitor midway through the season. It has been an absolute pleasure having him on the team for three straight World Driver’s Championship victories, and we look forward to what is still to come.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
    ],
    "image": "/thealternativef1-cloudflare/Season3/Images/Nick_Championship.png",
    "author": "McLaren Racing",
    "date": "February 10, 2025",
    "season": 3,
}
