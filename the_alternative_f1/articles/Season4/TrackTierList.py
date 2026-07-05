import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "The Definitive Ranking of Season 4 Tracks",
    "blurb": "While onboarding for this season, the editors told me that as the intern, I needed to create things that had not been done before.",
    "content": [
        rx.text(
            r"""While onboarding for this season, the editors told me that as the intern, I needed to create things that had not been done before. So, let's start that off with the league's first tier list.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Let's just get one thing straight before we get into this. Don't @ me. This list is definitive. I am correct. Your oppinion is invalid and that is simply facts. #DealWithIt""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.vstack(
            rx.text("Deal With It", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/deal_with_it.gif",
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
            r"""With that out of the way, enjoy the list. If you disagree, bummer, this is objectively correct. There is nothing that can make me move any of these tracks (well except maybe money), especially the first place and last place picks.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""More importantly, if you disagree you're free to make your own trash version of the list. But just know it will be wrong. Actually, on second thought, go vote here and let's see how wrong you all are on average: https://live.tiermaker.com/84368036""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.vstack(
            rx.text("Track Tier List", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Track_Tier_List.png",
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
    "image": "/Season4/Images/deal_with_it.gif",
    "author": "The Intern",
    "date": "August 25, 2025",
    "season": 4,
}
