import reflex as rx
from the_alternative_f1.articles.components import zoomable_image, image_carousel, fia_badge

article = {
    "title": "Josh on Josh Violence",
    "blurb": "Last year's champ versus this year's challenger turned ugly in the final corner. Yet another week with a maFIA ruling.",
    "content": [
        "Monza, oh how I love thee. In all my years of covering this jolly bunch of gamers, there has never once been a peaceful, \
            civilized, and controlled race at Monza. Penalties fly, brothers fight (twice...), and the maFIA gets all kinds of handsy. \
                This season, nothing has changed. If I had to summarize Monza in one meme, it would be:",
        
        rx.vstack(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Monza/m9-2.png", 
                width="100%",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            align_items="center",
            width="100%",
            margin_y="4",
        ),

        "But, I guess it wasn't all depression. There were some moments of stupidity as well. And honestly...you're gonna hear all about it \
            below. But let's do a silly little recap of how it all went down. Patrick and Nick both forgot how qualifying works and choked. \
                Jelly took home another pole, with Joshua hot on his heinie. Leo served his time in the sin bin and Eddie 'had homework.' \
                    After qualifying was sorted the race was a bit of a disaster. Each start or restart forced my boss into forgetting where \
                        his brake pedal was. Five wide before the timing line on a restart is also quite the choice...but that is just \
                            par for the course around here at this point. So, let's get to the memes.",

        rx.box(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Monza/m1.png", 
                float="right", 
                width="200px", 
                margin_left="16px", 
                margin_bottom="8px",
                margin_top="8px", 
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            rx.text(
                "On your right here you will find a lovely depiction of Leo waiting to get into the race, circa 2026, colorized. \
                    Below you will find two memes we curated from the dawn of time. Yes, these prehistoric memes depict the \
                        tomfoolery our league old guys decided to get up to during the race. In fact, rumor has it that both \
                            boomers are still trying to open this article as we speak. Technology can be a challenge for us all, it's ok guys. ",
                color="#E0E0E0",
                font_size="md",
                line_height="1.7",
            ),
            width="100%",
            margin_bottom="4",
        ),

        rx.grid(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Monza/m2.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Monza/m3.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            columns="2",
            spacing="3",
            width="100%",
            margin_bottom="4",
        ),

        "Now, now, now, I shouldn't just roast our old guys. We've got stupid young guys too! Most notably is reigning fast guy, Joshua. \
            This meme requires more context, so just enjoy the other ones first and then come on back up here after you've read the press \
                release from our dear leaders. I promise, it will all make sense. Trust me.",
        
        rx.vstack(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Monza/m4.gif", 
                width="100%",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            align_items="center",
            width="100%",
            margin_y="4",
        ),

        "Ok, and to round out the memery, here is a little rapid fire grid full of self-explanatory silliness. Sometimes, like \
            Evelo & Newman, you just need a little whimsy and dedication. Other times, like Eddie, you should do the math before \
                yapping. And, in rare occassions, you yell 'BALL DON'T LIE' after silencing the haters with some statement \
                    performances like the Tifosi at home.",      
        
        rx.grid(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Monza/m5.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Monza/m6.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Monza/m7.gif", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Recap/Monza/m8.png", 
                width="100%",
                height="auto",
                object_fit="contain",
                display="block",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            columns="2",
            spacing="3",
            width="100%",
            margin_bottom="4",
        ),

        "Finally, please enjoy some context for that Joshua meme above. I am sure this won't be the last you hear about this mess. \
            And honestly, I hope we get something even jucier later this season. But for like 2 weeks could we give our dear leaders \
                in the maFIA a break? They need it ok. I promise. I would never lie.",

        rx.box(
            rx.vstack(
                rx.heading("INCIDENT BETWEEN CADILLAC & RED BULL", font_size="xl", font_weight="bold", color="black", flex="1"),
                rx.text(
                    "For Immediate Release \nOfficial FIA Communication \n2026 Monza Grand Prix - Lap 27 Incident",
                    color="#555555",
                    font_size="md",
                    line_height="1.6",
                    white_space="pre-line",
                ),
                rx.divider(border_color="#363635", margin_y="3", width="100%"),
                rx.text(
                    "Through formal petition to the FIA, the final lap incident between Cadillac's Jelly and Red Bull's Joshua has been reviewed. \
                        This incident involved contact that was made in the final corner of the final lap of the race in Monza. The contact was \
                            made between Joshua and Jelly as they entered Parabolica for the final time in the race.",
                    color="black",
                    font_size="md",
                    line_height="1.6",
                ),
                rx.text(
                    "The governing body of the league reviewed the incident from both driver's onboard footage. But prior to reviewing, the FIA \
                        removed Patrick from duty for this investigation due to a major conflict of interest. The findings below were formed by \
                            the remainder of the governing body's members. The following facts were used to determine the final verdict.",
                    color="black",
                    font_size="md",
                    line_height="1.6",
                ),
                rx.unordered_list(
                    rx.list_item(
                        "Joshua's Red Bull was behind entering the corner.",
                    ),
                    rx.list_item(
                        "Joshua's Red Bull committed to the inside line to attempt an overtake.",
                    ),
                    rx.list_item(
                        "Joshua's Red Bull and Jelly's Cadillac made contact prior to the apex of the corner.",
                    ),
                    rx.list_item(
                        "Jelly's Cadillac was on and controlled the racing line entering the corner.",
                    ),
                    rx.list_item(
                        "Jelly's Cadillac was pushed wide due to the contact.",
                    ),
                    list_style_type="disc",
                    color="black",
                    font_size="md",
                    line_height="1.6",
                    padding_left="16px",
                    margin_bottom="2",
                ),
                rx.text(
                    "At the time of collision, neither car had made it to the apex fully. Additionally, had Jelly's Cadillac not been on its line, it was determined, \
                        through extensive review, that Joshua's Red Bull would have taken a wider line naturally.",
                    color="black",
                    font_size="md",
                    line_height="1.6",
                ),
                rx.text(
                    "VERDICT: ",
                    color="black",
                    font_weight="bold",
                    font_size="md",
                    line_height="1.6",
                ),
                rx.text(
                    "Due to the contact and loss of position for the Cadillac, Joshua will be penalized with a five (5) second time penalty to his \
                        finishing position along with a singular penalty point being added to his Super License. This penalty results in the following \
                            changes to the race results:",
                    color="black",
                    font_size="md",
                    line_height="1.6",
                ),
                rx.unordered_list(
                    rx.list_item(
                        "Jelly's Cadillac moves from second place to first.",
                    ),
                    rx.list_item(
                        "Jaden's Ferrari moves from third place to second.",
                    ),
                    rx.list_item(
                        "Joshua's Red Bull moves from first place to third.",
                    ),
                    list_style_type="disc",
                    color="black",
                    font_size="md",
                    line_height="1.6",
                    padding_left="16px",
                    margin_bottom="2",
                ),
                rx.divider(border_color="#363635", margin_y="3", width="100%"),
                rx.text(
                    "THE ALTERNATIVE F1 LEAGUE",
                    color="black",
                    font_weight="bold",
                    font_size="md",
                    line_height="0.5",
                ),
                rx.text(
                    "Where racing meets integrity and fair competition.",
                    color="#555555",
                    font_style="italic",
                    font_size="md",
                    line_height="0.5",
                ),
                spacing="3",
                align_items="start",
                width="100%",
            ),
            bg="white",
            padding="20px",
            border_radius="4px",
            border="1px solid #E0E0E0",
            border_left="4px solid #00b4da",
            font_family="sans-serif",
            margin_y="6",
            width="100%",
        ),    
    ],
    "image": "/thealternativef1-cloudflare/Season5/Race_Recap/Monza/monza_title.png",
    "author": "The Intern",
    "date": "October 8, 2026",
    "season": 5,
    "fia": True,
}
