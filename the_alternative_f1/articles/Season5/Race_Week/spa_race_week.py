import reflex as rx
from the_alternative_f1.articles.components import zoomable_image, image_carousel

article = {
    "title": "Race Week: Spa",
    "blurb": "A sprint and a day at the spa. Jelly and Cadillac take a commanding lead, but the league's last outing at Spa left scars.",
    "content": [
        "The league returns to Belgium for another sprint race week. Last season, Spa hosted a sprint and it was a doozy. Around the \
            paddock, drivers, team principals, and PR personnel are all actively trying to put out fires and rumors from last week's \
                race in Monza. With a self-painted target on his back, Joshua has emerged from the Red Bull garage ready to fight. \
                    As far as we can tell, there is a high chance that the majority of this season's race at Spa will center around \
                        the Red Bull squad. But, as we all know, the drama might not come out until the final corner on the final lap \
                            here in the Ardennes Forest.",

        "A day at the Spa may not be all that relaxing for the league. The track boasts enormous flat out stretches with neck bending \
            high-speed turns, along with setup options for the brave that are all risk with major reward. This season with the \
                additional complications of battery strategies, it will be more important than ever to nail a setup that allows \
                    a driver to defend every position they gain. Below is a quick overview of the track, its straight mode, \
                        and its handful of great overtaking corners.",

        rx.vstack(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Week/Spa_Track.jpeg", 
                width="100%",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            align_items="center",
            width="100%",
            margin_y="4",
        ),

        "But, Spa is not just the home of drama and good racing. It is also home to Nick's only remaining undefeated streak. During \
            Season 4, Nick lost his undefeated streak at Abu Dhabi, but, in Belgium, he remains unstoppable. This record is particularly \
                unique because Spa is one of the few remaining circuits that perennially make it onto The Alternative F1's schedule. \
                    However, with Jelly as rapid as he has been during the past few races, along with the vendetta Joshua has against the FIA, \
                        this week has the potential to end that streak.",

        rx.vstack(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Week/Spa_Analysis_Final-2.jpg",
                width="100%",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            align_items="center",
            width="100%",
            margin_y="4",
        ),

        "So, who do you think will win? Who will stand on the podium? A perennial driver at a perennial track? A sophmore driver with \
            a hot start? A new challenger for the title? Or maybe something else entirely? Whatever the result may be, you can be sure \
                our trusty intern will meme all over it.",

        rx.text(
            "Rumor Mill Round Up",
            font_weight="bold",
            color="white",
            margin_top="4",
            margin_bottom="2",
        ),

        "Finally, a return of a fan favorite section. Many rumors have begun spinning about league legend Erick. Will he return to society \
        and break free from his 'religion'? \
            Maybe not this week. But, the Williams team boss did let our reporter know that they believe they will have enough cash flow \
                to attend this week. Will Audi get their technical problems solved and field two drivers this week as well? If you think \
                    you have answers to these questions and many more, it might be time to raise the stakes and submit a prediction in the \
                        league's predictions market."
  
    ],
    "image": "/thealternativef1-cloudflare/Season5/Race_Week/Spa_Cover.jpg",
    "author": "Patrick",
    "date": "October 10, 2026",
    "season": 5,
}
