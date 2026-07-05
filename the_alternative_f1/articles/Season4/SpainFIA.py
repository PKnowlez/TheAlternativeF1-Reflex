import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "BREAKING NEWS",
    "blurb": "The FIA has released a ruling on the incident that caused immense drama during last night's race.",
    "content": [
        rx.text(
            r"""The FIA has released a ruling on the incident that caused immense drama during last night's race. In a surprising twist, the ruling body did not award either driver any form of race altering penalty. The findings were thorough and involved the review of expert racers from outside of the league.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""No official statements have been shared thus far from teams. However, murmors around the league are beginning.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""With this ruling in place, three drivers now have Super License points for the remainder of the season. Should these drivers or others continue to gain penalty points, they will incur larger penalties when they are involved in a more severe incident that ends or ruins another driver's race.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
    ],
    "image": "/Season4/Images/Trophy.png",
    "author": "Patrick",
    "date": "October 23, 2025",
    "season": 4,
}
