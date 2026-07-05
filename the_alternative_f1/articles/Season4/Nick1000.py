import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "A Monumental Milestone",
    "blurb": "Prior to hitting this mark in Mexico, Nick was interviewed and wanted to make sure he could express his gratitude for his teammate Travis and the m...",
    "content": [
        rx.vstack(
            rx.text("1000 Points Nick", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season4/Images/1000 Points Nick.png",
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
            "McLAREN TEAM STATEMENT",
            size="4",
            color="#00b4da",
            margin_top="6",
            margin_bottom="3",
            font_family="Outfit"
        ),
        rx.box(
            rx.text(
                "\"The team here at McLaren is so excited to congratulate Nick on achieving 1000 career points. Over the course of the last four seasons, Nick has battled to earn each of these points and his three Driver's Championships. We know this feat is momentous regardless of circumstances, but to be the league's first 1000 point driver is an extraordinary accomplishment. As the season continues, we look forward to watching Nick smash more records and compete for a fourth Driver's Championship.\"",
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
        rx.text(
            r"""Prior to hitting this mark in Mexico, Nick was interviewed and wanted to make sure he could express his gratitude for his teammate Travis and the man that pushed him to join the league Erick.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.box(
            rx.text(
                "\"Without both Travis and Erick this would never have been possible.\"",
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
        rx.text(
            r"""Our reporters also caught up with his teammate Travis who shared this sentimental image and had this to say:""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.box(
            rx.text(
                "\"Nick, thanks for carrying me since 2023. Congratulations on this huge win.\"",
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
        rx.vstack(
            rx.text("Travis 1000 Points", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season4/Images/Travis 1000 Points.jpg",
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
                src="/thealternativef1-cloudflare/Season4/Images/surfer.gif",
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
    "image": "/thealternativef1-cloudflare/Season4/Images/1000 Points Nick.png",
    "author": "Patrick",
    "date": "October 30, 2025",
    "season": 4,
}
