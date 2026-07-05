import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "The Hardware We're Racing For",
    "blurb": "Season 4 brings a refresh to the championship trophy.",
    "content": [
        rx.vstack(
            rx.text("Trophy", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season4/Images/Trophy.png",
                width="100%",
                max_width="400px",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.4)"
            ),
            align_items="center",
            width="100%",
            margin_y="4",
        ),
        rx.text(
            r"""Season 4 brings a refresh to the championship trophy. Like last year, each track is displayed. However, in addition to the tracks, the track name and winner of each track will be displayed. For the Constructor's Championship, the winning team will be listed instead of the winning driver which will be on the Driver's trophy.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""All of these details will be centered around the winner's car which is captured moments before crossing the finish line and claiming their hardware.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""At the bottom of the trophy the driver or team's statistics for the season will be displayed next to their respective IRL trophy for the respective championship.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Each trophy will be created with state of the art 3D printing technology and delivered to each of the winners, runners up, and third place finishers for each championship.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.vstack(
            rx.text("Trophy Side", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season4/Images/Trophy_Side.png",
                width="100%",
                max_width="400px",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.4)"
            ),
            align_items="center",
            width="100%",
            margin_y="4",
        ),
    ],
    "image": "/thealternativef1-cloudflare/Season4/Images/Trophy.png",
    "author": "Patrick",
    "date": "August 24, 2025",
    "season": 4,
}
