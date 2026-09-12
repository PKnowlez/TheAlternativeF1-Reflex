/**
 * zoomable_chart.js
 * Global event listener for zoomable_chart bar value inspection and selection.
 * Listens on document so all charts across articles, standings, results,
 * constructor/driver stats, and popout dialogs are supported without per-chart duplication.
 */
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
