import reflex as rx
from the_alternative_f1.articles.components import zoomable_image, image_carousel

article = {
    "title": "Race Week: Australia",
    "blurb": "Upside-down and ready to roar. The league eyes Australia for their first race of the saeson. Will the preseason rankings hold on or will a new pecking order begin to shine through?",
    "content": [
        "This season, The Intern and I have clear role definiton on who is authoring what. \
        You will find hard hitting analysis here about the upcoming race as well as power rankings \
            and predictions. In the race recaps, you will find memery, tomfoolery, and downright \
                slander about each of you per what has become the norm. As we enter into the first \
                    race of the season, please enjoy a bit of track analysis and the first stab at \
                        power rankings.",
        "First and foremost, the power rankings have been updated to reflect results from throughout \
            the preseason. Red Bull's new duo has proven to be powerful, even as a solo show in two of \
                the three races. Many pundits early on, pushed McLaren to the very front of the rankings \
                    until both Cadillac and Red Bull showed their form. Between the three teams, there \
                        is nearly a standstill on who is likely to take home the crown. While Red Bull, \
                            McLaren, and Cadillac are the early front runners, they are chased closely by \
                                Ferrari and Haas who sit in a two way battle to prove if they are best \
                                    of the rest or a top three podium team.",
        "Mercedes might be the most interesting and difficult to gauge right now. Insider sources say \
            Randy has been seen completing Testing of Previous Cars in Melbourne and showing times \
                near the front of the field. The most important question is, will Jairo live up to his promise of \
                    murdering Joshua?",
        "Finally, Audi and Williams both simply live in a shroud of mystery. Either could produce \
            electric rookie seasons and with Audi's vet finding form with new equipment, the sky is \
                the limit for either outfit.",
        rx.box(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Week/Australia_Track.jpeg",
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
                "Looking forward, the league heads down under to race the hybrid street track at Albert Park. \
                    The Aussie track boasts a number of unique features, a curvey back straight, five straight \
                        mode zones, and a slow speed final corner perfect for catching up and utilizing boost \
                            into the massive front straight.",
                "By the end of what many are expecting to be chaos, we will have a league leader in both \
                    chamionships. Targets will be placed on backs and rivalries will brew again. But \
                        maybe most importantly, we will see if all the simulations on overtaking, battery deployment, \
                            and tire management will prove to be true or just another ghost tale.",
                "Melbourne provides more overtaking places than one might notice at first glance. The obvious \
                    locations like Turn 1 and Turn 9 provide excellent places for battery micro-managers to power \
                        pass their opponents. Along with Turn 3, Turn 11, and Turn 13, drivers will have all the \
                            options to show their motorsport prowess and creativity.",
                color="#E0E0E0",
                font_size="md",
                line_height="1.7",
            ),
            width="100%",
            margin_bottom="4",
        ),
        "With anticipation floating through the air \
            for what is lined up to be a historic season, only a few days\
                and the driver's nervous jitters remain between now and the first official race day \
                    of The Alternative F1's Season 5. May the odds be ever in your favor."
    ],
    "image": "/thealternativef1-cloudflare/Season5/Race_Week/Australia_Cover.jpeg",
    "author": "Patrick",
    "date": "September 6, 2026",
    "season": 5,
}
