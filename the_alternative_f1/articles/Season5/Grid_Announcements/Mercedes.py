import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "The Champion is Back",
    "blurb": "The return of the king, and a new partner in crime.",
    "content": [
        "Jairo and Mercedes may have lost Jaden to Ferrari, but they are not letting off the throttle. All sources point to the team eyeing only one thing, a back-to-back constructor championship. But will it be possible with the new pairing?",
        "Randy is a wildcard, no one is certain what he will bring to the team. Can he score consistently? Can he defend against the likes of Nick, Jaden, and Joshua? Or will he find the wall faster than George Russell complains when someone jumps the start?",
        "The Intern caught up with Jairo to discuss his new teammate, the regulations, and the team's potential. The interview went smashingly. Jairo's energy was palpable about taking on another championship run. But, just as The Intern was wrapping things up, Jairo reached across the table, snatched our intern's handwritten transcript out of their hands, ripped it in half, and looked them dead in the eyes and said,",
        rx.box(
            rx.text(
                "\"Joshua's dying.\"",
                color="#CCCCCC",
                font_style="italic",
                font_size="md",
                line_height="1.6",
            ),
            padding_left="16px",
            border_left="4px solid #00b4da",
            margin_y="6",
            width="100%",
        ),
        "So with that, we are without much more content from the interview. However, it is clear to see there is unfinished business left on the table from last season."
        "With the champs back on the grid in a seemingly ruthless manner, every other team is certainly on notice. Jario and Austin look to do something no other team in league history has ever done, be the back-to-back undisputed champions.",
    ],
    "image": "/thealternativef1-cloudflare/Season5/Grid_Announcements/Grid_Mercedes.png",
    "author": "Patrick",
    "date": "July 17, 2026",
    "season": 5,
}
