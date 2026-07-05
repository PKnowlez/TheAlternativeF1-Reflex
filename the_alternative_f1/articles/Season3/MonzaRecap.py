import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Monza Recap: It’s-A Me, The Intern",
    "blurb": "Welcome to the greatest race recap of the year.",
    "content": [
rx.vstack(
    rx.text("Monza Intern Recap", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/thealternativef1-cloudflare/Season3/Images/Monza_Intern.png",
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
    r"""Welcome to the greatest race recap of the year. Yes, that’s right, me, the intern, was given the full reins to write the cringiest, most meme-ified race recap this league has ever seen. So let’s get down to business.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.text(
    r"""I got notes from Patrick, but no cap, it was just a list of Erick crashing into other drivers or making mistakes, and I heard you all liked the track map so here’s a quick summary of Erick’s tragedy of a race.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.vstack(
    rx.text("Erick Monza Incident Map", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/thealternativef1-cloudflare/Season3/Images/Monza_Erick_Map.png",
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
    r"""If I’m a Tifossi, I might try and cancel all of Ferrari after that one…""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.text(
    r"""Beyond Erick’s tirade, the league flexed on the AI and took the top 5 spots on the grid with Del securing his first pole position of the season. Tire strategies was the hottest goss on the track at the start of the race with Brently running the hards and literally everyone else running the mediums. However it turned out fine for him as he was able to battle through the Tavera sibling squabble and come out on the podium in third.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.text(
    r"""Nick and Del played nice together in the Italian sunshine and managed to tow each other all the way until the last few laps where Bottas decided he didn’t really like Del after all, blocking him and sealing the win for Nick.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.vstack(
    rx.text("Monza Finish - Nick and Del", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/thealternativef1-cloudflare/Season3/Images/Monza_Nick_Del.png",
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
    r"""Let me be real with you, this might as well have been Monaco though. Beyond the drama with the two Taveras and Nick overtaking Del nothing really happened to change anything after qualifying. However, I was not shook to hear that Eddie had the most penalties again, and honestly Del pitting for fastest lap was hella petty but we love to see it.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.text(
    r"""I was told I had to do a standings update at the end of the recap, but like that’s what the flipping standings tab is for so I’m just gonna yeet that section. Next week the league races in Abu Dhabi on Wednesday and in Austria on Saturday with the updated Sprint format.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.text(
    r"""Oh, also, I am just gonna leave this cringy little race radio screenshot here...""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.vstack(
    rx.text("Eddie Team Radio at Monza", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/thealternativef1-cloudflare/Season3/Images/Monza_Eddie.png",
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
    "image": "/thealternativef1-cloudflare/Season3/Images/Monza_Intern.png",
    "author": "The Intern",
    "date": "January 31, 2025",
    "season": 3,
}
