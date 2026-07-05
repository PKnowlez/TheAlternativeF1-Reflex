import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Canada Recap: An Ontario Scari-o Makes its Way to Montreal",
    "blurb": "The league took to the hybrid streets of Montreal’s Notre Dame Island and let’s beat to the chase, it was thrilling.",
    "content": [
rx.text(
    r"""The league took to the hybrid streets of Montreal’s Notre Dame Island and let’s beat to the chase, it was thrilling. Rain, tire strategies, spin outs, teams infighting, and penalties galore. The Canadian GP is well known for its infamous Wall of Champions, but for the league’s drivers, it became synonymous with corner cutting and time penalties. Infact, drivers all avoided making a fatal mistake at the Wall of Champions, but racked up incredible penalty totals as they lapped around and around the famed island.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.vstack(
    rx.text("Canada Start", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/Season3/Images/Canada_Start.png",
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
    r"""Most notably, Alpine’s Eddie topped the leaderboards in the worst way imaginable. With over 20 seconds in penalties, Eddie barely held onto points at the end of the race. On the flip side, the McLaren drivers Nick and Travis were extremely precise and managed to make it through the race without a corner dutting penalty. But, Nick wasn’t able to keep it completely clean, during the lone Virtual Safety Car of the race he was caught out just over the requisite delta and received a drive through penalty which may have cost him the race.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.text(
    r"""The race wasn’t all sunshine and penalties though. Sometime during the 13th lap, the heavens opened. Rain began to pitter patter down onto the track, cooling both surface and tire temperatures. Drivers began diving into the pits, opting for intermediate tires to lessen the difficulty of driving on the slick track. As the rain continued nearly everyone went in for intermediate tires. However, as the rain began to lighten up, some drivers gambled and swapped to slicks early. This proved to be an effective way to bring the slicks in gradually, but it was also tough sledding for a few laps as grip was nowhere to be found.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.vstack(
    rx.text("Canada Nick Collage", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/Season3/Images/Canada_Nick_Collage.png",
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
    "Others were not so lucky with their tire strategies and pit stops. The Milton Keynes outfit was down a driver for the race and on top of that they did not effectively support the one driver they had in the running. Boz was found speechless after his pit stops turned into a long string of slow nightmares. More on this in the league’s first ever ", rx.link("insider scoop", href="https://thealternativef124.streamlit.app/#insider-scoop-red-bull-s-drama-in-the-pits", color="#00b4da", text_decoration="underline"), " about the recent struggles at Red Bull.",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.vstack(
    rx.text("Canada Eddie and Erick Sibling Rivalry", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/Season3/Images/Canada_Eddie_Erick_Collage.png",
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
    r"""Boz’s tribulation and the rain were not the only dramatic happenings on track. The incredible saga of philia and zelos between the Tavera brothers continued to escalate in Canada. The brothers started one behind the other in 4th and 6th on the grid. As the race began they stayed out of each other’s ways, but as tire strategies and the weather pulled the two closer together, disaster struck. Alpine’s Eddie and Ferrari’s Erick wrestled back and forth for position. Just after Eddie overtook Erick in the back straight, the two sped into Turn 1 and Turn 2 where Eddie was too early on the throttle, oversteering his car perpendicular to the racing line. Erick, even with his incredible F1 reflexes that got him his seat at Ferrari, was unable to avoid slamming directly into Eddie’s sidepod. Both drivers recovered from the mishap with only lost time and hurt egos. However, Eddie’s teammate Joshua likely will find a bruise on his ego after an unforced error in Turn 7 had him spinning out and losing places.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.vstack(
    rx.text("Joshua Turn 7 Spin", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/Season3/Images/Canada_Joshua_Crash.png",
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
    r"""Most of the rest of the race was filled with good passes, some backfield lapping, and drivers doing the best they can to stay on the asphalt. While much of the race was nominal, the results were not. When the chequered flag flew, Aston Martin’s Del was the first to cross the finish line. With his first win of the season, Del begins to pull Aston Martin out of the bottom ranks of the Constructors and closer to contention with the midfield.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.vstack(
    rx.text("Del Victory in Canada", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/Season3/Images/Canada_Del.png",
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
    r"""The rest of the podium was filled out by Nick and Joshua, allowing Nick to continue to maintain his lead in the Driver’s World Championship. Nick’s edge over Joshua and Travis’ edge over Eddie allowed McLaren to overtake Alpine by two points for the Cosntructor’s World Championship. The VCARB pairing began to lose some of their ground to their nearest rivals. Del, with his win, closed the gap to VCARB’s Brently, while Erick closed the gap to VCARB’s Patrick. Finally, Travis took a cut out of the lead Boz had over him. Next week the league takes to the countryside of Italy to race around the Temple of Speed. Who knows if the Tavera Saga will continue, if McLaren can continue their lead in both championships, or if Eddie will keep his car between the white lines.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
    ],
    "image": "/Season3/Images/Canada_Start.png",
    "author": "Patrick Knowles with credit Erick & Nick",
    "date": "January 23, 2025",
    "season": 3,
}
