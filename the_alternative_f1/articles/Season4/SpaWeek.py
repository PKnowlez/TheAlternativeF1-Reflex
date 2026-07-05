import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Race Week: Spa",
    "blurb": "The longest lap on the calendar is here and the league won't just race it once, but twice with a sprint and full race on the docket for Wednesday n...",
    "content": [
        rx.vstack(
            rx.text("Spa Cover", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season4/Images/Spa_Cover.jpg",
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
            r"""The longest lap on the calendar is here and the league won't just race it once, but twice with a sprint and full race on the docket for Wednesday night.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""This will be a particularly grueling battle for many of the drivers with only one true DRS straight and a long defenseive and tight Sector 2. This all leads to a tantalizingly long flat out section up to the famed location of what once was the bus stop chicane.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.vstack(
            rx.text("Spa Circuit", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season4/Images/Spa_Circuit.png",
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
            "The track starts with a bare minimum run down to Turn 1.", rx.text("I have been requested by FIA officials to put a helpful reminder here, BRAKE EARLY.", as_="span", font_weight="bold"), "Turn 1, even on a standard mid-race lap is trecherous. At the beginning of the race it is truly a monster.",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Once the drivers have made it through Turn 1, it's pedal to the floor for the race to the Kemmel Straight. Those with enough gaul might even deploy their ERS up through the winding Eau Rogue twsists up Raidillon. The end of the Kemmel Straight is likely the best place for overtaking on the entire track. The wisest drivers will even allow their opponents to slip away a tiny bit up Eau Rogue, and then close with ERS and DRS on the straight. Overtaking and being side-to-side up the hill is simply put, unwise, for both the attacker and defender.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""After the famed uphill corners and straight, the technical downhill Sector 2 begins. Those running with enough downforce may catchup to the drivers with looser and slipperier setups. There are no traditional overtaking spots during Sector 2. But there are a few spots where an overtake is feasible, but potentially ill-advised.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""As Sector 2 ends, drivers are met with a flat out run all the way into the heaviest braking zone on the circuit. Here we may see a few attempt overtakes, but we may also see some drivers meet their demise as they go wide, hit the wall, or take a spin with a wheel dipped in the grass.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""With a sprint race on the schedule that means the drivers will participate in a special format. A single, short, qualifying session for the sprint and then a reverse grid race based on the results of the sprint race.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Looking back into the league's history, it appears that Nick and McLaren have never lost here. Back-to-back-to-back-to-back wins are on the line for both Jairo and Nick. For Jairo, it would be four straight in season wins. For Nick, it would be four straight wins at Spa. Either way, at least one, if not both of these streaks will end this week.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
    ],
    "image": "/thealternativef1-cloudflare/Season4/Images/Spa_Cover.jpg",
    "author": "Patrick",
    "date": "November 16, 2025",
    "season": 4,
}
