import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Abu Dhabi Recap: No, Erick, No, No, Erick, That Was So Not Right!",
    "blurb": "At this point I think I am the real employee here and Patrick is just the note taking intern.",
    "content": [
rx.text(
    r"""At this point I think I am the real employee here and Patrick is just the note taking intern. That’s right, I am back yet again. The notes kinda suck (shocker) so I’ll do my best. There apparently was a heaping mess of absolute garbage strategy and driving during quali. Like, the notes say hotshot Joshua didn’t even set a time in Q2? I kinda think Patrick just wrote the notes wrong…but after reviewing the quali results Joshua straight up fumbled the bag, giving Nick a golden opportunity to secure the championship under the lights in Abu Dhabi Max Verstappen style. I heard y’all loved the map of Erick’s mistakes so I decided to give you a variant of that, I call it Joshua’s quali line:""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.vstack(
    rx.text("Joshua Abu Dhabi Qualifying Line", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/Season3/Images/Abu_Dhabi_Joshua_Quali.png",
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
    r"""I also heard that Eddie biffed it during quali. Something about not knowing how to do the simplest of racing activities, a drag race. Apparently he earned himself a 5-place grid penalty for sucking so much at drag racing. His brother Erick also had a moment during quali where he was a bit too extra out of a corner and almost missed putting a time in during Q1.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.text(
    r"""High-key seems a little over the top for just a quali, but with it closed out it looked like VCARB and Nick had incredible opportunities to close in or even close out the championships. But y’all just can’t have a simple race, can you? As you are very aware at this point, I am low-key a huge fan of memes. So, Imma just recap the rest in my preferred art form.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.vstack(
    rx.text("Abu Dhabi Race Memes", color="#888888", font_size="xs", margin_bottom="1"),
    zoomable_image(
        src="/Season3/Images/Abu_Dhabi_Memes.png",
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
    r"""Yep, that’s right, Joshua came back from 15th, McLaren kept their lead alive with help from Travis and Nick even though Logan Sargeant tried to screw that up, Del and Erick went through a horror show with Ferrari, Boz cooked his tires, Eddie continued to be delulu, Brently and Erick battled like real F1 drivers, Patrick really screwed the pooch, and Fetty Wap kept bopping on the JBL speaker all night long.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
rx.text(
    r"""With only two races left, Aston Martin has been eliminated from the Constructor’s Championship contention, and realistically it's a 2.5 horse race between McLaren, Alpine, and sorta VCARB. The Driver’s Championship eliminated everyone but Nick and Joshua. However, while I brushed off the battle for third place last week, it's really heated up. Erick, Patrick, Brently, and Del are within one race win’s swing for third. Who knows, it could come down to quick math and team orders between the VCARB or Ferrari teammates depending on how the next two races and Sprints unfold. Buckle up for an exciting penultimate race in Austria.""",
    color="#E0E0E0",
    font_size="md",
    line_height="1.7",
    margin_bottom="4",
),
    ],
    "image": "/Season3/Images/Abu_Dhabi_Joshua_Quali.png",
    "author": "The Intern",
    "date": "February 6, 2025",
    "season": 3,
}
