import reflex as rx
import os
import httpx
import json
import html

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
    """Triggers backend download for an image file without opening a new tab."""
    return DownloadState.download_image(url)

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
                    on_click=lambda: DownloadState.download_image(src),
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
    def download_image(self, url: str):
        """Downloads an image file on the backend and sends an automatic download event to the browser."""
        full_url = rewrite_r2_url(url)
        filename = full_url.split("/")[-1].split("?")[0] or "image.png"
        
        # Local asset check
        if full_url.startswith("/"):
            rel_path = full_url.lstrip("/")
            for p in [os.path.join("assets", rel_path), os.path.join("public", rel_path), rel_path]:
                if os.path.exists(p):
                    with open(p, "rb") as f:
                        data = f.read()
                    return rx.download(data=data, filename=filename)

        # Remote URL fetch via HTTP Client (bypasses browser CORS)
        try:
            with httpx.Client(follow_redirects=True, timeout=15.0) as client:
                resp = client.get(full_url)
                resp.raise_for_status()
                mime = resp.headers.get("content-type")
                return rx.download(data=resp.content, filename=filename, mime_type=mime or None)
        except Exception as e:
            print(f"Error fetching image on backend for {full_url}: {e}")

    def download_chart(self, chart_id: str, title: str):
        js_code = f"""
        (async () => {{
            const loadHtml2Canvas = () => new Promise((resolve, reject) => {{
                if (window.html2canvas) return resolve(window.html2canvas);
                const script = document.createElement('script');
                script.src = 'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js';
                script.onload = () => resolve(window.html2canvas);
                script.onerror = reject;
                document.head.appendChild(script);
            }});

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
            
            const triggerFileDownload = (href, downloadFilename) => {{
                const downloadLink = document.createElement('a');
                downloadLink.href = href;
                downloadLink.download = downloadFilename;
                document.body.appendChild(downloadLink);
                downloadLink.click();
                document.body.removeChild(downloadLink);
            }};

            const cleanTitle = "{title}".replace(/[^a-zA-Z0-9' \\(\\)\\-_]/g, '').trim();
            const localDate = new Date();
            const year = localDate.getFullYear();
            const month = String(localDate.getMonth() + 1).padStart(2, '0');
            const day = String(localDate.getDate()).padStart(2, '0');
            const dateStr = `${{year}}-${{month}}-${{day}}`;
            const targetFilename = `${{cleanTitle}}_${{dateStr}}.png`;
            
            const fallbackPngExport = async () => {{
                try {{
                    const html2canvas = await loadHtml2Canvas();
                    const computedBg = getComputedStyle(document.documentElement).getPropertyValue('--main-bg-color').trim() || '#47474c';
                    const chartCanvas = await html2canvas(container, {{
                        scale: scaleFactor,
                        backgroundColor: computedBg,
                        useCORS: true,
                        allowTaint: true,
                        logging: false
                    }});
                    const pngURL = chartCanvas.toDataURL('image/png');
                    triggerFileDownload(pngURL, targetFilename);
                }} catch (err) {{
                    console.error('Chart html2canvas fallback failed:', err);
                }}
            }};

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
            
            const style = document.createElementNS('http://www.w3.org/2000/svg', 'style');
            style.type = 'text/css';
            style.textContent = fontCss + `
                text {{
                    font-family: 'Outfit', sans-serif !important;
                }}
            `;
            clonedSvg.insertBefore(style, clonedSvg.firstChild);
            
            let svgString = new XMLSerializer().serializeToString(clonedSvg);
            svgString = svgString.replace(/url\\(['"]?https?:\\/\\/[^'")\\s]+['"]?\\)/g, 'none');

            const svgBlob = new Blob([svgString], {{ type: 'image/svg+xml;charset=utf-8' }});
            const blobUrl = URL.createObjectURL(svgBlob);
            const image = new Image();
            image.crossOrigin = 'anonymous';

            image.onload = () => {{
                try {{
                    const canvas = document.createElement('canvas');
                    canvas.width = width * scaleFactor;
                    canvas.height = (height + titleSpace) * scaleFactor;
                    const context = canvas.getContext('2d');
                    
                    const computedColor = getComputedStyle(document.documentElement).getPropertyValue('--main-bg-color').trim() || '#47474c';
                    
                    context.fillStyle = computedColor;
                    context.fillRect(0, 0, canvas.width, canvas.height);
                    
                    context.fillStyle = '#FFFFFF';
                    context.font = `bold ${{Math.round(16 * scaleFactor)}}px Outfit, sans-serif`;
                    context.textBaseline = 'middle';
                    context.fillText("{title}", 20 * scaleFactor, (titleSpace / 2) * scaleFactor);
                    
                    context.drawImage(image, 0, titleSpace * scaleFactor, width * scaleFactor, height * scaleFactor);
                    
                    const pngURL = canvas.toDataURL('image/png');
                    triggerFileDownload(pngURL, targetFilename);
                    URL.revokeObjectURL(blobUrl);
                }} catch (e) {{
                    console.error('Chart canvas export error:', e);
                    fallbackPngExport();
                }}
            }};

            image.onerror = (err) => {{
                console.error('Chart SVG load error:', err);
                fallbackPngExport();
            }};

            image.src = blobUrl;
        }})();
        """
        return rx.call_script(js_code)

    def download_table(self, table_id: str, title: str):
        js_code = f"""
        (async () => {{
            const loadHtml2Canvas = () => new Promise((resolve, reject) => {{
                if (window.html2canvas) return resolve(window.html2canvas);
                const script = document.createElement('script');
                script.src = 'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js';
                script.onload = () => resolve(window.html2canvas);
                script.onerror = reject;
                document.head.appendChild(script);
            }});

            const tableElement = document.getElementById('{table_id}');
            if (!tableElement) {{
                console.error('Table element {table_id} not found');
                return;
            }}
            
            const triggerFileDownload = (href, downloadFilename) => {{
                const downloadLink = document.createElement('a');
                downloadLink.href = href;
                downloadLink.download = downloadFilename;
                document.body.appendChild(downloadLink);
                downloadLink.click();
                document.body.removeChild(downloadLink);
            }};

            const cleanTitle = "{title}".replace(/[^a-zA-Z0-9' \\(\\)\\-_]/g, '').trim();
            const localDate = new Date();
            const year = localDate.getFullYear();
            const month = String(localDate.getMonth() + 1).padStart(2, '0');
            const day = String(localDate.getDate()).padStart(2, '0');
            const dateStr = `${{year}}-${{month}}-${{day}}`;
            const targetFilename = `${{cleanTitle}}_${{dateStr}}.png`;

            const computedBg = getComputedStyle(document.documentElement).getPropertyValue('--main-bg-color').trim() || '#47474c';
            const scaleFactor = 2.5;
            const titleSpace = 50;

            try {{
                const html2canvas = await loadHtml2Canvas();
                const tableCanvas = await html2canvas(tableElement, {{
                    scale: scaleFactor,
                    backgroundColor: computedBg,
                    useCORS: true,
                    allowTaint: true,
                    logging: false
                }});

                const finalCanvas = document.createElement('canvas');
                finalCanvas.width = tableCanvas.width;
                finalCanvas.height = tableCanvas.height + Math.round(titleSpace * scaleFactor);
                const context = finalCanvas.getContext('2d');

                // Fill canvas background
                context.fillStyle = computedBg;
                context.fillRect(0, 0, finalCanvas.width, finalCanvas.height);

                // Draw Title Text at top
                context.fillStyle = '#FFFFFF';
                context.font = `bold ${{Math.round(16 * scaleFactor)}}px Outfit, sans-serif`;
                context.textBaseline = 'middle';
                context.fillText("{title}", Math.round(20 * scaleFactor), Math.round((titleSpace / 2) * scaleFactor));

                // Draw table canvas below title
                context.drawImage(tableCanvas, 0, Math.round(titleSpace * scaleFactor));

                const pngURL = finalCanvas.toDataURL('image/png');
                triggerFileDownload(pngURL, targetFilename);
            }} catch (err) {{
                console.error('Table PNG export error:', err);
                const bbox = tableElement.getBoundingClientRect();
                const fallbackCanvas = document.createElement('canvas');
                fallbackCanvas.width = Math.round((bbox.width || 500) * scaleFactor);
                fallbackCanvas.height = Math.round(((bbox.height || 400) + titleSpace) * scaleFactor);
                const context = fallbackCanvas.getContext('2d');
                context.fillStyle = computedBg;
                context.fillRect(0, 0, fallbackCanvas.width, fallbackCanvas.height);
                context.fillStyle = '#FFFFFF';
                context.font = `bold ${{Math.round(16 * scaleFactor)}}px Outfit, sans-serif`;
                context.textBaseline = 'middle';
                context.fillText("{title}", Math.round(20 * scaleFactor), Math.round((titleSpace / 2) * scaleFactor));
                const pngURL = fallbackCanvas.toDataURL('image/png');
                triggerFileDownload(pngURL, targetFilename);
            }}
        }})();
        """
        return rx.call_script(js_code)



