import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "BREAKING NEWS - DRIVER SWAP",
    "blurb": "The Alternative F124 League Where racing meets integrity and fair competition.",
    "content": [
rx.vstack(
    rx.text("Breaking News - Driver Swap", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/thealternativef1-cloudflare/Season3/Images/BN_Del_Zane.png",
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
    rx.text("The Alternative F124 League", as_="span", font_style="italic"), " <p style=\"color:lightgray;\">Where racing meets integrity and fair competition.</p>",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
    ],
    "image": "/thealternativef1-cloudflare/Season3/Images/BN_Del_Zane.png",
    "author": "System Administrator",
    "date": "February 20, 2025",
    "season": 3,
}
