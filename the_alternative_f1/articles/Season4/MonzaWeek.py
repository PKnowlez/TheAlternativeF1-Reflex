import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Race Week: Monza",
    "blurb": "One more race to finalize the results.",
    "content": [
        rx.text(
            r"""One more race to finalize the results. A season tighter than ever, all comes down to this. What a thrilling, competitive, spicy, and all around enjoyable season it has been.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""The league has been carried to new heights thanks to the talent, dedication, and excitement brought week in and week out by every driver and team. With all of the joy this season has brought, it is now time to decide who are champions will be, Mercedes or VCARB, Joshua or Jairo.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Shockingly, this has never happened before within the league. Typically, one of the two championships is clinched prior to the final race. This year though, at the track that gifted us The Intern last season, we are going to be gifted a thrilling and tense battle for both championships.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""So how can each driver or team win it? For Joshua, all he needs to do is win. In fact, it is a little easier than that even. Simply put, Jairo can win the race and all Joshua has to do is finish 8th or higher. But a Joshua DNF and a Jairo win flips the championship to the Mercedes rookie.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""On the constructor side of things, Mercedes simply needs to score 10 points, not including bonus points. If they do, VCARB is mathematically out of it. However, with bonus points in play, that bumps the threshold for a championship up to 14 points. So how can VCARB flip the script? To simplify the math, the following is all without bonus points.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""If VCARB finishes 1-2 and Mercedes only scores 9 points, then the trophy goes their way. If VCARB finishes 1-3 and Mercedes scores 6 points, then the trophy goes their way. If VCARB finishes 2-3 and Mercedes DNFs, then it will be a tie on points. League officials are already discussing how to break a tie like this and have determined a few metrics to base it off of if the need arises.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.vstack(
            rx.text("Monza Circuit", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season4/Images/Monza_Circuit.png",
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
            r"""Monza is an excellent track to host such a tight battle. With two incredible DRS zones and the pedal to the floor for nearly 80 percent of the lap, drivers are going to burn through tires and battle with track limits for all 27 laps.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Turn 1's chicane will likely provide fireworks throughout the race, but a few of the other braking zones might prove to provide unique overtaking moments if drivers are feeling brave. It will be a test of mental fortitude throughout and if there are safety cars, penalties could decide the race.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Last time out the league was in shambles around the Temple of Speed. So much so that I was incapable of writing an effective article, and so my trusty intern was hired. Who knows what this race will have in store for the league, but if nothing else, it will bring resolution to a tumultuous season.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.heading(
            "RUMOR MILL",
            size="4",
            color="#00b4da",
            margin_top="6",
            margin_bottom="3",
            font_family="Outfit"
        ),
        rx.text(
            r"""As this article goes out, our intrepid report, The Intern, brought in some intriguing news. The team from Maranello has reportedly signed a second driver to replace league legend Erick. With this being such incredibly breaking news, we will do our due diligence to confirm the rumors within the next week and announce the new lineup there.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Of course, rookie Leo will continue his drive with the team after showing an increase in skill over the last half of the season. Additionally, rumors still swirl about Audi or Williams or both. The Intern is set to interrogate (their words) one or both of the drivers in these conversations some time soon.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Be on the lookout for new information over the next few weeks.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.vstack(
            rx.text("Surfer", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season4/Images/surfer.gif",
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
                src="/thealternativef1-cloudflare/Season4/Images/VideoFile.mp4",
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
    "image": "/thealternativef1-cloudflare/Season4/Images/Monza_Circuit.png",
    "author": "Patrick",
    "date": "January 20, 2026",
    "season": 4,
}
