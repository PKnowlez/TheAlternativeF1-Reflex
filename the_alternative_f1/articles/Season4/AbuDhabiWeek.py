import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Race Week: Abu Dhabi",
    "blurb": "Forgive me for I have sinned.",
    "content": [
        rx.text(
            r"""Forgive me for I have sinned. Yes, I skipped a week of race week articles for the double header. However, I vow that this article will make up for it.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Abu Dhabi, where champions are born. For The Alternative F1 League, it is no different. While it is tight between the top drivers and constructors, there is still the possibility of a finalized pair of championships this week.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""So how can a driver or constructor take home the hardware? Let's start with the Driver's Championship. Alpine's Joshua has a 19 point lead over VCARB's Patrick, a 34 point lead over Mercedes' Jairo, and a 48 point lead over McLaren's Nick, the reigning champion. For the fastest, cleanest, and most incredibly talented drivers out there, a total of 58 points are left on the table this season.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            "This means that any of those mentioned above,", rx.text("could", as_="em"), "still win the championship. But the scenarios for each of them are few and far between. So how does Joshua lock it down this week? Win. If Joshua wins the race, he knocks Nick and Jairo out of the chase no matter what. On top of the win, Patrick must come in 3rd or lower. If Joshua wins and Patrick comes in 3rd or lower, the championship is sealed.",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Now, what about the Constructor's Championship? The race is quite tight between Mercedes and VCARB, and technically, through some extreme miracles, Alpine, the reigning champion, is still in the hunt for the crown. So how does Mercedes finish the job? There are 94 points left for a perfect pairing of drivers to achieve and Mercedes leads VCARB by 13 points. If Mercedes finishes 1-2, even without bonus points, they will take home the crown. However, if both drivers don't finish on the podium and they don't win the race, the fight is still on.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""This season has been incredibly tight all the way through, and with tracks that can induce incredible overtakes and mistakes, this is far from over. So, let's discuss Abu Dhabi and what it will provide for a penultimate race of the season.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.heading(
            "TRACK OVERVIEW",
            size="4",
            color="#00b4da",
            margin_top="6",
            margin_bottom="3",
            font_family="Outfit"
        ),
        rx.text(
            r"""When the race gets underway, drivers will face a moderate run down to Turn 1, which is a wide turn full of run off. The wisest drivers may take to the outside to avoid contact, but those fighting for a championship might get the elbows out here. But the elbows won't have room to stay out for too long as the next turns are narrow, winding, esses.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""As the league snakes through this early portion of the lap, they will inevitably be close together going into Turn 5. This could invite an early overtake or two during the first lap, however, going forward this will be an ill-advised location to overtake as the double DRS zones that follow will give the overtaken driver a good opportunity to fight back.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""As noted, Turn 5 shoots the drivers out into a long straight with a strong DRS zone, at the end of which, is a technical chicane that launches the drivers into a slightly curved DRS zone, ending in Turn 9's sweeping left turn.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""From this sweeper, the drivers will face the hotel section which provides an unconventional overtaking spot in the Turn 10, 11, 12 sequence. From there, a pair of paired corners to finish the lap with throttle modulation and braking galore right back onto the start-finish straight.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.vstack(
            rx.text("Abu Dhabi Circuit", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season4/Images/Abu_Dhabi_Circuit.png",
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
            r"""Abu Dhabi is a perennial track on The Alternative's schedule. While it has appeared in each season, only one driver has ever won, McLaren's Nick. Will he make it a 4-peat? Will Joshua finally win where he has come second twice? Could a new winner arise? Only time will tell.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.heading(
            "SILLY SEASON",
            size="4",
            color="#00b4da",
            margin_top="6",
            margin_bottom="3",
            font_family="Outfit"
        ),
        rx.text(
            r"""It has become a staple in these articles to wrap up the rumors from around the league, but with just two races to go, we are officially entering an early silly season.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Two official announcements have come from team principals. These pairing of announcements, interestingly, both deal with Red Bull. Two drivers are on their way out to a new team and two drivers are on their way in.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.heading(
            "HAAS ANNOUNCEMENT",
            size="4",
            color="#00b4da",
            margin_top="6",
            margin_bottom="3",
            font_family="Outfit"
        ),
        rx.vstack(
            rx.text("Haass5", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season4/Images/Silly Season/HaasS5.png",
                width="100%",
                max_width="400px",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.4)"
            ),
            align_items="center",
            width="100%",
            margin_y="4",
        ),
        rx.heading(
            "RED BULL ANNOUNCEMENT",
            size="4",
            color="#00b4da",
            margin_top="6",
            margin_bottom="3",
            font_family="Outfit"
        ),
        rx.vstack(
            rx.text("Redbulls5Contract", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season4/Images/Silly Season/RedBullS5Contract.png",
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
                src="/thealternativef1-cloudflare/Season4/Images/surfer.gif",
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
    "image": "/thealternativef1-cloudflare/Season4/Images/Abu_Dhabi_Circuit.png",
    "author": "Patrick",
    "date": "January 11, 2026",
    "season": 4,
}
