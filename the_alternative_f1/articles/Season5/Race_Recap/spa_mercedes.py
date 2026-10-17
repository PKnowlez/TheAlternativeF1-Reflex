import reflex as rx
from the_alternative_f1.articles.components import zoomable_image, image_carousel, fia_badge
from the_alternative_f1.constructor_colors import CONSTRUCTOR_COLORS

article = {
    "title": "Mercedes Official Statement - Spa",
    "blurb": "With the final results of the race in Spa released, Mercedes has provided a cryptic statement from their lead driver.",
    "content": [
        rx.box(
            rx.vstack(
                rx.heading("MERCEDES OFFICIAL STATEMENT", font_size="xl", font_weight="bold", color="white", flex="1"),
                rx.divider(border_color="white", margin_y="3", width="100%"),
                rx.text(
                    "TEAM STATEMENT: ",
                    color="white",
                    font_weight="bold",
                    font_size="md",
                    line_height="1.6",
                ),
                rx.text(
                    "While the team at Mercedes is remorseful for the circumstances and the actions of our driver, the \
                        penalty provided for the damage done appears exaggerated. Jairo drove from the back all the way \
                            to second with immense pace and racecraft. This final result is a shame. The team understands \
                                the rationale for the penalty, but not the final result. These next races will show our \
                                    commitment to excellent racing.",
                    color="white",
                    font_size="md",
                    line_height="1.6",
                ),
                rx.divider(border_color="white", margin_y="3", width="100%"),
                rx.text(
                    "DRIVER STATEMENT: ",
                    color="white",
                    font_weight="bold",
                    font_size="md",
                    line_height="1.6",
                ),
                rx.text(
                    "It is clear the league is against me. I'm gonna be on my Anakin to Vader arc. \
                        The next 9 races, watch out. What you're about to see is for me, for the controller \
                            players out there, and for my girl. - Jairo",
                    color="white",
                    font_size="md",
                    line_height="1.6",
                ),
                rx.text(
                    "Oh, and to PK, go Seahawks. Fuck them Niners.",
                    color="white",
                    font_style="italic",
                    font_weight="light",
                    font_size="md",
                    line_height="1.6",
                ),
                spacing="3",
                align_items="start",
                width="100%",
            ),
            bg="black",
            padding="20px",
            border_radius="4px",
            border="1px solid #E0E0E0",
            border_left=f"4px solid {CONSTRUCTOR_COLORS['Mercedes']}",
            font_family="sans-serif",
            margin_y="6",
            width="100%",
        ),    
    ],
    "image": "/thealternativef1-cloudflare/Season5/Race_Recap/Spa/OS-mercedes.png",
    "author": "Mercedes PR & Jairo",
    "date": "October 16, 2026",
    "season": 5,
    "fia": False,
}
