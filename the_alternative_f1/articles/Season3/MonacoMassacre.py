import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Postseason Testing - The Monaco Massacre",
    "blurb": "A new tradition was born this week.",
    "content": [
rx.text(
    r"""A new tradition was born this week. Many of the drivers and teams assembled for a joint postseason testing session. But it was not simply a friendly practice session, it was a competitive race around the famous streets of Monaco. The league agreed to let bygones be bygones and rip it around a circuit together one more time. Drivers voted for the race to even be at night, and regulators introduced some of the new rules for next season, which all increased the spiciness of the race. The results were something next to no one predicted, and the racing throughout was incredible. To wrap up this season, our intern is going to take it away. ONE. LAST. TIME.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.text(
    r"""What the hell was that race? Chaos, chaos, chaos. Some WWE, some rally driving, some crash outs (both physical and metaphysical), and carnage everywhere. I loved it. It was perfect. Please do it again. I never want to see another boring regular season race again. During qualifying we had wrecks, drivers miss the cut for Q3, and some of the most…intriguing…commentary ever heard. It even rained during qualifying. And if you thought the drivers were caught lacking during qualifying, you were right, but it's not like they actually figured it out in the race. The first fricking lap saw the world’s first ever formula car suplex.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.text(
    r"""Sir Isaac Newton left the chat after that one. With physics, gravity, and any remaining common sense out the window, the stewards had to restart the race. And guess what? For once, the drivers kept it moderately clean through the first couple of laps. But the real story of the race was damage. Wings here, sidepods there, egos bruised everywhere. It was incredible. We lost drivers throughout the race and as remaining laps whittled down a few safety cars helped front runners conserve their tires. But, dark knight Joshua, running in a Red Bull, began to find his groove. His teammate Eddie was long forgotten by these streets, but was providing commentary as Joshua chased down front runners Nick and Brently. Del and Boz meanwhile were holding down the back like a trustworthy caboose.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.vstack(
    rx.text("Monaco Polar Express Meme", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/Season3/Images/Monaco_Polar_Express.png",
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
    r"""But one can only hold it down for so long…as Nick and Brently caught up to Boz, disaster struck. With good intentions Boz pulls out of the way to allow the duo past, but does so in an unpredictable way. This is where a double whammy crashout occurs. Nick’s McLaren and Nick both CRASHED the F out.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.vstack(
    rx.text("Nick Monaco DNF", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/Season3/Images/Monaco_Nick.png",
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
    r"""It was gnarly, but it left Brently in position to win it all, as long as Joshua choked. And boy did Joshua deliver. Brother lost it, demolishing his front wing and even earning some penalties along the way. And so, rookie driver Brently took home his first win, in true Lightning McQueen style.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.vstack(
    rx.text("Brently Monaco Victory", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/Season3/Images/Monaco_Brently.png",
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
    r"""Until next season folks…""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
    ],
    "image": "/Season3/Images/Monaco_Polar_Express.png",
    "author": "A Joint Patrick & The Intern Production",
    "date": "February 20, 2025",
    "season": 3,
}