def zoomable_chart_script() -> rx.Component:
    """Injects global CSS and native JavaScript event listeners for zoomable_chart bar value selection."""
    js_code = """
    (function() {
        const IGNORED_KEYS = new Set([
            'x', 'y', 'cx', 'cy', 'width', 'height', 'depth', 'index', 'rx', 'ry', 'r',
            'strokeWidth', 'opacity', 'offset', 'minWidth', 'minHeight', 'maxHeight',
            'maxWidth', 'margin', 'top', 'left', 'bottom', 'right', 'z', 'zIndex'
        ]);

        function handleChartClick(ev) {
            const container = ev.target ? ev.target.closest('.zoomable-chart-popout-container, [role="dialog"]') : null;

            const removeExisting = () => {
                document.querySelectorAll('.bar-value-tag-box').forEach(t => t.remove());
                document.querySelectorAll('.selected-bar-highlight').forEach(el => {
                    el.classList.remove('selected-bar-highlight');
                    if (el.dataset.origStroke !== undefined) el.style.stroke = el.dataset.origStroke;
                    if (el.dataset.origStrokeWidth !== undefined) el.style.strokeWidth = el.dataset.origStrokeWidth;
                    if (el.dataset.origFilter !== undefined) el.style.filter = el.dataset.origFilter;
                });
            };

            if (!container) {
                removeExisting();
                return;
            }

            const clickX = ev.clientX;
            const clickY = ev.clientY;
            if (clickX === undefined || clickY === undefined) return;

            let barNodes = Array.from(container.querySelectorAll(
                '.recharts-bar-rectangle, .recharts-rectangle, .recharts-bar-rectangles path, .recharts-bar-rectangles rect, g.recharts-bar path, g.recharts-bar rect, path.recharts-bar-rectangle, rect.recharts-bar-rectangle, .recharts-bar path, .recharts-bar rect'
            ));

            barNodes = barNodes.filter(el => {
                const r = el.getBoundingClientRect();
                return r.width > 0 && r.height > 0;
            });

            if (barNodes.length === 0) {
                removeExisting();
                return;
            }

            let selectedBar = null;

            if (ev.target && (ev.target.tagName === 'path' || ev.target.tagName === 'rect' || ev.target.tagName === 'PATH' || ev.target.tagName === 'RECT')) {
                const r = ev.target.getBoundingClientRect();
                if (r.width > 0 && r.height > 0 && container.contains(ev.target)) {
                    selectedBar = ev.target;
                }
            }

            if (!selectedBar) {
                let selectedIdx = -1;
                let minDist = Infinity;

                for (let i = 0; i < barNodes.length; i++) {
                    const r = barNodes[i].getBoundingClientRect();
                    const minX = r.left - 6;
                    const maxX = r.right + 6;
                    const minY = Math.min(r.top, r.bottom) - 10;
                    const maxY = Math.max(r.top, r.bottom) + 10;

                    if (clickX >= minX && clickX <= maxX && clickY >= minY && clickY <= maxY) {
                        const dist = Math.abs(clickX - (r.left + r.width / 2));
                        if (dist < minDist) {
                            minDist = dist;
                            selectedBar = barNodes[i];
                            selectedIdx = i;
                        }
                    }
                }

                if (!selectedBar) {
                    for (let i = 0; i < barNodes.length; i++) {
                        const r = barNodes[i].getBoundingClientRect();
                        const centerX = r.left + r.width / 2;
                        const centerY = r.top + r.height / 2;
                        const dist = Math.hypot(clickX - centerX, clickY - centerY);
                        if (dist < minDist && dist < 45) {
                            minDist = dist;
                            selectedBar = barNodes[i];
                            selectedIdx = i;
                        }
                    }
                }
            }

            if (!selectedBar) {
                removeExisting();
                return;
            }

            removeExisting();

            selectedBar.classList.add('selected-bar-highlight');
            selectedBar.dataset.origStroke = selectedBar.style.stroke || '';
            selectedBar.dataset.origStrokeWidth = selectedBar.style.strokeWidth || '';
            selectedBar.dataset.origFilter = selectedBar.style.filter || '';
            selectedBar.style.stroke = '#FFFFFF';
            selectedBar.style.strokeWidth = '2px';
            selectedBar.style.filter = 'drop-shadow(0px 0px 6px rgba(255, 255, 255, 0.95))';

            let val = null;
            let nodeFiber = null;
            let elForFiber = selectedBar;
            while (!nodeFiber && elForFiber && elForFiber !== container) {
                for (let k in elForFiber) {
                    if (k.startsWith('__reactFiber') || k.startsWith('__reactInternalInstance')) {
                        nodeFiber = elForFiber[k];
                        break;
                    }
                }
                elForFiber = elForFiber.parentElement;
            }

            let currFiber = nodeFiber;
            let barDataKey = null;
            let chartData = null;
            let detectedLayout = 'horizontal';

            while (currFiber) {
                const props = currFiber.memoizedProps || currFiber.pendingProps;
                if (props) {
                    if (props.layout) detectedLayout = props.layout;
                    if (props.dataKey && typeof props.dataKey === 'string') barDataKey = props.dataKey;
                    if (props.data && Array.isArray(props.data)) chartData = props.data;

                    if (val === null) {
                        if (props.value !== undefined && props.value !== null) {
                            if (typeof props.value === 'number') {
                                val = props.value;
                            } else if (Array.isArray(props.value)) {
                                val = props.value.length >= 2 ? (props.value[1] - props.value[0]) : props.value[0];
                            } else if (typeof props.value === 'string' && !isNaN(parseFloat(props.value))) {
                                val = parseFloat(props.value);
                            }
                        }
                    }

                    if (val === null && props.payload && typeof props.payload === 'object') {
                        if (barDataKey && props.payload[barDataKey] !== undefined && props.payload[barDataKey] !== null) {
                            let p = parseFloat(props.payload[barDataKey]);
                            val = !isNaN(p) ? p : props.payload[barDataKey];
                        } else {
                            for (let key in props.payload) {
                                if (!IGNORED_KEYS.has(key) && key !== 'name' && key !== 'driver' && key !== 'team' && key !== 'race' && key !== 'track' && key !== 'placement' && key !== 'place' && key !== 'fill') {
                                    let v = props.payload[key];
                                    if (typeof v === 'number' && !isNaN(v)) {
                                        val = v;
                                        break;
                                    }
                                }
                            }
                        }
                    }
                }
                currFiber = currFiber.return;
            }

            if (val === null && chartData) {
                let barIdx = barNodes.indexOf(selectedBar);
                if (barIdx >= 0 && barIdx < chartData.length) {
                    const item = chartData[barIdx];
                    if (item) {
                        if (barDataKey && item[barDataKey] !== undefined && item[barDataKey] !== null) {
                            let p = parseFloat(item[barDataKey]);
                            val = !isNaN(p) ? p : item[barDataKey];
                        } else if (typeof item === 'object') {
                            for (let key in item) {
                                if (!IGNORED_KEYS.has(key) && key !== 'name' && key !== 'driver' && key !== 'team' && key !== 'race' && key !== 'track' && key !== 'placement' && key !== 'place' && key !== 'fill') {
                                    let v = item[key];
                                    if (typeof v === 'number' && !isNaN(v)) {
                                        val = v;
                                        break;
                                    }
                                }
                            }
                        }
                    }
                }
            }

            if (val === null || val === undefined) {
                const titleEl = selectedBar.querySelector('title') || (selectedBar.parentElement ? selectedBar.parentElement.querySelector('title') : null);
                if (titleEl && titleEl.textContent) {
                    const parts = titleEl.textContent.split(':');
                    const parsed = parseFloat(parts[parts.length - 1].trim());
                    if (!isNaN(parsed)) val = parsed;
                }
            }

            if (val === null || val === undefined) {
                val = 0;
            }

            let numVal = typeof val === 'number' ? val : parseFloat(val);
            let displayVal = !isNaN(numVal) ? (Number.isInteger(numVal) ? numVal.toString() : numVal.toFixed(1)) : String(val);

            const containerRect = container.getBoundingClientRect();
            const barRect = selectedBar.getBoundingClientRect();

            const tag = document.createElement('div');
            tag.className = 'bar-value-tag-box';
            tag.innerText = displayVal;

            const isHorizontalBarChart = detectedLayout === 'vertical';
            let tagTop, tagLeft;

            if (isHorizontalBarChart) {
                const isNegative = !isNaN(numVal) && numVal < 0;
                tagTop = (barRect.top - containerRect.top + (barRect.height / 2)) + 'px';
                tagLeft = isNegative
                    ? (barRect.left - containerRect.left - 12) + 'px'
                    : (barRect.right - containerRect.left + 12) + 'px';
            } else {
                const isNegative = !isNaN(numVal) && numVal < 0;
                tagTop = isNegative 
                    ? (barRect.bottom - containerRect.top + 8) + 'px'
                    : Math.max(0, barRect.top - containerRect.top - 38) + 'px';
                tagLeft = (barRect.left - containerRect.left + (barRect.width / 2)) + 'px';
            }

            Object.assign(tag.style, {
                position: 'absolute',
                top: tagTop,
                left: tagLeft,
                transform: isHorizontalBarChart ? 'translateY(-50%)' : 'translateX(-50%)',
                backgroundColor: '#FFFFFF',
                color: '#111115',
                fontSize: '13px',
                fontWeight: '800',
                padding: '4px 10px',
                borderRadius: '6px',
                boxShadow: '0 4px 12px rgba(0,0,0,0.6)',
                pointerEvents: 'none',
                zIndex: '10000',
                whiteSpace: 'nowrap',
                fontFamily: 'Outfit, sans-serif',
                border: '2px solid #00b4da'
            });

            const arrow = document.createElement('div');
            if (!isHorizontalBarChart) {
                const isNegative = !isNaN(numVal) && numVal < 0;
                if (isNegative) {
                    Object.assign(arrow.style, {
                        position: 'absolute',
                        top: '-7px',
                        left: '50%',
                        transform: 'translateX(-50%)',
                        width: '0',
                        height: '0',
                        borderLeft: '6px solid transparent',
                        borderRight: '6px solid transparent',
                        borderBottom: '7px solid #FFFFFF'
                    });
                } else {
                    Object.assign(arrow.style, {
                        position: 'absolute',
                        bottom: '-7px',
                        left: '50%',
                        transform: 'translateX(-50%)',
                        width: '0',
                        height: '0',
                        borderLeft: '6px solid transparent',
                        borderRight: '6px solid transparent',
                        borderTop: '7px solid #FFFFFF'
                    });
                }
            } else {
                const isNegative = !isNaN(numVal) && numVal < 0;
                if (isNegative) {
                    Object.assign(arrow.style, {
                        position: 'absolute',
                        right: '-7px',
                        top: '50%',
                        transform: 'translateY(-50%)',
                        width: '0',
                        height: '0',
                        borderTop: '6px solid transparent',
                        borderBottom: '6px solid transparent',
                        borderLeft: '7px solid #FFFFFF'
                    });
                } else {
                    Object.assign(arrow.style, {
                        position: 'absolute',
                        left: '-7px',
                        top: '50%',
                        transform: 'translateY(-50%)',
                        width: '0',
                        height: '0',
                        borderTop: '6px solid transparent',
                        borderBottom: '6px solid transparent',
                        borderRight: '7px solid #FFFFFF'
                    });
                }
            }

            tag.appendChild(arrow);
            container.appendChild(tag);
        }

        if (window.__zoomableChartHandler) {
            document.removeEventListener('click', window.__zoomableChartHandler, true);
            document.removeEventListener('pointerdown', window.__zoomableChartHandler, true);
        }
        window.__zoomableChartHandler = handleChartClick;
        document.addEventListener('click', handleChartClick, true);
        document.addEventListener('pointerdown', handleChartClick, true);
    })();
    """
    style_content = """
    .zoomable-chart-popout-container:focus,
    .zoomable-chart-popout-container:focus-visible,
    .zoomable-chart-popout-container:focus-within,
    .zoomable-chart-popout-container * :focus,
    .zoomable-chart-popout-container * :focus-visible {
        outline: none !important;
        box-shadow: none !important;
    }
    """
    return rx.fragment(
        rx.html(f"<style>{style_content}</style>"),
        rx.script(js_code),
    )


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
    
    return rx.fragment(
        zoomable_chart_script(),
        rx.dialog.root(
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
                        class_name="zoomable-chart-popout-container",
                        width="100%",
                        position="relative",
                        outline="none",
                        style={"outline": "none", "boxShadow": "none"},
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
        ),
    )


