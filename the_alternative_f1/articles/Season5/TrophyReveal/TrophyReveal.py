import reflex as rx
from the_alternative_f1.articles.components import zoomable_image, image_carousel

article = {
    "title": "Season 5 Trophy Reveal",
    "blurb": "With less than a week until the season begins, check out this year's trophy in detail.",
    "content": [
        "A day late, but for good reason. This season's trophy is going where no trophy has gone before, digital. Taking inspiration from Cadillac's entry into Formual 1, this season's trophy is cutting edge and modelled after the wheel Checo and Bottas regularly turn, for at least a couple laps, each race.",
        rx.vstack(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Trophy Reveal/Front.png", 
                width="100%",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            align_items="center",
            width="100%",
            margin_y="4",
        ),
        "But it isn't just a simple trophy. No, this year's trophy will include a digital display of the driver or constructor's season. Each race and its podium will be included, each name inscribed within the graphics on the display. A tactile button, much like ones used in a real F1 car will be used to switch modes and navigate the records within the trophy. Additionally, a small display stand will hoist the trophy high will providing a shelf for a 1:64 scale F1 car to rest. Yes, just like last year a team can choose a scale model provider of their liking and place it with their trophy and of course a placeholder vehicle will be included.",
        "Below you will find a series of renders of the trophy. Each driver or constructor to finish in the top 3 will recieve one. Their place in each championship will be indicated by the dials on the bottom of the wheel. Additionally, you will find a mockup of the loading screen and the individual race infographic that will be populated for each race within the trophy.",
        image_carousel(
            items=[
                "/thealternativef1-cloudflare/Season5/Trophy Reveal/Iso.png",
                "/thealternativef1-cloudflare/Season5/Trophy Reveal/Front.png",
                "/thealternativef1-cloudflare/Season5/Trophy Reveal/IsoWithStand.png",
                "/thealternativef1-cloudflare/Season5/Trophy Reveal/FrontWithStand.png",
                "/thealternativef1-cloudflare/Season5/Trophy Reveal/boot-up.gif",
                "/thealternativef1-cloudflare/Season5/Trophy Reveal/Sample.jpg",
            ],
            auto_progress_seconds=5.0,
            height="420px",
            width="100%",
            margin_y="4",
        ),
    ],
    "image": "/thealternativef1-cloudflare/Season5/Trophy Reveal/Season 5 Trophy.png",
    "author": "Patrick",
    "date": "September 3, 2026",
    "season": 5,
}
