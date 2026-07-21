import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Meet The Grid",
    "blurb": "A simple overview of this season's grid.",
    "content": [
        "This season the grid is taking shape to be one of the most dynamic in league history. Four rookies take to the tarmac, two original league drivers look to unleash their experience, and a host of other drivers expect ot be in the fight.",
        "From long time teammates like Joshua and Eddie, to newly formed duos like Nick and Del, the grid is full of exciting pairings.",
        "At the onset of the season, pundits from around the league have put their votes in for the first power rankings of the season.",
        "The top contenders are currently Cadillac, the new look McLaren and Mercedes teams, and Red Bull."
        "The midfield, however, is anyone's guess. Haas looks promising, Audi looks balanced, Ferrari has a chip on their shoulders, and Williams is simply an unknown data point.",
        "Strap in for what is sure to be an exciting season, and click below to download the grid.",
        rx.vstack(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Grid_Announcements/Grid_Graphic.png",
                width="100%",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.4)"
            ),
            align_items="center",
            width="100%",
            margin_y="4",
        ),
    ],
    "image": "/thealternativef1-cloudflare/Season5/Grid_Announcements/Grid_Graphic.png",
    "author": "Patrick",
    "date": "July 20, 2026",
    "season": 5,
}
