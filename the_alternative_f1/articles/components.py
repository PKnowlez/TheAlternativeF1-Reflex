import reflex as rx
import os

R2_CUSTOM_DOMAIN = os.getenv("R2_CUSTOM_DOMAIN", "https://pknowlez.com").rstrip("/")

def rewrite_r2_url(url: str) -> str:
    if isinstance(url, str) and url.startswith("/thealternativef1-cloudflare/"):
        return url.replace("/thealternativef1-cloudflare/", f"{R2_CUSTOM_DOMAIN}/", 1)
    return url

def rewrite_paths_in_component(component):
    if not isinstance(component, rx.Component):
        return
        
    for attr in ["src", "url"]:
        if hasattr(component, attr):
            val = getattr(component, attr)
            if hasattr(val, "_var_value"):
                val = val._var_value
            if isinstance(val, str) and val.startswith("/thealternativef1-cloudflare/"):
                new_val = val.replace("/thealternativef1-cloudflare/", f"{R2_CUSTOM_DOMAIN}/", 1)
                setattr(component, attr, new_val)
                if "_cached_render_result" in component.__dict__:
                    del component.__dict__["_cached_render_result"]
                    
    if hasattr(component, "children") and component.children:
        for child in component.children:
            rewrite_paths_in_component(child)

def download_external_image(url: str):
    filename = url.split("/")[-1] or "download"
    js_code = f"""
    (async () => {{
        try {{
            const response = await fetch('{url}');
            const blob = await response.blob();
            const blobUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = blobUrl;
            a.download = '{filename}';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(blobUrl);
        }} catch (e) {{
            console.error('Failed to download image', e);
            window.open('{url}', '_blank');
        }}
    }})();
    """
    return rx.call_script(js_code)

