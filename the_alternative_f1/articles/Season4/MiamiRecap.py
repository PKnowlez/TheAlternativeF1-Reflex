import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Race Recap - Miami: Vice City Mania",
    "blurb": "Tuh-tuh-tuh-today Junior, or, well, maybe next race.",
    "content": [
        rx.vstack(
            rx.text("Miami Cover", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season4/Images/miami_cover.png",
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
            r"""Tuh-tuh-tuh-today Junior, or, well, maybe next race. Last week one of the McLaren's served a race ban, and this week Alpine's Eddie simply decided not to show up. Something about "I'm going to a party and I don't care if my teammate needs me.\"""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""But that's not where the juice was this week. No, no, no, the drama this week would give reality TV a run for its money. A fast paced sprint, a reverse grid race, restarts, virtual safety cars, safety cars, and a whole lot of FIA intervention.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Honestly, y'all need to get it together with the race starts. Pit-i-ful. Also, veterans and rookies BOTH crashing out during safety cars, smh, pa-the-tic. Truly hard to watch.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""But let's talk the sprint. Teamwork? In The Alternative's league? WILD - truly wild. And to come from two rookies. IN-CRED-IBLE. A stunning sprint race from the Mercedes tandem. But that was pretty much the only positive thing I have in the notes from the sprint.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""The rest of y'all, dreadful racing. Turn 1 turned into a near standstill, Aston Martin's Boz turning himself into a spinning top and Alpine's Joshua forgetting that running into people is bad. Per the usual, my words can only be so good at retelling these tales.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.vstack(
            rx.text("Miami Sprint Memes", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season4/Images/miami_sprint_memes.png",
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
            r"""Enlightening right? Well, let me learn you something about the main race. Because it was stupid. Alpine's Joshua forgot that you have to start when the lights go out not while they are still on. An incredibly smooth brained maneuver that earned him an immediate driver through. SOMEHOW everyone just let him by and he finished third??? Do better people.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""But that was after the race actually started...and that did not happen right away...I'm surprised anyone kept watching any of the streams.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""You know what, I'm over it. Enjoy the memes and I'll be back at the end to do some "journalism" or whatever.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.vstack(
            rx.text("Miami Race Memes", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season4/Images/miami_race_memes.png",
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
            r"""After the FIA put down the hammer on Mercedes' Jayden, the podium was finalized with McLaren's Nick, Red Bull's Brently, and Alpine's Joshua. Somehow the Alpine driver made up for his boneheaded decision at the start of the race and landed on the podium...maybe I should have saved that George Russell meme template for this guy instead of Patrick.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""This was McLaren's first win of the season and Brently's first podium of the season. But for both Nick and Brently, they were the stars of their teams while their teammates finished in 5th...and...well...Matthew didn't finish. Ferrari's Erick somehow started 4th and finished 4th with only Brently and two AI in front of him. Maybe he really is in his Daniel Ricciardo era.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Aston Martin's Del and Mercedes' Jayden found themselves in pitched combat as well as being right near each other in the final standings as they probably would have been if not for the in-chi-dent.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""VCARB's Patrick and Ferrari's Leo also found themselves right next to each other, but instead of being up fighting for a podium they battled for 9th and 10th place respectively. A fall from graces for the driver who was leading the championship.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Aston Martin's Boz rounded out those who finished in 11th. Comfortably ahead of the three rookies who DNF-ed. Really living up to their rookie standings I see. And of course, last but not least, Eddie scored a whopping 0 points and +1 penalty point throughout this week.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""The final results mean McLaren and Nick take over both championships. Maybe the team can close it out this year? But when I asked ChatGPT, it told me to go pound sand, Max Verstappen will make a comeback.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.vstack(
            rx.text("Miami Joshua", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season4/Images/miami_joshua.png",
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
    "image": "/thealternativef1-cloudflare/Season4/Images/miami_cover.png",
    "author": "The Intern",
    "date": "October 10, 2025",
    "season": 4,
}
