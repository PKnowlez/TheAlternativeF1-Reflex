import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "The Rookie and The Vet",
    "blurb": "Audi looks to take the league by storm with their balance of experience and fresh energy.",
    "content": [
        "The German racing outfit is coming in hot with two drivers looking to prove themselves. Senad has been a perennial challenger in The Alternative F1's ranks. While Austin is bringing in a wealth of new energy, and some sources are saying, a wealth of .gifs and memes.",
        "Audi being a new constructor on the grid means the sky is the limit for the team. Expecations are of course set appropriately, but behind the scenes rumors are running through the paddock that the driver pairing is expected to do great things.",
        "Mattia Binotto discussed the team's potential with the media recently,",
        rx.box(
            rx.text(
                "\"There are very few times in this sport when you get the opportunity to truly start from scratch. This moment is one of those moments. The factory is prepared to put it all on the line for our drivers and nothing makes me more excited than seeing the energy the two bring to the garage...and the group chat.\"",
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
        "This season there are four new constructors to the grid. A big question that looms is who will end up supreme among them? And while there isn't much data out there yet, many bets seem to be on Audi."
    ],
    "image": "/thealternativef1-cloudflare/Season5/Grid_Announcements/Grid_Audi.png",
    "author": "Patrick",
    "date": "July 13, 2026",
    "season": 5,
}
