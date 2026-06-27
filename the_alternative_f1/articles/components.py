import reflex as rx

def zoomable_image(src: str, **kwargs) -> rx.Component:
    """An image component that opens a fullscreen modal with a download button when clicked.
    
    Supports float and positioning styles by wrapping the dialog root in a layout box.
    """
    # Extract layout properties to apply to the outer wrapper box
    # Set default values on styling keys if they aren't provided
    kwargs.setdefault("border_radius", "md")
    kwargs.setdefault("box_shadow", "0 4px 12px rgba(0,0,0,0.3)")
    kwargs.setdefault("cursor", "pointer")
    kwargs.setdefault("object_fit", "cover")
    
    # The small thumbnail image that triggers the modal gets all styles and layout props
    image_trigger = rx.image(
        src=src,
        **kwargs
    )
    
    return rx.dialog.root(
        rx.dialog.trigger(image_trigger),
        rx.dialog.content(
            # Close button (X) in the top-right corner
            rx.dialog.close(
                rx.button(
                    rx.icon("x", size=16),
                    variant="ghost",
                    color="white",
                    position="absolute",
                    top="12px",
                    right="12px",
                    _hover={"bg": "#00b4da"},
                    cursor="pointer",
                ),
            ),
            # Modal layout (Large image + Download button)
            rx.vstack(
                rx.image(
                    src=src,
                    width="100%",
                    max_height="75vh",
                    object_fit="contain",
                    border_radius="md",
                ),
                rx.button(
                    rx.hstack(
                        rx.icon("download", size=16),
                        rx.text("Download Image"),
                        spacing="2",
                    ),
                    on_click=rx.download(url=src),
                    bg="#00b4da",
                    color="white",
                    _hover={"bg": "#009bbd"},
                    cursor="pointer",
                    margin_top="4",
                ),
                align="center",
                width="100%",
                spacing="4",
            ),
            bg="#111111",
            border="1px solid #2C2C32",
            max_width="90vw",
            width="auto",
        ),
    )
