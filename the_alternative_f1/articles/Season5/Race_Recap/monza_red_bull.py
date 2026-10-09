import reflex as rx
from the_alternative_f1.articles.components import zoomable_image, image_carousel, fia_badge

article = {
    "title": "Red Bull Official Statement - Monza",
    "blurb": "In response to the Cadillac & Red Bull incident in Monza, Red Bull has provided an official statement.",
    "content": [
        rx.box(
            rx.vstack(
                rx.heading("RED BULL OFFICIAL STATEMENT", font_size="xl", font_weight="bold", color="white", flex="1"),
                rx.divider(border_color="white", margin_y="3", width="100%"),
                rx.text(
                    "TEAM STATEMENT: ",
                    color="white",
                    font_weight="bold",
                    font_size="md",
                    line_height="1.6",
                ),
                rx.text(
                    "First and foremost, the team at Red Bull will not petition the ruling, we wish nothing more than to move on from this moment. \
                        Upon reviewing the ruling from the FIA, Red Bull racing is appalled that this is the level of racing the league is willing to penalize. \
                            This ruling stripped Joshua of his first race win of the season. This ruling hampered the team's constructor championship charge. \
                                This ruling will be remembered as a stain on this season for years to come. Red Bull will continue to go racing and will ensure \
                                    the team is in contention, regardless of this appalling and weak ruling.",
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
                    "As I write this, I must acknowledge the deep respect I have for my competitors. Jelly and the entire Cadillac team are putting on a show. \
                        I respect that. I respect the 3 people I consider competition, you all know who you are. To the FIA though, I do not respect you. \
                            Fine me. I don't care. The FIA has a target on me. The FIA is keeping me down. The FIA is a dictatorship built to stop my dominance. \
                                But no one, ever, can stop me. The FIA can try, my competitors can try, but I will prevail. Going forward, I will let the track \
                                    do the talking. Championship run, loading. - Joshua",
                    color="white",
                    font_size="md",
                    line_height="1.6",
                ),
                spacing="3",
                align_items="start",
                width="100%",
            ),
            bg="#0F172A",
            padding="20px",
            border_radius="4px",
            border="1px solid #E0E0E0",
            border_left="4px solid red",
            font_family="sans-serif",
            margin_y="6",
            width="100%",
        ),    
    ],
    "image": "/thealternativef1-cloudflare/Season5/Race_Recap/Monza/OS-red-bull.png",
    "author": "Red Bull PR & Joshua",
    "date": "October 8, 2026",
    "season": 5,
    "fia": False,
}
