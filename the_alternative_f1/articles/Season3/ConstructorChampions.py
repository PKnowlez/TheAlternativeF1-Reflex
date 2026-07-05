import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Congratulations Joshua & Eddie - Constructor’s World Champions",
    "blurb": "Through battles, controversy, penalties, and determination, Joshua and Eddie brought home the season’s prize for our whole team.",
    "content": [
rx.vstack(
    rx.text("Alpine Constructor Champions Graphic", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/Season3/Images/Alpine_Champions.png",
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
    r"""Through battles, controversy, penalties, and determination, Joshua and Eddie brought home the season’s prize for our whole team. Our team, our championship, our way. Alpine is ecstatic with the results of this season and cannot congratulate Joshua and Eddie enough. It will be a pleasure to watch these two drive in the future, and we hope this team can defend its title together next season.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
    ],
    "image": "/Season3/Images/Alpine_Champions.png",
    "author": "Alpine F1 Team",
    "date": "February 20, 2025",
    "season": 3,
}
