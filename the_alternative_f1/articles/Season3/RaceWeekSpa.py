import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Race Week - Spa",
    "blurb": "The league heads out for a Spa day this week.",
    "content": [
rx.text(
    r"""The league heads out for a Spa day this week. However, this one probably won’t be all that relaxing. With the Constructor’s and Driver’s championships heating up, Spa will prove to be a place where everyone has the opportunity to make up ground. Historically known as a track favorable for overtaking, Spa’s sacred pavement is also known for being one of the most treacherous high-speed circuits on the calendar. Nestled deep in the Ardennes forest, Spa is riddled with corners, straights, and stories that have filled the racing history books.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.vstack(
    rx.text("Spa-Francorchamps Circuit Map", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/thealternativef1-cloudflare/Season3/Images/Spa_Circuit.png",
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
    r"""Famous early corners like La Source and Raidillon’s Eau Rogue will provide exhilarating braking and high-speed moments. Followed by the twisting turns of Le Combes, Pouhon, and Campus among others, the drivers are sure to provide incredible wheel-to-wheel action. Finally drivers will have the opportunity for late sends or strategic tailgating going into the chicane before the start-finish straight.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.vstack(
    rx.text("Spa Race Week Collage", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/thealternativef1-cloudflare/Season3/Images/Spa_Race_Week_Collage2.png",
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
    r"""Previously when the league navigated a day at Spa, McLaren’s Nick took home the win. He finished just seconds before the then Mercedes driver, now Aston Martin driver Del. While Ferrari’s Erick rounded out the podium. Current league leader, and Alpine driver, Joshua was unable to start the race along with three other drivers. In fact, Joshua has not run a race at Spa in the last two seasons, and reigning champion Nick has not lost at Spa in recent memory. Ferrari’s pairing of Erick and Zane have also had historically good races, with Erick boasting a second and third place finish, and Zane placing fourth on his last two outings. With the addition of last week’s regulation changes and the thrilling nature of the Circuit of Spa-Francorchamps, this week is aimed at being another piece of absolute cinema. Hopefully none of the drivers end up just a few tire marbles short of a win.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
    ],
    "image": "/thealternativef1-cloudflare/Season3/Images/Spa_Circuit.png",
    "author": "Patrick Knowles",
    "date": "December 14, 2024",
    "season": 3,
}
