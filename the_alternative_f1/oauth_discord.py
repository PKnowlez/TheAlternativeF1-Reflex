import reflex as rx
import os

def load_env():
    # Load .env file from the workspace root (parent of 'the_alternative_f1')
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)
    env_path = os.path.join(root_dir, ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip()
                    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                        v = v[1:-1]
                    os.environ[k] = v

# Run on startup when module is imported
load_env()

class OauthState(rx.State):
    username: str = "Lewis Hamilton"
    avatar: str = "https://api.dicebear.com/7.x/avataaars/svg?seed=Lewis"

    discord_username: str = rx.LocalStorage("", name="discord_username", sync=True)
    discord_avatar: str = rx.LocalStorage("", name="discord_avatar", sync=True)

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
        self.discord_username = self.username
        self.discord_avatar = self.avatar
        return rx.call_script("window.close();")

    def cancel(self):
        return rx.call_script("window.close();")

    @rx.var
    def is_oauth_callback(self) -> bool:
        return bool(self.router.url.query_parameters.get("code"))

    def handle_on_load(self):
        import urllib.request
        import urllib.parse
        import json

        # Check if code is present in query parameters
        code = self.router.url.query_parameters.get("code")
        if not code:
            return

        try:
            client_id = os.getenv("DISCORD_CLIENT_ID", "").strip()
            client_secret = os.getenv("DISCORD_CLIENT_SECRET", "").strip()
            redirect_uri = os.getenv("DISCORD_REDIRECT_URI", "").strip()

            if not client_id or not client_secret or not redirect_uri:
                print("Missing Discord client ID, secret, or redirect URI in environment.")
                return

            # Exchange code for token
            data = {
                'client_id': client_id,
                'client_secret': client_secret,
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': redirect_uri
            }
            encoded_data = urllib.parse.urlencode(data).encode('utf-8')

            req = urllib.request.Request(
                'https://discord.com/api/oauth2/token',
                data=encoded_data,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': 'Reflex-Discord-OAuth'
                },
                method='POST'
            )

            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                access_token = res_data.get('access_token')

            if not access_token:
                print("Failed to retrieve access token from Discord.")
                return

            # Fetch user details
            req_user = urllib.request.Request(
                'https://discord.com/api/users/@me',
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'User-Agent': 'Reflex-Discord-OAuth'
                },
                method='GET'
            )

            with urllib.request.urlopen(req_user) as response:
                user_info = json.loads(response.read().decode('utf-8'))

            username = user_info.get('global_name') or user_info.get('username', 'Unknown')
            user_id = user_info.get('id')
            avatar_hash = user_info.get('avatar')

            if avatar_hash:
                avatar_url = f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.png"
            else:
                avatar_url = f"https://api.dicebear.com/7.x/avataaars/svg?seed={username}"

            self.discord_username = username
            self.discord_avatar = avatar_url

            return rx.call_script("window.close();")
        except Exception as e:
            print(f"OAuth callback handling failed: {e}")


@rx.page(route="/oauth/discord", title="Discord Authorize", on_load=OauthState.handle_on_load)
def oauth_discord() -> rx.Component:
    return rx.center(
        rx.cond(
            OauthState.is_oauth_callback,
            # Show a beautiful loading spinner during OAuth callback processing
            rx.vstack(
                rx.spinner(size="3", color="#5865F2"),
                rx.text("Authorizing with Discord...", color="white", font_weight="700", font_size="lg", margin_top="4"),
                rx.text("Please do not close this window.", color="#b9bbbe", font_size="sm"),
                align="center",
                spacing="2",
                bg="#36393f",
                padding="8",
                border_radius="lg",
                box_shadow="0 8px 16px rgba(0,0,0,0.2)",
            ),
            # Otherwise show the mock dashboard
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
        ),
        width="100%",
        height="100vh",
        bg="#2f3136",
    )
