import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Spa & Spain Recap: Two Tracks, Tons of Turmoil, and Terrible Teamwork",
    "blurb": "Buckle your helmet straps, pull up your gloves, and button your firesuits, because this recap is juicy.",
    "content": [
rx.text(
    r"""Buckle your helmet straps, pull up your gloves, and button your firesuits, because this recap is juicy. First we will cover the results of the races. Then we will take a trip down turmoil lane to unpack the dramatic happenings of the double header. Finally, we will highlight the evening’s attempted works of teamwork.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.vstack(
    rx.text("Spain Cover Photo", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/thealternativef1-cloudflare/Season3/Images/Spain_Cover.png",
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
    rx.text("Two Tracks", as_="span", font_weight="bold"),
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.text(
    r"""Drivers took on two high speed, long, and arduous tracks. First, the league started at Spa where a surprise qualifying occurred with both Kick Sauber cars out pacing all of the drivers by leaps and bounds. However, neither Kick car was able to fend off the league’s drivers for more than a few laps. As the race continued a few safety cars brought the field together which allowed McLaren’s Nick to take home his second win of the season, with Alpine’s Joshua coming in second, and Aston Martin’s Del taking home his second podium of the season. Notably, both Del and VCARB’s Brently made up multiple places over the course of the race. After the race the midfield standings saw a few changes. In the Constructor’s Championship VCARB overtook Ferrari. While in the Driver’s Championship Brently overtook VCARB’s Patrick, Del overtook Ferrari’s Zane, and Red Bull’s Boz separated from Aston Martin’s Gary.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.text(
    r"""After a quick break the league strapped in for 33 laps in Barcelona, Spain. Qualifying saw Nick outpace Ferrari’s Erick by a thin margin. However at the end of the race, Joshua ended up taking home the victory, with Nick just behind, and Erick rounding out the podium. Just like in Spa, the race was full of turmoil but also a notable performance by Red Bull’s Yeti. Starting in 14th, Yeti ripped through the field, passing nearly every contender and battling all the way up into 5th place for his best finish of the season. Yeti’s notable performance resulted in the only change in the championship standings, with him overtaking Zane.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.vstack(
    rx.text("Yeti in Spain", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/thealternativef1-cloudflare/Season3/Images/Spain_Yeti.png",
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
    rx.text("Tons of Turmoil", as_="span", font_weight="bold"),
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.text(
    r"""With the important updates out of the way, let’s get into the drama from the double header. First and foremost, the FIA was under fire again with numerous penalties granted to drivers in Spa for exceeding track limits. So much so, and to the delight of corner cutters everywhere, the regulators decided to loosen up on their penalty calls while in Spain.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.text(
    r"""With plenty of penalties awarded for track limits, the FIA was surprisingly quiet when it came to penalizing aggressive drivers who ran their competitors off track. Right out of the gate in Spa, Joshua took an assertive position on the exit of Turn 1, forcing Nick off track on their way down to Eau Rogue. Within the next lap, Joshua chose to slow down and allow Nick to pass in a gesture of good faith and motor-sportsmanship. Unfortunately, this was not the only incident where a driver ended up off track. While battling, Erick began an attack on Patrick on the outside of the main start-finish straight. Patrick, unaware of how far Erick had advanced, held his line, and forced Erick to take drastic actions on the grass and gravel runaway of Turn 1. After review, neither incident was deemed sufficient enough for further penalty to any driver.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.vstack(
    rx.text("Nick and Joshua Battle at Spa", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/thealternativef1-cloudflare/Season3/Images/Spa_Nick_Joshua.png",
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
    r"""Spa also delivered two extraordinarily long safety cars. The first was caused by Erick losing control at the top of Eau Rogue. Nearly all the drivers immediately pitted for new tires and queued up behind the insanely erratic safety car. Alpine’s Eddie found himself in front of his teammate Joshua and attempted to provide a meaningful position swap at the restart, more on this later. This maneuver, along with a poorly contrived passing attempt by Patrick, ended with another safety car after Patrick accidentally pit maneuvered Yeti, log jamming the whole field (except Erick who made up 12 places in one turn).""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.vstack(
    rx.text("Spa Log Jam Incident", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/thealternativef1-cloudflare/Season3/Images/Spa_Log_Jam.png",
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
    r"""Safety cars were a theme in both races. While in Spain the drivers faced a relatively early safety car at the end of Lap 13. Many drivers pitted, and committed to tire saving throughout the race. The restart was mostly uneventful with nominal slipstream passes and great battles due to the grouped up drivers. One such battle occurred between Nick, Patrick, and Erick headed into La Caixa at the beginning of Sector 3. In what can only be described as an act of vengeance, Erick forgot to brake and nearly sideswiped Patrick and t-boned Nick. However, he gently grazed both drivers and neither incurred any damage.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.text(
    r"""Spain ended with one last bit of turmoil as Joshua began to tout his fastest lap streak. Conveniently, Patrick was on a two stopper with his final stint on the soft compound tires. With a full battery, fresh tires, and fuel low, Patrick changed his engine mode and pushed, securing the fastest lap of the race for the moment. In spite of the time set, a pair of teammates were determined to try and take the fastest lap, more on this later.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.text(
    rx.text("Terrible Teamwork", as_="span", font_weight="bold"),
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.text(
    r"""While not terrible, a few teammates were unable to race one or both races which resulted in some of the standings changes mentioned previously. But, remarkably terrible teamwork came out of the French outfit in both races. While lapping through the Ardennes Forest, Joshua ended up behind Eddie during the first safety car. The two conjured up the idea to let Joshua by on the shortest straight of the track coming out of the slowest corner on the track. This failed miserably as Joshua jumped the gun and Eddie forgot where his accelerator was. Causing Yeti, Patrick, Joshua, and Eddie to be 4-wide coming across the DRS activation line. The league watched it back like an end of year fail recap from a mildly unsuccessful sim racing streamer. Laughs were shared, teammates yelled at one another, and it felt like we were back at the Christmas Eve dining table listening to family debate meaningless politics, knowing full well how silly the whole scenario is.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.text(
    r"""Now if that were the only silly teammate moment, this article would be done. But, as you can see, it isn’t. As previously mentioned Joshua had won the fastest lap award at every single race this season. But in Spain, Patrick had a prime opportunity to snag a fastest lap near the end of the race. Joshua, afraid to lose his victory, did not pit and try to retaliate, instead, he had his teammate Eddie pit and attempt to snag the fastest lap. They tried new tires, slipstreaming, and what some are calling “coaching,” but to no avail. Joshua’s streak ended and on the last lap the Alpine pair were at each other’s throats.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.vstack(
    rx.text("Alpine Team Radio at Spa", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/thealternativef1-cloudflare/Season3/Images/Spa_Alpines.png",
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
    r"""The league takes on China next week in the first Sprint race in league history. There are sure to be fireworks as regulations are set to change back to strict for exceeding track limits and the new Sprint format is bound to cause some sort of drama.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
    ],
    "image": "/thealternativef1-cloudflare/Season3/Images/Spain_Cover.png",
    "author": "Patrick Knowles",
    "date": "January 2, 2025",
    "season": 3,
}
