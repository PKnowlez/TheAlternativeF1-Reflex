import reflex as rx
from the_alternative_f1.articles.components import zoomable_image, image_carousel, fia_badge
from the_alternative_f1.constructor_colors import CONSTRUCTOR_COLORS

article = {
    "title": "Cadillac Official Statement - Brazil",
    "blurb": "A level headed and realistic response to the compromise made regarding Brazil's final result.",
    "content": [
        rx.box(
            rx.vstack(
                rx.heading("OFFICIAL STATEMENTS", font_size="xl", font_weight="bold", color="white", flex="1"),
                rx.divider(border_color="white", margin_y="3", width="100%"),
                rx.text(
                    "TEAM STATEMENT: ",
                    color="white",
                    font_weight="bold",
                    font_size="md",
                    line_height="1.6",
                ),
                rx.text(
                    "The team here in Fishers, Indiana are full of mixed emotions. Proud of our driver Jelly for his accomplishments this season, \
                        disappointed in the scenario that unfolded in Brazil, and grateful for competitors willing to have a joint discussion. \
                            As we proceed forward, we know we have taken the high road, and appreciate that the FIA was willing to bend the rules \
                                in such a way that the spirit of competition can remain strong. Regulation 7 saved Jelly's race, but in reality, \
                                    his great drive earned him the right to employ the regulation. We will never regret this decision and have no \
                                        expectation that we will ever look back on this moment with anything other than integrity.",
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
                    "I believe I fought hard for a podium spot in Brazil and have proved to the league that I am one of the best drivers. \
                        It pains me that I had to take a DT penalty and I pushed like hell to make up the necessary time to finish within 20 \
                            seconds of the race leader at the checkered flag. I believe that by the rules I earned P1 but I also admit that \
                                I did not have to fight for a podium spot at the end of the race and I would have loved that battle. This is \
                                    not how I want to win, at the back of the grid with a bogus DT penalty instead of up front with the greatest \
                                        names of this league.",
                    color="white",
                    font_size="md",
                    line_height="1.6",
                ),
                rx.text(
                    "If the race ended at that last safety car I would have finished P3 behind Joshua and Jaden and I accept P3 as my official position. \
                        I have huge respect for Joshua and Jaden, I am frustrated at the missed opportunity to race them to the flag.",
                    color="white",
                    font_size="md",
                    line_height="1.6",
                ),
                rx.text(
                    "I accept this demotion because I have full confidence in my abilities and I will prove in Silverstone and the rest of the season why \
                        I can be world champion. This is a setback and the first time this season I have not led the championship but know that this will \
                            only strengthen me. - Jelly",
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
            border="1px solid #E0E0E0",
            border_left=f"4px solid {CONSTRUCTOR_COLORS['Cadillac']}",
            font_family="sans-serif",
            margin_y="6",
            width="100%",
        ),    
    ],
    "image": "/thealternativef1-cloudflare/Season5/Race_Recap/OS-cadillac.png",
    "author": "Cadillac PR & Jelly",
    "date": "October 30, 2026",
    "season": 5,
    "fia": False,
}
