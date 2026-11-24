import reflex as rx
from the_alternative_f1.articles.components import zoomable_image, image_carousel

article = {
    "title": "Godzilla vs. Kong",
    "blurb": "Joshua sucks. Bro can't even keep a lead on like the hardest track to pass on. Doo-doo. And Jelly is inevitable, one last time before GTA VI.",
    "content": [
        "Alright, so I, the illustrious intern, have been busy. Sue me. Maybe pay a guy if you want instant article gratification sheesh. Now, I have been hearing some of you want to see memes. And lots of em. So, today, as a lazy, unpaid, intern, I will satisfy that need and only that need. Well, I guess the Rumor Mill Round Up.",

        rx.box(
            image_carousel([]),
            width="100%",
            margin_y="4",
        ),
    ],
    "image": "/thealternativef1-cloudflare/Season5/Race_Recap/Suzuka/suzuka_title.jpeg",
    "author": "The Intern",
    "date": "November 23, 2026",
    "season": 5,
}
