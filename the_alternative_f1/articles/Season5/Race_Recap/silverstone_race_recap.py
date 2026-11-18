import reflex as rx
from the_alternative_f1.articles.components import zoomable_image, image_carousel, fia_badge

article = {
    "title": "The King Is Back",
    "blurb": "This guy seems to only win when he profusely complains about a track. Miami S4, Silverstone S5, what's next?",
    "content": [        
        rx.vstack(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Silverstone/s9.png", 
                width="100%",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            align_items="center",
            width="100%",
            margin_y="4",
        ),

        "No cap, an interesting race. I am not about to sit here and glaze Nick, but dayum, ok boomer, nice moves. Now on the young guy side, Jaden might be \
            making some moves in the standings. And this Jelly guy? Honestly, he's just bad at sprints at this point. Del did have a heater too all the way to \
                fourth at the finish line. Now, other than that, the rest of you \
                need to learn how to drive. Leo driving into people. Newman going ghost mode. Stig doing his best Slowbro impersonation. Brently and PK just \
                    being dogwater. Jairo and Evelo were you even there? Oh and Eddie, what a promising start, but his flash of brilliance was dimmer than \
                        than one of those potato lights people made for the science fair. So yeah, not much to report on. I'm lazy. Enjoy the memes. Intern OUT.",

        rx.grid(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Silverstone/s1.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Silverstone/s2.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Silverstone/s3.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Silverstone/s4.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Silverstone/s5.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Silverstone/s6.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Silverstone/s7.gif", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Silverstone/s8.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            columns="2",
            spacing="3",
            width="100%",
            margin_bottom="4",
        ),

        rx.box(
            rx.vstack(
                rx.heading("DOUBLE OVERTAKE CONTACT", font_size="xl", font_weight="bold", color="black", flex="1"),
                rx.text(
                    "For Immediate Release \nOfficial FIA Communication \n2026 Silverstone Grand Prix - Double Overtake Contact",
                    color="#555555",
                    font_size="md",
                    line_height="1.6",
                    white_space="pre-line",
                ),
                rx.divider(border_color="#363635", margin_y="3", width="100%"),
                rx.text(
                    "Following the race, a review ensued of an incident including the Cadillac of Patrick, the Haas of Brently, and the Red Bull of Joshua. This \
                        review analyzed an on track incident where Brently and Patrick were engaged in side-by-side action with Joshua closely following. \
                            Prior to entering the famous esses of Silverstone, Joshua attempted to overtake both Brently and Patrick. The following are details \
                                pertaining to that overtake:",
                    color="black",
                    font_size="md",
                    line_height="1.6",
                ),
                rx.unordered_list(
                    rx.list_item(
                        "Brently and Patrick were directly wheel to wheel, with the Cadillac slightly ahead of the Haas on the right side.",
                    ),
                    rx.list_item(
                        "The Red Bull contact the left barge board of the Cadillac and the right floor and sidepod of the Haas.",
                    ),
                    rx.list_item(
                        "The Red Bull passed both the Cadillac and the Haas through this maneuver.",
                    ),
                    rx.list_item(
                        "Joshua, within half a lap, returned the place to Patrick. Brently had fallen more than one place behind due to the contact at this point.",
                    ),
                    rx.list_item(
                        "Directly after the esses, there was an opportunity to return the place to both drivers that was not used.",
                    ),
                    rx.list_item(
                        "Regulation 16 allows for FIA judgement based on the level of damage sustained by cars within the incident.",
                    ),
                    list_style_type="disc",
                    color="black",
                    font_size="md",
                    line_height="1.6",
                    padding_left="16px",
                    margin_bottom="2",
                ),
                rx.text(
                    "VERDICT: ",
                    color="black",
                    font_weight="bold",
                    font_size="md",
                    line_height="1.6",
                ),
                rx.text(
                    "After review the FIA, without Brently or Patrick involved, determined that Regulation 16 must be invoked. However, there were a number of both \
                        escalating and mitigating circumstances that led to the final verdict. First, the damage to both vehicles was irreparable, meaning Regulation \
                            16 allows the FIA to apply either a 2 or 3 place penalty. Second, Joshua carries two (2) penalty points on his license, which means \
                                two (2) additional places must be added to the final determination based on Regulation 10. However, Joshua did return the place to \
                                    Patrick in a marginally reasoable timeframe. Therefore, the FIA will remove one (1) of the two additional places required by \
                                        Regulation 10. Additionally, because this was handled on track, prior to FIA discussions, no further penalty points will be \
                                            added to Joshua's super license. Finally, the FIA has determined the contact only meets the two (2) place severity \
                                                of Regulation 16, not the optional three (3) place severity. Therfore, Joshua is handed a two (2) place penalty plus an \
                                                    additional one (1) place penalty, for a total of a three (3) place penalty and NO penalty point addition to his license.",
                    color="black",
                    font_size="md",
                    line_height="1.6",
                ),
                rx.unordered_list(
                    rx.list_item(
                        "The Ferrari of Leo moves from sixth place to fifth.",
                    ),
                    rx.list_item(
                        "The Cadillac of Patrick moves from seventh to sixth.",
                    ),
                    rx.list_item(
                        "The Haas of Matthew moves from eighth to seventh.",
                    ),
                    rx.list_item(
                        "The Red Bull of Joshua moves from fifth to eighth.",
                    ),
                    list_style_type="disc",
                    color="black",
                    font_size="md",
                    line_height="1.6",
                    padding_left="16px",
                    margin_bottom="2",
                ),
                rx.text(
                    "Finally, the FIA would like to openly commend Joshua for taking on track action. Had it occurred in the straight immediately \
                        after the esses, and both the damaged drivers were handed their places back, there would have been no grounds for investigation \
                            or penalty.",
                    color="black",
                    font_size="md",
                    line_height="1.6",
                ),
                rx.divider(border_color="#363635", margin_y="3", width="100%"),
                rx.text(
                    "THE ALTERNATIVE F1 LEAGUE",
                    color="black",
                    font_weight="bold",
                    font_size="md",
                    line_height="0.5",
                ),
                rx.text(
                    "Where racing meets integrity and fair competition.",
                    color="#555555",
                    font_style="italic",
                    font_size="md",
                    line_height="0.5",
                ),
                spacing="3",
                align_items="start",
                width="100%",
            ),
            bg="white",
            padding="20px",
            border_radius="4px",
            border="1px solid #E0E0E0",
            border_left="4px solid #00b4da",
            font_family="sans-serif",
            margin_y="6",
            width="100%",
        ),

        rx.box(
            rx.vstack(
                rx.heading("CADILLAC ATTEMPTED OVERTAKE ON FERRARI", font_size="xl", font_weight="bold", color="black", flex="1"),
                rx.text(
                    "For Immediate Release \nOfficial FIA Communication \n2026 Silverstone Grand Prix - Attempted Overtake In Final Corners",
                    color="#555555",
                    font_size="md",
                    line_height="1.6",
                    white_space="pre-line",
                ),
                rx.divider(border_color="#363635", margin_y="3", width="100%"),
                rx.text(
                    "Upon entering the final three corners, the Cadillac of Patrick attempted an overtake on the Ferrari of Leo. This overtake was deemed \
                        unsafe and unnecessary. However, no complaint was submitted to the FIA. Instead, Cadillac brought forth the evidence openly to \
                            the FIA to ensure racing integrity is upheld. Because of this gesture, the FIA has deemed the below verdict a reasonable punishment \
                                based on the following information.",
                    color="black",
                    font_size="md",
                    line_height="1.6",
                ),
                rx.unordered_list(
                    rx.list_item(
                        "Patrick lost control during an attempted overtake.",
                    ),
                    rx.list_item(
                        "Patrick immediately handed the position back to Leo.",
                    ),
                    rx.list_item(
                        "Neither car lost position on track.",
                    ),
                    rx.list_item(
                        "Leo did not submit this incident for review, Cadiallac did.",
                    ),
                    list_style_type="disc",
                    color="black",
                    font_size="md",
                    line_height="1.6",
                    padding_left="16px",
                    margin_bottom="2",
                ),
                rx.text(
                    "VERDICT: ",
                    color="black",
                    font_weight="bold",
                    font_size="md",
                    line_height="1.6",
                ),
                rx.text(
                    "The Cadillac of Patrick will be awarded one (1) penalty point that will remain on his super license for the remainder of the season. \
                        If another incident occurs, this penalty point will ensure the penalization will adequately impact his results in a future race.",
                    color="black",
                    font_size="md",
                    line_height="1.6",
                ),
                rx.divider(border_color="#363635", margin_y="3", width="100%"),
                rx.text(
                    "THE ALTERNATIVE F1 LEAGUE",
                    color="black",
                    font_weight="bold",
                    font_size="md",
                    line_height="0.5",
                ),
                rx.text(
                    "Where racing meets integrity and fair competition.",
                    color="#555555",
                    font_style="italic",
                    font_size="md",
                    line_height="0.5",
                ),
                spacing="3",
                align_items="start",
                width="100%",
            ),
            bg="white",
            padding="20px",
            border_radius="4px",
            border="1px solid #E0E0E0",
            border_left="4px solid #00b4da",
            font_family="sans-serif",
            margin_y="6",
            width="100%",
        ),    
    ],
    "image": "/thealternativef1-cloudflare/Season5/Race_Recap/Silverstone/silverstone_title.png",
    "author": "The Intern",
    "date": "November 5, 2026",
    "season": 5,
    "fia": True,
}
