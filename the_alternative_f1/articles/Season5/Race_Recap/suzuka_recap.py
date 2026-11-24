import reflex as rx
from the_alternative_f1.articles.components import zoomable_image, image_carousel

article = {
    "title": "Godzilla vs. Kong",
    "blurb": "Joshua sucks. Bro can't even keep a lead on like the hardest track to pass on. Doo-doo. And Jelly is inevitable, one last time before GTA VI.",
    "content": [
        "Alright, so I, the illustrious intern, have been busy. Sue me. Maybe pay a guy if you want instant article gratification sheesh. Now, I have been hearing some of you want to see memes. And lots of em. So, today, as a lazy, unpaid, intern, I will satisfy that need and only that need. Well, I guess the Rumor Mill Round Up.",

        rx.box(
            image_carousel(["/thealternativef1-cloudflare/Season5/Race_Recap/Suzuka/s1.png", "/thealternativef1-cloudflare/Season5/Race_Recap/Suzuka/s2.png", "/thealternativef1-cloudflare/Season5/Race_Recap/Suzuka/s3.png", "/thealternativef1-cloudflare/Season5/Race_Recap/Suzuka/s4.gif", "/thealternativef1-cloudflare/Season5/Race_Recap/Suzuka/s5.gif", "/thealternativef1-cloudflare/Season5/Race_Recap/Suzuka/s7.png", "/thealternativef1-cloudflare/Season5/Race_Recap/Suzuka/s11.png", "/thealternativef1-cloudflare/Season5/Race_Recap/Suzuka/s12.png", "/thealternativef1-cloudflare/Season5/Race_Recap/Suzuka/s10.png", "/thealternativef1-cloudflare/Season5/Race_Recap/Suzuka/s6.gif", "/thealternativef1-cloudflare/Season5/Race_Recap/Suzuka/s8.png", "/thealternativef1-cloudflare/Season5/Race_Recap/Suzuka/s9.png"]),
            width="100%",
            margin_y="4",
        ),

        rx.heading(
            "Rumor Mill Round Up",
            size="4",
            color="#00b4da",
            margin_top="6",
            margin_bottom="3",
            font_family="Outfit",
        ),

        "Alright, alright, alright, it is all quiet on the Erick Tavera front this week. Maybe that bum will get off his ass and race again. However, there are lots of rumors about Brently and his seat at Haas. We've heard the crew at FOM have reached out for exclusive broadcasting of league races. But that would mean dropping the wheel...which his teammate Newman is hotly against. Rumor also has it that this whole F2 car thing is really coming to reality. the maFIA has been in discussions about running F2 cars in the final remaining sprints for 'purer racing,' whatever that means. Oh, and finally, yes, I am still unpaid if you didn't catch that earlier.",
    ],
    "image": "/thealternativef1-cloudflare/Season5/Race_Recap/Suzuka/suzuka_title.jpeg",
    "author": "The Intern",
    "date": "November 23, 2026",
    "season": 5,
}
