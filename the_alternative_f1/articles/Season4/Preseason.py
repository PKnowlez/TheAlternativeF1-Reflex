import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Preseason Race Recap: We Are So Back",
    "blurb": "What a flipping mess.",
    "content": [
        rx.vstack(
            rx.text("Mumscar", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/MumsCar.jpg",
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
            r"""What a flipping mess. Terrible settings (thanks Patrick), VSC and SC, carbon fiber everywhere, and some drivers failed to even start their cars...""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Everyone was a rookie during this one. Surprisingly two of the rookies were the only ones who drove like veterans, with Jairo and Jayden putting Mercedes on the podium and well up the midfield respectively. The same cannot be said for some of our returning drivers...""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Some of the driving seen today was disgraceful, no cap. So what if it was raining, these guys shouldn't be that bad. Some of them even forgot where their clutches were in the pits, sheesh.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Beyond all the rust being dusted off, there were some bright moments. Rookie Matthew crashed out during Q1 and his mechanic team miraculously had him up and running for Q2. Others, like Nick battled back from setbacks and completed plenty of overtakes. Joshua qualified well and kept his ish together to remain on the podium, honestly a shocker he even finsied Q1 the way he ended last season.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""But let's talk about the stupidity that ran through everyone's veins, and as I always say, memes are worth 1,000,000 words.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.vstack(
            rx.text("Preseasonmemes", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/PreseasonMemes.png",
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
                src="/Season4/Images/surfer.gif",
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
    "image": "/Season4/Images/MumsCar.jpg",
    "author": "The Intern",
    "date": "September 25, 2025",
    "season": 4,
}
