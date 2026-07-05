import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Race Recap: Austria (Reverse) - The Hills Were Certainly Alive with Something",
    "blurb": "Restarts, safety cars, dial up internet, and a whole lot of 'inchidents,' this week's race was simply lovely.",
    "content": [
        rx.vstack(
            rx.text("Austriarcover", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season4/Images/AustriaRCover.png",
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
            r"""Restarts, safety cars, dial up internet, and a whole lot of 'inchidents,' this week's race was simply lovely. I thrive on chaos and the notes for this race recap are filled with insane little chaotic moments. There apparently was even some reckless driving. I am so looking forward to these memes. But before I jump into memes, here is the abbreviated formal recap:""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.box(
            rx.text(
                "\"Qualifying got under way and a couple drivers reported injuries and illness. This lead to self proclaimed Captain Slow making it into Q3, which meant all 4 Red Bull sponsored drivers were in the final round. Allthough, with 4 out of 10 drivers in the mix you would assume they could, I dunno, get into the top 4. Wrong. They suck. The top 4 was occuppied by a throwback pair on the front row with Alpine's Joshua and McLaren's Nick followed by the rising Mercedes duo on the second row. The VCARB duo were split up by a dude who had 5 total points. Patrick really needs to get it figured out because he's getting bodied by a rookie in qualifying lately and lost to Alpine's Eddie. Leo the lone Ferrari in Q3 has started to show his stuff and qualified in 8th. Behind him were the Red Bull bozos prepping for their weekly last to mid field runs they are pros at. After qualifying the race was supposed to get underway, but people couldn't listen to instructions and kept trying to be absolutely ridiculous into Turn 1. From going 3 wide to forgetting to brake, there ended up being multiple restarts due to all these numbskulls driving like grannies after a night at the bingo hall and one too many glasses of fruit punch. Once the drive got underway, there were incidents left, right, and center. I'll keep those for the memes below. But, spoiler, Joshua couldn't do crap and ended up losing to Jairo for a third straight race.\"",
                color="#CCCCCC",
                font_style="italic",
                font_size="md",
                line_height="1.6",
            ),
            padding_left="16px",
            border_left="4px solid #00b4da",
            margin_y="6",
            width="100%",
        ),
        rx.vstack(
            rx.text("Austriarmemes", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season4/Images/AustriaRMemes.png",
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
            r"""So yeah, it was wild. But this means that Mercedes has a commanding lead in the Constructor's Championship and, unsurprisingly, the man with three straight wins is now leading the Driver's Championship by 9 points.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Not that I am superstitious, but no driver has been able to hold the Driver's Championship lead for more than two straight weeks so far this season. So the writing is on the wall, someone else may jump into first in Spa next week with a Sprint and Race on the schedule.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Whatever happens, I just hope we get some full blown carnage. It's been a tiny bit too clean for my liking these past few races.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.vstack(
            rx.text("Austriarend", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season4/Images/AustriaREnd.png",
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
    "image": "/thealternativef1-cloudflare/Season4/Images/AustriaRCover.png",
    "author": "The Intern",
    "date": "November 13, 2025",
    "season": 4,
}
