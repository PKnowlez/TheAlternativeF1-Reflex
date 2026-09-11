import reflex as rx
from the_alternative_f1.articles.components import zoomable_image, image_carousel

article = {
    "title": "A Bout Between New Heavy Weights",
    "blurb": "Jelly win before GTA VI? Is there a new contender this season for driver's champion? Will Bernd ever get a week off? And how many teams have a shot at winning it all?",
    "content": [
        "This was a stellar 'fan's' race. Safety cars, battles, split strategies, and oh so many stupid mistakes by the reigning champ. Glorious. Lowkirkenuinely, this was a banger and makes me excited for the rest of this crazy season.",
        rx.box(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Australia/a1.png", 
                float="right", 
                width="200px", 
                margin_left="16px", 
                margin_bottom="8px",
                margin_top="8px",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            rx.text(
                "So, let's talk about qualifying, because there was some absolute madness there even before the race got rolling. We had drivers crashing in Q1. We had geniuses running inters and wets to 'save' softs for the race. We even had the vet Nick up in the top three. Truly glorious all around. But let's talk about some of the...er...less than stellar performances in the race.",
                color="#E0E0E0",
                font_size="md",
                line_height="1.7",
            ),
            width="100%",
            margin_bottom="4",
        ),
        rx.vstack(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Australia/a2.png", 
                width="100%",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            align_items="center",
            width="100%",
            margin_y="4",
        ),
        
        rx.heading(
            "Season 5's First Race Commences", 
            size="4", 
            color="#00b4da", 
            margin_top="6", 
            margin_bottom="3",
            font_family="Outfit"
        ),

        "Well...sorta...",
        
        rx.vstack(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Australia/a3.png", 
                width="100%",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            align_items="center",
            width="100%",
            margin_y="4",
        ),

        "Ok, so then the racing got going and it was truly good for a moment or two. For this league, a clean start does include at least one car turning into a beyblade, so check there with Brentuar rotating like ballerina. After that, I am pleased to report, clean racing for like 2 laps. Then the safety cars attacked. And just when the league needed him most, Travis disappeared (or just wasn't there anyways).",

        rx.box(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Australia/a4.gif", 
                float="left", 
                width="200px", 
                margin_right="16px", 
                margin_bottom="8px",
                margin_top="8px", 
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            rx.text(
                "In this recap, I want to actually start near the end, with a monumental move by our great leader, I mean reigning champ. This guy sees a backmarker and just turns his targeting computer right into the side of the poor Williams driver. I tried to find a pundit in the paddock to defned him but the best I got was 'yeesh, retcon that guy's championship please,' from a team principal who would like to remain anonymous but wears a lot of orange, and might have a little bit of a Nick bias.",
                color="#E0E0E0",
                font_size="md",
                line_height="1.7",
            ),
            width="100%",
            margin_bottom="4",
        ),

        rx.box(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Australia/a5.gif", 
                float="right", 
                width="200px", 
                margin_left="16px", 
                margin_bottom="8px", 
                margin_top="8px",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            rx.text(
                "However, this wasn't the biggest news of the race. In my mind, the crown jewel was 15/16 drivers participating and all of them finishing the race. STUNNING. Never thought something like that could happen. Not with these guys behind the wheel. It really brings a tear to my unpaid eyes as I write this in the dungeon...I mean basement... Now, some of you are going to say that the real crown jewel was the winner. And yeah, this guy deserves his laurels. Somehow left his car mid-race, hopped back in during a VSC, and then drove the air out of the tires all the way to the finish line. Jelly with the W was huge. Does this mean he is D1 for Cadillac? Probably. Patrick is a washed old man who can literally only get 4th in 5 outings this year.",
                color="#E0E0E0",
                font_size="md",
                line_height="1.7",
            ),
            width="100%",
            margin_bottom="4",
        ),

        rx.box(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Australia/a6.gif", 
                float="left", 
                width="200px", 
                margin_right="16px", 
                margin_bottom="8px",
                margin_top="8px", 
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            rx.text(
                "Unsurprising to no one, we also saw the reigning constructor duo on the podium with Jelly. But...this time...as nemeses instead of teammates. I for one can't wait until they sandwich Joshua and send him into the wall somehow later in the season. Taking bets, ping me in the comments for the CashApp. Now, it would be silly not to talk about all the other epic racing we saw. Both Williams drivers gave it the college try and frankly did pretty well. Boz chose to play Tarkov instead. Nick and Patrick are getting slower and older each day. Eddie was having a full on D&D conversation during the race and got too scared to switch his tires. Del had 7 cylinders in his engine if you catch my drift. Newman and Brently both had races to forget. Leo was back to his old antics trying to murder Patrick. And most importantly, Evelo is the new defacto Audi D1.",
                color="#E0E0E0",
                font_size="md",
                line_height="1.7",
            ),
            width="100%",
            margin_bottom="4",
        ),

        "As we wrap up, the maFIA has a few warnings for people to consider. Thankfully, none of you did anything too crazy and we have nothing under review...but I am waiting...I love the juicy 'you're fired' articles.",

        rx.box(
            rx.heading(
                "FIA Warnings", 
                size="4", 
                color="black", 
                margin_top="0", 
                margin_bottom="1rem", 
                font_family="Outfit"
            ),
            rx.text(
                "Upon reviewing the race, there were a number of moments where drivers had the right to protest. However, many drivers chose the high ground and kept it gentlemanly. The FIA has no intention of pushing forward with anything listed below, however they are critical to note so that all drivers are aware of moments that could have lead to larger reviews had the fallout been of larger magnitude.",
                color="black",
                font_weight="600",
                font_size="sm",
                margin_bottom="1rem",
            ),
            rx.text(
                "During qualifying there was an incident where the Red Bull of Joshua was on the racing line while the Haas of Brently was on a hot lap. This incident had a minor impact to the Haas, but should be noted as the wrong choice by the Red Bull.",
                color="black",
                font_weight="600",
                font_size="sm",
                margin_bottom="1rem",
            ),
            rx.text(
                "During the race there was another instance with the Red Bull of Joshua where he collided with a back marker during a dive into Turn 1. Neither party is completely at fault, however, any car making a pass must respect the space of the car ahead.",
                color="black",
                font_weight="600",
                font_size="sm",
                margin_bottom="1rem",
            ),
            rx.text(
                "Earlier in the race, under safety car, when the safety car broke off and the lead driver was forced to slow, drivers in the rear of the train caused a domino effect of crashes. These are completely avoidable and all driers must remain aware during safety cars as to not cause incident under them. There are no circumstances where an accident during safety car is reasonable.",
                color="black",
                font_weight="600",
                font_size="sm",
                margin_bottom="1rem",
            ),
            rx.text(
                "Finally, during the closing lap of the race, the Red Bull of Joshua and the Cadillac of Patrick caused a racing incident. Both drivers discussed the issue live on track and came to resolution. However, this scenario should not have occurred, and had either driver been seriously hampered due to it, a larger conversation would have ensued.",
                color="black",
                font_weight="600",
                font_size="sm",
            ),
            bg="white",
            padding="20px",
            border_radius="2px",
            border="1px solid #E0E0E0",
            width="100%",
            margin_y="16px",
        ),
    ],
    "image": "/thealternativef1-cloudflare/Season5/Race_Recap/Australia/australia_title.png",
    "author": "The Intern",
    "date": "September 10, 1 AK",
    "season": 5,
}
