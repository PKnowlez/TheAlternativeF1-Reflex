import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Race Week - Canada",
    "blurb": "The league takes to Montreal’s Notre Dame Island this week to rip some laps around the Circuit Gilles-Villeneuve.",
    "content": [
        rx.vstack(
rx.text("Oh Canada!", text_align="center", color="#E0E0E0", font_style="italic", font_size="md", line_height="1.5"),
rx.text("Our neighbor and next race track!", text_align="center", color="#E0E0E0", font_style="italic", font_size="md", line_height="1.5"),
rx.text("True driver love in all of us command.", text_align="center", color="#E0E0E0", font_style="italic", font_size="md", line_height="1.5"),
rx.text("With glowing exhausts we see thee rise,", text_align="center", color="#E0E0E0", font_style="italic", font_size="md", line_height="1.5"),
rx.text("The True North fast and free!", text_align="center", color="#E0E0E0", font_style="italic", font_size="md", line_height="1.5"),
rx.text("From far and wide,", text_align="center", color="#E0E0E0", font_style="italic", font_size="md", line_height="1.5"),
rx.text("Oh Canada, we drive our cars for thee.", text_align="center", color="#E0E0E0", font_style="italic", font_size="md", line_height="1.5"),
rx.text("FIA keep our track fast and free!", text_align="center", color="#E0E0E0", font_style="italic", font_size="md", line_height="1.5"),
rx.text("Oh Canada, we drive our cars for thee.", text_align="center", color="#E0E0E0", font_style="italic", font_size="md", line_height="1.5"),
rx.text("Oh Canada, we drive our cars for thee.", text_align="center", color="#E0E0E0", font_style="italic", font_size="md", line_height="1.5"),
            width="100%",
            margin_y="4",
            spacing="1",
            align_items="center",
        ),
rx.text(
    r"""The league takes to Montreal’s Notre Dame Island this week to rip some laps around the Circuit Gilles-Villeneuve. With the standings closer than ever and an increasingly small margin for error, drivers and constructors will be putting it all on the line at a circuit known for its high risk reward ratio. Drivers will be challenged by The Wall of Champions found at Turn 14 as well as the twisting and technical Sector 1. When the lights go out, drivers will likely be wheel to wheel in the Turn 1 and 2 combo. As they leave those turns and head into the end of Sector 1, many drivers will begin to queue up for the high-speed straights in Sector 2 and 3. Notable passing opportunities will occur at both Turn 10 and Turn 13, but drivers who are brave may find chances in Turn 1, 6, and 8.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.vstack(
    rx.text("Circuit Gilles-Villeneuve Map", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/thealternativef1-cloudflare/Season3/Images/Canada_Circuit.png",
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
    r"""With over a season between now and the last time the league took on Canada, it will be interesting to see how drivers improve from the last outing. The last performance from the league was lackluster with only one driver on the podium and no other drivers finishing above 8th place. With the standings as close as they are, no one can afford a major mishap here. With respect to the Constructor’s Championship, Red Bull will be looking to overtake Aston Martin, McLaren will be looking to overtake Alpine, and both Ferrari and VCARB will be poised to capitalize on any opportunity afforded them. Drivers like Alpine’s Eddie, Ferrari’s Erick, and Red Bull’s Yeti will all be looking to get on the offensive and overtake their nearest rivals. While drivers like Ferrari’s Zane, Aston Martin’s Del, and VCARB’s Patrick will all be looking to further themselves in the standings from those just behind them.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.text(
    r"""There are rumors of a double this week, so stay tuned for another update if the drivers are taking a quick flight to the Italian countryside for laps around Monza.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
    ],
    "image": "/thealternativef1-cloudflare/Season3/Images/Canada_Circuit.png",
    "author": "Patrick Knowles",
    "date": "January 18, 2025",
    "season": 3,
}
