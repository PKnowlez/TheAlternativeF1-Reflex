import reflex as rx
from the_alternative_f1.articles.components import zoomable_image, image_carousel, fia_badge
from the_alternative_f1.constructor_colors import CONSTRUCTOR_COLORS

article = {
    "title": "Red Bull, Ferrari,& Cadillac Official Statement - Brazil",
    "blurb": "A league first joint statement from teams. Historic resolution to the final results of the Brazil GP.",
    "content": [
        rx.box(
            rx.vstack(
                rx.heading("JOINT OFFICIAL STATEMENT", font_size="xl", font_weight="bold", color="white", flex="1"),
                rx.divider(border_color="white", margin_y="3", width="100%"),
                rx.text(
                    "TEAM STATEMENT: ",
                    color="white",
                    font_weight="bold",
                    font_size="md",
                    line_height="1.6",
                ),
                rx.text(
                    "Upon request from Cadillac, the FIA evaluated the on track scenario caused by the VSC delta glitch. While the final ruling was \
                        adjuducated fairly within the regulations, drivers from both Red Bull and Ferrari came forward to protest the change in final results. \
                            While protestes were being finalized, the FIA connected all three drivers (Jelly, Joshua, and Jaden), for a joint discussion. \
                                During this discussion the drivers and teams came to a joint decision to honor the FIA's ruling, but request a modification.",
                    color="white",
                    font_size="md",
                    line_height="1.6",
                ),
                rx.text(
                    "Instead of leaving the final result with Jelly claiming victory, the teams determined it was most reasonable to move Jelly to \
                        third place. This was subsequently reviewed and agreed to by the FIA. All three teams want to praise teh current FIA \
                            governing body for their willingness to find a solution that still honors teh spirit of the regulations, while still \
                                ensuring a fair result for the driver that was wronged.",
                    color="white",
                    font_size="md",
                    line_height="1.6",
                ),
                rx.divider(border_color="white", margin_y="3", width="100%"),
                rx.text(
                    "DRIVER STATEMENTS: ",
                    color="white",
                    font_weight="bold",
                    font_size="md",
                    line_height="1.6",
                ),
                rx.text(
                    "Like always, fuck the FIA. Always. Fine me if you want. My respect for Jelly, has only grown from this incident. \
                        That’s a true champion not like others. - Joshua",
                    color="white",
                    font_size="md",
                    line_height="1.6",
                ),
                rx.text(
                    "I will say, Mr. Jelly, not only do I have respect for you as a driver, but as a person. You are a very understanding \
                        man, God bless you. - Jaden",
                    color="white",
                    font_size="md",
                    line_height="1.6",
                ),
                rx.text(
                    "I respect both of you on and off the track. But forgive me for cooking your ass the rest of the season. - Jelly",
                    color="white",
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
            position="relative",
            overflow="hidden",
            border="1px solid #E0E0E0",
            border_left="none",
            _before={
                "content": "''",
                "position": "absolute",
                "top": "0",
                "left": "0",
                "bottom": "0",
                "width": "4px",
                "background": (
                    f"linear-gradient(to bottom, "
                    f"{CONSTRUCTOR_COLORS['Cadillac']} 0%, "
                    f"{CONSTRUCTOR_COLORS['Red Bull']} 50%, "
                    f"{CONSTRUCTOR_COLORS['Ferrari']} 100%)"
                ),
            },
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
