import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Baku Recap: Castles and Crashes",
    "blurb": "First and foremost, the late breaking news must be addressed.",
    "content": [
rx.text(
    r"""First and foremost, the late breaking news must be addressed. With the FIA’s update to the penalty for Alpine’s Joshua, the standings swung back into his favor as he took the lead by one point over McLaren’s Nick. Critics and pundits of the league are expressing concerns that this may undermine the future credibility of the FIA’s decision making process. This will likely remain a hot topic going into future races.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.vstack(
    rx.text("Baku Midfield - Travis and Eddie", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/thealternativef1-cloudflare/Season3/Images/Baku_Travis_Eddie.png",
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
    r"""With the past in the proverbial rearview mirror, cars roared to life, however, some garages stayed silent. For the first time, the league went into a qualifying session with only half of the drivers. Some are saying drivers deliberately boycotted the race due to its location, while others are reporting that many of the drivers were simply too scared to take to the tightly walled streets of Baku. Regardless, after qualifying finished the drivers who were in attendance made up the first three rows of the grid. McLaren and VCARB both had season best qualifying sessions as teams, while Alpine’s Eddie and Red Bull’s Boz really showed up for their teams with their best qualifying performances of the year.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.text(
    r"""Just in the nick of time, Aston Martin’s Del arrived at the paddock and entered into the race in 20th. Which meant the grid was finalized and it was time to rocket down the long straights of Baku. Notably, the grid was set without both Erick and Zane’s Ferraris, Gary’s Aston Martin, Yeti’s Red Bull, and Joshua’s Alpine. When the lights went out, most drivers got reasonable starts, and the front runners held their positions through the first corner. Positions swapped, tire strategies came into play, and a few minor incidents occurred throughout the first half of the race.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.text(
    r"""But just as the race passed the halfway point, the first safety car of the evening occurred. The primary strategy of the race had been a single stop from the hard compound to the medium compound. Therefore, most drivers were not ready to risk extending a new set of mediums for half of the race. So with most drivers staying out, the safety car parade began. However Eddie, who had been running in second, had a damaged front wing and required a pitstop. But either because he was screaming about something Marvel Rivals related over the radio or because his pit crew was worn out from dealing with all the spinouts during qualifying, Alpine did not swap his wing. This error forced Eddie to pit again on the following lap, still under safety car.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.text(
    r"""While tumbling backwards in position, Eddie prepared for the race restart on new tires with a fresh front wing. Many of the drivers were positioned near the front of the queue and began to spar in the tight turns of the circuit’s first sector. However, after a lap, there were again no major incidents. The drivers were keeping it as civil as they could with the occasional “I’m gonna dive bomb you,” being shouted from those trying to make up positions. As the sparring continued, Del unfortunately met an early demise which led to the second safety car of the evening.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.text(
    r"""With a few of the front runners hoping to stretch their original tires for a chance at fresh softs, a risky choice became clear, pit now for mediums, or hold out for softs later. Nick made the decision to pit for the medium compound tires and gamble that he could get through all of the traffic from halfway down the field. This decision put VCARB’s Patrick, Red Bull’s Boz, and Alpine’s Eddie in the top three at the onset of the restart. On the front stretch the drivers took off and Eddie managed to get past Boz within a lap or two. During that time, Nick came screaming up the ranks and managed to position himself into third. As Patrick, Eddie, Nick, and Boz entered the castle section, Eddie made a race losing mistake. With a minor lapse in concentration he spun at the top of the castle turns and collided nose first with the right wall. Nick narrowly avoided clipping his rear, but as Eddie began to get off of the racing line he blocked Boz’s path causing an additional collision.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.vstack(
    rx.text("Eddie Baku Incident", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/thealternativef1-cloudflare/Season3/Images/Baku_Eddie.png",
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
    r"""Eddie and Boz would recover from this and manage to finish the race at the back of the pack, even with some last corner shenanigans. Due to a drive through penalty gained during the safety car and a collision caused by Perez, VCARB’s Brently finished in the middle of the field. McLaren’s Travis was also caught out due to the Perez-Brently incident but managed to finish the race as well. So with one driver off to the shores of the Caspian Sea, and four drivers out of the points, it came down to reigning champion Nick and rookie driver Patrick.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.vstack(
    rx.text("Baku Overtake - Nick and Patrick", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/thealternativef1-cloudflare/Season3/Images/Baku_Nick_Patrick_Pass.png",
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
    r"""As the duo entered the front straight, it was clear that Nick was positioned for an overtake. With his battery depleted, Patrick was only able to defend up to the finish line where Nick overtook going into the final lap, therefore all but securing another win for himself and McLaren. Nick’s win along with Travis’ performance brings McLaren within two points of Alpine in the Constructor’s Championship. Red Bull and Aston Martin are now within one point of one another in the battle for 5th. This win also pushes Nick an entire race win ahead of Joshua in the Driver’s Championship, and Patrick’s second place pushed him ahead of Erick for third.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.vstack(
    rx.text("Baku Race Collage", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/thealternativef1-cloudflare/Season3/Images/Baku_Collage.png",
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
    "image": "/thealternativef1-cloudflare/Season3/Images/Baku_Travis_Eddie.png",
    "author": "Patrick Knowles with credit Nick",
    "date": "January 17, 2025",
    "season": 3,
}
