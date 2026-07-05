import reflex as rx
from the_alternative_f1.articles.components import zoomable_image

article = {
    "title": "Untitled",
    "blurb": "For Immediate Release",
    "content": [
        rx.text(
            rx.text("Press Release", as_="span", font_weight="bold"), "", rx.text("For Immediate Release", as_="span", font_weight="bold"), "", rx.text("Date: October 9, 2025", as_="span", font_style="italic"),
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.heading(
            "Miami Race Results & Driver Penalty Points Update:",
            size="4",
            color="#00b4da",
            margin_top="6",
            margin_bottom="3",
            font_family="Outfit"
        ),
        rx.text(
            r"""Race officials have reviewed the incident in the final moments of the race between Mercedes' Jayden and Aston Martin's Del. It has been deemed that the maneuver was not on purpose but was on the fault of the Mercedes driver. Therefore, Jayden has been penalized five (5) places down to 8th place, and will have one (1) penalty point added to his license for the season.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Additionally, upon reviewing the incident between VCARB's Patrick and Ferrari's Leo, the FIA has determined there will be no action taken that affects the final results. Leo will not receive a penalty point on his license.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Finally, Alpine's Eddie was served a private written warning for his actions during the start of the Bahrain Grand Prix. This warning also adds one (1) penalty point to his license for the remainder of the season.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""The FIA co-presidents are open to inquiries, clarifications, and formal correspondence. For further discussion, please contact Erick Tavera or Nick Beglin.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            r"""Jayden and Eddie's verdicts should not be considered the standard or norm for the league. These decisions were determined due to unprecedented circumstances and factors that will not continue to be considered valid throughout the remainder of the season. Going forward, the FIA will uphold its written regulations with full rigor. This release should serve as the final regulation reminder and warning to all drivers.""",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.text(
            "League regulations can be found in the league's", rx.link("main app", href="https://thealternativef1.streamlit.app/", color="#00b4da", text_decoration="underline"), "under the Regulations & Settings sidebar dropdown.",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
        rx.vstack(
            rx.text("Surfer", color="#888888", font_size="xs", margin_bottom="1"),
            zoomable_image(
                src="/thealternativef1-cloudflare/Season4/Images/surfer.gif",
                width="100%",
                max_width="400px",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.4)"
            ),
            align_items="center",
            width="100%",
            margin_y="4",
        ),
    ],
    "image": "/thealternativef1-cloudflare/Season4/Images/surfer.gif",
    "author": "System Administrator",
    "date": "Season 4",
    "season": 4,
}
