import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Alpine Team Statement: Spain Incident",
    "blurb": "Now that's what I call racing.",
    "content": [
        rx.vstack(
            rx.text("Spain Alpine Statement", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Spain Alpine Statement.png",
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
            r"""Now that's what I call racing. Dirty air, mistakes, and battles for every single position. From qualifying, to the start, to the finish, this race was insane.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Let's just get qualifying out of the way. McLaren came in without even a tiny bit of a game plan. Something to do with Papaya Rules and making things fair... This lack of a plan lead to them starting in 13th and 14th, with Aston Martin's Del showing up hella late and starting in 15th.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""The Mercedes wunderkinds showed out. Jairo took his second pole position of the season and is starting to show up as a mainline contender, and the dude is just a rookie. Jayden was cooking during Q1 and Q2 but slowed up a bit in Q3, landing 5th on the gird for the race start.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""A shock performance from VCARB's Josh put him way the heck up the grid into 3rd and the Red Bull rookie Matthew also out performed his teammate to start in 4th.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""But, that's enough of all that reading, please enjoy the two major highlights of qualifying in meme form.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.vstack(
            rx.text("Spain Qualifying", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Spain Qualifying.png",
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
            r"""Now, once qualifying was settled Del decided he would grace the league with his presence and joined the race. And boy did he have a race! Something about some super powers from something he ate or something. It wasn't clear what he ate in Patrick's notes, but whatever it was, he should do that again. From 15th to 8th in a normal race format is in--wait for it--sane.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""But that was not the only insanity that the race brought ot us. Oh no, we had much, much more. I'm bringing back a classic format here for this recap. If you're a fan of my origin story, you'll recognize this as an homage to the first ever article that the league let me write. Enjoy.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.vstack(
            rx.text("Spain Race", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Spain Race.png",
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
            r"""1) Sabotage - Matthew did his best to crash out Patrick 2) The power of friendship - Josh and Patrick unite as a team 3) Top tier tango - Jairo and Joshua go all out 4) A new career approaches, bus driver - Erick reveals a hidden talent 5) Eddie "No Balls" Tavera Jr. - Eddie's failed overtake on Erick 6) Mystery VSC - Who knows why this even happened 7) Eddie "Delta Denier" Tavera Jr. - Eddie ignores his delta 8) Del sees red - Something about whatever he ate 9) Blue flag of death - Boz's race ending moment 10) Josh "Delta Denier" Anderson - Josh ignores his delta 11) Wide boi Josh - The SoCal Minister of Defense 12) Jairo the hero - A first win!""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""For those who came to watch some racing, there were some epic moments. For those who came for the soap opera, don't worry there was DRAMA after the race in the cooldown room.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Pink and orange clashed just like they do in color theory. The McLaren duo argued that Eddie drove erratically while the boys in pink defended that it was just a racing incident.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""The verdict is still out on this one, but one thing is clear, the McLaren and Alpine rivalry is alive and well.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Enough with that nonsense though, how does this change the standings? VCARB jumps up back into the lead of the Constructor's fight and Nick slips behind Joshua and Patrick in the Driver's Championship.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Jairo and Matthew both made up 4 places in the field, while also skyrocketing their team's standings. Most importantly, this is Jairo's first win in the league.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""The season is still young, but it is turning out to be a banger thus far. I can't lie, I live for this drama. Until next time nerds.""",
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
    "image": "/Season4/Images/Spain Alpine Statement.png",
    "author": "The Intern",
    "date": "October 23, 2025",
    "season": 4,
}
