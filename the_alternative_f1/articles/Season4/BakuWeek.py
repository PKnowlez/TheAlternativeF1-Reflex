import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Race Week: Baku",
    "blurb": "It's ~~Race~~ Chaos Week.",
    "content": [
        rx.text(
            r"""It's ~~Race~~ Chaos Week. The league has faced street circuits before and come out clean. However, none have been as treacherous as the one that lies in front of them this week.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Baku is not just the track with the longest continuous full throttle section of the season, but also a track that the league will likely take heavy casualties during. Tight and narrow straights, heavy braking, sharp turns, and little to no run off means the drivers will need to be on their toes during every moment.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Not to mention how strong tire wear will be during the hard acceleration zones after each full stop braking zone. In an effort to gauge the league's vibes heading into this one, our intern has been polling the league on how many safety cars and incidents we will see. Thus far the results are estimating at least one virtual safety car, two safety cars, and one red flag. Additionally some drivers are expecting there to be as many as ten DNFs during this race.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.vstack(
            rx.text("Baku Circuit", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Baku_Circuit.png",
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
            r"""Last season the league took to the streets in Azerbaijan and chaos did truly ensue. Eddie was on for potentially his first ever win, but crashed out at the top of the castle section. Nick found a tire hack and cruised into a victory with an incredible tire saving strategy, and only two of the league's drivers even finished in the top 10, with Patrick finishing in second. Promoted VCARB driver Brently finished in 11th with Travis, Boz, and Eddie behind. While Del met an untimely end, part way through the race. Erick, Joshua, Zane, Yeti, and Gary did not even make it to the starting line.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""The street circuit showed no mercy and it likely will not this go around. But for the drivers who do survive the heavy braking in the first turn, they will likely be rewarded with a VSC or SC. If the league survives the first turn altogether, they will likely be two wide going into the second turn and then begin to string out into a line on the way down to Turn 3.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""After coming out through Turn 4 the drivers will head directly into the most technical sector of the track. The castle section invites drivers to push the double apex left turn to its very limits and brake just early enough to coast through the sweeping chicane at the top of the castle turret. From there a high speed sweeping turn, similar to what the drivers will face later this season in Jeddah, will take the drivers to the most technical braking zone of the season.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""The downhill, left hand, semi-blind turn will challenge every driver and will potentially catch a few out and end their fight for the podium this race. For those who survive, Sector 3 starts just around the next corner.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Sector 3 is flat out, full tilt, and later in the race, a place where a lapse in judgement will likely see someone smashing into an outside wall. Yet again, for those who survive, the track's only true overtaking zone will occur on the front straight and into the first turn. While some may see Turns 2 and 3 as opportunities to overtake, in many cases drivers will be better off waiting until the start of the lap so that they do not need to defend down the front straight.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.vstack(
            rx.text("Surfer", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/surfer.gif",
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
    "image": "/Season4/Images/Baku_Circuit.png",
    "author": "Patrick",
    "date": "November 3, 2025",
    "season": 4,
}
