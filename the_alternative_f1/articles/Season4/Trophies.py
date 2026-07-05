import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Race Week: Monaco",
    "blurb": "This week the league takes to the streets of Monte Carlo, where drivers will be tested around the tightest street circuit on the calendar.",
    "content": [
        rx.text(
            r"""This week the league takes to the streets of Monte Carlo, where drivers will be tested around the tightest street circuit on the calendar. The ultimate racing challenge. A driver's skill, attention, and guts will be tested by this iconic circuit.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Due to this being a post-season race, there are no points, no, only honor, glory, and bragging rights are on the line during this race. On top of the bragging rights, the winner will be awarded an Alternative sylized Monaco trophy.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""With all this said, it is about time to dissect the championship trophies earned by our season champions as well as the special Monaco trophy.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.heading(
            "WHAT'S IN THE CHAMPION'S TROPHY",
            size="4",
            color="#00b4da",
            margin_top="6",
            margin_bottom="3",
            font_family="Outfit"
        ),
        rx.vstack(
            rx.text("Trophys4 Text", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/TrophyS4 Text.png",
                width="100%",
                max_width="400px",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.4)"
            ),
            align_items="center",
            width="100%",
            margin_y="4",
        ),
        rx.vstack(
            rx.text("Trophys4 Photo", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/TrophyS4 Photo.jpg",
                width="100%",
                max_width="400px",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.4)"
            ),
            align_items="center",
            width="100%",
            margin_y="4",
        ),
        rx.heading(
            "MONACO TROPHY",
            size="4",
            color="#00b4da",
            margin_top="6",
            margin_bottom="3",
            font_family="Outfit"
        ),
        rx.vstack(
            rx.text("Monaco Trophy Wide", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Monaco Trophy Wide.png",
                width="100%",
                max_width="400px",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.4)"
            ),
            align_items="center",
            width="100%",
            margin_y="4",
        ),
        rx.vstack(
            rx.text("Surfer", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Images/surfer.gif",
                width="100%",
                max_width="400px",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.4)"
            ),
            align_items="center",
            width="100%",
            margin_y="4",
        ),
        rx.vstack(
            rx.text("Videofile", color="#888888", font_size="xs", margin_bottom="1"),
            rx.video(
                src="/Images/VideoFile.mp4",
                width="100%",
                height="auto",
                controls=True,
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.4)"
            ),
            align_items="center",
            width="100%",
            margin_y="4",
        ),
    ],
    "image": "/Season4/Images/TrophyS4 Text.png",
    "author": "Patrick",
    "date": "January 26, 2026",
    "season": 4,
}
