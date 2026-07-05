import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Race Week - Spa & Spain",
    "blurb": "Motorsports fans are in for a treat.",
    "content": [
rx.text(
    r"""Motorsports fans are in for a treat. The league is kicking off the New Year with a double feature: Spa Part 2 Electric Boogaloo followed by high speed thrills in Barcelona Spain. As the perils of Spa have been covered in a previous post, this will focus on Spain and its high speed twists and turns. Track limits, tire wear, and plenty of places for aggressive overtakes should all combine for an unpredictable event.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.vstack(
    rx.text("Circuit de Barcelona-Catalunya Map", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/thealternativef1-cloudflare/Season3/Images/Spain_Circuit.png",
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
    r"""Once the lights go out the drivers will have a long straight to draft, bump, and position themselves for the first pair of corners. Both are wide enough to allow for drivers to go two or even three wide for the brave. The third corner will require incredible courage for the drivers to be wheel to wheel throughout, but during the first lap who knows what might happen. Sector 2 will help queue up the drivers for the circuit’s back straight. If everyone’s wings, wheels, and side pods are still intact, the drivers will need to test the track limits on their way to the final corner at full tilt. With two DRS straights, there will be plenty of room for conventional overtaking. However, with sweeping high speed and medium speed corners, the circuit will allow for harrowing battles throughout each lap.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.text(
    r"""The drivers will need to respect the track limits both for penalty's sake as well as the heavy amount of gravel that lines the high speed portions of the circuit. Penalties, crashes, and yellow or red flags all could lead to some incredible shifts in the standings. Drivers will also have to battle through the fatigue of the day’s double header. Which they did not have to contend with the last time out in Spain. That outing provided a close race between McLaren’s defending champion Nick and the then Mercedes driver, now Ferrari driver, Erick with the other Ferrari brother, then Aston Martin driver, Zane rounding out the podium. Three of the league’s drivers DNS and two of the AI DNF. Spain should provide plenty of exciting racing for every driver who makes it to the starting line.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
    ],
    "image": "/thealternativef1-cloudflare/Season3/Images/Spain_Circuit.png",
    "author": "Patrick Knowles",
    "date": "December 29, 2024",
    "season": 3,
}
