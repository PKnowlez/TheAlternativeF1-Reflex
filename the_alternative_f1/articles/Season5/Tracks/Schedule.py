import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Schedule Announcement",
    "blurb": "Mark your calendars nerds, its about to be time to go racing!",
    "content": [
        "To all who ranked tracks, thank you. To all who didn't, you suck. Ranking has now closed and the schedule is set!",
        "Scouring the data of the votes, I noticed a few intriguing things...most importantly two of you ranked Spa as F tier. If it ever comes out who did that, I am personally hacking the app and subtracting 100 points from each of you.",
        rx.vstack(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Schedule Announcement/right-to-jail.gif",
                width="100%",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.4)"
            ),
            align_items="center",
            width="100%",
            margin_y="4",
        ),
        "Now, I also noticed that some of you hated on Qatar, and bummer news for you, one of our top three finishers had selected it so its on the calendar, even though it pretty much had the lowest ranking of all.",
        "If you would like to download the schedule image feel free to click below. Additionally, the final rankings are available for view as well.",
        rx.vstack(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Schedule Announcement/Schedule_Graphic.png",
                width="100%",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.4)"
            ),
            align_items="center",
            width="100%",
            margin_y="4",
        ),
        rx.vstack(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Schedule Announcement/Season5TrackRankings.png",
                width="100%",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.4)"
            ),
            align_items="center",
            width="100%",
            margin_y="4",
        ),
    ],
    "image": "/thealternativef1-cloudflare/Season5/Schedule Announcement/Schedule_Graphic.png",
    "author": "The Intern",
    "date": "July 10, 2026",
    "season": 5,
}
