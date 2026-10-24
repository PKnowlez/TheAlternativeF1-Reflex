import reflex as rx
from the_alternative_f1.articles.components import zoomable_image, image_carousel

article = {
    "title": "Race Week: Brazil",
    "blurb": "Cadillac licking their wounds. Ferrari on the up-and-up. Rumors swirling. Brazil has a chance to really shake things up.",
    "content": [
        rx.box(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Week/Brazil_Spa_Photo.jpg",
                float="right", 
                width="50%", 
                margin_left="16px",
                margin_bottom="8px", 
                margin_top="8px", 
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            rx.text(
                "Spa was a thrilling race. One where we saw drama unfold lap after lap in qualifying, the sprint, and the feature race. Drivers \
                    fought for positions. Cars crashed. Penalties flew. But most importantly, the gap closed in both the Constructor and the Driver \
                        Championships.",
                color="#E0E0E0",
                font_size="md",
                line_height="1.7",
            ),
            width="100%",
            margin_bottom="4",
        ),

        rx.box(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Week/Brazil_Projection.png",
                float="left", 
                width="250px", 
                margin_right="16px",
                margin_bottom="8px", 
                margin_top="8px", 
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            rx.text(
                "For the Constructor title, there is no longer a four-way fight for second. Instead, it is now a two-way fight \
                            for first, a two-way fight for second, and a drifting Mercedes may soon see competition from Haas. Brazil might just \
                                bring all of these fights out of speculation and into reality. \
                In the Driver Championship, Joshua has surmounted a strong rally, narrowing the gap to leader Jelly to just one, single, point. \
                    How will the frontrunner respond? Will he go on the offensive and strike first, or will the pressure build and become too \
                        overwhelming to handle? Will Joshua ditch his dirty driving ways and clean up to win without controversy? Will Jairo's \
                            message be more than just words? This mid-season break is allowing all of this to simmer, but when rubber meets the \
                                road in Sao Paulo, the temperature will surely rise.",
                color="#E0E0E0",
                font_size="md",
                line_height="1.7",
                margin_bottom="1rem",
            ),
            rx.text(
                "Brazil brings not only this drama, but an incredible venue for this regulation of vehicles. With a technical and downforce heavy \
                    middle sector, similar to Spa, drivers will need to balance top speed and cornering speed to maximize their driving potential. \
                        The league has raced in Interlagos twice before. In Season 4, Jaden took home his first feature race win, while in Season 1, \
                            Nick was closing out his dominant inagural Driver Championship. In fact, Nick has been on the podium all three times the \
                                league has recorded a start in Brazil, with his 3rd place finish in both the sprint and feature race during Season 4. ",
                color="#E0E0E0",
                font_size="md",
                line_height="1.7",
            ),
            width="100%",
            margin_bottom="4",
        ),

        "So what does the track really have to offer the drivers? An enourmous main straight with the potential for a drag race photo finish if \
            strategies align just right. The Senna S will offer the brave a place to muscle their way past their opponents, while Turn 4 and \
                Turn 12 provide more traditional braking zones for overtakes. But the creative might find themselves with opportunities into \
                    Turns 8 and 10 throughout the race. The primary challenge in Brazil is keeing the rear tires alive, and subsequently, \
                        keeping the car pointed forward on track at all times. The map below highlights the nuanced differences between each \
                            sector of the track.",

        rx.vstack(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Week/Brazil_Track.jpeg", 
                width="100%",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            align_items="center",
            width="100%",
            margin_y="4",
        ),

        rx.text(
            "Rumor Mill Round Up",
            font_weight="bold",
            color="white",
            margin_top="4",
            margin_bottom="2",
        ),

        "While the last rumor mill focused on the more senior Tavera brother, this time we are hearing rumors about Junior. \
            Will Eddie get back in the car? Will the team provide hardware that allows him to succeed? Is this the Red Bull \
                second seat curse carrying itself out in The Alternative F1 league? We have also heard that parts upgrades are \
                    imminent for the Audi veteran Boz. Could he surpass rookie Evelo? Or will Evelo hold the D1 title through Brazil, \
                        or even further?",

        "Finally, we heard rumor of a secret, for points, friendly race. Though the standings have yet to update from it, we were \
            able to get a reporter there where they witnessed Nick beating Jelly on track in a fierce head-tohead battle. As rumors circle, \
                we will be sure to keep you posted and bring the latest breaking news here."                
  
    ],
    "image": "/thealternativef1-cloudflare/Season5/Race_Week/Brazil_Cover.jpeg",
    "author": "Patrick",
    "date": "October 21, 2026",
    "season": 5,
}
