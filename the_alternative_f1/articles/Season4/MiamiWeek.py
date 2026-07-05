import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Race Week: Miami",
    "blurb": "With the drama of Bahrain solidly in the rearview mirror, the drivers have their eyes set on Miami's Hard Rock Stadium.",
    "content": [
        rx.vstack(
            rx.text("Miami Header", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season4/Images/Miami_Header.jpg",
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
            r"""With the drama of Bahrain solidly in the rearview mirror, the drivers have their eyes set on Miami's Hard Rock Stadium. A temporary street circuit with high speed turns, low speed thrills, and plenty of passing opportunities; Miami should provide some excellent racing.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""On top of the circuit itself, the league will be facing its first sprint of the year. That means drivers and teams need to come prepared with multiple tire strategies and the right setup to be fast during a short stint but safe on tires in a longer stint.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Drivers will qualify in an abbreviated qualifying format and head into the sprint race. Finishing position means everything for the points and for starting position during the main race. The race's grid will be set in reverse order from the final standings of the sprint race, likely lining up early championship front runners in the backfield and enabling huge opportunities to level the playing field across the standings.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""When the lights go out, the drivers will accelerate up to Turn 1 where heavy braking could induce some incidents. In the best case scenario, the drivers all make it out unscathed and rapidly rip through Turns 2 & 3 on their way into the complicated esses of Turns 4, 5, & 6. At this point the drivers are likely to be lined up like ducks in a row following the leader into Sector 2.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""While there are a few bends between Turns 8 and 11, the drivers will be slipstreaming down this nearly straight high speed section. In later laps, this will serve as a primary overtaking location with the aid of DRS and a good exit from Turn 8. However, during Lap 1 the drivers are likely to keep it steady through here and prepare to attack in Sector 3 under heavy braking going into Turn 17 or early on the front straight and into Turn 1.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.vstack(
            rx.text("Miami Circuit", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season4/Images/Miami_Circuit.png",
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
            r"""The league hasn't had an official race in Miami since Season 1 where Miami's biggest hater (McLaren's Nick) took home the win with a double podium for the then Mercedes drivers Erick and Marcus.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Nick and Erick both qualified where they finished, but Marcus battled up from 5th to finish on the podium. McLaren's Travis fell from qualifying 3rd into finishing in 9th. Then Red Bull driver Boz qualified in 6th and battled up to 4th with then Aston Martin driver Zane doing nearly the exact opposite, going from 4th to 7th.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""The league recorded a pre-season session in Miami at the onset of Season 3 where Alpine's Joshua took home the win with Nick and VCARB's Patrick rounding out the podium. Ferrari's Erick missed the podium by mere seconds landing himself in 4th with Red Bull's Yeti and Boz in 16th and 17th respectively, and Aston Martin's Del and Gary in 18th and 19th respectively.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""With a sprint and reverse grid race in play, this week's race has the ability to really shift the standings early on and create an even playing field for many of our drivers going into the first break of the season.""",
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
    ],
    "image": "/thealternativef1-cloudflare/Season4/Images/Miami_Header.jpg",
    "author": "Patrick",
    "date": "October 4, 2025",
    "season": 4,
}
