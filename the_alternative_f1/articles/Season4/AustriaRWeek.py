import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Race Week: Austria (Reverse)",
    "blurb": "The league has never faced a challenge like this one; a track no official F1 race has ever run on, turns no one has ever really tested to the limit...",
    "content": [
        rx.vstack(
            rx.text("Austria Reverse", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/austria_reverse.jpg",
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
            r"""The league has never faced a challenge like this one; a track no official F1 race has ever run on, turns no one has ever really tested to the limit, and a guessing game on what setups and strategies will play out best.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""But that's what makes this something to look forward to. The Red Bull Ring is sure to provide some thrilling racing with it's three DRS zones, uphill sweepers, and tight track limits. While examining the track, it is clear that there are only a few true overtaking locations. The most obvious two spots are at the end of the final DRS zone and Turn 1. The turn at the end of the second DRS zone might entice some drivers, but it is likely not worth the late braking and overtake due to the immediate DRS gift the overtaking driver will give to the driver who was overtaken.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""In addition to the unique DRS enabled overtaking zones, there might be moments at the top of the uphill portion of Sector 2 where a driver could feasibly squeeze their opponents and make a side-by-side maneuver. This opportunity would allow the overtaker to take advantage of the upcoming DRS zone to secure the move.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.vstack(
            rx.text("Austria Circuit", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Austria_Circuit.png",
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
            r"""Since the league has never raced in this configuration, there are no previous results and it is all to play for. However, the league has begun to hear rumors of retirements, team swaps, and even a shakeup in the FIA leadership structure. Below, we will recap some of the rumors from around the leaue.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            rx.text("RUMOR MILL", as_="span", font_weight="bold"), "The strongest rumor running around is that one of the drivers in Papaya will be moving on from their position as a driver to a new rank within the FIA at the end of the season. There are no names associated with this rumor just yet, and it is unclear what role within the FIA is opening up or if a new one is being created. More on this as it develops.",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""In addition to the rumors surrounding McLaren, there are rumors around the upcoming 11th team on the grid. Word on the street is that four drivers are looking to combine forces on what they are calling Team USA. This was discovered from leaked carrier bald eagle messages that the group of four has been sending to covertly communicate their plans. Handwriting analyses are underway and we will likely find answers in the near future on who these potential drivers are.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""With Kick Sauber finding the end of their run as a team this season, there have also been rumors of who might race with rings next year. Some solid rumors are coming in that a good lineup is coming to Audi next season. Whoever these drivers are they "gotta go fast, like Sonic, like Sonic" with all those rings.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
    ],
    "image": "/Season4/Images/austria_reverse.jpg",
    "author": "Patrick",
    "date": "November 10, 2025",
    "season": 4,
}
