import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Race Recap: Monaco Mayhem 2 Electric-Boo-Ga-Loo",
    "blurb": "What's more iconic the wine and cheese?",
    "content": [
        rx.text(
            r"""What's more iconic the wine and cheese? Nick and Monaco crash outs. No cap this was the wildest race, potentially, in league history. A truly incredible, monumental, and movie worthy post-season debacle.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.vstack(
            rx.text("Cinema", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Monaco/cinema.png",
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
            r"""The craziest part of this whole race was simply Erick. This man was a loose cannon from start to finish. Dude was dive bombing, rage racing, and providing some incredibly questionable small talk... To commemorate all of this, please enjoy the reaction from league pundit Brentuar as well as some commemorative memes.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.vstack(
            rx.text("Erick Bodies", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Monaco/erick_bodies.png",
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
            rx.text("Erick Clip", color="#888888", font_size="xs", margin_bottom="1"),
            rx.video(
                src="/Season4/Images/Monaco/erick_clip.mp4",
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
            rx.text("Erick Pk", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Monaco/erick_pk.png",
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
            rx.text("Erick Dive", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Monaco/erick_dive.png",
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
            rx.text("Erick Crash", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Monaco/erick_crash.png",
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
            r"""A true masterpiece from the now McLaren driver. His first outing in papaya and he has gone loco. Erick wasn't the only idiot to crash out though. Only two of these so called "drivers" even finised the race. But how we got to that point was nothing less than miraculous. Like I could not have paid these guys to provide this much content. Mostly because they still don't pay me, but also because this was true entropy in motion.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""The Mercedes duo decided it was their sole purpose in life to cause absolute carnage.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.vstack(
            rx.text("Jairo Joshua", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Monaco/jairo_joshua.png",
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
            rx.text("Jaden Leo", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Monaco/jaden_leo.png",
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
            r"""And guess what...""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.vstack(
            rx.text("Everyone Liked", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Monaco/everyone_liked.png",
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
            r"""But Jairo didn't accomplish his great feat alone. No, he had some help from his fellow Driver's Championship podium-mate.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.vstack(
            rx.text("Pk Jairo", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Monaco/pk_jairo.png",
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
            r"""Now no one would say my boss Patrick is all that put together. But this guy was goofing, goofing, especailly with the settings...""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.vstack(
            rx.text("Settings", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Monaco/settings.png",
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
            r"""He and Brently also just straight drove their cars into walls. So much for the senior drivers of the Red Bull squad.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.vstack(
            rx.text("Pk Crash", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Monaco/pk_crash.png",
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
            rx.text("Brentuar", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Monaco/brentuar.png",
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
            rx.text("Team Usa", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Monaco/team_usa.png",
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
            r"""I mentioned that only 2 drivers finished, and yes it was somehow the two Red Bull rookies Joshua and Newman. True heroes of the league. A first win for Joshua and a first podium for Newman.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Now, because of the magnitude of this moment, the league determined that not just a Monaco winner's trophy was due, but also a second place trophy to ensure drivers understand how huge it was to simply survive this race. There was literally a red flag restart with only four drivers...truly INSANE.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""This might have backfired though and reports are surfacing that the duo of finishers are ego-maxing in their team group chat.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.vstack(
            rx.text("Josh Newman", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Monaco/josh_newman.png",
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
            r"""Some of you may be wondering, how has Eddie survived being roasted this entire article? Well, we saved the best for last. This guy straight up crashed texting and driving. How is that even possible? Bro was driving an imaginary car that he can put into autopilot and he still managed to wreck. It is truly a talent that he possesses.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.vstack(
            rx.text("Eddie Texting", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Monaco/eddie_texting.png",
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
            "SILLY SEASON",
            size="4",
            color="#00b4da",
            margin_top="6",
            margin_bottom="3",
            font_family="Outfit"
        ),
        rx.text(
            r"""Don't worry, the reporting on silly season continues friends. Mercedes has locked in half their lineup. Jairo has committed to another season with the Brackley outfit.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Rumor has it, he has even begun contract negotiations with a rookie teammate to attempt to run it back.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""In response to Mercedes running it back, the McLaren duo responded, "We'll see about that.\"""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Until the next one.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.vstack(
            rx.text("Surfer", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Images/surfer.gif",
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
            rx.text("Videofile", color="#888888", font_size="xs", margin_bottom="1"),
            rx.video(
                src="/Images/VideoFile.mp4",
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
    ],
    "image": "/Season4/Images/Monaco/cinema.png",
    "author": "The Intern",
    "date": "January 30, 2026",
    "season": 4,
}