def image_carousel(
    items: list,
    auto_progress_seconds: float = 5.0,
    height: str = "450px",
    width: str = "100%",
    max_width: str = "100%",
    border_radius: str = "12px",
    **kwargs
) -> rx.Component:
    """An interactive image and GIF carousel component.
    
    Features:
    - Touch swipe gestures & desktop mouse drag
    - Left/Right click zones and glassmorphic chevron buttons
    - Auto-progression every N seconds (default: 5.0)
    - Smooth animated progress bar & pause on hover
    - Pagination dots and item counter pill
    - Supports both static images (.png, .jpg, .webp) and animated GIFs
    - Automatically rewrites Cloudflare R2 URLs
    """
    normalized_items = []
    for item in items:
        if isinstance(item, str):
            src = rewrite_r2_url(item)
            normalized_items.append({"src": src, "caption": ""})
        elif isinstance(item, dict):
            src = rewrite_r2_url(item.get("src", ""))
            caption = item.get("caption", item.get("title", ""))
            normalized_items.append({"src": src, "caption": caption})
        elif isinstance(item, (list, tuple)) and len(item) >= 1:
            src = rewrite_r2_url(item[0])
            caption = item[1] if len(item) > 1 else ""
            normalized_items.append({"src": src, "caption": caption})

    items_json = json.dumps(normalized_items)
    escaped_items_json = html.escape(items_json, quote=True)
    auto_progress_ms = int(auto_progress_seconds * 1000)

    carousel_html = (
        f'<f1-carousel data-items="{escaped_items_json}" '
        f'auto-progress="{auto_progress_ms}" '
        f'style="width: 100%; height: 100%; display: block; border-radius: {border_radius};">'
        f'</f1-carousel>'
    )

    margin_y = kwargs.pop("margin_y", "4")

    return rx.fragment(
        rx.script(src="/carousel.js"),
        rx.box(
            rx.html(
                carousel_html,
                height="100%",
                width="100%",
                style={"height": "100%", "width": "100%"},
            ),
            width=width,
            max_width=max_width,
            height=height,
            border_radius=border_radius,
            overflow="hidden",
            margin_y=margin_y,
            **kwargs,
        ),
    )