def zoomable_image(src: str, **kwargs) -> rx.Component:
    """An image component that opens a fullscreen modal with a download button when clicked.
    
    Supports float and positioning styles by wrapping the dialog root in a layout box.
    """
    src = rewrite_r2_url(src)
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
                    on_click=download_external_image(src),
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
            
            const bbox = svgElement.getBoundingClientRect();
            const width = bbox.width || 800;
            const height = bbox.height || 450;
            const scaleFactor = 3.125; // 300 DPI / 96 DPI
            const titleSpace = 50;
            
            // Try to fetch, convert and inline Outfit font from Google Fonts dynamically
            let fontCss = "";
            try {{
                const cssResponse = await fetch("https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&display=swap");
                let cssText = await cssResponse.text();
                const urlRegex = /url\\(['"]?(https:\\/\\/fonts\\.gstatic\\.com\\/[^'")\\s]+)['"]?\\)/g;
                let match;
                const urlsToReplace = [];
                while ((match = urlRegex.exec(cssText)) !== null) {{
                    urlsToReplace.push(match[1]);
                }}
                for (const fontUrl of urlsToReplace) {{
                    try {{
                        const fontResponse = await fetch(fontUrl);
                        const fontBlob = await fontResponse.blob();
                        const reader = new FileReader();
                        const base64Promise = new Promise((resolve) => {{
                            reader.onloadend = () => resolve(reader.result);
                        }});
                        reader.readAsDataURL(fontBlob);
                        const base64Url = await base64Promise;
                        cssText = cssText.replaceAll(fontUrl, base64Url);
                    }} catch (err) {{
                        console.warn("Could not inline font file:", fontUrl, err);
                    }}
                }}
                // Strip out any remaining remote gstatic urls to prevent tainting the canvas
                cssText = cssText.replace(/url\\(['"]?https:\\/\\/fonts\\.gstatic\\.com\\/[^'")\\s]+['"]?\\)/g, "local('Outfit')");
                fontCss = cssText;
            }} catch (e) {{
                console.warn("Could not fetch or inline Outfit font:", e);
            }}
            
            // Clone the SVG element and set high-res dimensions
            const clonedSvg = svgElement.cloneNode(true);
            clonedSvg.setAttribute('width', width * scaleFactor);
            clonedSvg.setAttribute('height', height * scaleFactor);
            if (!clonedSvg.getAttribute('viewBox')) {{
                clonedSvg.setAttribute('viewBox', `0 0 ${{width}} ${{height}}`);
            }}
            
            // Inject styles with embedded font-face to the SVG cloned element
            const style = document.createElementNS('http://www.w3.org/2000/svg', 'style');
            style.type = 'text/css';
            style.textContent = fontCss + `
                text {{
                    font-family: 'Outfit', sans-serif !important;
                }}
            `;
            clonedSvg.insertBefore(style, clonedSvg.firstChild);
            
            // Serialize SVG to XML string
            const svgString = new XMLSerializer().serializeToString(clonedSvg);
            const svgBlob = new Blob([svgString], {{ type: 'image/svg+xml;charset=utf-8' }});
            
            const reader = new FileReader();
            reader.onloadend = () => {{
                const dataURL = reader.result;
                const image = new Image();
                image.onload = () => {{
                    const canvas = document.createElement('canvas');
                    canvas.width = width * scaleFactor;
                    canvas.height = (height + titleSpace) * scaleFactor;
                    const context = canvas.getContext('2d');
                    
                    // Get main bg color from CSS variable dynamically
                    const computedColor = getComputedStyle(document.documentElement).getPropertyValue('--main-bg-color').trim() || '#47474c';
                    
                    // Fill canvas background
                    context.fillStyle = computedColor;
                    context.fillRect(0, 0, canvas.width, canvas.height);
                    
                    // Draw Title Text at the top
                    context.fillStyle = '#FFFFFF';
                    context.font = `bold ${{Math.round(16 * scaleFactor)}}px Outfit, sans-serif`;
                    context.textBaseline = 'middle';
                    context.fillText("{title}", 20 * scaleFactor, (titleSpace / 2) * scaleFactor);
                    
                    // Draw SVG image shifted below the title
                    context.drawImage(image, 0, titleSpace * scaleFactor, width * scaleFactor, height * scaleFactor);
                    
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
                }};
                image.src = dataURL;
            }};
            reader.readAsDataURL(svgBlob);
        }})();
        """
        return rx.call_script(js_code)

    def download_table(self, table_id: str, title: str):
        js_code = f"""
        (async () => {{
            const tableElement = document.getElementById('{table_id}');
            if (!tableElement) {{
                console.error('Table element {table_id} not found');
                return;
            }}
            
            const bbox = tableElement.getBoundingClientRect();
            const width = bbox.width || 500;
            const height = bbox.height || 600;
            const scaleFactor = 3.125; // 300 DPI / 96 DPI
            const titleSpace = 50;
            
            // Try to fetch, convert and inline Outfit font from Google Fonts dynamically
            let fontCss = "";
            try {{
                const cssResponse = await fetch("https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&display=swap");
                let cssText = await cssResponse.text();
                const urlRegex = /url\\(['"]?(https:\\/\\/fonts\\.gstatic\\.com\\/[^'")\\s]+)['"]?\\)/g;
                let match;
                const urlsToReplace = [];
                while ((match = urlRegex.exec(cssText)) !== null) {{
                    urlsToReplace.push(match[1]);
                }}
                for (const fontUrl of urlsToReplace) {{
                    try {{
                        const fontResponse = await fetch(fontUrl);
                        const fontBlob = await fontResponse.blob();
                        const reader = new FileReader();
                        const base64Promise = new Promise((resolve) => {{
                            reader.onloadend = () => resolve(reader.result);
                        }});
                        reader.readAsDataURL(fontBlob);
                        const base64Url = await base64Promise;
                        cssText = cssText.replaceAll(fontUrl, base64Url);
                    }} catch (err) {{
                        console.warn("Could not inline font file:", fontUrl, err);
                    }}
                }}
                // Strip out any remaining remote gstatic urls to prevent tainting the canvas
                cssText = cssText.replace(/url\\(['"]?https:\\/\\/fonts\\.gstatic\\.com\\/[^'")\\s]+['"]?\\)/g, "local('Outfit')");
                fontCss = cssText;
            }} catch (e) {{
                console.warn("Could not fetch or inline Outfit font:", e);
            }}
            
            // Helper function to clone element and inline all computed styles recursively, stripping remote/external url() references
            const cloneWithStyles = (element) => {{
                const clone = element.cloneNode(true);
                const descClone = clone.getElementsByTagName('*');
                const descOrig = element.getElementsByTagName('*');
                
                const sanitizeStyle = (styleObj, targetStyle) => {{
                    for (let i = 0; i < styleObj.length; i++) {{
                        const prop = styleObj[i];
                        let val = styleObj.getPropertyValue(prop);
                        
                        if (val && val.includes('url(')) {{
                            if (!val.includes('url("data:') && !val.includes("url('data:") && !val.includes("url(data:")) {{
                                val = 'none';
                            }}
                        }}
                        targetStyle.setProperty(prop, val, styleObj.getPropertyPriority(prop));
                    }}
                }};
                
                sanitizeStyle(getComputedStyle(element), clone.style);
                
                for (let i = 0; i < descOrig.length; i++) {{
                    sanitizeStyle(getComputedStyle(descOrig[i]), descClone[i].style);
                }}
                
                // Sanitize any img tags in the clone
                const images = clone.getElementsByTagName('img');
                for (let img of images) {{
                    if (img.src && !img.src.startsWith('data:')) {{
                        img.src = '';
                    }}
                }}
                return clone;
            }};
            
            const clonedTable = cloneWithStyles(tableElement);
            
            // Inject font and global styles inside the foreignObject SVG
            const svgString = `
                <svg xmlns="http://www.w3.org/2000/svg" width="${{width}}" height="${{height}}">
                    <foreignObject width="100%" height="100%">
                        <div xmlns="http://www.w3.org/1999/xhtml" style="width:100%; height:100%; padding:0; margin:0; font-family: 'Outfit', sans-serif !important;">
                            <style type="text/css">
                                ${{fontCss}}
                                * {{
                                    font-family: 'Outfit', sans-serif !important;
                                    box-sizing: border-box !important;
                                }}
                            </style>
                            ${{new XMLSerializer().serializeToString(clonedTable)}}
                        </div>
                    </foreignObject>
                </svg>
            `;
            
            const svgBlob = new Blob([svgString], {{ type: 'image/svg+xml;charset=utf-8' }});
            
            const reader = new FileReader();
            reader.onloadend = () => {{
                const dataURL = reader.result;
                const image = new Image();
                image.onload = () => {{
                    const canvas = document.createElement('canvas');
                    canvas.width = width * scaleFactor;
                    canvas.height = (height + titleSpace) * scaleFactor;
                    const context = canvas.getContext('2d');
                    
                    // Get main bg color from CSS variable dynamically
                    const computedColor = getComputedStyle(document.documentElement).getPropertyValue('--main-bg-color').trim() || '#47474c';
                    
                    // Fill canvas background
                    context.fillStyle = computedColor;
                    context.fillRect(0, 0, canvas.width, canvas.height);
                    
                    // Draw Title Text at the top
                    context.fillStyle = '#FFFFFF';
                    context.font = `bold ${{Math.round(16 * scaleFactor)}}px Outfit, sans-serif`;
                    context.textBaseline = 'middle';
                    context.fillText("{title}", 20 * scaleFactor, (titleSpace / 2) * scaleFactor);
                    
                    // Draw SVG image shifted below the title
                    context.drawImage(image, 0, titleSpace * scaleFactor, width * scaleFactor, height * scaleFactor);
                    
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
                }};
                image.src = dataURL;
            }};
            reader.readAsDataURL(svgBlob);
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
    
    bar_click_js = f"""
    (() => {{
        const container = document.getElementById('{chart_id}');
        if (!container) return;
        const existing = container.querySelectorAll('.bar-value-tag-box');
        existing.forEach(e => e.remove());

        const ev = (typeof event !== 'undefined' && event) ? event : (window.event || null);
        if (!ev) return;
        let target = ev.target || (ev.touches && ev.touches[0] ? ev.touches[0].target : null);
        if (!target) return;

        let barElem = target.closest('.recharts-bar-rectangle, .recharts-rectangle, rect, path, .recharts-bar-cursor, .recharts-bar-symbol');
        if (!barElem) return;

        let val = null;

        const extractFromProps = (p) => {{
            if (!p) return null;
            if (p.payload && p.dataKey && p.payload[p.dataKey] !== undefined && p.payload[p.dataKey] !== null) {{
                return p.payload[p.dataKey];
            }}
            if (p.value !== undefined && p.value !== null) return p.value;
            if (p.val !== undefined && p.val !== null) return p.val;
            return null;
        }};

        const findProps = (el) => {{
            if (!el) return null;
            for (let k in el) {{
                if (k.startsWith('__reactProps') || k.startsWith('__reactFiber')) {{
                    let res = extractFromProps(el[k]);
                    if (res !== null) return res;
                    if (el[k].memoizedProps) {{
                        res = extractFromProps(el[k].memoizedProps);
                        if (res !== null) return res;
                    }}
                }}
            }}
            return null;
        }};

        let curr = barElem;
        while (curr && curr !== container && val === null) {{
            val = findProps(curr);
            curr = curr.parentElement;
        }}

        if (val === null || val === undefined) {{
            const tooltipVal = container.querySelector('.recharts-tooltip-item-value, .recharts-default-tooltip');
            if (tooltipVal && tooltipVal.textContent) {{
                let txt = tooltipVal.textContent.trim();
                let matches = txt.match(/[-+]?\\d*\\.?\\d+/);
                if (matches) val = matches[0];
            }}
        }}

        if (val === null || val === undefined) {{
            let titleEl = barElem.querySelector('title') || (barElem.parentElement ? barElem.parentElement.querySelector('title') : null);
            if (titleEl && titleEl.textContent) {{
                let parts = titleEl.textContent.split(':');
                val = parts[parts.length - 1].trim();
            }}
        }}

        if (val === null || val === undefined) return;

        if (typeof val === 'number') {{
            val = Number.isInteger(val) ? val.toString() : val.toFixed(1);
        }}

        const containerRect = container.getBoundingClientRect();
        const barRect = barElem.getBoundingClientRect();

        const tag = document.createElement('div');
        tag.className = 'bar-value-tag-box';
        tag.innerText = String(val);
        Object.assign(tag.style, {{
            position: 'absolute',
            top: Math.max(0, barRect.top - containerRect.top - 32) + 'px',
            left: (barRect.left - containerRect.left + (barRect.width / 2)) + 'px',
            transform: 'translateX(-50%)',
            backgroundColor: '#00b4da',
            color: '#ffffff',
            fontSize: '11px',
            fontWeight: 'bold',
            padding: '3px 8px',
            borderRadius: '4px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.5)',
            pointerEvents: 'none',
            zIndex: '1000',
            whiteSpace: 'nowrap',
            fontFamily: 'Outfit, sans-serif'
        }});

        const arrow = document.createElement('div');
        Object.assign(arrow.style, {{
            position: 'absolute',
            bottom: '-5px',
            left: '50%',
            transform: 'translateX(-50%)',
            width: '0',
            height: '0',
            borderLeft: '5px solid transparent',
            borderRight: '5px solid transparent',
            borderTop: '5px solid #00b4da'
        }});
        tag.appendChild(arrow);
        container.appendChild(tag);
    }})();
    """

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
                    position="relative",
                    on_click=rx.call_script(bar_click_js),
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

