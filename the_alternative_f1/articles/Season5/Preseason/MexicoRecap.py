import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Mexico Recap: Vamos Safety Car",
    "blurb": "Bernd earned his paycheck during this one, and then some.",
    "content": [
        "Guys, it isn't even the regular season, wtf was all that? Be so for real with me right now why are we five wide during a restart. I have seen better racing from Toto's kid Jack, in his Mercedes Power Wheels.",
        "But it wasn't just the restarts, the whole race was a disaster. Jelly DSQing himself with his 'strategy,' Jairo with a DNF, and let's not even start with Brently getting 'ooo shinied.' I expect insanity from you all but you've genuinely raised the bar to inifinity and beyond. Ok, so just watch this ridiculous restart and then catch back up with me when you realize that was toddler level decision making.",
        rx.vstack(
            rx.video(
                src="/thealternativef1-cloudflare/Season5/Preseason/Mexico/mex5wide.mp4",
                width="100%",
                height="auto",
                controls=True,
                loop=True,
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.4)"
            ),
            align_items="center",
            width="100%",
            margin_y="4",
        ),
        "Ok, so have you learned your lesson? No? I didn't think so. Well, the race was truly crazy. So many safety cars, penalties streaming in via the bot, and honestly all 13 drivers doing some both great and truly unspeakable things.",
        "Oh! And dont forget you can click and download the memes now, you're welcome.",
        rx.grid(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Preseason/Mexico/mex1.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Preseason/Mexico/mex2.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Preseason/Mexico/mex3.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Preseason/Mexico/mex4.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Preseason/Mexico/mex5.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Preseason/Mexico/mex6.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Preseason/Mexico/mex8.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Preseason/Mexico/mex7.png", 
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
        "To close this article out, I do need to inform you all of a few changes for the next race in Vegas. Below is a short statement from the league's maFIA.",
        rx.box(
            rx.vstack(
                rx.text(
                    "During the first pre-season outing, the FIA and race stewards agreed to two major rules downgrades to allow the league to ease into racing again.",
                    color="#CCCCCC",
                    font_style="italic",
                    font_size="md",
                    line_height="1.6",
                ),
                rx.text(
                    "First, the damage a vehicle could sustain was reduced to Damage: Simulation & Damage Rate: Standard. For the next pre-season race, the Damage Rate will be increased to Simulation. Second, Parc Ferme was not enforced between qualifying and the race. In the next pre-season race it will be enforced to ensure parity across qualifying and the race.",
                    color="#CCCCCC",
                    font_style="italic",
                    font_size="md",
                    line_height="1.6",
                ),
                rx.text(
                    "Finally, as a first warning to all drivers, any intentional dive-bomb or endangering another driver will carry consequences once the season begins.\"",
                    color="#CCCCCC",
                    font_style="italic",
                    font_size="md",
                    line_height="1.6",
                ),
                spacing="3",
                align_items="start",
                width="100%",
            ),
            padding_left="16px",
            border_left="4px solid #00b4da",
            margin_y="6",
            width="100%",
        ),
    ],
    "image": "/thealternativef1-cloudflare/Season5/Preseason/Mexico/mexTitle.png",
    "author": "The Intern",
    "date": "August 13, 2026",
    "season": 5,
}
