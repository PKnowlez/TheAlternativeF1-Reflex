import reflex as rx
from the_alternative_f1.articles.components import zoomable_image, image_carousel, fia_badge

article = {
    "title": "Controllers Back in Control",
    "blurb": "Jairo, the Season 4 runner up, was back to his winning ways in Miami, Jaden won another sprint race, and Nick finds himself on the podium yet again.",
    "content": [
        "Real racing? From you lot? Incredible. The sprint, chef's kiss. The race, well...another chef's kiss! Nothing but epic \
            action and clean racing, oh, I am hearing from the field that last part is not entirely true. So, let's bloody talk about it.",

        "First was quali. And what an absolute fuster-cluck that was. Joshua simply doesn't join. Jairo decides it ain't worth doing. \
            And Jelly claims another pole.",

        rx.grid(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Miami/m1.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Miami/m2.png", 
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

        "No cap, goofiest qualifying ever. But hey, sometimes its gotta be stupid for the racing to be epic. \
            And, truly, for once, the racing was actually (I mean it) good? Yeah...I know, completely off-brand \
                for this group of 'drivers'. But the most important thing to note is that Jaden is an absolute \
                    sprint race merchant. This guy is the king of not winning real races, but winning sprints.",

        rx.vstack(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Miami/m3.gif", 
                width="100%",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            align_items="center",
            width="100%",
            margin_y="4",
        ),

        "But not all of the racing was good. Some was atrocious. Talking about whatever that was on Lap 1 \
            Evelo. Pull it together brother. Also, Leo had a heat seeker on for the McLaren's, he was seeing \
                orange one might say. But more about that later, from the maFIA.",

        rx.grid(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Miami/m4.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Miami/m5.gif", 
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
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Miami/m6.png", 
                float="right", 
                width="200px", 
                margin_left="16px", 
                margin_bottom="8px",
                margin_top="8px", 
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            rx.text(
                "So yeah the sprint was bonkers. But the race, also pretty bonkers. Jairo won again, Jelly lost his win streak, \
                Newman ran his car into a ghost, Patrick was on his 4th place grind again, Evelo was trapped behind the \
                safety car, and Joshua, well, he drove erraditcly while fighting Nick, which is par for the course.",
                color="#E0E0E0",
                font_size="md",
                line_height="1.7",
            ),
            width="100%",
            margin_bottom="4",
        ),
        
        rx.grid(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Miami/m7.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Miami/m8.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Miami/m9.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Miami/m10.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Miami/m11.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Miami/m12.png", 
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

        "With all that said, there is some important business to attend to. If you are anyone except Leo, enjoy.",

        rx.box(
            rx.vstack(
                rx.heading("INCIDENT BETWEEN McLAREN & FERRARI", font_size="xl", font_weight="bold", color="black", flex="1"),
                rx.text(
                    "For Immediate Release \nOfficial FIA Communication \n2026 Miami Grand Prix - Lap 1 Incident",
                    color="#555555",
                    font_size="md",
                    line_height="1.6",
                    white_space="pre-line",
                ),
                rx.divider(border_color="#363635", margin_y="3", width="100%"),
                rx.text(
                    "Upon petition by McLaren, the FIA has reviewed the incident between Del and Leo during the opening lap of last night's race. \
                        The review entailed analyzing onboard video feeds and telemetry of multiple vehicles, including but not limited to both cars involved, \
                            cars ahead, and cars behind the incident.",
                    color="black",
                    font_size="md",
                    line_height="1.6",
                ),
                rx.text(
                    "A determination was made by reviewing the incident against fair racing criteria and the mitigating circumstances around this scenario. The following \
                        are the primary findings of this investigation.",
                    color="black",
                    font_size="md",
                    line_height="1.6",
                ),
                rx.unordered_list(
                    rx.list_item(
                        "Del's McLaren was ahead going into the incident.",
                    ),
                    rx.list_item(
                        "Del's McLaren collided with the right side wall and moved to the left prior to Leo coming completely alongside.",
                    ),
                    rx.list_item(
                        "The incident occurred during Turn 9 of the circuit.",
                    ),
                    rx.list_item(
                        "Leo's Ferrari was not front axle to front axle with Del's McLaren at the apex of the turn.",
                    ),
                    rx.list_item(
                        "Leo's Ferrari did have time to back out of the move prior to the collision.",
                    ),
                    list_style_type="disc",
                    color="black",
                    font_size="md",
                    line_height="1.6",
                    padding_left="16px",
                    margin_bottom="2",
                ),
                rx.text(
                    "Leo's Ferrari did not have the racing right to continue the move (behind at the apex), and \
                        it was determined that there was enough time to take mitigating or avoiding action, which were not taken.",
                    color="black",
                    font_size="md",
                    line_height="1.6",
                ),
                rx.text(
                    "VERDICT: ",
                    color="black",
                    font_weight="bold",
                    font_size="md",
                    line_height="1.6",
                ),
                rx.text(
                    "Leo's Super License will have a penalty point added to it. Along with this, Leo will be unable to qualify during \
                        the next race they compete in.",
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
    "image": "/thealternativef1-cloudflare/Season5/Race_Recap/Miami/miami_title.png",
    "author": "The Intern",
    "date": "October 1, 2026",
    "season": 5,
    "fia": True,
}
