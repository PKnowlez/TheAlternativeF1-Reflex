import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Race Week: Zandvoort",
    "blurb": "What an incredible season thus far.",
    "content": [
        rx.vstack(
            rx.text("Zandvoort", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season4/Images/Zandvoort.jpg",
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
            r"""What an incredible season thus far. Competitive, thrilling, and passionate all around. With five races to go, there has never been a tighter battle for the Driver's Championship. And while the Constructor's Championship is not as tight, there are still plenty of points still on the table.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""After the league survived Austria for a second time, a new driver took the lead of the Driver's Championship. Last season's runner up, and primary Alpine driver, Joshua has taken the lead by just three points.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""McLaren's Nick and VCARB's Patrick swapped places as well, while Mercedes' Jaden closed the gap to the top four just to make things a bit more exciting.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""On the Constructor's side, both Alpine and VCARB closed a small amount on Mercedes. But enough with the season recap, it is time for some analysis of what the drivers should expect in Zandvoort this week.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.vstack(
            rx.text("Netherlands Circuit", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season4/Images/Netherlands_Circuit.png",
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
            r"""When the lights go out, drivers will accelerate down a moderately short starting straight. As they enter the first corner, every driver will need to keep their whits about them as the right hand curb butts directly up against a race ending wall. As drivers proceed through the first corner, the exit could potentially spin out a driver or two on the steep raised curbs.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""This is a theme in Zandvoort. Many of the exit corners have steep, brightly colored, and extremely dangerous curbs that can send a driver straight into a DNF if they are not careful. After surviving the first couple of turns, drivers will be met with the tightly banked fourth corner.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Here we may see some late braking high-to-low overtaking for the drivers who have soft or medium tires strapped on. Those with hard compound tires will be hoping they can keep it on the circuit as they proceed into the high speed winding esses that conclude Sector 1.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""The next Sector is the most braking intensive of the track and is dangerously narrow in some areas. With killer curbs on many turns, Sector 2 will likely be a parade for most of the race.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""But as the drivers leave Sector 2 and enter the next, there will be a chance to close the gap with a small dose of DRS into the modified chicane at the end of the back straight. As drivers exit that section, they will be met with the most dangerous curb on track just before the insanely high speed banked corner leading to the front straight. This portion of the track could provide a thrilling drag race to the finish line on the final lap.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""The league has faced the famous circuit twice before. In both times Erick and Nick have found the podium. Erick won the first outing and Nick won the second. Surprisingly during the first race, no one from the league finished third. However, this year's chmpionship leader Joshua finished third on the podium last time out.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.heading(
            "RUMOR MILL UPDATE",
            size="4",
            color="#00b4da",
            margin_top="6",
            margin_bottom="3",
            font_family="Outfit"
        ),
        rx.text(
            r"""In a surprising twist, McLaren has squashed the rumor that they are losing both of their drivers and have officially resigned Nick to a year-to-year deal. Travis has not officially confirmed that he is leaving the team, but all signs point towards a new role for him in the FIA in the coming season.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""The newest rumor points towards McLaren looking to sign a veteran driver who is in search of a turn-around season next year. With these signings and rumors, silly season has somehow begun with five races left in the championship. When approached about this, Erick was very coy with his answers. Our beat reporter (Intern) believes this is a sign that he may be the mystery signing. Only time will tell.""",
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
    "image": "/thealternativef1-cloudflare/Season4/Images/Zandvoort.jpg",
    "author": "Patrick",
    "date": "December 16, 2025",
    "season": 4,
}
