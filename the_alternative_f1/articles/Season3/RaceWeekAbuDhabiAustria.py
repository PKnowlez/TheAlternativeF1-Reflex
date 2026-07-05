import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Race Week - Abu Dhabi & Austria",
    "blurb": "Only two weeks remain for the league and the standings are tight.",
    "content": [
rx.text(
    r"""Only two weeks remain for the league and the standings are tight. Everything is still to play for, but the focus of this article is the potential action on the tracks coming up this week. While there are only two weeks left, there are three races and two Sprints scheduled for our drivers. The first of this week’s races will take place in Abu Dhabi at the Yas Marina Circuit which was made infamous for providing Max Verstappen’s first Driver’s Championship victory. The second race of the week takes the drivers to Austria to rip around the Red Bull Ring, not once, but twice in a Sprint and main race.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.text(
    r"""Let’s tackle the twists and turns of Yas Marina first. The start finish straight is a short one, but it leads into a medium braking corner and two full tilt turns just after that. Once drivers are up to speed they are met with a wide hairpin that could allow for some early passing and late stage desperation. Once the harrowing overtaking is done in Turn 5, drivers will face the long back straight where lead cars will be at risk of being overtaken into the Turn 6 & 7 chicance. But drivers who play their cards right should be able to battle back immediately after the chicane with the second DRS zone heading into the sweeping Turn 9. The middle of Sector 3 is where the drivers will earn their paychecks as they face the extremely technical hotel section and the challenging braking zones of the final two turns.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.vstack(
    rx.text("Yas Marina Circuit Map", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/thealternativef1-cloudflare/Season3/Images/Abu_Dhabi_Circuit.png",
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
    r"""In the prior two seasons McLaren’s Nick has found himself successful around Yas Marina Circuit, winning both of the races. Alpine’s Joshua and retired driver Mark have both found themselves on the second step of the podium once, and Ferrari’s Erick has found himself on the podium in third place during both of those instances""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.text(
    r"""Now let’s review the opportunities the drivers will have at the Red Bull Ring, the shortest track on the league’s calendar this season. Even though the Red Bull Ring is rather short, it is not short of challenging turns and passing opportunities. As the drivers floor it up the steep front straight and into the first turn, some drivers may be given the opportunity to jump the inside line or, if they have a grip advantage, take the outside line for an overtake. The drivers will then head down and back up the twisting DRS zone up to Turn 3. Here drivers will have their best opportunity for overtaking throughout the race. Pinching off their opponents, drivers will then open their back wings again on the back straight down to Turn 4. As the elevation begins to change the drivers will sweep around Turns 4, 5, 6, 7, and 8 in quick succession. The brave, or maybe the foolish, may try overtaking on the outside of these turns if they have the grip and pace. Then the last two turns on the track will rear their ugly heads. If drivers are cautious they will stay within the white lines, but knowing this league, expect to see time penalties being handed out left, right, and center on the exits of each of the last two turns.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.vstack(
    rx.text("Red Bull Ring Map", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/thealternativef1-cloudflare/Season3/Images/Austria_Circuit.png",
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
    "This will be the first Sprint with the revised format and rules that were proposed and ratified after the Sprint in China. The league will qualify in a shortened Sprint qualifying style. This means that each lap of qualifying will matter just a touch more. From there the drivers will line up for the Sprint in the order they qualified and rip it around the Red Bull Ring at full tilt with little to no regard to tires or strategy. With the dust settled the drivers will be lined back up for the main race. However, the starting grid will be set in reverse from the results of the Sprint. There are a few minor exceptions for the reverse grid which are listed below. > 1) All drivers will line up behind ", rx.text("ALL", as_="span", font_style="italic"), " AI regardless of the position the AI finished in during the Sprint. > 2) Any driver that DNF or DNS the Sprint will line up behind the drivers that did start and finish the Sprint.",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.text(
    r"""With all that said, last time out where the hills are alive with the sound of racecars, the league saw the now Ferrari driver Del hoist the winner’s trophy. The season before that, Nick was on the top step of the podium. The following steps of the podium have seen Nick and now Aston Martin driver Zane in second as well as Joshua and Erick in third.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.text(
    r"""<p style=\"color:lightgray;\">THE INTERN WILL RETURN</p>""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
    ],
    "image": "/thealternativef1-cloudflare/Season3/Images/Abu_Dhabi_Circuit.png",
    "author": "Patrick Knowles",
    "date": "February 3, 2025",
    "season": 3,
}
