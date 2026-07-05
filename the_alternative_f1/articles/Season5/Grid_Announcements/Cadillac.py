import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Cadillac Racing Roars to Life",
    "blurb": "Can this pair avoid a sophomore slump and take home the crown?",
    "content": [
        "With their second place finish behind them, Patrick and Josh inked a new deal with Cadillac, the newest constructor on the grid. Josh impressed the Indianapolis based team with his impressive rookie season and with Patrick’s ability to avoid a sophomore slump, Cadillac says the negotiations were short and simple. A Cadillac media correspondent also told our beat reporter,",
        rx.box(
            rx.text(
                "\"The team of Josh and Patrick showcase and embody what we call, an unrelenting drive for success. Our goal is simple: win as early and often as we can, and always be in the mix if there are scraps to clean up.\"",
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
        "As last season’s runner-ups, pundits are ranking the Cadillac team nearly as high as the squad at Red Bull Racing. Without a proven championship, some media outlets are worried the pressure may mount too high for the pairing. Keeping eyes on how the two perform and if they keep their cool throughout the season will certainly be a narrative to keep tabs on.",
        "What might be the most likely storyline for these two is who will become the driver up front. Will there be a skirmish? Will there be ‘Papaya Rules,’ or maybe even a Spain 2016 scenario? Maybe their contracts are authored in such a way we run into another ‘Multi-21’ situation. Or maybe, just maybe things will be completely amicable between the brother-in-law duo.",
        "Regardless, it is an exciting second season for this pairing as they strive to improve and take home their first championship. Surprisingly, when approached for comment only Josh was willing to provide a statement,",
        rx.box(
            rx.text(
                "\"I'll do my talking on the track.\"",
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
    "image": "/thealternativef1-cloudflare/Season5/Grid_Announcements/Grid_Cadillac.png",
    "author": "Patrick",
    "date": "July 3, 2026",
    "season": 5,
}
