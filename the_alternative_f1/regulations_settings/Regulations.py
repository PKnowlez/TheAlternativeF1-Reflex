import reflex as rx

def Regulations() -> rx.Component:
    rules_data = [
        ("Points Eligibility", "Points are only awarded to drivers that complete the race. No points are awarded to those who DNS or DNF."),
        ("Finishing Points", "Points are awarded based on finishing position in each race and follow the following pattern: 1st - 25, 2nd - 18, 3rd - 15, 4th - 12, 5th - 10, 6th - 8, 7th - 6, 8th - 4, 9th - 3, 10th - 2, 11th to 20th - 1."),
        ("Fastest Lap Award", "One (1) point will be awarded to the driver with the Fastest Lap at the end of the race."),
        ("Driver of the Day Award", "One (1) point will be awarded to the driver who earns Driver of the Day at the end of the race."),
        ("Most Overtakes Award", "One (1) point will be awarded to the driver with the Most Overtakes at the end of the race."),
        ("Cleanest Driver Award", "One (1) point will be awarded to the driver who earns Cleanest Driver at the end of the race."),
        ("VSC or Safety Car Delta Glitch", "If a driver wrongfully receives a Drive Through Penalty due to a VSC or Safety Car delta glitch, the driver will have their finishing time improved by 20 seconds. This remedy will only be applied upon driver request and review by the FIA, if no Safety Car or Red Flag occurs after the glitch occurred."),
        ("Endangering or Ruining Another Driver's Race*", "If a driver's race is ruined (DNF) or endangered (more than 3 lost places) due to reckless driving actions of another driver, the reckless driver will be awarded a 5 place penalty to their finishing position. If the reckless driving is deemed intentional, the driver will be disqualified.*"),
        ("Right to Protest", "Any driver that disagrees with a ruling, has the right to protest the ruling within one day of the final ruling. This protest will be reviewed by the league and require a 2/3rds majority vote to overturn."),
        ("Penalty Points", "Drivers who earn an Endangering or Ruining Another Driver's Race penalty will also earn a penalty point. If a driver earns two (2) penalty points, their next offense will increase the severity by an additional two (2) places. For every additional 2 penalty points after that, the place penalty will increase by three (3) places."),
        ("Sprint Day Format", "Sprint Qualifying > Sprint > Race Qualifying = Reverse Grid set by Sprint Results (All AI will be placed in front of ALL drivers, regardless of finishing position)"),
        ("Sprint Race Finishing Points", "Points are awarded based on finishing position in each race and follow the following pattern: 1st - 8, 2nd - 7, 3rd - 6, 4th - 5, 5th - 4, 6th - 3, 7th - 2, 8th - 1, 9th to 20th - 0.5."),
        ("Race Start Incident", "During the start of a race or Red Flag restart, any driver found to be the cause of an incident will be penalized in the next main race they participate in.** An incident in this scenario is any collision, squeeze, or brake check, involving one or more cars getting damage or losing more than 3 places due to the incident. The driver at fault will be penalized by being unable to compete in Q2 of the next race. In other words, the driver will qualify last, unless there are late drivers, in which those drivers that are late will start behind the offending driver from the previous race. A penalty point will also be added to the driver's super license for the remainder of the season."),
        ("Causing a Collision", "In some scenarios, drivers may cause a collision that is not severe enough to meet the requirements of Regulation 8 - Endangering or Ruining Another Driver's Race. In these scenarios, drivers who cause a collision will be penalized with a 5 second or 10 second penalty to their finishing position. The size of the penalty will be based on league review and severity of the incident. A penalty point will also be added to the driver's super license for remainder of the season."),
        ("Race Restarts", "Races will not be restarted for racing incidents. If there is a bug or glitch during or before the race start, the race may be restarted depending on the scenario.")
    ]

    return rx.vstack(
        rx.heading("Sporting & Technical Regulations", size="6", color="white", font_weight="900", margin_bottom="4", padding_y="2.5%", padding_x="2%"),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("#", width=["30px", "40px"], color="#00b4da"),
                    rx.table.column_header_cell("Regulation", width=["100px", "150px", "220px"], color="#00b4da"),
                    rx.table.column_header_cell("Definition / Rule Description", color="#00b4da"),
                )
            ),
            rx.table.body(
                *[
                    rx.table.row(
                        rx.table.cell(str(idx + 1), font_weight="bold", color="#888888"),
                        rx.table.cell(title, color="white", font_weight="700"),
                        rx.table.cell(definition, color="#CCCCCC"),
                        _hover={"bg": "#1C1C20"},
                    )
                    for idx, (title, definition) in enumerate(rules_data)
                ]
            ),
            gap = "5%",
            width="100%",
            variant="ghost",
        ),
        # Footnotes
        rx.vstack(
            rx.text(
                "*This regulation only applies after the first 2 laps of the race or restart. If reckless driving occurs during a start or restart, the incident will be reviewed per request of the driver whose race was endangered or ruined.",
                font_size="xs",
                color="#888888",
            ),
            rx.text(
                "**This regulation will be modified for the final race of the season to penalize the driver on their finishing position in the final race, rather than carrying over to the next season.",
                font_size="xs",
                color="#888888",
            ),
            spacing="1",
            margin_top="6",
            align_items="start",
            width="100%",
            padding="2.5%",
        ),
        gap = "5%",
        width="100%",
        bg="#18181C",
        padding="6",
        border_radius="xl",
        border="1px solid #2C2C32",
        align_items="start",
        margin_bottom="160px",
    )