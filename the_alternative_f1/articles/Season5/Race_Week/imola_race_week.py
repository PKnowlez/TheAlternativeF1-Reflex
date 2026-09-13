import reflex as rx
from the_alternative_f1.articles.components import zoomable_image, image_carousel

article = {
    "title": "Race Week: Imola",
    "blurb": "A track the league has never run, a new era of cars, and a first chance to start noticing trends.",
    "content": [
        "The league's first race of the season quickly became a statement win for the young Cadillac driver. \
            Cadillac's Josh took home his first golden piece of hardware in what ended up being a dominant performance \
                over the favorites like McLaren's Nick, Red Bull's Joshua, and Mercedes' Jario. This performance, paired with \
                    Patrick's fourth place finish propelled the Cadillac duo into the front of the power rankings.",

        rx.box(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Week/Power_Rankings_Pre_Imola.png",
                float="left", 
                width="250px", 
                margin_right="16px",
                margin_bottom="8px", 
                margin_top="8px", 
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            rx.text(
                "This season, rather than relying on voting and polls similar to the increasingly infamous College Football Playoffs, \
                    the league's power rankings are calculated through a complex algorithm taking in qualifying, positions gained, previous races, \
                        and a number of other inputs. As the season progresses, these race week articles will include deeper analysis with respect to \
                            the power rankings, but today, there is simply not enough data to point to.",
                color="#E0E0E0",
                font_size="md",
                line_height="1.7",
            ),
            width="100%",
            margin_bottom="4",
        ),

        "With one last look back at Australia, let us discuss some of the big news surrounding the race. In three races, across three seasons, \
            down under, the league has had three separate driver and three seaparate constructors take to the top step. This season, we also did \
                not see any podium repeaters with three sophomore drivers locking in the top places.",

        "Looking forward to Imola, there is not too much to discuss in the realm of league history. In fact, the league has never run an officially \
            tracked session there. Not a single preseason, postseason, or in season race has ever occurred in Imola. Last season the league planned \
                to make a splash in the Italian country side as the final race of the season. However, that splash would have been a bit too big due \
                    flooding, and so the season finale moved to Monza as we all know.",

        
        rx.box(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Week/Imola_Track.jpg",
                float="right", 
                width="250px", 
                margin_left="16px",
                margin_right="16px",
                margin_bottom="8px", 
                margin_top="8px", 
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            rx.text(
                "Though, what we do know about Imola is that it is a punishing track when it comes to track limits. Margins are razor thin, passing must be \
                    incredibly precise, and mistakes can add up quickly over the course of a race distance. Sector 1 kicks off within an incredible run to the \
                        first turn. The slight bend in the run up allows for a couple unique lines to be gambled with throughout the race, but probably not \
                            during the first lap for those seriously trying to win. \
                                After the first chicane, drivers will have a moment to get on the throttle early and challenge their rivals early into the next higher speed chicane. \
                                    Even with that complete, another overtaking moment presents itself in the hairpin. From there, the drivers will likely run in line together \
                                        through the next handful of corners as tires squeal and batteries run low. All of this leads to the final sector where a chicane and a double \
                                            apex final corners force the drivers to scruntch up before the lengthy front straight.",
                    color="#E0E0E0",
                    font_size="md",
                    line_height="1.7",
            ),
            width="100%",
            margin_bottom="4",
        ),

        "With the nerves knocked out, it will be interesting to see who becomes a consistent front runner this week. Will qualifying force the answer of who \
            wins? Will the league's fastest find themselves saddled with numerous time penalties? How will tires and batteries play a factor? Will drivers take \
                the warnings from the FIA seriously? All of this and so much more will be answered on Wednesday.",

        "Finally, the league's app has had a number of minor cosmetic and data driven updates. The power rankings now follow an animated format and even extend back to \
            previous seasons. The all time stats pages now have a number of new numeric summaries and charts to visualize the history of the league. Some of these \
                new charts even leak into the seasonal statistics for users to peruse. Last, but certainly not least, this nationwide league now boasts a map \
                    visualization for users to see just how widespread our competition reaches.",
    ],
    "image": "/thealternativef1-cloudflare/Season5/Race_Week/Imola_Cover.jpg",
    "author": "Patrick",
    "date": "September 12, 2026",
    "season": 5,
}
