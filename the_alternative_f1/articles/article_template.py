import reflex as rx

article = {
    "title": "Article Template & Sample Rich Card",
    "blurb": "A showcase of dynamic content, images, subheaders, quotes, white boxes, gifs, and video elements.",
    "content": [
        # Two paragraphs with bold, italics, underline, and highlighted text throughout
        rx.text(
            "Welcome to the ",
            rx.text("rich content article template", as_="span", font_weight="bold"),
            "! This sample demonstration page shows how we can use inline styles and custom elements. Here, we highlight key information with a ",
            rx.text("vibrant cyan background", as_="span", bg="#00b4da", color="black", padding_x="1", border_radius="sm"),
            ", emphasize concepts using ",
            rx.text("elegant italics", as_="em"),
            ", and make headers or terms distinct using ",
            rx.text("underlined text", as_="span", text_decoration="underline"),
            ". This allows for highly expressive storytelling.",
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
        
        # A sub header after the two paragraphs before another paragraph
        rx.heading(
            "Technical Performance & Data Insights", 
            size="4", 
            color="#00b4da", 
            margin_top="6", 
            margin_bottom="3",
            font_family="Outfit"
        ),
        
        # A paragraph with a white background and black text in its own box within the article
        rx.box(
            rx.text(
                "CRITICAL UPDATE: This is a standalone callout box configured with a solid white background and crisp black text. It provides maximum contrast to immediately pull the reader's attention to warnings, official regulations, or race announcements.",
                color="black",
                font_weight="600",
                font_size="sm",
            ),
            bg="white",
            padding="4",
            border_radius="md",
            border="1px solid #E0E0E0",
            width="100%",
            margin_y="4",
        ),
        
        # A .gif
        rx.vstack(
            rx.text("Dynamic GIF Asset", color="#888888", font_size="xs", margin_bottom="1"),
            rx.image(
                src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExM3BxeDR6bXY0N3Rrb3V4dnZ0YnRqcDZ6N2x1eGFsZ3FhcDZtc3E3ZCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o7TKSjRrfIPjei1fG/giphy.gif",
                width="100%",
                max_width="400px",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.4)"
            ),
            align_items="center",
            width="100%",
            margin_y="4",
        ),
        
        # A .mp4
        rx.vstack(
            rx.text("Video Broadcast Loop", color="#888888", font_size="xs", margin_bottom="1"),
            rx.video(
                src="https://media.w3.org/2010/05/sintel/trailer_hd.mp4",
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
        
        # An indented paragraph in a lighter font like a quote from someone
        rx.box(
            rx.text(
                "\"The engineering team has unlocked tremendous aerodynamic balance with the new front wing package, giving both drivers the confidence to push harder through the high-speed curves.\"",
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
        
        # A paragraph that includes quotation marks mid sentence
        rx.text(
            "When asked about their targets for the weekend, the lead race engineer stated that they are focusing on \"maximizing tire life through the final stint\" to secure the podium.",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
    ],
    "image": "/article_f1_future.png",
    "author": "System Administrator",
    "date": "June 24, 2026",
    "season": 5,
}
