import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Season 4 Champions",
    "blurb": "Congratulations to our Season 4 Champions.",
    "content": [
        rx.flex(
            zoomable_image(src="/thealternativef1-cloudflare/Season4/Images/Championship/JoshuaChampionship.png", width="100%", max_width="500px", border_radius="md", box_shadow="0 4px 12px rgba(0,0,0,0.4)", margin="2"),
            zoomable_image(src="/thealternativef1-cloudflare/Season4/Images/Championship/MercedesChampionship.png", width="100%", max_width="500px", border_radius="md", box_shadow="0 4px 12px rgba(0,0,0,0.4)", margin="2"),
            zoomable_image(src="/thealternativef1-cloudflare/Season4/Images/image.png", width="100%", max_width="500px", border_radius="md", box_shadow="0 4px 12px rgba(0,0,0,0.4)", margin="2"),
            zoomable_image(src="/thealternativef1-cloudflare/Season4/Images/image.png", width="100%", max_width="500px", border_radius="md", box_shadow="0 4px 12px rgba(0,0,0,0.4)", margin="2"),
            flex_wrap="wrap",
            justify="center",
            width="100%",
            margin_y="4",
        ),
    ],
    "image": "/thealternativef1-cloudflare/Season4/Images/Championship/JoshuaChampionship.png",
    "author": "The Alternative F1 League",
    "date": "January 22, 2026",
    "season": 4,
}
