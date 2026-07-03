import reflex as rx
import os

def load_env():
    # Load .env file from the current directory
    env_path = ".env"
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

load_env()

config = rx.Config(
    app_name="the_alternative_f1",
    db_url=os.getenv("DATABASE_URL", "sqlite:////tmp/reflex.db" if os.name != "nt" else "sqlite:///reflex.db"),
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)