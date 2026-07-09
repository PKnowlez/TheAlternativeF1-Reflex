import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Two New Challengers Approach the Grid",
    "blurb": "Williams hopes to bottle the same magic Mercedes had last season with two rookies.",
    "content": [
        "Williams has finally made their way to The Alternative F1's grid with a pairing of rookies. Grayson and Josh C. have arrived ready to cut it up and prove to the grid they are here to fight.",
        "Both drivers join the grid with previous sim racing experience, and Josh even brings a wealth of IRL racing in multiple series. This new pairing has a unique connection to a current driver on the grid. The Intern caught up with Patrick and asked what he thinks about Grayson and Josh.",
        rx.box(
            rx.text(
                "\"After an enourmous amount of coaxing, both Grayson and Josh finally agreed to joining the league. Quite frankly I have been vying for these two to join us for years, and with a little help from Erick, we have gotten them both on the grid. It should be exciting watching these guys race, and I suspect they will form a bond in making fun of me.\"",
                color="#CCCCCC",
                font_style="italic",
                font_size="md",
                line_height="1.6",
            ),
            padding_left="16px",
            border_left="4px solid #00b4da",
            margin_y="6",
            width="100%",
        ),
        "The Williams team back at the factory seem very excited to bring this pairing forward. Due to the large level of previous experience from both drivers, pundits around the paddock are having a hard time stopping themselves from ranking the team well into the midfield."
    ],
    "image": "/thealternativef1-cloudflare/Season5/Grid_Announcements/Grid_Williams.png",
    "author": "Patrick",
    "date": "July 8, 2026",
    "season": 5,
}
