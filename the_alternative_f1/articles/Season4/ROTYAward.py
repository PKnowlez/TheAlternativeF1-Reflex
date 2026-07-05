import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "The rookies are coming! The rookies are coming!",
    "blurb": "Shouts around the paddock this week have been all about the rookies.",
    "content": [
        rx.vstack(
            rx.text("New Foe", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season4/Images/New Foe.png",
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
            r"""Shouts around the paddock this week have been all about the rookies. As some begin to post times in time trial and others participate in full race weekend simulations with their teammates, the league's rookies are starting to heat up their tires.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Wheels are spinning, tires are screeching, and gravel and grass are most certainly being touched. Their practice efforts are clearly all aimed at one goal, performing. None of the five rookies are here just to turn some laps. Each of them is here to see what they are made of. They want to win and they want to help elevate their teams to the next level.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""But with five fresh drivers zipping around the league, this is the first year it has made sense for a new award to be fought for.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""That's right, this season, there will be an award for the rookie who brings home the most points across the course of the season. In addition to the award, a new filter has been added to the driver comparison tab within the Season 4 app, allowing users to narrow down the results of the app to just the five rookie drivers.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.vstack(
            rx.text("Rookie Button", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season4/Images/Rookie Button.png",
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
            r"""All this means that when the lights go out for the first time this season, there will be so much more at play than just the two main championships. Yes, a four-peat is on the line for the Driver's Championship, and yes the Constructor's Championship is certainly way up in the air. But maybe more importantly, the league's rookies are going to be elevated well above where they might normally be and put straight into the spotlight from day one.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Each of these rookies will be racing for their own copy of the league's trophy that lists them as the one and only rookie of the year for The Alternative F1 Season 4.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
    ],
    "image": "/thealternativef1-cloudflare/Season4/Images/New Foe.png",
    "author": "Patrick",
    "date": "September 8, 2025",
    "season": 4,
}
