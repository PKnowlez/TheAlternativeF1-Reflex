import reflex as rx
from the_alternative_f1.articles.components import zoomable_image, image_carousel

article = {
    "title": "Race Week: Monza",
    "blurb": "A penalized Ferrari in Italy, a four way fight for second in the Constructor Championship, and a narrowing Driver Championship lead.",
    "content": [
        "With Miami in the rearview, drivers and constructors set their sights on the Temple of Speed. However, after \
            this week's league wide vote, one home favorite will be hoping for a signature outing. Ferrari's Leo \
                peitioned the league to overturn their no qualifying penalty, which narrowly did not succeed. Due to \
                    this, Leo will start from the back of the grid in Monza.",

        "The Alternative F1 has never missed a chance to put rubber to the road at this hallowed spectacle of a circuit. \
            Season 5 will be no different as a 5th running of the Tifosi's favorite grand prix is just around the \
                corner. This week, Jairo will not only look to take home a back-to-back victory for this season, he \
                    will also look to defend his Season 4 Monza win. So how did last season's running in Monza pan out? \
                        First and foremost, it was a replacement race for a flooded Imola that finished with then Alpine \
                            driver Joshua taking home his first Driver's Championship.",
        
        "This year, Monza has the potential to shake up the standings much earlier in the season. This week's \
                    race could see McLaren jumping up in the standings and moving past Ferrari. Much of this rests \
                        on the laurels of Nick who is the only active driver who has raced at Monza every single season. \
                            In addition to this, Leo starting from the rear may aid McLaren in this effort. \
                                The most critical battle is between Jairo and Jelly who are separated by just 9 points \
                                    going into the race this week.",

        rx.vstack(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Week/Monza_Analysis_Final.jpg",
                width="100%",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            align_items="center",
            width="100%",
            margin_y="4",
        ),

        "Around the paddock, pundits are weighing in on the incident between Leo and Del. Many are providing statements \
            sympathizing with Leo, while one particular CEO has been vocally for the ruling. Our intrepid beat reporter, \
                The Intern, caught up with McLaren Racing's CEO who had this to say: ",

        rx.box(
            rx.text(
                "\"Both McLaren drivers were damaged by Leo's decisions in Miami. Ferrari is lucky that the FIA talked us \
                    out of submitting evidence against Leo for the damage inflicted during the sprint race.\"",
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

        "While this stance is clearly based on direct impact to their own team, other constructors voiced varying \
            different opinions. One such spokesperson for Red Bull met with our beat reporter and provided the following \
                statement:",

        rx.box(
            rx.text(
                "\"We love to see hard racing. We also encourage drivers to give each other room. During a race start, \
                    on occassion, the lines can blur between those two stances and incidents can occur. At Red Bull we look \
                        forward to seeing his [Leo's] continued progress in the league. He has improved on racecraft \
                            and speed, end over end since last season.\"",
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

        "Now what do the drivers really face in Monza? An enormously long straight with a mix of high and low speed chicanes \
            along with parabalica will leave tires screaming for relief. If driver's can survive the tire wear, many \
                may fall victim to the circuit's lack of major recharging zones. All of this combined together, \
                    should allow the quickest drivers with strong racecraft to prevail. Finally, the circuit boasts \
                        four straight mode zones, meaning drivers will need to be on their toes throughout each lap \
                            to ensure they are maximizing every single exit and lap.",

        rx.vstack(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Week/Monza_Track.jpeg", 
                width="100%",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            align_items="center",
            width="100%",
            margin_y="4",
        ),
  
    ],
    "image": "/thealternativef1-cloudflare/Season5/Race_Week/Monza_Cover.jpeg",
    "author": "Patrick",
    "date": "October 4, 2026",
    "season": 5,
}
