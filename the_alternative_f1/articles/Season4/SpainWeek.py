import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "**BREAKING NEWS**",
    "blurb": "Source: Trust me bro - The Intern",
    "content": [
        rx.heading(
            "TWITCH TV TO RETAIN RIGHTS TO CURRENT LEAGUE STREAMS",
            size="4",
            color="#00b4da",
            margin_top="6",
            margin_bottom="3",
            font_family="Outfit"
        ),
        rx.text(
            rx.text("Source: Trust me bro - The Intern", as_="em"),
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.vstack(
            rx.text("Spain Banner", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Spain_Banner.jpg",
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
            r"""IT'S RAWE CEEK!!! After an early season break the league returns to action in Spain. With the drama of Miami behind us, the league is primed and ready for a heater in Spain.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""While Miami posed a challenge for the drivers because of its tire wear and lack of maintained flow across a lap, Spain provides a new challenge with plenty of flow while still forcing drivers to combat tire wear and one another.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Last season, the drivers took to Spain and had a jaw dropping race. Battles in the front, mid, and back field ensued throughout the entire race. After all the tire marbles settled, Alpine's Joshua took home the win but lost his incredible streak of Fastest Laps. McLaren's Nick and Ferrari's Erick finished on the podium respectively.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Then VCARB's Brently took home 4th place with retired Red Bull driver Yeti just behind him. Further back in 6th was VCARB's Patrick who took home the Fastest Lap after taking damage earlier in the race. Aston Martin's Del found himself finishing in 8th, with McLaren's Travis in 18th and Alpine's Eddie in 19th. The then Red Bull driver Boz, retired Ferrari driver Zane, and retired Aston Martin driver Gary all were unable to start the race.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.vstack(
            rx.text("Spain Circuit", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Spain_Circuit.png",
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
            r"""This year though, the competition seems a bit steeper up near the front, with multiple drivers and teams competing for wins and podiums. The drivers who make the most of their tires and avoid disaster early will likely bring home big point hauls in Spain.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""The circuit is not designed for catching up from too far back, so staying within the wake of the car in front will be critical for each driver. However, this could prove challenging as much of the track is comprised of high and medium speed turns that make it tough to follow with dirty air washing over a car's wings.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Sector 1 is predominantly flat out, other than the medium-hard braking into Turn 1. From there the drivers will likely line up single file into the beginning of Sector 2 at the top of the initial hill climb.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""That braking zone may result in some side-by-side action going into Turn 5 where the driver's may have a decent non-DRS chance to make a few overtakes. Sector 2 then sweeps its way back uphill to the back straight where, after the first lap, we will likely see some DRS usage for overtakes or preparation for overtake on the front straight.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""The third sector of the track is filled with tricky corners for accelerating. Tires will be overheated in this sector as the race proceeds. The drivers near the end of the lap will find themselves going full throttle through the final few corners trying to avoid track limits into the long front straight. As they reapproach Turn 1, moments for overtaking are likely to occur as the combination of the slipstream, DRS, and ERS should allow for some ground to be gained into the braking zone.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""With all this said, this week's race should begin to show some trends for those who are contending for this season's crowns.""",
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
    "image": "/Season4/Images/Spain_Banner.jpg",
    "author": "Patrick",
    "date": "October 16, 2025",
    "season": 4,
}
