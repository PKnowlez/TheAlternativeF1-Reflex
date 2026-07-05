import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Race Week: Brazil",
    "blurb": "After a thriller of a sprint in Spa, the league sets its sights on the iconic track in Interlagos.",
    "content": [
        rx.vstack(
            rx.text("Raweceek1", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/RaweCeek1.png",
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
            r"""After a thriller of a sprint in Spa, the league sets its sights on the iconic track in Interlagos. This week’s battle is also the final sprint of the season and marks the beginning of the second half of the season. With a tight four-way battle in the Driver’s Championship as well as a streaking VCARB and a falling Mercedes in the Constructor’s Championship, the second half of the season looks to be shaping up for an exciting set of races. Especially with both the reigning Driver’s and Constructor’s champions on the back foot, there could be new crowns all around.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Before we get into the Race Week update, league officials have asked that we include some mid-season regulations updates. First and foremost the league is enacting a policy of no restarts going forward. This will enable drivers who make mistakes in the first turn of the race to be identified and officials the opportunity to speak with and coach them to improve racing quality for all in the league. For this first week, it will be unlikely that there will be any penalties for this new rule. However, there will be a penalty for first turn offenses going forward. This is still under development and will likely affect a driver’s next race rather than the current race. Additionally, a new time based penalty for causing a collision is in the works. This will likely not be in play during Brazil, but instead, warnings will be issued. For future races, be prepared to have small but meaningful penalties for incidents that are deemed more than just “racing inchidents.”""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""With respect to this week’s race, it is once again a single qualifying session, a sprint race, and a reverse grid lineup for the race based on the results of the sprint. As league officials made clear in Spa, there is a no tolerance policy for tomfoolery and abusing loopholes in this format.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""The league hasn’t found itself racing around this circuit during either of the last two seasons, but did face its incredible twists and turns during the inaugural season. In that race, McLaren took home the win. Red Bull and Mercedes came in second and third respectively. Nick, Boz, and Erick stood tall on the podium. Nick was able to make some overtakes and come from fourth to win the race, while Boz started and finished in second, and Erick made his way up from 5th. Retired drivers Zane, David, and Marcus all fell back from their qualifying positions and ended in midfield positions. Travis, Josh L., and Gary all were unable to make the start.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""This week, the drivers will be faced with tough tire decisions. Go for the one stop and drive conservatively on the throttle out of the corners or take a more conventional route and run a two stop with more aggression. During the sprint, drivers will be able to choose to run any of the three tire compounds as long as they can keep them alive or light them up in time to be competitive.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""One of the most challenging aspects of this week’s race will be overtaking. While entirely feasible on this circuit, patience will be key for every driver to find the right moment to strike and gain positions. Overtaking too early might just hand the DRS to your opponent. Which, in turn, may cause a back and forth that will wear tires to the brink.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.vstack(
            rx.text("Brazil Circuit", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/Season4/Images/Brazil_Circuit.png",
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
            "At the start of the race, drivers will likely end up two wide going into Turns 1 and 2.", rx.text("Extreme", as_="span", font_weight="bold"), "caution will be required on the exits of both turns as drivers get onto the throttle and weave through Turn 3 and onto the first straight of the race. Some drivers may overtake here early, but many will conserve both their battery and tires and simply follow through Sector 2. Launching an attack at the beginning of Sector 3 to stay close to the car in front through Turns 1 and 2, drivers will hope to maintain a tight following position through Turn 3. If close enough on the exit of Turn 3 on Lap 2, DRS will aid chasing drivers in their pursuit to overtake on the straight. Like Spa, Brazil lends itself to offense in Sectors 1 and 3 and defense in Sector 2. The wisest drivers will know that a tire delta at the end of the race could make the difference in a drag race to the finish line.",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""As it stands, no driver or constructor is technically out of the championship. As the season goes on, keep your eyes peeled here for updates in the race to the finish. As it currently stands, Jairo has a strong lead in the Driver’s Championship with a 15 point lead over Joshua in second, a 17 point lead over Nick in third, and a 27 point lead over Patrick in fourth. Streaking his way up, Josh has solidified himself in sixth and is chasing Jaden in fifth and his teammate in fourth while defending against the senior Red Bull team driver Brently.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""In the Constructor’s Championship, the battle is a bit wider with Mercedes in the lead by 46 points over VCARB. Alpine and Mclaren are tight in the battle for third with last year’s champion ahead by 11 points. Red Bull, Aston Martin, and Ferrari are battling for fifth as it currently stands, but a few good weeks could change them from battling for fifth to battling for fourth or even further up the ranks. Notably, Ferrari has seemingly found some pace in their car with both Leo and Erick beginning to perform more admirably in qualifying and race stints.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""For the remainder of the season, 183 points are available in the Driver’s Championship and 316 points are available in the Constructor’s Championship. It is truly all up for grabs. A DNF or DNS from anyone could turn the tide in anyone’s favor. Along with that, a well timed safety car or two may bring some drivers into contention at extremely opportune times.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
    ],
    "image": "/Season4/Images/RaweCeek1.png",
    "author": "Patrick",
    "date": "December 2, 2025",
    "season": 4,
}
