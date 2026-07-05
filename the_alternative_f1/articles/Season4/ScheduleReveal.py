import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "The League's Longest Season to Date",
    "blurb": "As drivers around the league begin preparing with their teams, the FIA has been hard at work finalizing this season's schedule.",
    "content": [
        rx.text(
            r"""As drivers around the league begin preparing with their teams, the FIA has been hard at work finalizing this season's schedule. Due to the length of this season the FIA has elected to include a few deliberate breaks in the action to allow drivers and their teams a moment of rest during the 14 race season plus both pre and post-season sessions.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""The league will hit the track for pre-season testing in Silverstone on Wednesday September 24, 2025. At 8:45PM Eastern, the engines will roar to life for the first qualifying round of the year. When discussing the intricacies of this season, the FIA made it clear that races will start promptly at 8:45PM Eastern, with a small bit of spare time for drivers who are just barely running behind.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""After pre-season testing, the drivers will take on the first two races of the year and then be met with an early Fall Break to allow for a bit of rest and extra practice for the rookies after their first stint in the league.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""From there, the drivers will take on the longest stint of regular season races on the calendar, which will end with a time of rest around Thanksgiving. Once the drivers are fat and happy, they will take to the streets again for a three race stint that gives way to the final pause of the season, Winter Break.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Finally, with Winter Break completed, there will be four races that close out the season and then the post-season race at the end of January. Below, you will see the schedule in full with all of the races on Wednesday nights, except the New Year showdown in Jeddah.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.vstack(
            rx.text("Schedule Reveal", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season4/Images/Schedule_Reveal.png",
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
    "image": "/thealternativef1-cloudflare/Season4/Images/Schedule_Reveal.png",
    "author": "Patrick",
    "date": "August 21, 2025",
    "season": 4,
}
