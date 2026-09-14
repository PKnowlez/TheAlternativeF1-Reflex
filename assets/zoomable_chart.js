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

    let lastChartClickTime = 0;

    function handleChartClick(ev) {
        if (ev.target && ev.target.closest('button, [data-html2canvas-ignore="true"], .rt-Button, a, input, select, textarea')) {
            return;
        }

        const container = ev.target ? ev.target.closest('.recharts-wrapper, .zoomable-chart-popout-container, [role="dialog"]') : null;

        const removeExisting = () => {
            document.querySelectorAll('.bar-value-tag-box').forEach(t => t.remove());
            document.querySelectorAll('.selected-bar-highlight').forEach(el => {
                el.classList.remove('selected-bar-highlight');
                if (el.dataset.origStroke !== undefined) {
                    if (el.dataset.origStroke) el.style.stroke = el.dataset.origStroke;
                    else el.style.removeProperty('stroke');
                }
                if (el.dataset.origStrokeWidth !== undefined) {
                    if (el.dataset.origStrokeWidth) el.style.strokeWidth = el.dataset.origStrokeWidth;
                    else el.style.removeProperty('stroke-width');
                }
                if (el.dataset.origFilter !== undefined) {
                    if (el.dataset.origFilter) el.style.filter = el.dataset.origFilter;
                    else el.style.removeProperty('filter');
                }
            });
            document.querySelectorAll('.recharts-cartesian-grid-bg, .recharts-background, .recharts-bar-background').forEach(el => {
                el.classList.remove('selected-bar-highlight');
                el.style.removeProperty('stroke');
                el.style.removeProperty('stroke-width');
                el.style.removeProperty('filter');
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

        if (!selectedBar && ev.target) {
            const candidate = ev.target.closest('.recharts-bar-rectangle, .recharts-rectangle, .recharts-bar rect, .recharts-bar path');
            if (candidate && container.contains(candidate)) {
                const r = candidate.getBoundingClientRect();
                if (r.width > 0 && r.height > 0) {
                    selectedBar = candidate;
                }
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

        const wasSelected = selectedBar.classList.contains('selected-bar-highlight');
        removeExisting();
        if (wasSelected) {
            return;
        }

        selectedBar.classList.add('selected-bar-highlight');
        selectedBar.dataset.origStroke = selectedBar.style.stroke || '';
        selectedBar.dataset.origStrokeWidth = selectedBar.style.strokeWidth || '';
        selectedBar.dataset.origFilter = selectedBar.style.filter || '';
        selectedBar.style.stroke = '#FFFFFF';
        selectedBar.style.strokeWidth = '2px';
        selectedBar.style.filter = 'drop-shadow(0px 0px 6px rgba(255, 255, 255, 0.95))';

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
        let fiberValue = null;
        let fiberPayload = null;

        while (currFiber) {
            const props = currFiber.memoizedProps || currFiber.pendingProps;
            if (props) {
                if (props.layout && typeof props.layout === 'string') detectedLayout = props.layout;
                if (props.dataKey && typeof props.dataKey === 'string' && !barDataKey) barDataKey = props.dataKey;
                if (props.data && Array.isArray(props.data) && !chartData) chartData = props.data;

                if (fiberValue === null && props.value !== undefined && props.value !== null) {
                    fiberValue = props.value;
                }

                if (fiberPayload === null && props.payload && typeof props.payload === 'object') {
                    fiberPayload = props.payload;
                }
            }
            currFiber = currFiber.return;
        }

        let val = null;
        if (fiberValue !== null) {
            if (typeof fiberValue === 'number') {
                val = fiberValue;
            } else if (Array.isArray(fiberValue)) {
                val = fiberValue.length >= 2 ? (fiberValue[1] - fiberValue[0]) : fiberValue[0];
            } else if (typeof fiberValue === 'string' && !isNaN(parseFloat(fiberValue))) {
                val = parseFloat(fiberValue);
            }
        }

        if (val === null && fiberPayload) {
            if (barDataKey && fiberPayload[barDataKey] !== undefined && fiberPayload[barDataKey] !== null) {
                let p = parseFloat(fiberPayload[barDataKey]);
                val = !isNaN(p) ? p : fiberPayload[barDataKey];
            } else {
                for (let key in fiberPayload) {
                    if (!IGNORED_KEYS.has(key) && key !== 'name' && key !== 'driver' && key !== 'team' && key !== 'race' && key !== 'track' && key !== 'placement' && key !== 'place' && key !== 'fill') {
                        let v = fiberPayload[key];
                        if (typeof v === 'number' && !isNaN(v)) {
                            val = v;
                            break;
                        }
                    }
                }
            }
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
            const vAttr = selectedBar.getAttribute('value') || selectedBar.getAttribute('data-value');
            if (vAttr !== null && !isNaN(parseFloat(vAttr))) {
                val = parseFloat(vAttr);
            }
        }

        if (val === null || val === undefined) {
            val = 0;
        }

        let numVal = typeof val === 'number' ? val : parseFloat(val);
        let displayVal;
        if (!isNaN(numVal)) {
            if (Number.isInteger(numVal)) {
                displayVal = numVal.toString();
            } else {
                displayVal = parseFloat(numVal.toFixed(2)).toString();
            }
        } else {
            displayVal = String(val);
        }

        const containerRect = container.getBoundingClientRect();
        const barRect = selectedBar.getBoundingClientRect();

        const tag = document.createElement('div');
        tag.className = 'bar-value-tag-box';
        tag.innerText = displayVal;
        tag.dataset.value = displayVal;

        const isHorizontalBarChart = (detectedLayout === 'vertical') || (barRect.width > barRect.height * 1.5);
        let tagTop, tagLeft, tagTransform, arrowDir;

        const isNegative = !isNaN(numVal) && numVal < 0;

        if (isHorizontalBarChart) {
            tagTop = (barRect.top - containerRect.top + (barRect.height / 2)) + 'px';
            if (isNegative) {
                tagLeft = (barRect.left - containerRect.left - 12) + 'px';
                tagTransform = 'translate(-100%, -50%)';
                arrowDir = 'right';
            } else {
                tagLeft = (barRect.right - containerRect.left + 12) + 'px';
                tagTransform = 'translate(0%, -50%)';
                arrowDir = 'left';
            }
        } else {
            tagLeft = (barRect.left - containerRect.left + (barRect.width / 2)) + 'px';
            tagTransform = 'translateX(-50%)';
            if (isNegative) {
                tagTop = (barRect.bottom - containerRect.top + 10) + 'px';
                arrowDir = 'up';
            } else {
                tagTop = (barRect.top - containerRect.top - 38) + 'px';
                arrowDir = 'down';
            }
        }
        tag.dataset.arrowDir = arrowDir;

        Object.assign(tag.style, {
            position: 'absolute',
            top: tagTop,
            left: tagLeft,
            transform: tagTransform,
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
            border: '2px solid #00b4da',
            lineHeight: '1.2'
        });

        const arrow = document.createElement('div');
        if (!isHorizontalBarChart) {
            if (isNegative) {
                Object.assign(arrow.style, {
                    position: 'absolute',
                    top: '-5px',
                    left: '50%',
                    width: '8px',
                    height: '8px',
                    backgroundColor: '#FFFFFF',
                    borderLeft: '2px solid #00b4da',
                    borderTop: '2px solid #00b4da',
                    transform: 'translateX(-50%) rotate(45deg)',
                    zIndex: '10001'
                });
            } else {
                Object.assign(arrow.style, {
                    position: 'absolute',
                    bottom: '-5px',
                    left: '50%',
                    width: '8px',
                    height: '8px',
                    backgroundColor: '#FFFFFF',
                    borderRight: '2px solid #00b4da',
                    borderBottom: '2px solid #00b4da',
                    transform: 'translateX(-50%) rotate(45deg)',
                    zIndex: '10001'
                });
            }
        } else {
            if (isNegative) {
                Object.assign(arrow.style, {
                    position: 'absolute',
                    right: '-5px',
                    top: '50%',
                    width: '8px',
                    height: '8px',
                    backgroundColor: '#FFFFFF',
                    borderRight: '2px solid #00b4da',
                    borderTop: '2px solid #00b4da',
                    transform: 'translateY(-50%) rotate(45deg)',
                    zIndex: '10001'
                });
            } else {
                Object.assign(arrow.style, {
                    position: 'absolute',
                    left: '-5px',
                    top: '50%',
                    width: '8px',
                    height: '8px',
                    backgroundColor: '#FFFFFF',
                    borderLeft: '2px solid #00b4da',
                    borderBottom: '2px solid #00b4da',
                    transform: 'translateY(-50%) rotate(45deg)',
                    zIndex: '10001'
                });
            }
        }

        tag.appendChild(arrow);
        container.appendChild(tag);
    }

    function safeChartClickHandler(ev) {
        if (Date.now() - lastChartClickTime < 50) return;
        lastChartClickTime = Date.now();
        handleChartClick(ev);
    }

    if (window.__zoomableChartHandler) {
        document.removeEventListener('click', window.__zoomableChartHandler, true);
        if (window.__zoomableChartResizeHandler) {
            window.removeEventListener('resize', window.__zoomableChartResizeHandler);
        }
    }
    window.__zoomableChartHandler = safeChartClickHandler;
    window.__zoomableChartResizeHandler = () => {
        document.querySelectorAll('.bar-value-tag-box').forEach(t => t.remove());
        document.querySelectorAll('.selected-bar-highlight').forEach(el => {
            el.classList.remove('selected-bar-highlight');
            if (el.dataset.origStroke) el.style.stroke = el.dataset.origStroke;
            else el.style.removeProperty('stroke');
            if (el.dataset.origStrokeWidth) el.style.strokeWidth = el.dataset.origStrokeWidth;
            else el.style.removeProperty('stroke-width');
            if (el.dataset.origFilter) el.style.filter = el.dataset.origFilter;
            else el.style.removeProperty('filter');
        });
        document.querySelectorAll('.recharts-cartesian-grid-bg, .recharts-background, .recharts-bar-background').forEach(el => {
            el.classList.remove('selected-bar-highlight');
            el.style.removeProperty('stroke');
            el.style.removeProperty('stroke-width');
            el.style.removeProperty('filter');
        });
    };
    document.addEventListener('click', safeChartClickHandler, true);
    window.addEventListener('resize', window.__zoomableChartResizeHandler);

    // ── Interactive Line Chart Highlighting (Animated Power Rankings Style) ─────
    const LINE_HIGHLIGHT_STORE = (window.__TAF1_LINE_STORE = window.__TAF1_LINE_STORE || {});

    function colorsMatch(c1, c2) {
        if (!c1 || !c2) return false;
        c1 = c1.trim().toLowerCase();
        c2 = c2.trim().toLowerCase();
        if (c1 === c2) return true;
        const toRgb = (c) => {
            if (c.startsWith('#')) {
                let h = c.slice(1);
                if (h.length === 3) h = h.split('').map(x => x + x).join('');
                return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)];
            }
            const m = c.match(/\d+/g);
            return m ? m.slice(0, 3).map(Number) : null;
        };
        const r1 = toRgb(c1);
        const r2 = toRgb(c2);
        return !!(r1 && r2 && r1[0] === r2[0] && r1[1] === r2[1] && r1[2] === r2[2]);
    }

    function getRechartsLineName(el) {
        if (!el) return null;
        try {
            const key = Object.keys(el).find(k => k.startsWith('__reactFiber') || k.startsWith('__reactInternalInstance'));
            let fiber = el[key];
            while (fiber) {
                const p = fiber.memoizedProps;
                if (p) {
                    if (p.name && typeof p.name === 'string') return p.name.trim();
                    if (p.dataKey && typeof p.dataKey === 'string') return p.dataKey.trim();
                }
                fiber = fiber.return;
            }
        } catch(e) {}
        return null;
    }

    function toggleLineHighlight(chartId, targetName, targetColor, targetIdx) {
        if (!chartId) return;
        const current = LINE_HIGHLIGHT_STORE[chartId];
        const isCurrentActive = current && (
            (targetName && current.name === targetName) ||
            (targetIdx !== undefined && targetIdx !== null && current.idx === targetIdx)
        );
        const newTarget = isCurrentActive ? null : { name: targetName, color: targetColor, idx: targetIdx };
        LINE_HIGHLIGHT_STORE[chartId] = newTarget;
        applyLineHighlight(chartId, newTarget ? newTarget.name : null, newTarget ? newTarget.color : null, newTarget ? newTarget.idx : null);
    }

    function applyLineHighlight(chartId, activeName, activeColor, activeIdx) {
        // 1. Update Key Badges
        const keyContainers = document.querySelectorAll(`[data-key-for-chart="${chartId}"]`);
        keyContainers.forEach(container => {
            const items = container.querySelectorAll('.taf1-chart-key-item');
            items.forEach(item => {
                const iName = item.getAttribute('data-name');
                const iIdxStr = item.getAttribute('data-idx');
                const iIdx = iIdxStr !== null ? parseInt(iIdxStr, 10) : null;
                const textEl = item.querySelector('.taf1-key-text') || item;

                if (!activeName) {
                    item.style.opacity = '1.0';
                    item.style.borderColor = '#2A2A34';
                    item.style.background = '#1B1B22';
                    item.style.boxShadow = 'none';
                    if (textEl) textEl.style.color = '#FFFFFF';
                } else {
                    const isKeyMatch = (activeIdx !== undefined && activeIdx !== null && iIdx === activeIdx) ||
                                       (iName && activeName && iName.trim().toLowerCase() === activeName.trim().toLowerCase());
                    if (isKeyMatch) {
                        item.style.opacity = '1.0';
                        item.style.borderColor = '#00b4da';
                        item.style.background = '#252532';
                        item.style.boxShadow = '0 0 10px rgba(0, 180, 218, 0.45)';
                        if (textEl) textEl.style.color = '#00b4da';
                    } else {
                        item.style.opacity = '0.40';
                        item.style.borderColor = '#2A2A34';
                        item.style.background = '#1B1B22';
                        item.style.boxShadow = 'none';
                        if (textEl) textEl.style.color = '#FFFFFF';
                    }
                }
            });
        });

        // 2. Update Lines & Dots in Chart Containers (Small Card and Popout Dialog)
        const chartContainers = document.querySelectorAll(
            `#card-${chartId}, #${chartId}, [data-chart-id="${chartId}"]`
        );

        chartContainers.forEach(chartContainer => {
            const lineGroups = chartContainer.querySelectorAll('.recharts-line');
            let matchedGroup = null;

            lineGroups.forEach((g, idx) => {
                const path = g.querySelector('.recharts-line-curve, path');
                const dotsGroup = g.querySelector('.recharts-line-dots');
                if (!path) return;

                if (path.dataset.origStrokeWidth === undefined) {
                    path.dataset.origStrokeWidth = path.getAttribute('stroke-width') || '2';
                }

                if (!activeName) {
                    g.style.opacity = '1.0';
                    g.style.transition = 'opacity 0.2s ease';
                    path.style.opacity = '1.0';
                    path.style.strokeWidth = path.dataset.origStrokeWidth + 'px';
                    path.style.filter = '';
                    g.querySelectorAll('circle, .recharts-dot').forEach(c => {
                        c.style.opacity = '1.0';
                        c.style.fillOpacity = '1.0';
                        c.style.strokeOpacity = '1.0';
                    });
                    if (dotsGroup) {
                        dotsGroup.style.opacity = '1.0';
                    }
                } else {
                    const strokeVal = path.getAttribute('stroke') || path.style.stroke;
                    const lineName = getRechartsLineName(g);

                    // Strict, exclusive matching:
                    // 1. First by fiber line name (if available)
                    // 2. Otherwise by sequential index activeIdx (1:1 with key item)
                    // 3. ONLY if both fail, fallback to color
                    let isMatch = false;
                    if (activeName && lineName) {
                        isMatch = (lineName.trim().toLowerCase() === activeName.trim().toLowerCase());
                    } else if (activeIdx !== undefined && activeIdx !== null && activeIdx >= 0) {
                        isMatch = (idx === activeIdx);
                    } else if (activeColor) {
                        isMatch = colorsMatch(strokeVal, activeColor);
                    }

                    if (isMatch) {
                        matchedGroup = g;
                        g.style.opacity = '1.0';
                        g.style.transition = 'opacity 0.2s ease';
                        path.style.opacity = '1.0';
                        path.style.strokeWidth = '4.5px';
                        path.style.filter = `drop-shadow(0 0 7px ${activeColor || strokeVal})`;
                        g.querySelectorAll('circle, .recharts-dot').forEach(c => {
                            c.style.opacity = '1.0';
                            c.style.fillOpacity = '1.0';
                            c.style.strokeOpacity = '1.0';
                        });
                        if (dotsGroup) {
                            dotsGroup.style.opacity = '1.0';
                        }
                    } else {
                        // User request: non-selected points and lines at 40% opacity from original
                        g.style.opacity = '0.40';
                        g.style.transition = 'opacity 0.2s ease';
                        path.style.opacity = '0.40';
                        path.style.strokeWidth = path.dataset.origStrokeWidth + 'px';
                        path.style.filter = '';
                        g.querySelectorAll('circle, .recharts-dot').forEach(c => {
                            c.style.opacity = '0.40';
                            c.style.fillOpacity = '0.40';
                            c.style.strokeOpacity = '0.40';
                        });
                        if (dotsGroup) {
                            dotsGroup.style.opacity = '0.40';
                        }
                    }
                }
            });

            // Also check any standalone dots groups in the chart container
            const allDotsGroups = chartContainer.querySelectorAll('.recharts-line-dots');
            allDotsGroups.forEach((dg, dIdx) => {
                if (dg.closest('.recharts-line')) return;

                if (!activeName) {
                    dg.style.opacity = '1.0';
                    dg.querySelectorAll('circle, .recharts-dot').forEach(c => {
                        c.style.opacity = '1.0';
                        c.style.fillOpacity = '1.0';
                        c.style.strokeOpacity = '1.0';
                    });
                } else {
                    const dgName = getRechartsLineName(dg);
                    let isDotsMatch = false;
                    if (activeName && dgName) {
                        isDotsMatch = (dgName.trim().toLowerCase() === activeName.trim().toLowerCase());
                    } else if (activeIdx !== undefined && activeIdx !== null && activeIdx >= 0) {
                        isDotsMatch = (dIdx === activeIdx);
                    } else if (activeColor) {
                        const sampleCircle = dg.querySelector('circle');
                        const fillVal = sampleCircle ? (sampleCircle.getAttribute('fill') || sampleCircle.getAttribute('stroke')) : null;
                        isDotsMatch = colorsMatch(fillVal, activeColor);
                    }

                    if (isDotsMatch) {
                        dg.style.opacity = '1.0';
                        dg.querySelectorAll('circle, .recharts-dot').forEach(c => {
                            c.style.opacity = '1.0';
                            c.style.fillOpacity = '1.0';
                            c.style.strokeOpacity = '1.0';
                        });
                    } else {
                        dg.style.opacity = '0.40';
                        dg.querySelectorAll('circle, .recharts-dot').forEach(c => {
                            c.style.opacity = '0.40';
                            c.style.fillOpacity = '0.40';
                            c.style.strokeOpacity = '0.40';
                        });
                    }
                }
            });

            // Elevate the highlighted line group to the top layer in SVG
            if (matchedGroup && matchedGroup.parentElement) {
                matchedGroup.parentElement.appendChild(matchedGroup);
            }
        });
    }

    window.taf1ToggleLineHighlight = toggleLineHighlight;
    window.taf1ApplyLineHighlight = applyLineHighlight;

    // Delegated click listener
    document.addEventListener('click', (ev) => {
        // A. Clicked a Key Badge
        const keyItem = ev.target ? ev.target.closest('.taf1-chart-key-item') : null;
        if (keyItem) {
            const chartId = keyItem.getAttribute('data-chart-id');
            const name = keyItem.getAttribute('data-name');
            const color = keyItem.getAttribute('data-color');
            const idxStr = keyItem.getAttribute('data-idx');
            const idx = idxStr !== null ? parseInt(idxStr, 10) : null;
            toggleLineHighlight(chartId, name, color, idx);
            return;
        }

        // B. Clicked a Line Curve in a Chart
        const lineCurve = ev.target ? ev.target.closest('.recharts-line, .recharts-line-curve') : null;
        if (lineCurve) {
            const chartContainer = lineCurve.closest('[data-chart-id], [id^="card-"], .zoomable-chart-popout-container');
            if (chartContainer) {
                let chartId = chartContainer.getAttribute('data-chart-id') || chartContainer.id;
                if (chartId && chartId.startsWith('card-')) chartId = chartId.replace('card-', '');
                const g = lineCurve.closest('.recharts-line');
                if (g && chartId) {
                    const allLines = Array.from(g.parentElement ? g.parentElement.querySelectorAll('.recharts-line') : []);
                    const idx = allLines.indexOf(g);
                    const path = g.querySelector('.recharts-line-curve, path');
                    const stroke = path ? (path.getAttribute('stroke') || path.style.stroke) : null;
                    const lineName = getRechartsLineName(g);
                    const keyItem = (lineName ? document.querySelector(`[data-key-for-chart="${chartId}"] .taf1-chart-key-item[data-name="${lineName}"]`) : null) ||
                                    document.querySelector(`[data-key-for-chart="${chartId}"] .taf1-chart-key-item[data-idx="${idx}"]`);
                    const name = keyItem ? keyItem.getAttribute('data-name') : (lineName || (stroke ? stroke : 'line-' + idx));
                    toggleLineHighlight(chartId, name, stroke, idx);
                }
            }
        }
    });

    // Observer to re-apply active highlight when charts are mounted or re-rendered
    const lineObserver = new MutationObserver((mutations) => {
        for (const m of mutations) {
            if (m.type === 'childList') {
                for (const node of m.addedNodes) {
                    if (node.nodeType === 1) {
                        const chartEl = (node.matches && (node.matches('[data-chart-id], [id^="card-"], .zoomable-chart-popout-container')))
                            ? node
                            : (node.querySelector ? node.querySelector('[data-chart-id], [id^="card-"], .zoomable-chart-popout-container') : null);
                        if (chartEl) {
                            let chartId = chartEl.getAttribute('data-chart-id') || chartEl.id;
                            if (chartId && chartId.startsWith('card-')) chartId = chartId.replace('card-', '');
                            const active = LINE_HIGHLIGHT_STORE[chartId];
                            if (active && active.name) {
                                setTimeout(() => applyLineHighlight(chartId, active.name, active.color, active.idx), 60);
                            }
                        }
                    }
                }
            }
        }
    });
    lineObserver.observe(document.body, { childList: true, subtree: true });
})();
