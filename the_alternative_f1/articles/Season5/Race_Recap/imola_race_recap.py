import reflex as rx
from the_alternative_f1.articles.components import zoomable_image, image_carousel

article = {
    "title": "The Wunderkind Strikes Again",
    "blurb": "It's peanut butter JELLY time! And you all are getting smoked by this guy. Oh and Bernd got his week off finally.",
    "content": [
        "Wow, I thought Joshua was fast, preseason apparently means nothing. That guy was all smoke and now \
            he's getting owned by his own namesake??? What a story. Rumor has it he doesn't even know how to \
                turn his battery on and fueled his car to maximum...brilliant. But he wasn't the only laughable \
                    driver on track this week, app-guy Patrick decided he didn't really need that front wing or \
                        his 4th place streak. Dude was an absolute catastrophe on wheels. So, let's get down to \
                            business. Roasting you all. Here are some lovely highlights:",
        rx.unordered_list(
            rx.list_item(
                "Eddie logs on and doesn't realize he is in Q3 with literally 2 minutes left.",
                margin_bottom="2",
            ),
            rx.list_item(
                "Newman, Josh, Patrick, and Brently all did laps on wet weather tires...in the dry.",
                margin_bottom="2",
            ),
            rx.list_item(
                "Nick kept ruining his quali laps in Sector 2.",
                margin_bottom="2",
            ),
            rx.list_item(
                "Joshua, not to be out done by Nick, kept ruining his lap in Turn 1.",
            ),
            rx.list_item(
                "The whole Williams team, mechanics, and drivers no-showed.",
            ),
            rx.list_item(
                "And last, but certainly not least, Evelo binned it into the pits on his last quali lap. A true right of passage in The Alternative F1 league. He is now destined for greatness like Joshua and Nick.",
            ),
            list_style_type="disc",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            padding_left="24px",
            margin_bottom="4",
        ),
        "But you all aren't really here for a detailed recap, you guys are here for MEMES. Please enjoy the lovely selection of tomfoolery and shenanigans.",
        rx.grid(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Imola/i1.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Imola/i2.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Imola/i3.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Imola/i4.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Imola/i5.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Imola/i6.gif", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Imola/i7.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Imola/i8.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Imola/i9.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Imola/i10.gif", 
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
        "And with that my lovely friends, look out for a bit of way too early analysis next week followed by some time off before you all wreck over and over in Miami.",
    ],
    "image": "/thealternativef1-cloudflare/Season5/Race_Recap/Imola/imola_title.png",
    "author": "The Intern",
    "date": "September 17, 2026",
    "season": 5,
}
