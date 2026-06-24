import reflex as rx

article = {
    "title": "New App, Who Dis?",
    "blurb": "A short walkthrough of how to navigate the new app.",
    "content": [
        # Two paragraphs with bold, italics, underline, and highlighted text throughout
        rx.text(
            "Welcome to Season 5 of The Alternative F1's sim racing league, where racing meets integrity, or whatever Erick used to say. This season we have a new app with new UI. Because of that, the boss man figured I needed to walk all you numbskulls through how the app works. This feels really rudimentary...but I, the illustrious intern, have authored the following guide to the features that work now and the features that are coming soon to the app."
            "First and foremost, all",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        
        # An inline image within one of the paragraphs justified on the right
        rx.box(
            rx.image(
                src="/article_f1_tech.png", 
                float="right", 
                width="150px", 
                margin_left="16px", 
                margin_bottom="8px", 
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.3)"
            ),
            rx.text(
                "This paragraph demonstrates wrapping text around an inline image on the right. By utilizing CSS float properties, the text naturally flows around the image boundary. This is perfect for team logos, sponsor badges, or telemetry chart snapshots that enhance the article. We also add standard decoration like a ",
                rx.text("subtle shadow", as_="span", font_weight="bold"),
                " and a rounded border to the image to keep the interface feeling premium.",
                color="#E0E0E0",
                font_size="md",
                line_height="1.7",
            ),
            width="100%",
            margin_bottom="4",
        ),
    ],
    "image": "/logo_with_black.png",
    "author": "The Intern",
    "date": "June 24, 2026",
    "season": 0,
}
