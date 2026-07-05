import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Race Recap: Mama Mia, Here We Go One Last Time",
    "blurb": "So the league had one last race.",
    "content": [
        rx.text(
            r"""So the league had one last race. One last race to determine who sucks the least out of these amateur "drivers." And honestly, it kind of delivered? Maybe? Well at least there were some memeable moments.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""I'll leave the recap and what it all means for Patrick later on in this post, but I've pulled out the original, the one and only, my true genesis, to recap this one.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.vstack(
            rx.text("Monza2026", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season4/Images/Monza2026.png",
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
            r"""Thank you to our illustrious intern for that lovely bit of memery. The plan here is to succinctly wrap up the race in a short paragraph or two. From there, the reader will be treated to some significant stats synopsis.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""The race got off to a bumpy start for the championship hopefully at Alpine. Joshua found himself starting 10th due to his self-caused, accident on track during qualifying. Beyond that mistake, there were very few issues during qualifying.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""With drivers lined up on the grid, league officials warned everyone to be cautious into the first turn. Unfortunately, the other Alpine driver seemed to have radio communication issues during those warnings and created a multi-car pileup in the chicane. This forced a race restart and an immediate penalty for Eddie who would start last, behind Boz and Erick.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Once the restart occured, drivers were careful and began a DRS train of sorts with micro battles ensuing over the course of the first few laps. During these micro battles, Joshua made his way up the standings and essentailly secured his championship with a finish. The VCARB duo was chasing Jairo, with Jaden just behind them.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""To clinch the championship on the constructor side, the Mercedes duo simply held the line. Jairo's race win solidified the team's second ever championship and the rookie duo's first ever championship.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""And so, Alpine's Joshua won his first ever Driver's Championship, the second driver in league history to achieve this feat. Mercedes snagged their second Constructor's Championship, becoming the first constructor to win multiple championships. This season had a number of other significant statistics which are listed below.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""- Lowest DNS percentage in league history (12.75%) - First Driver's Champion to not win the most races in the season (Joshua) - First Driver's and Constructor's Championship decisions both in the final race - First ever 1000 point driver (Nick) - First and Second 1000 point teams (McLaren and Mercedes)""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.heading(
            "SILLY SEASON",
            size="4",
            color="#00b4da",
            margin_top="6",
            margin_bottom="3",
            font_family="Outfit"
        ),
        rx.text(
            r"""With the season closed out, some important silly season updates have come to light. The first, however, is not driver or team related. For Post-Season Testing, the teams will take to the streets of Monaco again. This time, they will run in cockpit view as well as with full Parc Ferme in effect.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""But maybe more importantly, Ferrari has confirmed their lineup with our intrepid beat reporter. Please see below for their formal driver lineup.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.vstack(
            rx.text("Ferraris5", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season4/Images/Silly Season/FerrariS5.png",
                width="100%",
                max_width="400px",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.4)"
            ),
            align_items="center",
            width="100%",
            margin_y="4",
        ),
        rx.vstack(
            rx.text("Surfer", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/thealternativef1-cloudflare/Images/surfer.gif",
                width="100%",
                max_width="400px",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.4)"
            ),
            align_items="center",
            width="100%",
            margin_y="4",
        ),
        rx.vstack(
            rx.text("Videofile", color="#888888", font_size="xs", margin_bottom="1"),
            rx.video(
                src="/thealternativef1-cloudflare/Images/VideoFile.mp4",
                width="100%",
                height="auto",
                controls=True,
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.4)"
            ),
            align_items="center",
            width="100%",
            margin_y="4",
        ),
    ],
    "image": "/thealternativef1-cloudflare/Season4/Images/Monza2026.png",
    "author": "A Joint Patrick & The Intern Production",
    "date": "January 25, 2026",
    "season": 4,
}
