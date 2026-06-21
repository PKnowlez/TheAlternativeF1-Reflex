import reflex as rx

config = rx.Config(
    app_name="the_alternative_f1",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)