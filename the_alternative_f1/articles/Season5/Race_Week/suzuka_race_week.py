import math as m
import reflex as rx
from the_alternative_f1.articles.components import zoomable_image, image_carousel

article = {
    "title": "Race Week: Suzuka",
    "blurb": "The second half of the season is upon us. With mid-season overtake by Joshua in the driver championship, what does this half have in store for us?",
    "content": [
        "With a break in the rearview mirror, drivers are preparing for the gauntlet of a second half of the season. \
            Suzuka, Abu Dhabi, Bahrain, COTA, Zandvoort, Qatar, and Singapore await the league. Some new to the calendar \
                and some nearly perenial circuits. In a coming article we will dive deep into who has to do what to win it \
                    all, but today, the article will focus on the flowing Japanese circuit.",

        rx.vstack(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Week/Suzuka_Track.jpeg", 
                width="100%",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            align_items="center",
            width="100%",
            margin_y="4",
        ),

        "Suzuka opens with an entirely enthralling sweeping turn, which quickly exits into a challenging uphill set of esses. \
            Sectors two and three are some of the only sectors on the calendar that overlap one another. But the real question \
                is, where will the battery games begin? Will life imitate art? Will we see two drivers moving 50mph different \
                    collide on the way to the hairpin? It is entirely possible.",

        "The primary challenge drivers will face is the decision to save battery for the third sector and 130R or will they \
            spend their allotment much earlier in the lap attempting to make up ground on drivers ahead. With only one, single, \
                point separating Joshua and Jelly, it is more than likely that we could see a shakeup in the standings. Additionally, \
                    both McLaren and Ferrari look keen on overtaking the Cadillac duo. But with a larger gap there, it might take \
                        more time for those teams to move up the standings.",

        rx.text(
            "Rumor Mill Round Up",
            font_weight="bold",
            color="white",
            margin_top="4",
            margin_bottom="2",
        ),

        "The most serious rumor we are hearing rumbles of is the F2 testing that was done in Silverstone during the break. \
            Drivers from nearly every team attended. Testing concluded and league officials are still analyzing the data \
                for whatever decision they are targetting to make.",

        "This week is the first week our reporters also saw glimpses of Erick. Does this mean the rumors are true and he \
            is returning to racing? No official news just yet, but if he does arrive in the paddock, we will be sure \
                to catch a late breaking interview with him to understand what changed.",

        "Finally, a rumor was confirmed. McLaren's Del will now be present during qualifying for more races after the team \
            rearranged his media tour. This might mean more opportunties for McLaren to overtake Ferrari in the standings. \
                All of which should simply lead to some exciting racing."              
  
    ],
    "image": "/thealternativef1-cloudflare/Season5/Race_Week/Suzuka_Cover.jpeg",
    "author": "Patrick",
    "date": "Novemeber 17, 2026",
    "season": 5,
}
