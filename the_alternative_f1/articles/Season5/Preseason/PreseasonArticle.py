import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Preseason Round-Up",
    "blurb": "With just a few weeks left before rubber meets the roads, let's take a look at the tracks the drivers will tackle during preseason.",
    "content": [
        "This season, the drivers will take on the longest preseason in league history. Three tracks, three chances to dust off the gloves and 'lock in' as our reigning driver's champ, Joshua, might scream. Before our illustrious intern takes over and recaps how the league has faired at each track previously, let's talk about a few of the historic aspects of this season.",
        "First and foremost, this will be the largest number of drivers and teams to ever grace The Alternative F1 League's paddock. With 8 constructors and 16 drivers vying for championships, we may see one of the most competitive seasons yet. In addition to the strong grid, we also have all new constructors taking to the field with Williams, Haas, Cadillac, and Audi all bringing entries. This does, however, mean we have lost a few regular runners like Aston Martin and VCARB, but as the league grows we are sure to see them return.",
        "With such a shakeup, it is critical to look into how dynamic some of the pairings are. Does Nick finally have a consistent teammate to battle for the Constructors Championship? Will the Cadillac duo bring the heat they had last season? Can the new look Mercedes team pull themselves up by the proverbial bootstraps?",
        "This year, we will begin to see answers to these questions in Mexico City. A track famous for its stadium section, and in the league, infamous for its rainy day supremacy by Jario and Jaden last season. It is unlikely that during this event a true pecking order will identify itself. However, with three preseason races, we are likely to have a good understanding of the power rankings as we head down under for the first official race of the season."
        "But before we put a shrimp on the barbie, the league will head to Las Vegas for a thrilling night race chase down The Strip. This season, the regulations will stretch strategists to consider new methods for tires, battery, and when to attack on this straight dominant circuit. Once the checkered flag flies in Vegas, drivers will quickly shift their thinking towards Hungary where we will race a first of its kind preseason Sprint race. In fact, Hungary will host a number of firsts this season as the league has never raced there in any capacity. With all this said, let's enjoy a bit of a walk down memory lane, authored by The Intern.",
        rx.box(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Preseason/Mexico_Missing.png", 
                float="right", 
                width="200px", 
                margin_left="16px",
                margin_top="8px", 
                margin_bottom="8px", 
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            rx.text(
                "Get ready to rumble folks, because every time these bafoons have taken Mexico or Vegas, drama has ensued. And guess what twin, it isn't always fun racing drama. Mexico last season was a truly dominant outing by the Mercs. So much so that the maFIA linked up with those politicians that have all those weather controlling machines and shut down any chance of rain for the rest of the season. But that wasn't all, we were also delivered a first podium for rookie Josh, Nick's 1000th point, and the first 1-2 since Season 1. The Tavera bros also ghosted their teammates...let's hope for all of our sakes, Eddie doesn't ghost Joshua...I am sure many of you can already hear him whining about it...",
                color="#E0E0E0",
                font_size="md",
                line_height="1.7",
            ),
            width="100%",
            margin_bottom="4",
        ),
        rx.vstack(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Preseason/Vegas_Finish.png",
                width="100%",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.4)"
            ),
            align_items="center",
            width="100%",
            margin_y="4",
        ),
        "Now Vegas was drama for all sorts of other reasons. A double header no one wanted but everyone got, a crazy 1-2-3 photo finish, Del toasted, Yuki fighting Newman, Joshua and Jairo screaming at each other post race, Leo becoming the defacto Ferrari #1, and 1,000,000 VSCs and SCs.",
        rx.vstack(
            rx.video(
                src="/thealternativef1-cloudflare/Season5/Preseason/Vegas.mp4",
                width="100%",
                height="auto",
                controls=True,
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.4)"
            ),
            align_items="center",
            width="100%",
            margin_y="4",
        ),
        rx.vstack(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Preseason/Vegas_Leo.png",
                width="100%",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.4)"
            ),
            align_items="center",
            width="100%",
            margin_y="4",
        ),
        rx.vstack(
            zoomable_image(
                src="/thealternativef1-cloudflare/Season5/Preseason/Vegas_Joshua.png",
                width="100%",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.4)"
            ),
            align_items="center",
            width="100%",
            margin_y="4",
        ),
        "And with all this said, I, your faithful intern, am so stoked to meme on you clowns for another great season. If you feel offended, suck it up. If you don't, let me know in the comments so I can amp it up. Cheers nerds."
    ],
    "image": "/thealternativef1-cloudflare/Season5/Preseason/Preseason.png",
    "author": "Patrick and The Intern",
    "date": "July 27, 2026",
    "season": 5,
}