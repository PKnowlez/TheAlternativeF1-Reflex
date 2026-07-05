import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Race Week - Monza",
    "blurb": "Patrick is MIA, something about skiing or whatever.",
    "content": [
rx.text(
    r"""Patrick is MIA, something about skiing or whatever. So they gave me, the intern, the keys to the castle. Monza is a fast track or something, I literally just took this job because they pay well...""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.text(
    r"""Ok, so as I was typing that someone came by and said they don't pay me. So this is all you're getting.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.vstack(
    rx.text("Monza Race Week Update", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/thealternativef1-cloudflare/Season3/Images/Monza_Update.png",
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
    "image": "/thealternativef1-cloudflare/Season3/Images/Monza_Update.png",
    "author": "The Intern",
    "date": "January 29, 2025",
    "season": 3,
}
