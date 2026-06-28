import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "The Legend and The Rookie",
    "blurb": "McLaren rebuilds after Travis retires and Erick’s new found lifestyle takes him away from the sport.",
    "content": [
        "What happens when a seat vacates just weeks before the season begins? A rookie steps into the limelight to showcase their speed. Grayson joins Nick at McLaren in an effort to bring the team back to its former Season 2 championship glory. But will the rookie survive racing in the legend’s shadow?",
        "Nick had a down season last year. Many throughout the paddock are claiming he has peaked. But he has been overheard telling people that his distraction with WEC is over, ensuring that nothing but a championship this season will be considered a success. His Testing of Previous Car (TPC) efforts earlier this pre-season have a handful of pundits believing him.",
        "But what of his teammate? A rookie hasn’t driven for McLaren since their first season in the league. Last season’s rookie class set an incredibly high standard for rookies going forward. Will Grayson have what it takes to score consistently? Our intrepid Intern reached out to Grayson for comments on all this speculation and he said,",
        rx.box(
            rx.text(
                "\"\"",
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
        "His teammate Nick has shown a great deal of public support as well,",
        rx.box(
            rx.text(
                "\"\"",
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
    "image": "/Season5/Grid_Announcements/Grid_McLaren.png",
    "author": "Patrick",
    "date": "July 5, 2026",
    "season": 5,
}
