import reflex as rx

class OauthState(rx.State):
    username: str = "Lewis Hamilton"
    avatar: str = "https://api.dicebear.com/7.x/avataaars/svg?seed=Lewis"

    def select_preset(self, name: str):
        self.username = name
        presets = {
            "Max Verstappen": "https://api.dicebear.com/7.x/avataaars/svg?seed=Max",
            "Lewis Hamilton": "https://api.dicebear.com/7.x/avataaars/svg?seed=Lewis",
            "Lando Norris": "https://api.dicebear.com/7.x/avataaars/svg?seed=Lando",
            "Charles Leclerc": "https://api.dicebear.com/7.x/avataaars/svg?seed=Charles",
            "Oscar Piastri": "https://api.dicebear.com/7.x/avataaars/svg?seed=Oscar",
        }
        self.avatar = presets.get(name, f"https://api.dicebear.com/7.x/avataaars/svg?seed={name}")

    def handle_username_change(self, val: str):
        self.username = val
        self.avatar = f"https://api.dicebear.com/7.x/avataaars/svg?seed={val}"

    def authorize(self):
        # Escaped single quotes to prevent javascript string breaking
        safe_username = self.username.replace("'", "\\'")
        safe_avatar = self.avatar.replace("'", "\\'")
        return rx.call_script(
            f"window.opener.postMessage({{type: 'discord_login', username: '{safe_username}', avatar: '{safe_avatar}'}}, '*'); window.close();"
        )

    def cancel(self):
        return rx.call_script("window.close();")


@rx.page(route="/oauth/discord", title="Discord Authorize")
def oauth_discord() -> rx.Component:
    return rx.center(
        rx.vstack(
            # Card Container
            rx.vstack(
                # Discord Logo/Header
                rx.hstack(
                    rx.image(
                        src="https://assets-global.website-files.com/6257adef93867e50d84d30e2/636e0a6a49cf127bf92de1e2_icon_clyde_blurple_RGB.png",
                        height="40px",
                        object_fit="contain",
                    ),
                    rx.heading("Discord", size="6", color="white", font_weight="700"),
                    spacing="2",
                    align="center",
                    margin_bottom="4",
                ),
                
                # App Title & Description
                rx.text(
                    "An external application, The Alternative F1, wants to access your Discord account.",
                    color="#b9bbbe",
                    font_size="sm",
                    text_align="center",
                    margin_bottom="6",
                ),

                # Permissions Requested List
                rx.vstack(
                    rx.text("THIS WILL ALLOW THE DEVELOPER OF THE ALTERNATIVE F1 TO:", color="#b9bbbe", font_size="10px", font_weight="800", align_self="start"),
                    rx.hstack(
                        rx.icon("circle-user", color="#4f545c", size=18),
                        rx.text("Access your username and avatar", color="#dcddde", font_size="sm"),
                        spacing="3",
                        align="center",
                    ),
                    spacing="3",
                    align_items="start",
                    width="100%",
                    bg="#2f3136",
                    padding="4",
                    border_radius="md",
                    margin_bottom="6",
                ),

                # Mock Profile Selector Header
                rx.text("SELECT OR TYPE DISCORD USERNAME TO TEST:", color="#b9bbbe", font_size="10px", font_weight="800", align_self="start"),

                # Quick Presets
                rx.flex(
                    *[
                        rx.button(
                            name,
                            size="1",
                            bg=rx.cond(OauthState.username == name, "#5865F2", "#4f545c"),
                            color="white",
                            on_click=lambda name=name: OauthState.select_preset(name),
                            _hover={"bg": "#5865F2"},
                            cursor="pointer",
                        )
                        for name in ["Max Verstappen", "Lewis Hamilton", "Lando Norris", "Charles Leclerc", "Oscar Piastri"]
                    ],
                    flex_wrap="wrap",
                    gap="2",
                    width="100%",
                    margin_bottom="4",
                ),

                # Custom Username input
                rx.vstack(
                    rx.input(
                        value=OauthState.username,
                        on_change=OauthState.handle_username_change,
                        placeholder="Or type custom username...",
                        width="100%",
                        bg="#202225",
                        border="1px solid #202225",
                        color="white",
                    ),
                    rx.hstack(
                        rx.avatar(
                            src=OauthState.avatar,
                            size="3",
                            fallback="U",
                            bg="#5865F2",
                        ),
                        rx.text(OauthState.username, color="white", font_weight="bold", font_size="sm"),
                        spacing="3",
                        align="center",
                        bg="#2f3136",
                        width="100%",
                        padding="2.5%",
                        border_radius="md",
                    ),
                    width="100%",
                    spacing="3",
                    margin_bottom="6",
                ),

                # Bottom Action Buttons
                rx.hstack(
                    rx.button(
                        "Cancel",
                        bg="#4f545c",
                        color="white",
                        _hover={"bg": "#686d73"},
                        on_click=OauthState.cancel,
                        width="48%",
                        cursor="pointer",
                    ),
                    rx.button(
                        "Authorize",
                        bg="#5865F2",
                        color="white",
                        _hover={"bg": "#4752c4"},
                        on_click=OauthState.authorize,
                        width="48%",
                        cursor="pointer",
                    ),
                    width="100%",
                    justify="between",
                ),

                width="100%",
                max_width="480px",
                bg="#36393f",
                padding="15%",
                border_radius="lg",
                box_shadow="0 8px 16px rgba(0,0,0,0.2)",
            ),
            width="100%",
            height="100vh",
            bg="#2f3136",
            justify="center",
            align="center",
            padding="4",
        ),
        width="100%",
        height="100vh",
        bg="#2f3136",
    )
