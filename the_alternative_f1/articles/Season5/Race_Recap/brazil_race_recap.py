import reflex as rx
from the_alternative_f1.articles.components import zoomable_image, image_carousel, fia_badge

article = {
    "title": "Jelly Wins? NO, Joshua Wins!",
    "blurb": "Turmoil, stupidity, and lots of yelling. Viva Brasil! And Joshua's first win of the season.",
    "content": [        
        rx.vstack(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Brazil/b6.png", 
                width="100%",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            align_items="center",
            width="100%",
            margin_y="4",
        ),

        "This was a race. And just like in 2008 Brazil delivers another absolute stunner. So yeah, I cannot wait to read the comments and all the cap \
            Joshua is gonna spew all over the place. 'The league's against me,' 'the FIA is a bunch of meanies,' wah wah wah wah wah. But hey, we finally got \
                to use that silly Woody meme again. Maybe that will make him happy. Because the results below sure as hell won't.",

        "Now, I haven't really addressed the elephant in the room. Yes, I was fired. Along with Nick, Patrick, Travis and Erick. We were all subsequently rehired \
            by our dear leader Brently. He is now in the captain's seat. So get ready for his first rulings as Brentuar the dicta-tuar. And because of all the \
                bs paperwork our dear leader made me fill out, I am not writing a single other thing. Enjoy the meme carnage instead. Oh, and the JUICY maFIA \
                    report below.",

        rx.vstack(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Brazil/b1.png", 
                width="100%",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            align_items="center",
            width="100%",
            margin_y="4",
        ),

        rx.text(
            "MEMES!",
            font_weight="bold",
            color="white",
            margin_top="4",
            margin_bottom="2",
        ),

        rx.grid(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Brazil/b2.gif", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Brazil/b3.gif", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Brazil/b4.gif", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Brazil/b5.gif", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Brazil/br1.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Brazil/br3.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Brazil/br2.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Brazil/br4.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Brazil/br5.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Brazil/br7.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Brazil/br6.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Brazil/br8.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Brazil/br10.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Brazil/br11.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Brazil/br9.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Brazil/br12.png", 
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
                rx.heading("DRIVE THROUGH PENALTY GLITCH", font_size="xl", font_weight="bold", color="black", flex="1"),
                rx.text(
                    "For Immediate Release \nOfficial FIA Communication \n2026 Brazilian Grand Prix - VSC Drive Through Glitch",
                    color="#555555",
                    font_size="md",
                    line_height="1.6",
                    white_space="pre-line",
                ),
                rx.divider(border_color="#363635", margin_y="3", width="100%"),
                rx.text(
                    "During the preceedings of the race, official timing and scoring systems incorrectly assessed the Cadillac of Jelly a \
                        drive through penalty while under a Virtual Safety Car. This led to a required drive through penalty being served by \
                            Jelly to ensure his car was not disqualified from the race.",
                    color="black",
                    font_size="md",
                    line_height="1.6",
                ),
                rx.text(
                    "The FIA immediately began investigating and attempted to clarify issues live during the race. However, because the \
                        software systems cannot be controlled during the race, the FIA determined it must rectify the situation post-race. \
                            During review of the moment when the penalty was awarded, no wrong doing from the Cadillac was determined. \
                                The following circumstances were considered when complying with Regulation 7:",
                    color="black",
                    font_size="md",
                    line_height="1.6",
                ),
                rx.unordered_list(
                    rx.list_item(
                        "No intention for abusing the regulations were noted in video review or discussion with the Cadillac driver.",
                    ),
                    rx.list_item(
                        "The Cadillac driver came to a near complete stand still to avoid the delta penalty.",
                    ),
                    rx.list_item(
                        "The Cadillac of Jelly finished the race 14s behind the leader, plus a 3s penalty, resulting in a total net time of 17s behind the leader.",
                    ),
                    rx.list_item(
                        "Joshua's Red Bull and Jelly's Cadillac both raced in clean air on tires with only a single lap of difference in age, with Joshua's tires being fresher.",
                    ),
                    rx.list_item(
                        "All drivers were verbally issued a statement that the FIA would handle the Drive Through glitch after the race.",
                    ),
                    rx.list_item(
                        "Regulation 7 requires that 20s be subtracted from the driver's finishing time, which is the average time a drive through penalty incurs across all pitlanes.",
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
                    "After reviewing the scenario in full detail, the FIA, without Patrick's involvement due to a conflict of interest, determined the following \
                        changes to the race results are necessary.",
                    color="black",
                    font_size="md",
                    line_height="1.6",
                ),
                rx.unordered_list(
                    rx.list_item(
                        "The Cadillac of Jelly moves from ninth place to third (originally first).",
                    ),
                    rx.list_item(
                        "The Red Bull of Joshua has no change (originally moves from first place to second).",
                    ),
                    rx.list_item(
                        "The Ferrari of Jaden has no change (originally moves from second place to third).",
                    ),
                    rx.list_item(
                        "The Mercedes of Jairo moves from third place to fourth.",
                    ),
                    rx.list_item(
                        "The McLaren of Nick moves from fourth place to fifth.",
                    ),
                    rx.list_item(
                        "The Ferrari of Leo moves from fifth place to sixth.",
                    ),
                    rx.list_item(
                        "The Cadillac of Patrick moves from sixth place to seventh.",
                    ),
                    rx.list_item(
                        "The Haas of Brently moves from seventh place to eighth.",
                    ),
                    rx.list_item(
                        "The McLaren of Del moves from eighth place to ninth.",
                    ),
                    list_style_type="disc",
                    color="black",
                    font_size="md",
                    line_height="1.6",
                    padding_left="16px",
                    margin_bottom="2",
                ),
                rx.divider(border_color="#363635", margin_y="3", width="100%"),
                rx.text(
                    "THE ALTERNATIVE F1 DICTA-TUAR-SHIP",
                    color="black",
                    font_weight="bold",
                    font_size="md",
                    line_height="0.5",
                ),
                rx.text(
                    "Where racing meets an iron fist and fair competition.",
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
                rx.heading("ATTEMPTED RACE MANIPULATION", font_size="xl", font_weight="bold", color="black", flex="1"),
                rx.text(
                    "For Immediate Release \nOfficial FIA Communication \n2026 Brazilian Grand Prix - Premature Race Start and Safety Cars",
                    color="#555555",
                    font_size="md",
                    line_height="1.6",
                    white_space="pre-line",
                ),
                rx.divider(border_color="#363635", margin_y="3", width="100%"),
                rx.text(
                    "Once all cars completed their reconnaissance laps and officially returned to the grid for the race start, \
                        one driver started the race start procedures prior to all mechanics and officials safely \
                            clearing the start grid. The FIA deems this an attempt to manipulate the race.",
                    color="black",
                    font_size="md",
                    line_height="1.6",
                ),
                rx.text(
                    "Additionally, during the race, two safety cars were brought out due to the same driver's mistakes. Both of which were \
                        deemed preventable and avoidable. Due to these incidents and the race start error, Red Bull Racing is officially \
                            warned about the reprecussions of race manipulation. The following was used to determine the final verdict.",
                    color="black",
                    font_size="md",
                    line_height="1.6",
                ),
                rx.unordered_list(
                    rx.list_item(
                        "In the stewards office, Eddie admitted to league officials he started the race prematurely.",
                    ),
                    rx.list_item(
                        "During the race there was chatter of if a safety car would help or hinder Joshua, in multiple scenarios.",
                    ),
                    rx.list_item(
                        "Eddie chose to 'Think different' and park it up in the grass, remaining motionless for longer than was deemed reasonable.",
                    ),
                    rx.list_item(
                        "The second safety car caused by Red Bull Racing directly created the scenario in which Jelly's Cadillac received the glitch.",
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
                    "Both Red Bull Racing drivers will be awarded a penalty point to their super license for the remainder of the season. \
                        Eddie will also receive a 1 place penalty to his final result in Brazil (DNF to DNF+1). Due to his honesty with league \
                            officials, this penalty was reduced from a 10s result penalty in the upcoming Silverstone race to a finishing \
                                place penalty in Brazil.",
                    color="black",
                    font_size="md",
                    line_height="1.6",
                ),
                rx.divider(border_color="#363635", margin_y="3", width="100%"),
                rx.text(
                    "THE ALTERNATIVE F1 DICTA-TUAR-SHIP",
                    color="black",
                    font_weight="bold",
                    font_size="md",
                    line_height="0.5",
                ),
                rx.text(
                    "Where racing meets an iron fist and fair competition.",
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
    "image": "/thealternativef1-cloudflare/Season5/Race_Recap/Brazil/brazil_title_base.png",
    "author": "The Intern",
    "date": "October 29, 2026",
    "season": 5,
    "fia": True,
}
