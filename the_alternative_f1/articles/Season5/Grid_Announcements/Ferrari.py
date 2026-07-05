import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Forza Ferrari",
    "blurb": "A ferrocious new look Ferrari looks to capitalize during the year of the horse.",
    "content": [
        "Last season, Leo made his debut for Ferrari as a rookie in the league. After a shaky start, it was clear he had the factory's full support. With the confidence of the team at his back, Leo is joined by another rookie from last season, Jaden.",
        "The duo looks to bring Ferrari a championship this season. But will pecking order and intra-team rivalry cause havoc? Or will the sophomore drivers put down the stigma and just drive?",
        "With Jairo remaining at Mercedes and Erick lost to a cult, it seems likely that Jaden and Leo will work together to strive for Leo's first championship and a repeat for Jaden.",
        "An anonymous mechanic at Ferrari had this to say about the pair,",
        rx.box(
            rx.text(
                "\"We truly support both our drivers here at Ferrari. We think that is evident in how we went racing last year. Even when Leo had his chaotic moments, we rallied around him and ensured he was ready for success. By the end of the season we think we unlocked the right setup and driver combination that helped propel Leo to new heights. We plan on doing the same for him and Jaden this season as we look to shake things up at the top of the field.\"",
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
        "A combination of pedigree and an upward trend at the end of last season should allow Ferrari to reclaim a top spot this season. But with new regulations and other driver pairings still to come, pundits are not totally confident on exactly how far up the order these two will make it."
    ],
    "image": "/thealternativef1-cloudflare/Season5/Grid_Announcements/Grid_Ferrari.png",
    "author": "Patrick",
    "date": "July 5, 2026",
    "season": 5,
}
