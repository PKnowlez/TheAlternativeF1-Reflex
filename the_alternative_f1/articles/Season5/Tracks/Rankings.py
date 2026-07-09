import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Track Rankings",
    "blurb": "It is time to rank this season's tracks!",
    "content": [
        "With all tracks selected by drivers, it is time to rank them all from the greatest of all time to not worth licking the asphalt. Honestly, some of you picked some trash tracks, you better hope other people don't agree with me...talking about you Singapore.",
        "Here are a few things you need to know:",
        rx.box(
            rx.text(
                "\"1) Only 14 of the se tracks will make it to the regular season.\"",
                "\"2) 3 of these tracks are already guaranteed to be on the season calendar, but I won't be telling you which are safe.\"",
                "\"3) The two lowest ranked tracks that aren't one of the 3 mentioned in rule 2, will be used for preseason, so no worries we are racing them all!\"",
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
        rx.center(
            rx.link(
                rx.button(
                    "Rank the Tracks",
                    bg="#00b4da",
                    color="white",
                    padding_x="6",
                    padding_y="4",
                    border_radius="xl",
                    cursor="pointer",
                    _hover={
                        "bg": "#0093b3",
                        "box_shadow": "0 0 15px rgba(0, 180, 218, 0.4)",
                        "transform": "scale(1.05)",
                    },
                    transition="all 0.25s ease-in-out",
                ),
                href="https://live.tiermaker.com/68117289",
                is_external=True,
                text_decoration="none",
                _hover={
                    "text_decoration": "none",
                }
            ),
            width="100%",
            margin_y="6",
        ),
    ],
    "image": "/thealternativef1-cloudflare/Season5/Schedule Announcement/Season5Tracks.png",
    "author": "The Intern",
    "date": "July 9, 2026",
    "season": 5,
}
