import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Race Recap: Jeddah & Las Vegas - Viva Las Double Header",
    "blurb": "First and foremost I must apologize for my lazy boss who didn't pen up a race week article...must have had you all lost out there not knowing where...",
    "content": [
        rx.vstack(
            rx.text("Vegascover", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Jeddah Vegas/VegasCover.png",
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
            "JEDDAH RECAP",
            size="4",
            color="#00b4da",
            margin_top="6",
            margin_bottom="3",
            font_family="Outfit"
        ),
        rx.text(
            r"""First and foremost I must apologize for my lazy boss who didn't pen up a race week article...must have had you all lost out there not knowing where to overtake and stuff. Let's blame all your bad driving and mishaps on that, yeah? K cool.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""With that out of the way, let's talk about two of the most thrilling finishes we have seen this season. Jeddah, where we were just ~~one~~ ~~no two~~ three major mistakes away from a totally different podium. Let's start with the first big mistake. Reigning champ Nick calculated that the walls were made of pillows. His calculations were completely incorrect. First lap out there during qualifying, DNF.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""This guy might need to get his head checked after that one... Onto the second mistake. The master baker, Del, decided to snack on one too many little treats and also calculated that the walls were made of pillows mid-race. Taking himself from fighting for 3rd to sitting in the paddock.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Now, the most egregious error of them all came from none other than the rookie phenom Jairo. With what some were calling the greatest strategy call of all time (insert eyeroll), Jairo put on a faster set of tires under safecty car and, well, wore them into the slipperiest set of rubber known to mankind. He found himself facing backwards multiple times during the final lap of the race spinning and spinning like a merry-go-round with a punctured rear tire.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""The race wasn't an entire bust though. Eddie from the backrow made it up into 7th. Nick, from even further back did manage to salvage his crappy qualifying and make it to 4th. The VCARB pair capitalized on everyone else's mistakes and took home a double podium. Erick made up a place or two as well, and finally, Joshua took home his second win in a row and this season. But let me immortalize a few of the glorious moments in memes below.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.vstack(
            rx.text("Jeddah1", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Jeddah Vegas/Jeddah1.png",
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
            rx.text("Jeddah2", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Jeddah Vegas/Jeddah2.png",
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
            rx.text("Jeddah3", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Jeddah Vegas/Jeddah3.png",
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
            rx.text("Jeddah4", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Jeddah Vegas/Jeddah4.png",
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
            rx.text("Jeddah5", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Jeddah Vegas/Jeddah5.png",
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
            rx.text("Jeddah6", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Jeddah Vegas/Jeddah6.png",
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
            "LAS VEGAS RECAP",
            size="4",
            color="#00b4da",
            margin_top="6",
            margin_bottom="3",
            font_family="Outfit"
        ),
        rx.text(
            r"""Now, the league didn't just have one chance to mess things up, this was, of course, a double header. And boy howdy did they carpe the diem out of that opportunity. Eddie was simply too afraid to make another mistake so he bailed. Then he started chatting nonsense mid-qualifying about anime (the crowd truly booed), and his teammate cooked nearly every hot lap he tried. Alpine has really fallen from their throne after last year's win.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""In total these goons only mustered 7 finishers for this race. 9 started, 11 were present, and 3 gone with the wind. But this finish was like nothing we have ever seen before. No script, no skills, and a whole lot of luck lead to five drivers being right on top of each other coming out of the final braking zone on the track. This lead to a near three way tie for first. Now, you'd think the guy who was in first and started in second would be in that fight, but you would be wrong. Joshua was leading but this guy is allergic to staying within the white lines and so, because of how tight it was, he fell all the way to 5th after the smoke cleared.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Jairo, Patrick, and Nick, all within 0.088s of each other, finshed in 1st through 3rd. Leo found himself just off the podium a few tenths back.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""A true masterpiece of a finish, that even I cannot truly meme on. Please enjoy a short clip of this excitement below as well as some glorious race memes.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.vstack(
            rx.text("Vegas", color="#888888", font_size="xs", margin_bottom="1"),
            rx.video(
                src="/Season4/Images/Jeddah Vegas/Vegas.mp4",
                width="100%",
                height="auto",
                controls=True,
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.4)"
            ),
            align_items="center",
            width="100%",
            margin_y="4",
        ),
        rx.vstack(
            rx.text("Vegas1", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Jeddah Vegas/Vegas1.png",
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
            rx.text("Vegas2", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Jeddah Vegas/Vegas2.png",
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
            rx.text("Vegas3", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Jeddah Vegas/Vegas3.png",
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
            rx.text("Vegas4", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Jeddah Vegas/Vegas4.png",
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
            rx.text("Vegas5", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Jeddah Vegas/Vegas5.png",
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
            rx.text("Vegas6", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Jeddah Vegas/Vegas6.png",
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
            r"""Now, my friends, there were some moments and memes that superseded just one race. And so I present to you an assortment of memes that span the entirety of the double header evening.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.vstack(
            rx.text("Jeddahvegas1", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Jeddah Vegas/JeddahVegas1.png",
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
            rx.text("Jeddahvegas2", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Jeddah Vegas/JeddahVegas2.png",
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
            rx.text("Jeddahvegas3", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Jeddah Vegas/JeddahVegas3.png",
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
            rx.text("Jeddahvegas4", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Jeddah Vegas/JeddahVegas4.png",
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
            "RUMOR MILL",
            size="4",
            color="#00b4da",
            margin_top="6",
            margin_bottom="3",
            font_family="Outfit"
        ),
        rx.text(
            r"""There have been plenty of rumors this season, but we are nearing the end of our season. Which means, some of these rumors are about to go up in flames or come out as true through press releases. Sources are saying we will hear about the new look Red Bull team sometime next week as well as who is driving for Haas, Cadillac, and McLaren.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""But while those juicy rumors are soon to be made real, we've got something even bigger than that on the horizon. Reports are coming in that there has been massive flooding in Imola. The paddock is currently 8 feet deep in water. Parts of the track's surface are severely damaged due to debris overflowing and smashing into the surface at the onslaught of the flash flood.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""This is putting the season finale in jeapordy. But there is a rumor circulating that the Italian promoters of the event have identified a suitable substitute...""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.heading(
            "The Temple of Speed",
            size="4",
            color="#00b4da",
            margin_top="6",
            margin_bottom="3",
            font_family="Outfit"
        ),
        rx.text(
            r"""So for those who have been simming in Imola, it might be time to begin practicing for the fastest lap of the year instead. Take this rumor as an official announcement, because there is no way y'all are running your cars in Atlantis, I mean, Imola in two weeks.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
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
    "image": "/Season4/Images/Jeddah Vegas/VegasCover.png",
    "author": "The Intern",
    "date": "January 8, 2026",
    "season": 4,
}
