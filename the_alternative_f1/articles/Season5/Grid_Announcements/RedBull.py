import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Red Bull Racing Reborn",
    "blurb": "A team and duo with strong legacies. #FuckJoshua",
    "content": [
        "One of the grid’s most dynamic duos returns. A duo where you never know if it is going to be love or hate coming out of their mouths next. Each passing moment is another bit or antic with these two. Regardless of all of their off-track nonsense, they are a strong contender for this season’s championship. Pundits have them ranked near the top of the grid because of their previous championship campaign in Season 3.",
        "Joshua is clearly aimed at one goal and one goal only, winning, both championships. That is a feat only one team and one driver has ever accomplished, and Joshua seems highly motivated to make this duo the second to ever do it.",
        "One major change to this consistent team is their main sponsor. After a long relationship with the French outfit, Joshua and Eddie have declined to return for a fourth season with Alpine. Instead they have made the swap over to Red Bull Racing. Mekies was heard discussing the negotiation period in the media pen recently where he said,",
        rx.box(
            rx.text(
                "\"The two drivers were a non-negotiable package for us here at Red Bull. Their previous success together, even with its unconventional style, is seen as an extreme asset around the paddock.\"",
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
        "The only rumor still floating around is Eddie’s commitment to the team. In recent times his loyalty seems to be diminishing with new avenues like his collegiate studies taking up time. He did stop to give our Intern one quote before rushing off,",
        rx.box(
            rx.text(
                "\"#FuckJoshua\"",
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
    ],
    "image": "/thealternativef1-cloudflare/Season5/Grid_Announcements/Grid_RedBull.png",
    "author": "Patrick",
    "date": "June 28, 2026",
    "season": 5,
}
