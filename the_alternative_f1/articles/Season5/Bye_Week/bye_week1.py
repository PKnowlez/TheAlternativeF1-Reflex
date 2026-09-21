import reflex as rx
from the_alternative_f1.articles.components import zoomable_image, image_carousel

article = {
    "title": "The League's First Bye Week",
    "blurb": "New pole sitters, race winners, and features oh my! Give this a read to learn all about it.",
    "content": [
        "'Twas the first bye week of the season, when all through the paddock, not an engine was purring, not even at reigning champion Joshua's house.",
        "In fact, our sources say he has been playing 2k instead of practicing for the first sprint of the year. So much for all that bickering with his \
            teammate last week. The paddock is still, however, full of rumors and speculation on how the remainder of this historic season will play out. \
                Most intriguing, is of course the sophomore standout at Cadillac with his first pole, first two wins, and league leading 50 points. We will \
                    certainly take a moment to review each driver thus far this season, but before we do so, there are a number of new features in the app \
                        worth noting.",
        
        rx.heading(
            "Prediction Market, Teammate Network, League Map, & a Host of New Graphs and Stats", 
            size="4", 
            color="#00b4da", 
            margin_top="6", 
            margin_bottom="3", 
            font_family="Outfit"
        ),

        rx.box(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Bye_Week/Bye1/bw1-1.png", 
                float="right", 
                width="200px", 
                margin_left="16px", 
                margin_bottom="8px", 
                margin_top="8px",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            rx.text(
                "The most unique new feature to land in the app is the ability to wager for or against each constructor as the season progresses. \
                    Not only are league drivers able to login and make wagers, anyone with a Discord account can join in on the fun and make it up the \
                        predictons market leaderboard. Submitting a prediction is as simple as navigating to the Power Rankings section of the app, assesing the \
                            projections tab, and then logging in and submitting a prediction on the predictions tab. Most importantly, all new logins receive 100 free \
                                Alternative Points. But that is all you get, so make your wagers count!",
                color="#E0E0E0",
                font_size="md",
                line_height="1.7",
            ),
            width="100%",
            margin_bottom="4",
        ),

        "As a reminder to all, the predictions market is simply for entertainment purposes, no money is tied to this market. But, the predictions market is not the only \
            new feature to make its way into the app recently. A new method for seeing driver lineages has been added to the All Time Stats section. The teammate \
                network depicts all directly and indirectly related drivers as a web of bubbles and degrees of separation. This feature, along with the new league map \
                    provide a more wholisitic, non-stats oriented, view of the entire league. Throughout the app users will also notice an increase of new pie charts, \
                        improved graph downloads, and keys on many graphs that help filter just to a single driver or team.",

        rx.heading(
            "League Round-Up and Assessments", 
            size="4", 
            color="#00b4da", 
            margin_top="6", 
            margin_bottom="3", 
            font_family="Outfit"
        ),

        "With all this said, it is time to review just where the league stands after two races. Pundits around the league have been flooding our \
            inboxes with praise, commentary, and expectations for the rest of the season. One such pundit overheard a small group of drivers discussing the new \
                projections algorithms, where one driver was discussing how the models might not feel accurate and another said with a bit of confidence:",

        rx.box(
            rx.text(
                "\"I'll break the models.\"",
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

        "Other conversations around the league are centered around how well ex-teammates Jaden and Jario are doing with their current status being second and third. \
            But many critics are saying, even if they were still teammates, they would still be 12 points behind the Cadillac duo.",

        "While analyzing these different critiques and reviews of drivers, an intriguing statistic came to light. Three times in league history, the first two races \
            were won by the same driver. In Season 1, then rookie McLaren driver Nick won in both Bahrain and Jeddah. He then went on to win his first Driver's Championship. \
                In Season 3, then Alpine driver Joshua took home the win in Suzuka and Silverstone. He and his long-time teammate Eddie went on to win their first \
                    Constructor's Championship. This season, the streaking sophomore Josh has won the first two races of the season. Does this mean he is destined \
                        for at least one championship? Or maybe, following the pattern through, both. One thing we do know, today, no one has ever won the first \
                            three races in a single season.",

        "Both Nick and Joshua are intriguing drivers to consider this season. Both having won championships. Both seeking another Cosntructor's Championship. \
            Interestingly, all-time league leader, Nick has bounced back mariginally with his start this season. Scoring a few more points thus far and standing on \
                the second step of the podium already. Joshua, however, is trending in the other direction with only a third place podium thus far. Both drivers \
                    are certainly worth following throughout the season."

        "With the top few drivers discussed, it is prudent to take a moment and note some of the bright moments further down into the midfield. An extremely notable \
            performance so far this season is the commanding first seat that Evelo has taken for Audi. Currently, Boz has found himself with a bum vehicle in both \
                regular season races. Meaning, he has been unable to score thus far, and Evelo has taken as much of an advantage as he can so far. In similar fashion, \
                    new Mercedes driver and league rookie, Randy, has impressed in his first official outing with the team. In fact, this season, with 6 places gained \
                        in Australia, he holds the best average for gaining positions.",

        "Randy's record may soon be overtaken if Del and his revitalized pace have anything to say about it. Unfortunately Del has had to make starts from the back each \
            race due to improper time management by team boss Zak Brown and how he has Del scheduled for media and propmotional events. As the season progresses, \
                this may not always be the case and we may begin to see Del driving and commanding races from the front.",

        "Mixed up in the midfield are both Patrick and Eddie. The latter of which has been doing everything his teammate has asked of him 'just score points.' \
            Patrick has also found himself scoring points, but has had his worst two race start to a season yet. The shining spot for his drive so far has been adding \
                an additional fastest lap to his all-time statistics. His ex-teammate Brently has also found himself in a similarly down position early in the season. \
                    As time progresses, will we see the once promising duo regain confidence and speed? Both Josh and Matthew hope so.",

        "Speaking of Matthew, he has found himself in a rather even keel position compared to his rookie season. With his high-speed performance in Hungary, many \
            correspondents have begun expecting him to knock it out of the park in Miami under the same sprint format. Speaking of sprints in Miami, Leo finds \
                himself faster, but not yet converting all that pace into points. He certainly hopes to overcome the chaos that occurred in last year's Miami weekend \
                    by putting a statement race down into the records in a week's time.",

        "Finally, the two rookies at Williams are left to discuss. Grayson and Josh C. are both neck and neck to be prove out who will be the team's lead driver. \
            Time will be the only indicator of who has what it takes between the two of them. As we wait on that, enjoy the week away, the new features, and time \
                to pracitce the lovely hybrid circuit around Miami's Hard Rock Stadium. Until we meet again, cheers."
    ],
    "image": "/thealternativef1-cloudflare/Season5/Bye_Week/Bye1/bw1-cover.png",
    "author": "Patrick",
    "date": "September 20, 2026",
    "season": 5,
}
