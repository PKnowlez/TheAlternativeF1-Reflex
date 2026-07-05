import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "The Final Race Week - COTA",
    "blurb": "Ya heard right folks.",
    "content": [
rx.vstack(
    rx.text("Texas Charles Leclerc", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/Season3/Images/COTA_Charles.png",
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
rx.text("The cars all lined up", text_align="center", color="#E0E0E0", font_style="italic", font_size="md", line_height="1.5"),
rx.text("Are ready to be fired up", text_align="center", color="#E0E0E0", font_style="italic", font_size="md", line_height="1.5"),
rx.text("Deep in the heart of Texas", text_align="center", color="#E0E0E0", font_style="italic", font_size="md", line_height="1.5"),
rx.text("The track’s finish line", text_align="center", color="#E0E0E0", font_style="italic", font_size="md", line_height="1.5"),
rx.text("Chequered by design", text_align="center", color="#E0E0E0", font_style="italic", font_size="md", line_height="1.5"),
rx.text("Deep in the heart of Texas", text_align="center", color="#E0E0E0", font_style="italic", font_size="md", line_height="1.5"),
rx.text("The season ready to close", text_align="center", color="#E0E0E0", font_style="italic", font_size="md", line_height="1.5"),
rx.text("With standings froze", text_align="center", color="#E0E0E0", font_style="italic", font_size="md", line_height="1.5"),
rx.text("Deep in the heart of Texas", text_align="center", color="#E0E0E0", font_style="italic", font_size="md", line_height="1.5"),
rx.text("A final race tonight", text_align="center", color="#E0E0E0", font_style="italic", font_size="md", line_height="1.5"),
rx.text("Every driver ready to fight", text_align="center", color="#E0E0E0", font_style="italic", font_size="md", line_height="1.5"),
rx.text("Deep in the heart of Texas", text_align="center", color="#E0E0E0", font_style="italic", font_size="md", line_height="1.5"),
            width="100%",
            margin_y="4",
            spacing="1",
            align_items="center",
        ),
rx.text(
    r"""Ya heard right folks. The league has made it to its final circuit of the year in the grand ole U S of A, where the red, white, and blue run thicker than molasses, deep in the heart of Texas. In the state’s capital lies a hallowed track known as the Circuit of the Americas or COTA for short. In the famed state, infamous for its cowboys, guns, and outlaws, our drivers will face a track shaped like a rifle while staring down the barrel of the end of the season. One last chance to taste glory. One last lap with their current teams. One last chance to step one rung higher in the standings.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.text(
    r"""Beyond just being a tricky track with some incredible elevation changes, high speed turns, and lengthy straights, COTA is the home race of McLaren’s Travis and nearly a home race for Ferrari’s Erick, VCARB’s Patrick, and Aston Martin’s Zane. Which means added pressure for them all to perform. Whether it is the steep elevation change up to Turn 1, or down into the esses to follow, every driver is going to be right on the limit of what they and their car can handle. Sector 1 at COTA is no joke. An incredibly steep uphill battle from the starting grid up to Turn 1, followed by high speed thrills down into Sector 2 where the drivers are treated to an incredibly long straight perfect for jockeying for position. From there the battle will continue as the drivers navigate additional high speed twists and turns around an amphitheater and famed 500 foot tall viewing platform. Just as the drivers exit some incredible fast turns they are met with the decision to lift or throttle back into a harrowing corner just before the twentieth and final corner of the lap. Each of these moments will test the entire field and could cause some crazy moments.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.vstack(
    rx.text("Circuit of the Americas Map", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/Season3/Images/COTA_Circuit.png",
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
    r"""All signs now point to a rainy Sprint and a potentially drier race. But until the drivers have passed the final finish line, we won’t know for certain. Rumor has it that many teams are already beginning their search for what is next. Driver line ups are bound to change and rumblings of rookie drivers are all over the media pen. This week will no doubt be a thrilling conclusion to an exciting season. Alpine and McLaren still have a chance at glory in the World Constructor’s Championship, and as previously mentioned, four drivers have a shot at third place in the World Driver’s Championship.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
    ],
    "image": "/Season3/Images/COTA_Charles.png",
    "author": "Patrick",
    "date": "February 11, 2025",
    "season": 3,
}
