import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Silverstone Recap: “007 You Only Win Twice”",
    "blurb": "Another week, another race.",
    "content": [
rx.vstack(
    rx.text("Silverstone Start", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/thealternativef1-cloudflare/Season3/Images/Silverstone_Start.png",
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
    r"""Another week, another race. The sun mercifully shone down on the British Isles and provided the perfect weather for an eventful race. Reigning WDC Nick, and Alpine’s top driver Joshua, battled it out for 26 laps straight. Joshua took the win after a little bit of questionable contact and a helpful dose of backmarker blocking. This is Alpine and Joshua’s second win of the season. Alpine also had some 007 magic from their second seat, Eddie, who had 0 intention of racing, 0 practice, and placed 7th. Coincidentally this was also his second time placing 7th this season. Let’s see if this pattern continues for the French outfit.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.vstack(
    rx.text("Silverstone Final Turn", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/thealternativef1-cloudflare/Season3/Images/Silverstone_Final_Turn.png",
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
    r"""The podium was rounded out by Ferrari ace, Erick, who raced a lonely set of laps around the hallowed airfield. Ferrari’s other driver Zane battled with VCARB’s Patrick in a tightly contested tango where the drivers had opposite tire strategies (softs to mediums and mediums to softs respectively). However, in the end, a bit of contact left Zane just out of reach on the final lap.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.vstack(
    rx.text("Silverstone PK and Zane", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/thealternativef1-cloudflare/Season3/Images/Silverstone_PK_Zane.png",
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
    "image": "/thealternativef1-cloudflare/Season3/Images/Silverstone_Start.png",
    "author": "Patrick Knowles with credit Eddie & Nick",
    "date": "December 4, 2024",
    "season": 3,
}
