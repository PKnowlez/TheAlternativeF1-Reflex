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
    discord_username: str = rx.LocalStorage("", name="discord_username", sync=True)
    discord_avatar: str = rx.LocalStorage("", name="discord_avatar", sync=True)
    error_message: str = ""

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
            self.error_message = "No Discord authorization code was received. Please try logging in again from the main site."
            return

        try:
            client_id = os.getenv("DISCORD_CLIENT_ID", "").strip()
            client_secret = os.getenv("DISCORD_CLIENT_SECRET", "").strip()
            redirect_uri = os.getenv("DISCORD_REDIRECT_URI", "").strip()

            if not client_id or not client_secret or not redirect_uri:
                print("Missing Discord client ID, secret, or redirect URI in environment.")
                self.error_message = "Discord OAuth client settings are missing on the server. Please contact an administrator."
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

            with urllib.request.urlopen(req, timeout=10) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                access_token = res_data.get('access_token')

            if not access_token:
                print("Failed to retrieve access token from Discord.")
                self.error_message = "Failed to retrieve access token from Discord. Please try again."
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

            with urllib.request.urlopen(req_user, timeout=10) as response:
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

            return rx.call_script(
                "if (window.opener) { "
                "  try { "
                "    const btn = window.opener.document.getElementById('complete-discord-login-btn');"
                "    if (btn) btn.click();"
                "  } catch (e) { "
                "    console.error('Error accessing opener document:', e);"
                "  }"
                "} "
                "window.close();"
            )
        except Exception as e:
            print(f"OAuth callback handling failed: {e}")
            self.error_message = f"An error occurred during authentication ({str(e)}). Please try logging in again from the main site."


@rx.page(route="/oauth/discord", title="Discord Authorize", on_load=OauthState.handle_on_load)
def oauth_discord() -> rx.Component:
    return rx.center(
        rx.cond(
            OauthState.error_message != "",
            # Show error message if it's set
            rx.vstack(
                rx.icon("x", color="#f43f5e", size=48),
                rx.text("Invalid Login Attempt", color="white", font_weight="700", font_size="lg", margin_top="4"),
                rx.text(OauthState.error_message, color="#b9bbbe", font_size="sm", text_align="center"),
                align="center",
                spacing="2",
                bg="#36393f",
                padding="8",
                border_radius="lg",
                box_shadow="0 8px 16px rgba(0,0,0,0.2)",
                max_width="400px",
            ),
            # Show a beautiful loading spinner during OAuth callback processing (or default while waiting)
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
        ),
        width="100%",
        height="100vh",
        bg="#2f3136",
    )
