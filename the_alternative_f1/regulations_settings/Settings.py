import reflex as rx

def Settings() -> rx.Component:
    assist_restrictions = [
        ("Steering Assist", "Off"),
        ("Braking Assist", "Off"),
        ("Anti-Lock Brakes (ABS)", "On"),
        ("Traction Control", "Full"),
        ("Dynamic Racing Line", "Corners Only"),
        ("Gearbox", "Automatic"),
        ("Pit Assist", "On"),
        ("Pit Release Assist", "On"),
        ("ERS Assist", "Off"),
        ("DRS Assist", "Off"),
        ("Force Cockpit Camera", "Off"),
    ]

    simulation_settings = [
        ("Equal Car Performance", "On"),
        ("Recovery Mode", "None"),
        ("Surface Type", "Realistic"),
        ("Low Fuel Mode", "Easy"),
        ("Race Starts", "Manual"),
        ("Unsafe Pit Release", "Off"),
        ("Car Damage", "Simulation"),
        ("Car Damage Rate", "Simulation"),
        ("Collisions", "On"),
        ("Off for First Lap Only", "Disabled"),
        ("Off for Griefing", "Disabled"),
        ("Weather", "Dynamic"),
    ]

    rules_flags = [
        ("Rules & Flags", "On"),
        ("Corner Cutting Stringency", "Strict*"),
        ("Parc Ferme Rules", "On"),
        ("Pit Stop Experience", "Immersive"),
        ("Safety Car", "Increased"),
        ("Safety Car Experience", "Immersive"),
        ("Formation Lap", "Off"),
        ("Red Flags", "Standard"),
        ("Affects Licence Level", "Off"),
    ]

    weekend_structure = [
        ("Weekend Structure", "Standard"),
        ("Practice Format", "Off"),
        ("Qualifying Format", "Full"),
        ("Session Length", "Long (50%)"),
        ("Starting Grid", "Qualifying"),
    ]

    sprint_weekend = [
        ("Weekend Structure", "Sprint"),
        ("Practice Format", "Off"),
        ("Sprint Qualifying Format", "Short"),
        ("Race Qualifying Format", "Off"),
        ("Sprint Session Length", "Long"),
        ("Race Session Length", "Long"),
        ("Sprint Starting Grid", "Qualifying"),
        ("Race Starting Grid", "Reverse Sprint Results"),
    ]

    def mini_table(title: str, val_header: str, items: list) -> rx.Component:
        return rx.vstack(
            rx.heading(title, size="4", color="white", font_weight="800", padding="2.5%"),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell(title, color="#00b4da"),
                        rx.table.column_header_cell(val_header, color="#00b4da", justify="end"),
                    )
                ),
                rx.table.body(
                    *[
                        rx.table.row(
                            rx.table.cell(name, color="white", font_size="sm"),
                            rx.table.cell(val, color="#CCCCCC", justify="end", font_size="sm", font_weight="bold"),
                            _hover={"bg": "#1C1C20"},
                        )
                        for name, val in items
                    ]
                ),
                gap = "5%",
                width="100%",
                variant="ghost",
            ),
            width="100%",
            bg="#18181C",
            padding="4",
            border_radius="xl",
            border="1px solid #2C2C32",
        )

    return rx.vstack(
        rx.heading("League Settings & Configuration", size="6", color="white", font_weight="900", margin_bottom="4", padding="2.5%"),
        
        # Row 1: Assist Restrictions & Simulation Settings
        rx.grid(
            mini_table("Assist Restrictions", "Setting", assist_restrictions),
            mini_table("Simulation Settings", "Setting", simulation_settings),
            columns=rx.breakpoints(initial="1", md="2"),
            spacing="5",
            width="100%",
        ),
        
        rx.divider(border_color="#2C2C32", margin_y="40px"),

        # Row 2: Rules & Flags, Regular Weekend, Sprint Weekend
        rx.grid(
            mini_table("Rules & Flags", "Setting", rules_flags),
            mini_table("Regular Weekend Structure", "Parameter", weekend_structure),
            mini_table("Sprint Weekend Structure", "Setting", sprint_weekend),
            columns=rx.breakpoints(initial="1", md="3"),
            spacing="5",
            width="100%",
        ),

        # Footnote
        rx.text(
            "*Depending on the track this setting may be adjusted to ensure a competitive and enjoyable racing experience.",
            font_size="xs",
            color="#888888",
            margin_top="4",
            padding="2.5%",

        ),
        gap = "5%",
        width="100%",
        align_items="start",
    )
