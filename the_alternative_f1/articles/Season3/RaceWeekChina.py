import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Race Week - China",
    "blurb": "The league’s relentless schedule continues this week in China.",
    "content": [
rx.text(
    r"""The league’s relentless schedule continues this week in China. Home to the third longest straight on the league’s calendar, Shanghai Audi International Circuit will allow drivers to overtake at high speed as well as through twisting and daring low and medium speed turns. Both straights include DRS zones which should enable thrilling wheel to wheel action in both the sweeping Turn 1 & 2 combination as well as Turn 14’s hairpin.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.vstack(
    rx.text("Shanghai Circuit Map", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/thealternativef1-cloudflare/Season3/Images/China_Circuit.png",
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
    r"""While the circuit has many twists and turns, the biggest twist for the league is the week’s format. Not only will a standard race occur on Wednesday, the league will face its first ever Sprint race. If that wasn’t enough, league officials have devised an exciting plan to bring some variety to the race week. Drivers will face a standard three session qualifying to help set the grid for the Sprint. From there the drivers will complete a short stint of laps around the circuit at full tilt to score points. The results of the Sprint race will be used to set the grid order for the race, in reverse. That’s right, qualifying, Sprint, and the main race grid set in reverse off of the results of the Sprint. The format is sure to force drivers into daring passing scenarios, fingers crossed everyone keeps it between the white lines.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.text(
    r"""So how much does this race matter? With the added 8 points available from the Sprint race, the Driver’s Championship can turn topsy-turvy, especially with the added suspense of the reverse grid. With respect to the Constructor’s Championship, nearly every team has the ability to make up ground or even leap-frog the current leader. As we adjourn this race week update, let’s take a look at the results of yesteryear. Last season saw McLaren’s Nick take home the win, with the then Mercedes driver, now Aston Martin driver, Del stepping up to the second step of the podium, and the then Red Bull driver, now Ferrari driver, Zane bringing home third. However, with two wins up for grabs and the new format almost anything is possible.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
    ],
    "image": "/thealternativef1-cloudflare/Season3/Images/China_Circuit.png",
    "author": "Patrick Knowles",
    "date": "January 5, 2025",
    "season": 3,
}
