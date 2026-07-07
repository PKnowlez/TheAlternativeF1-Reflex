import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "The Legend and The Hopeful",
    "blurb": "McLaren rebuilds after Travis retires and Erick’s new found lifestyle takes him away from the sport.",
    "content": [
        "What happens when a seat vacates just weeks before the season begins? A controversial silly season occurs. Del joins Nick at McLaren in an effort to bring the team back to its former Season 2 championship glory. But will he survive racing in the legend’s shadow?",
        "Nick had a down season last year. Many throughout the paddock are claiming he has peaked. But he has been overheard telling people that his distraction with WEC is over, ensuring that nothing but a championship this season will be considered a success. His Testing of Previous Car (TPC) efforts earlier this pre-season have a handful of pundits believing him.",
        "But what of his teammate? A new driver hasn’t driven for McLaren since their second season in the league, the season that the pairing took them to a championship. Will Del have what it takes to score consistently? Our intrepid Intern reached out to Del for comments on all this speculation and he said,",
        rx.box(
            rx.text(
                "\"I’m joining a great team. Nick and I have had some really good races against eachother so I think being teammates will help bring this team back to its former glory. As for people wondering if I can score consistently; McLaren in 13.\"",
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
        "His teammate Nick has shown a great deal of public support as well,",
        rx.box(
            rx.text(
                "\"Thrilled to have Del join McLaren. When he joined the league we fought on track constantly. He forced me to up my game. I remember at Abu Dhabi when we both spun while wheel to wheel at turn 9 almost killing the rest of the grid. We always gave each other room to race though. After last season we both need to come back fighting. I was distracted with WEC and the rumors Del was racing after indulging a left-handed cigarette from time to time. Maybe these new regs will suit us better than last years cars.\"",
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
    ],
    "image": "/thealternativef1-cloudflare/Season5/Grid_Announcements/Grid_McLaren_2.png",
    "author": "Patrick",
    "date": "July 7, 2026",
    "season": 5,
}
