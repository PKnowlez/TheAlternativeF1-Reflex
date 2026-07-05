import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Spa Update",
    "blurb": "The league’s battle at Spa has been postponed until 1/1/2025 or later.",
    "content": [
rx.vstack(
    rx.text("Race Postponed Notice", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/thealternativef1-cloudflare/Season3/Images/Postponed.png",
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
    r"""The league’s battle at Spa has been postponed until 1/1/2025 or later. Something about some driver ditching to party in Mexico and a few drivers unable to connect to EA's crappy servers. However this did allow some of the drivers to run some laps in Saudi Arabia as a mid-season practice session. The FIA will be working to finalize the upcoming schedule for the remainder of the season as rumor has it there will be a week or two of double headers. The league takes a short break as we head into this holiday season to allow drivers to recuperate and spend time with loved ones.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
    ],
    "image": "/thealternativef1-cloudflare/Season3/Images/Postponed.png",
    "author": "Patrick Knowles",
    "date": "December 22, 2024",
    "season": 3,
}
