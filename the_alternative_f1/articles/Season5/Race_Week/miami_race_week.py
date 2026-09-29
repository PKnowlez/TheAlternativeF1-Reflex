import reflex as rx
from the_alternative_f1.articles.components import zoomable_image, image_carousel

article = {
    "title": "Race Week: Miami",
    "blurb": "Notoriously Nick's favorite track, and the league's first official sprint race. Could this shake things up in the standings? Will Jelly continue his current dominance? Has the reigning champ's honeymoon hangover finally cleared?",
    "content": [
        "Sprint races have been an integral part of The Alternative F1 league's schedule for the past two seasons. \
            This season, officials signed six tracks to host sprints. This week's race, Miami, will be the first  \
                for the drivers to overcome. As the season progresses, the league will face sprints at each of the \
                    following tracks: Miami, Spa, Silverstone, Bahrain, Zandvoort, and Singapore.",

        "Beyond just the points teams can secure via the sprint race itself, the results of the sprint will determine \
            the grid positions for the feature race, by reversing the order of the sprint results. Historically, sprint \
                races for the league have allowed for shakeups in the standings along with new winners and a number of  \
                    other driver and team advancements.",
        
        rx.box(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Week/overtakes_sprint_vs_regular.png",
                float="left", 
                width="250px", 
                margin_right="16px",
                margin_bottom="8px", 
                margin_top="8px", 
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            rx.text(
                "One of the most intriguing statistics to come out of the first ever sprint relates, unsurprisingly, to overtakes. \
                    The intrigung nature of the statistic is not just that there were lots of overstakes due to the reverse grid, \
                        but that in Season 3 the first ever sprint race provided double the total overtakes than all of the previous \
                            races combined. For the fans who love racing, sprints certainly deliver. In two out of the previous six sprint  \
                                weeks, first time winners have been crowned. Additionally, two drivers have made it onto the podium \
                                    for their first time. One final statistic that correlates with sprint weeks is how often they \
                                        swing momentum. In Season 4, Nick broke Jairo's four race win streak in Spa. In Season 3, \
                                            the race in China snapped the winners duopoly Nick and Joshua had been busy creating.",
                color="#E0E0E0",
                font_size="md",
                line_height="1.7",
            ),
            width="100%",
            margin_bottom="4",
        ),

        rx.box(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Week/miami_constructor_results.png",
                float="right", 
                width="250px", 
                margin_left="16px",
                margin_bottom="8px", 
                margin_top="8px", 
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            rx.text(
                "Taking a look back at how sprints change the league's overall composition is only one part of the big picture \
                    drivers are about to face. So, let us take a moment and look back at the few Miami results the league has \
                        recorded over time. Only four constructors have ever stood on an in-season Miami feature race podium. \
                            But more importantly, only one constructor has ever won in during a feature race in Miami. With two wins to his name, Nick, \
                                the outspoken Miami hater, has won in both Season 1 and Season 4. Nick has even won during a \
                                    preseason race in Miami ahead of Season 3. So what will Season 5 bring? \
                                    Can Nick keep this streak alive? Can Jelly keep his current in season win streak alive? Can Joshua \
                                        break out of the funk and return to the top step? Can previously dominant contenders \
                                            like Jairo, Jaden, or Patrick get things going? Can a surprise winner take home \
                                                their first ever win?",
                color="#E0E0E0",
                font_size="md",
                line_height="1.7",
            ),
            width="100%",
            margin_bottom="4",
        ),

        rx.vstack(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Race_Week/Miami_Track.jpeg", 
                width="100%",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            align_items="center",
            width="100%",
            margin_y="4",
        ),

        "Finally, it is time to take a look at the track itself. With three straight mode zones, a very flowy first sector, and a \
            challenging second sector, Miami has enough to provide some exciting racing. \
                Each lap, drivers will be presented with a nominal overtake spot at the end of the back straight. \
                However, for those with unique battery strategies the run up to Turn 11 may provide a simple moment for a safe \
                    overtake. Both of these otpions have their own consequences as overtaking in Turn 17 provides your opponent \
                        with boost and overtaking during the straight mode up to Turn 11 has a few narrow bends that the racing \
                            line sticks to, forcing the driver to be cautious. This week's race is sure to be interesting due \
                                to the track and the nature of the league's sprint format.",   
    ],
    "image": "/thealternativef1-cloudflare/Season5/Race_Week/Miami_Cover.jpeg",
    "author": "Patrick",
    "date": "September 28, 2026",
    "season": 5,
}
