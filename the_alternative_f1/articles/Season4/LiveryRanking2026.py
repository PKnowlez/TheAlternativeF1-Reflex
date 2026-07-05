import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "2026 F1 Livery Ranking",
    "blurb": "It is time.",
    "content": [
        rx.vstack(
            rx.text("Babe Wakeup", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season4/Images/Livery/Babe Wakeup.png",
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
            r"""It is time. Go crazy nerds and rank to your heart's content.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""If any of you disrespect the Hot Wheels car, let's just say, your points will simply disappear.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            "Click", rx.link("here", href="https://live.tiermaker.com/41582090", color="#00b4da", text_decoration="underline"), "to rank.",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.vstack(
            rx.text("Intern Ranking", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season4/Images/Livery/Intern Ranking.png",
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
                src="/thealternativef1-cloudflare/Images/surfer.gif",
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
                src="/thealternativef1-cloudflare/Images/VideoFile.mp4",
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
    "image": "/thealternativef1-cloudflare/Season4/Images/Livery/Babe Wakeup.png",
    "author": "The Intern",
    "date": "February 9, 2026",
    "season": 4,
}
