import reflex as rx
from the_alternative_f1.articles.components import zoomable_image, image_carousel

article = {
    "title": "Race Week: Silverstone",
    "blurb": "The season's feature race and sprint race halfway point is here. Drivers will race the hollowed grounds of the defunct airfield in an effort to shake up the standings and claim glory.",
    "content": [
        rx.box(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Week/silverstone-_brazil_agreement.jpg",
                float="right", 
                width="50%", 
                margin_left="16px",
                margin_bottom="8px", 
                margin_top="8px", 
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            rx.text(
                "Brazil delivered in more ways than one. This regulation of racecar performed admirably in the challenging sectors found in Sao Paulo. However, \
                    the cars were not the only stars that delivered. Penalties, league interventions, and an off-track first of it's kind decision, \
                        all took place last week. Jelly, Joshua, and Jaden came to a historic agreement. Rather than protest Jelly's rightful drive-through \
                            penalty fix, the three season leading drivers came to a mutual agreement. Clearly, in most circumstances, an agreement like \
                                this could never be possible. However, because the incident was repairing an incorrect penalty rather than a racing incident or \
                                    crash, the FIA allowed the drivers to solve this within the spirit of the regulation. The regulation is put in place to ensure \
                                        no driver is unfairly and incorrectly scammed out of a final position during a VSC or SC. By the book, the rule \
                                            promotes the driver by 20s. In many cases that is just right. In this case it missed the mark. But it ends with a mostly \
                                                happy ending for all three drivers. Joshua retains his hard fought win, Jaden retains his podium and Jelly is moved \
                                                    from nearly dead last to third where he likely would have been without the penalty.",
                color="#E0E0E0",
                font_size="md",
                line_height="1.7",
            ),
            width="100%",
            margin_bottom="4",
        ),

        rx.vstack(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Week/Silverstone_Track.jpeg", 
                width="100%",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            align_items="center",
            width="100%",
            margin_y="4",
        ),

        "But that is enough with the past, what does the future hold? Next week is the mid-season break. In fact, half the feature races and half of the sprints will \
            be complete at that point. This means we will have a season's worth of trends and data to review. Stay on the lookout for an analysis of where each \
                team and driver stands next week.",

        "However, before we get there, the drivers must face the fast corners of Silverstone. Many drivers around the league are already worried about both \
            tire and battery management. Will teams be able to out smart one another? Will the sprint hold up league leaders? Will Jelly bounce back and regain \
                first place? With the track's four straight modes and a heavy emphasis on deployment strategies, the more cerebral drivers may see an opportunity \
                    to make up ground on the talent based drivers.",

        rx.box(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Week/Silverstone_Grand_Prix_Infographic.png",
                float="left", 
                width="35%", 
                margin_right="16px",
                margin_bottom="8px", 
                margin_top="8px", 
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            rx.text(
                "Taking a look at historical statistics for league racing at Silverstone, it should be noted that the track was notably skipped in Season 4. This means \
                    some drivers who joined this season or last, have never raced at Silverstone in an official capacity. Though, for those who have raced here, they \
                        have been treated to incredible racing and a different winner each season. Erick, Del, and Joshua have taken home the gold in Seasons 1, 2, and 3 respectively. Interestingly, Erick has \
                        never missed a podium. With his first place and two third place finishes, Erick rivals active drivers like Del and Nick in terms of potency at \
                            Silverstone.",
            color="#E0E0E0",
                font_size="md",
                line_height="1.7",
                margin_bottom="1rem",
            ),
            rx.text(
                "However, with him sidelined by enlightenment from his new cult, based on statistics, Del has the highest odds of taking \
                                home the win. Using the league's Alternative Intelligence, the analysis shown here predicts McLaren to perform incredibly this week. \
                                    The question is, how will the sprint format shake up the ability to take home a win? Silverstone has never hosted a sprint, \
                                        so all bets are shots in the dark. This should be an exciting opportunity for the \
                                        standings to see a few changes prior to the mid-season break.",
            color="#E0E0E0",
                font_size="md",
                line_height="1.7",
            ),
            width="100%",
            margin_bottom="4",
        ),

        rx.text(
            "Rumor Mill Round Up",
            font_weight="bold",
            color="white",
            margin_top="4",
            margin_bottom="2",
        ),

        "The rumors are hot and heavy this week. Erick is becoming an increasingly common name around the paddock. But no official news just yet. \
            One rumor has been circulating and becoming increasingly real in the minds of many. League officials are considering a new way to go \
                racing during sprint weeks. League official Nick plans to host a friendly testing event during the mid-season break to test this \
                    new methodology for sprint races. Our reporters are hearing that F2 cars may soon find a use in the league for a new level \
                        of equal machinery racing during sprints. We will be sure to report back on this as it evolves.",

        "Finally, last week we saw the reign of a new administration for the FIA. While it is not officially over, a new figurehead is appearing \
            as a primary decision maker. Retired driver Travis plans to get more involved with decisions bringing a new more neutral opinion into \
                the mix as we go forward."                
  
    ],
    "image": "/thealternativef1-cloudflare/Season5/Race_Week/Silverstone_Cover.jpg",
    "author": "Patrick",
    "date": "Novemeber 2, 2026",
    "season": 5,
}
