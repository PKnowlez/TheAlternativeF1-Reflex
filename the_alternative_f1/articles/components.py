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


class DownloadState(rx.State):
    def download_chart(self, chart_id: str, title: str):
        js_code = f"""
        (async () => {{
            const container = document.getElementById('{chart_id}');
            if (!container) {{
                console.error('Chart container {chart_id} not found');
                return;
            }}
            const svgElement = container.querySelector('svg');
            if (!svgElement) {{
                console.error('SVG not found inside container {chart_id}');
                return;
            }}
            
            // Serialize SVG to XML string
            const svgString = new XMLSerializer().serializeToString(svgElement);
            const svgBlob = new Blob([svgString], {{ type: 'image/svg+xml;charset=utf-8' }});
            const URL = window.URL || window.webkitURL || window;
            const blobURL = URL.createObjectURL(svgBlob);
            
            const image = new Image();
            image.onload = () => {{
                const canvas = document.createElement('canvas');
                const bbox = svgElement.getBoundingClientRect();
                const width = bbox.width || 800;
                const height = bbox.height || 450;
                const titleSpace = 50;
                
                canvas.width = width;
                canvas.height = height + titleSpace;
                const context = canvas.getContext('2d');
                
                // Get main bg color from CSS variable dynamically
                const computedColor = getComputedStyle(document.documentElement).getPropertyValue('--main-bg-color').trim() || '#47474c';
                
                // Fill canvas background
                context.fillStyle = computedColor;
                context.fillRect(0, 0, canvas.width, canvas.height);
                
                // Draw Title Text at the top
                context.fillStyle = '#FFFFFF';
                context.font = 'bold 16px Outfit, sans-serif';
                context.textBaseline = 'middle';
                context.fillText("{title}", 20, titleSpace / 2);
                
                // Draw SVG image shifted below the title
                context.drawImage(image, 0, titleSpace, width, height);
                
                // Trigger download
                const pngURL = canvas.toDataURL('image/png');
                const downloadLink = document.createElement('a');
                const cleanTitle = "{title}".replace(/[^a-zA-Z0-9' \\(\\)\\-_]/g, '').trim();
                
                const localDate = new Date();
                const year = localDate.getFullYear();
                const month = String(localDate.getMonth() + 1).padStart(2, '0');
                const day = String(localDate.getDate()).padStart(2, '0');
                const dateStr = `${{year}}-${{month}}-${{day}}`;
                
                downloadLink.href = pngURL;
                downloadLink.download = `${{cleanTitle}}_${{dateStr}}.png`;
                document.body.appendChild(downloadLink);
                downloadLink.click();
                document.body.removeChild(downloadLink);
                URL.revokeObjectURL(blobURL);
            }};
            image.src = blobURL;
        }})();
        """
        return rx.call_script(js_code)


def zoomable_chart(chart_factory, title: str, chart_id: str, height: int = 350, large_height: int = 450) -> rx.Component:
    """Wraps a chart component to make it expandable in a modal dialog with a dynamic background download PNG button."""
    
    small_chart_trigger = rx.box(
        chart_factory(height),
        cursor="pointer",
        width="100%",
        border_radius="md",
        transition="transform 0.15s ease-in-out, box-shadow 0.15s ease-in-out",
        _hover={
            "transform": "scale(1.005)",
            "box_shadow": "0 4px 20px rgba(0,0,0,0.15)",
        },
    )
    
    return rx.dialog.root(
        rx.dialog.trigger(small_chart_trigger),
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
            # Modal layout (Large chart + Title + Download button)
            rx.vstack(
                rx.text(title, color="white", font_weight="700", font_size="md", align_self="start", margin_bottom="2"),
                rx.box(
                    chart_factory(large_height),
                    id=chart_id,
                    width="100%",
                ),
                rx.button(
                    rx.hstack(
                        rx.icon("download", size=16),
                        rx.text("Download PNG"),
                        spacing="2",
                    ),
                    on_click=lambda: DownloadState.download_chart(chart_id, title),
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
            bg="var(--main-bg-color)",
            border="1px solid #5a5a60",
            max_width="90vw",
            width=["100%", "90vw", "800px"],
        ),
    )
