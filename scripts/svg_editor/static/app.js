/* ============================================================
   PPT Master - SVG Editor  |  app.js
   Vanilla JS, IIFE pattern
   ============================================================ */
(function () {
    "use strict";

    // ---- i18n -------------------------------------------------------
    var MESSAGES = {
        en: {
            page_title: "PPT Master - Live Preview",
            panel_slides: "Slides",
            panel_annotations: "Annotations",
            placeholder_select_slide: "Select a slide on the left to begin",
            label_selected_element: "Selected element",
            empty_selected_element: "Click an element on the slide to select it",
            btn_enter_child_mode: "Enter child elements",
            btn_return_group_mode: "Return to group",
            selection_path_label: "Current: ",
            selected_help_group: "Default: select the whole block first. Use the button below to enter child elements.",
            selected_help_drag: "Drag selected elements to generate move annotations.",
            label_edit_instruction: "Edit instruction",
            label_layout_issues: "Layout issues",
            placeholder_annotation: "Describe how the AI should modify this element...",
            placeholder_annotation_multi: "Describe how to modify all {count} elements...",
            btn_add_annotation: "Add annotation",
            btn_reset_preview: "Reset preview",
            label_annotations_on_slide: "Annotations on this slide",
            btn_submit_annotations: "Submit annotations",
            btn_exit_preview: "Exit preview",
            modal_submit: "Submit",
            modal_cancel: "Cancel",
            empty_waiting_slides: "Waiting for generated slides...",
            empty_no_slides: "No slides found",
            placeholder_live_ready: "Live preview is ready. Generated slides will appear here.",
            placeholder_slide_writing: "Slide is still being written. Waiting for the next refresh...",
            empty_annotations: "No annotations yet",
            tooltip_remove_annotation: "Remove annotation",
            multi_selected: "{count} elements selected",
            multi_mixed: "mixed",
            err_load_slides: "Failed to load slides: ",
            err_load_slide: "Failed to load slide: ",
            err_add_annotation: "Failed to add annotation: ",
            err_remove_annotation: "Failed to remove annotation: ",
            err_save: "Save failed: ",
            modal_confirm_submit: "Submit annotations to disk?\n\nThe preview service will keep running. Click Exit preview when you want to stop it.",
            modal_success_submit: "Annotations saved.\n\nReturn to the chat and tell the AI to apply them (e.g. \"apply my annotations\"). The preview service is still running.",
            modal_confirm_exit: "Exit preview and stop the local server?\n\nUnsaved annotations will be discarded.",
            modal_success_exit: "Preview stopped.\n\nYou can close this tab and return to the chat.",
            modal_stopping: "Stopping preview server...",
            lang_toggle_title: "Switch language",
            nav_first: "First slide (Home)",
            nav_prev: "Previous slide (←)",
            nav_next: "Next slide (→)",
            nav_last: "Last slide (End)",
            nav_counter: "{current} / {total}",
            nav_empty: "— / —"
        },
        zh: {
            page_title: "PPT Master - 实时预览",
            panel_slides: "幻灯片",
            panel_annotations: "标注",
            placeholder_select_slide: "在左侧选择一张幻灯片开始",
            label_selected_element: "已选元素",
            empty_selected_element: "点击幻灯片中的元素进行选择",
            btn_enter_child_mode: "进入子元素",
            btn_return_group_mode: "返回整体",
            selection_path_label: "当前：",
            selected_help_group: "默认先选整体，需要时再进入子元素。",
            selected_help_drag: "拖拽已选元素，可自动生成移动类批注。",
            label_edit_instruction: "修改说明",
            label_layout_issues: "排版问题",
            placeholder_annotation: "描述希望 AI 如何修改该元素……",
            placeholder_annotation_multi: "描述希望如何修改所选 {count} 个元素……",
            btn_add_annotation: "添加标注",
            btn_reset_preview: "复位预览",
            label_annotations_on_slide: "本页标注",
            btn_submit_annotations: "提交标注",
            btn_exit_preview: "退出预览",
            modal_submit: "提交",
            modal_cancel: "取消",
            empty_waiting_slides: "正在等待生成幻灯片……",
            empty_no_slides: "未找到幻灯片",
            placeholder_live_ready: "实时预览已就绪,生成的幻灯片会在这里出现。",
            placeholder_slide_writing: "幻灯片仍在写入,等待下次刷新……",
            empty_annotations: "暂无标注",
            tooltip_remove_annotation: "删除标注",
            multi_selected: "已选 {count} 个元素",
            multi_mixed: "混合",
            err_load_slides: "加载幻灯片失败:",
            err_load_slide: "加载幻灯片失败:",
            err_add_annotation: "添加标注失败:",
            err_remove_annotation: "删除标注失败:",
            err_save: "保存失败:",
            modal_confirm_submit: "确认将标注保存到磁盘?\n\n预览服务会继续运行。需要关闭时请点击退出预览。",
            modal_success_submit: "标注已保存。\n\n请回到对话窗口并告诉 AI 应用这些标注(例如\"应用我的标注\")。预览服务仍在运行。",
            modal_confirm_exit: "退出预览并停止本地服务?\n\n未保存的标注将被丢弃。",
            modal_success_exit: "预览已停止。\n\n可以关闭本标签页并回到对话窗口。",
            modal_stopping: "正在停止预览服务……",
            lang_toggle_title: "切换语言",
            nav_first: "第一页 (Home)",
            nav_prev: "上一页 (←)",
            nav_next: "下一页 (→)",
            nav_last: "末页 (End)",
            nav_counter: "{current} / {total}",
            nav_empty: "— / —"
        }
    };

    var LANG = (function () {
        try {
            var stored = window.localStorage.getItem("ppt_lang");
            if (stored === "zh" || stored === "en") return stored;
        } catch (e) { /* ignore */ }
        var nav = (navigator.language || navigator.userLanguage || "en").toLowerCase();
        return nav.indexOf("zh") === 0 ? "zh" : "en";
    })();

    function t(key, params) {
        var dict = MESSAGES[LANG] || MESSAGES.en;
        var msg = dict[key];
        if (msg === undefined) msg = MESSAGES.en[key];
        if (msg === undefined) return key;
        if (params) {
            Object.keys(params).forEach(function (p) {
                msg = msg.replace("{" + p + "}", params[p]);
            });
        }
        return msg;
    }

    function applyI18n() {
        document.documentElement.setAttribute("lang", LANG === "zh" ? "zh-CN" : "en");
        document.title = t("page_title");
        document.querySelectorAll("[data-i18n]").forEach(function (el) {
            el.textContent = t(el.getAttribute("data-i18n"));
        });
        document.querySelectorAll("[data-i18n-placeholder]").forEach(function (el) {
            el.placeholder = t(el.getAttribute("data-i18n-placeholder"));
        });
        document.querySelectorAll("[data-i18n-title]").forEach(function (el) {
            el.title = t(el.getAttribute("data-i18n-title"));
        });
        updateNavLabel();
    }

    function setLang(lang) {
        if (lang !== "zh" && lang !== "en") return;
        LANG = lang;
        try { window.localStorage.setItem("ppt_lang", lang); } catch (e) { /* ignore */ }
        applyI18n();
        var toggleBtn = document.getElementById("btn-lang-toggle");
        if (toggleBtn) {
            toggleBtn.textContent = lang === "zh" ? "EN" : "中";
            toggleBtn.title = t("lang_toggle_title");
        }
        // Re-render dynamic regions so they pick up the new language
        updateSelectionPanel();
        updateAnnotationList();
        loadSlides();
    }

    // ---- DOM refs ---------------------------------------------------
    var slideListEl       = document.getElementById("slide-list");
    var btnResetPreview   = document.getElementById("btn-reset-preview");
    var svgPlaceholder    = document.getElementById("svg-placeholder");
    var svgContent        = document.getElementById("svg-content");
    var svgContainerEl    = document.getElementById("svg-container");
    var selectedElementEl = document.getElementById("selected-element");
    var selectionActionsEl = document.getElementById("selected-element-actions");
    var btnToggleSelectionMode = document.getElementById("btn-toggle-selection-mode");
    var selectionPathEl   = document.getElementById("selection-path");
    var selectedElementHelpEl = document.getElementById("selected-element-help");
    var annotationInput   = document.getElementById("annotation-input");
    var annotationText    = document.getElementById("annotation-text");
    var btnAddAnnotation  = document.getElementById("btn-add-annotation");
    var annotationsEl     = document.getElementById("annotations");
    var layoutIssuesEl    = document.getElementById("layout-issues");
    var layoutIssuesListEl = document.getElementById("layout-issues-list");
    var layoutIssuesActionsEl = document.getElementById("layout-issues-actions");
    var btnSave           = document.getElementById("btn-save");
    var btnExitPreview    = document.getElementById("btn-exit-preview");
    var modalOverlay      = document.getElementById("modal-overlay");
    var modalMessage      = document.getElementById("modal-message");
    var modalConfirm      = document.getElementById("modal-confirm");
    var modalCancel       = document.getElementById("modal-cancel");
    var elementPropsEl    = document.getElementById("element-props");

    var navFirstBtn       = document.getElementById("nav-first");
    var navPrevBtn        = document.getElementById("nav-prev");
    var navNextBtn        = document.getElementById("nav-next");
    var navLastBtn        = document.getElementById("nav-last");
    var navCounterEl      = document.getElementById("nav-counter");
    var navNameEl         = document.getElementById("nav-name");

    // ---- State ------------------------------------------------------
    var currentSlide      = null;   // filename, e.g. "slide_01.svg"
    var slideNames        = [];     // ordered slide filenames for navigation
    var selectedElementIds = new Set(); // id attrs of selected SVG elements
    var slideAnnotations  = {};     // {element_id: annotation_text} for current slide
    var currentLayoutIssues = [];
    var liveMode          = false;
    var slidePollTimer    = null;
    var pendingModalAction = "submit";
    var suppressNextElementClick = false;
    var EditorLogic       = window.PptSvgEditorLogic || null;
    var previewOffsetsBySlide = {};
    var previewScalesBySlide = {};
    var previewTextHintsBySlide = {};
    var selectionMode     = "group";
    var activeGroupId     = null;
    var activeChildId     = null;
    var dragState = {
        active: false,
        started: false,
        sourceId: null,
        startMouse: null,
        startSvg: null,
        currentDx: 0,
        currentDy: 0,
        ids: [],
        originalTransforms: {}
    };
    var scaleState = {
        active: false,
        objectId: null,
        handle: null,
        startMouse: null,
        startBox: null,
        startScaleX: 1,
        startScaleY: 1
    };
    var scaleHandleLayer = null;
    var DRAG_THRESHOLD = 4;

    function currentSlideIndex() {
        if (!currentSlide) return -1;
        return slideNames.indexOf(currentSlide);
    }

    function gotoSlideIndex(idx) {
        if (idx < 0 || idx >= slideNames.length) return;
        var name = slideNames[idx];
        if (name === currentSlide) return;
        var item = slideListEl.querySelector('.slide-item[data-name="' + cssAttr(name) + '"]');
        selectSlide(name, item || undefined);
    }

    function cssAttr(value) {
        return String(value).replace(/"/g, '\\"');
    }

    function updateNavLabel() {
        if (!navCounterEl) return;
        var total = slideNames.length;
        if (total === 0 || !currentSlide) {
            navCounterEl.textContent = t("nav_empty");
            if (navNameEl) navNameEl.textContent = "";
        } else {
            var idx = currentSlideIndex();
            navCounterEl.textContent = t("nav_counter", { current: idx + 1, total: total });
            if (navNameEl) navNameEl.textContent = currentSlide;
        }
        var idx2 = currentSlideIndex();
        var hasCurrent = idx2 >= 0;
        if (navFirstBtn) navFirstBtn.disabled = !hasCurrent || idx2 === 0;
        if (navPrevBtn)  navPrevBtn.disabled  = !hasCurrent || idx2 <= 0;
        if (navNextBtn)  navNextBtn.disabled  = !hasCurrent || idx2 >= total - 1;
        if (navLastBtn)  navLastBtn.disabled  = !hasCurrent || idx2 >= total - 1;
    }

    function getSvgRoot() {
        return svgContent.querySelector("svg");
    }

    function getSvgPoint(clientX, clientY) {
        var svg = getSvgRoot();
        if (!svg || typeof svg.createSVGPoint !== "function") return null;
        var pt = svg.createSVGPoint();
        pt.x = clientX;
        pt.y = clientY;
        var ctm = svg.getScreenCTM();
        if (!ctm || typeof ctm.inverse !== "function") return null;
        return pt.matrixTransform(ctm.inverse());
    }

    function isSelectableElement(node) {
        return !!(node && node.classList && node.classList.contains("svg-selectable"));
    }

    function isEditableChildTag(tag) {
        return tag === "text" || tag === "tspan" || tag === "rect" || tag === "image" || tag === "path";
    }

    function isSimpleEditablePath(el) {
        if (!el || el.tagName.toLowerCase() !== "path") return false;
        var d = el.getAttribute("d") || "";
        return d.length > 0 && d.length <= 400;
    }

    function isEditableChildElement(el) {
        if (!el) return false;
        var tag = el.tagName.toLowerCase();
        if (!isEditableChildTag(tag)) return false;
        if (tag === "path") return isSimpleEditablePath(el);
        return true;
    }

    function findNearestGroupAncestor(el) {
        var cur = el;
        while (cur && cur !== getSvgRoot()) {
            if (cur.tagName && cur.tagName.toLowerCase() === "g" && cur.id) {
                return cur;
            }
            cur = cur.parentNode;
        }
        return null;
    }

    function getEditableChildren(groupEl) {
        if (!groupEl || !groupEl.querySelectorAll) return [];
        return Array.from(groupEl.querySelectorAll("*")).filter(function (el) {
            return isEditableChildElement(el);
        });
    }

    function resetSelectionModeState() {
        selectionMode = "group";
        activeGroupId = null;
        activeChildId = null;
    }

    function getCurrentPreviewOffsets() {
        if (!currentSlide) return {};
        if (!previewOffsetsBySlide[currentSlide]) {
            previewOffsetsBySlide[currentSlide] = {};
        }
        return previewOffsetsBySlide[currentSlide];
    }

    function getCurrentPreviewScales() {
        if (!currentSlide) return {};
        if (!previewScalesBySlide[currentSlide]) {
            previewScalesBySlide[currentSlide] = {};
        }
        return previewScalesBySlide[currentSlide];
    }

    function getCurrentPreviewTextHints() {
        if (!currentSlide) return {};
        if (!previewTextHintsBySlide[currentSlide]) {
            previewTextHintsBySlide[currentSlide] = {};
        }
        return previewTextHintsBySlide[currentSlide];
    }

    function getCurrentTargetId() {
        return activeChildId || activeGroupId || selectedElementIds.values().next().value || null;
    }

    function markPreviewBaseTransforms() {
        var svg = getSvgRoot();
        if (!svg) return;
        svg.querySelectorAll("*").forEach(function (el) {
            if (!el.getAttribute) return;
            if (el.getAttribute("data-preview-base-transform") === null) {
                el.setAttribute("data-preview-base-transform", el.getAttribute("transform") || "");
            }
        });
    }

    function applyPreviewOffsetsForCurrentSlide() {
        var offsets = getCurrentPreviewOffsets();
        var scales = getCurrentPreviewScales();
        var allIds = new Set(Object.keys(offsets).concat(Object.keys(scales)));
        allIds.forEach(function (id) {
            var el = svgContent.querySelector("#" + CSS.escape(id));
            if (!el) return;
            var offset = offsets[id] || { dx: 0, dy: 0 };
            var scale = scales[id] || { scaleX: 1, scaleY: 1 };
            var dx = Number(offset.dx) || 0;
            var dy = Number(offset.dy) || 0;
            var scaleX = Number(scale.scaleX) || 1;
            var scaleY = Number(scale.scaleY) || 1;
            var base = el.getAttribute("data-preview-base-transform") || "";
            var bbox = elementBBoxSafe(el);
            var hasMove = Math.abs(dx) >= 1 || Math.abs(dy) >= 1;
            var hasScale = Math.abs(scaleX - 1) >= 0.01 || Math.abs(scaleY - 1) >= 0.01;
            if (!hasMove && !hasScale) {
                if (base) el.setAttribute("transform", base);
                else el.removeAttribute("transform");
                delete offsets[id];
                delete scales[id];
                return;
            }
            var parts = [];
            if (base) parts.push(base);
            if (hasMove) parts.push("translate(" + dx.toFixed(2) + " " + dy.toFixed(2) + ")");
            if (hasScale && bbox) {
                var cx = bbox.x + bbox.width / 2;
                var cy = bbox.y + bbox.height / 2;
                parts.push(
                    "translate(" + cx.toFixed(2) + " " + cy.toFixed(2) + ")" +
                    " scale(" + scaleX.toFixed(3) + " " + scaleY.toFixed(3) + ")" +
                    " translate(" + (-cx).toFixed(2) + " " + (-cy).toFixed(2) + ")"
                );
            }
            if (parts.length) el.setAttribute("transform", parts.join(" "));
            else el.removeAttribute("transform");
        });
    }

    function resetPreviewOffsets(clearTextarea) {
        if (currentSlide) {
            previewOffsetsBySlide[currentSlide] = {};
            previewScalesBySlide[currentSlide] = {};
            previewTextHintsBySlide[currentSlide] = {};
        }
        var svg = getSvgRoot();
        if (svg) {
            svg.querySelectorAll("*").forEach(function (el) {
                if (!el.getAttribute) return;
                var base = el.getAttribute("data-preview-base-transform");
                if (base === null) return;
                if (base) el.setAttribute("transform", base);
                else el.removeAttribute("transform");
            });
        }
        if (clearTextarea) {
            annotationText.value = "";
        }
    }

    function updateMergedAnnotationForCurrentTarget() {
        var targetId = getCurrentTargetId();
        if (!targetId || !EditorLogic) return;
        var offsets = getCurrentPreviewOffsets()[targetId] || { dx: 0, dy: 0 };
        var scales = getCurrentPreviewScales()[targetId] || { scaleX: 1, scaleY: 1 };
        var hints = getCurrentPreviewTextHints()[targetId] || [];
        annotationInput.style.display = "block";
        annotationText.value = EditorLogic.generateMergedAnnotation({
            dx: offsets.dx || 0,
            dy: offsets.dy || 0,
            scaleX: scales.scaleX || 1,
            scaleY: scales.scaleY || 1,
            textHints: hints,
            count: selectedElementIds.size || 1,
            lang: LANG
        });
    }

    function getMergedAnnotationForTarget(targetId) {
        if (!targetId || !EditorLogic) return "";
        var offsets = getCurrentPreviewOffsets()[targetId] || { dx: 0, dy: 0 };
        var scales = getCurrentPreviewScales()[targetId] || { scaleX: 1, scaleY: 1 };
        var hints = getCurrentPreviewTextHints()[targetId] || [];
        return EditorLogic.generateMergedAnnotation({
            dx: offsets.dx || 0,
            dy: offsets.dy || 0,
            scaleX: scales.scaleX || 1,
            scaleY: scales.scaleY || 1,
            textHints: hints,
            count: selectedElementIds.size || 1,
            lang: LANG
        });
    }

    function resetDragState() {
        dragState.active = false;
        dragState.started = false;
        dragState.sourceId = null;
        dragState.startMouse = null;
        dragState.startSvg = null;
        dragState.currentDx = 0;
        dragState.currentDy = 0;
        dragState.ids = [];
        dragState.originalTransforms = {};
    }

    function resetScaleState() {
        scaleState.active = false;
        scaleState.objectId = null;
        scaleState.handle = null;
        scaleState.startMouse = null;
        scaleState.startBox = null;
        scaleState.startScaleX = 1;
        scaleState.startScaleY = 1;
    }

    function ensureScaleHandleLayer() {
        if (scaleHandleLayer) return scaleHandleLayer;
        scaleHandleLayer = document.createElement("div");
        scaleHandleLayer.setAttribute("id", "scale-handle-layer");
        document.body.appendChild(scaleHandleLayer);
        return scaleHandleLayer;
    }

    function clearScaleHandles() {
        if (!scaleHandleLayer) return;
        scaleHandleLayer.innerHTML = "";
        scaleHandleLayer.style.display = "none";
    }

    function buildHandle(x, y, handleName) {
        var handle = document.createElement("div");
        handle.className = "scale-handle";
        handle.style.left = (x - 6) + "px";
        handle.style.top = (y - 6) + "px";
        handle.dataset.handle = handleName;
        handle.addEventListener("mousedown", function (e) {
            if (e.button !== 0) return;
            e.stopPropagation();
            e.preventDefault();
            beginScale(handleName, e);
        });
        return handle;
    }

    function renderScaleHandles() {
        clearScaleHandles();
        if (selectedElementIds.size !== 1) return;
        var targetId = getCurrentTargetId();
        if (!targetId) return;
        var el = svgContent.querySelector("#" + CSS.escape(targetId));
        var bbox = elementBBoxSafe(el);
        var ctm = el && el.getScreenCTM ? el.getScreenCTM() : null;
        if (!el || !bbox || !ctm) return;

        var layer = ensureScaleHandleLayer();
        var corners = [
            { name: "nw", x: bbox.x, y: bbox.y },
            { name: "ne", x: bbox.x + bbox.width, y: bbox.y },
            { name: "sw", x: bbox.x, y: bbox.y + bbox.height },
            { name: "se", x: bbox.x + bbox.width, y: bbox.y + bbox.height }
        ];
        layer.style.display = "block";
        corners.forEach(function (corner) {
            var sx = corner.x * ctm.a + corner.y * ctm.c + ctm.e;
            var sy = corner.x * ctm.b + corner.y * ctm.d + ctm.f;
            layer.appendChild(buildHandle(sx, sy, corner.name));
        });
    }

    function beginScale(handleName, event) {
        var targetId = getCurrentTargetId();
        if (!targetId) return false;
        var el = svgContent.querySelector("#" + CSS.escape(targetId));
        var bbox = elementBBoxSafe(el);
        if (!el || !bbox) return false;
        var currentScale = getCurrentPreviewScales()[targetId] || { scaleX: 1, scaleY: 1 };
        scaleState.active = true;
        scaleState.objectId = targetId;
        scaleState.handle = handleName;
        scaleState.startMouse = { x: event.clientX, y: event.clientY };
        scaleState.startBox = { width: bbox.width, height: bbox.height };
        scaleState.startScaleX = Number(currentScale.scaleX) || 1;
        scaleState.startScaleY = Number(currentScale.scaleY) || 1;
        return true;
    }

    function updateScalePreview(event) {
        if (!scaleState.active || !scaleState.startMouse || !scaleState.startBox) return;
        var dx = event.clientX - scaleState.startMouse.x;
        var dy = event.clientY - scaleState.startMouse.y;
        var delta = Math.max(dx, dy);
        var factor = Math.max(0.2, 1 + delta / Math.max(scaleState.startBox.width, 120));
        var scales = getCurrentPreviewScales();
        scales[scaleState.objectId] = {
            scaleX: scaleState.startScaleX * factor,
            scaleY: scaleState.startScaleY * factor
        };
        applyPreviewOffsetsForCurrentSlide();
        renderScaleHandles();
        updateMergedAnnotationForCurrentTarget();
    }

    function finishScale() {
        if (!scaleState.active) return false;
        var applied = true;
        resetScaleState();
        renderScaleHandles();
        return applied;
    }

    function clearDragPreview(keepCurrentPosition) {
        dragState.ids.forEach(function (id) {
            var el = svgContent.querySelector("#" + CSS.escape(id));
            if (!el) return;
            if (!keepCurrentPosition && Object.prototype.hasOwnProperty.call(dragState.originalTransforms, id)) {
                var original = dragState.originalTransforms[id];
                if (original) el.setAttribute("transform", original);
                else el.removeAttribute("transform");
            }
            el.classList.remove("svg-drag-preview");
        });
    }

    function beginDrag(elem, event) {
        if (!elem || !elem.id) return false;
        if (!selectedElementIds.has(elem.id)) {
            selectElement(elem, false);
        }
        var startSvg = getSvgPoint(event.clientX, event.clientY);
        if (!startSvg) return false;

        dragState.active = true;
        dragState.started = false;
        dragState.sourceId = elem.id;
        dragState.startMouse = { x: event.clientX, y: event.clientY };
        dragState.startSvg = { x: startSvg.x, y: startSvg.y };
        dragState.currentDx = 0;
        dragState.currentDy = 0;
        dragState.ids = Array.from(selectedElementIds);
        dragState.originalTransforms = {};
        dragState.ids.forEach(function (id) {
            var target = svgContent.querySelector("#" + CSS.escape(id));
            dragState.originalTransforms[id] = target ? (target.getAttribute("transform") || "") : "";
        });
        return true;
    }

    function updateDragPreview(event) {
        if (!dragState.active || !dragState.startSvg) return;

        var dxScreen = event.clientX - dragState.startMouse.x;
        var dyScreen = event.clientY - dragState.startMouse.y;
        if (!dragState.started && Math.sqrt(dxScreen * dxScreen + dyScreen * dyScreen) < DRAG_THRESHOLD) {
            return;
        }

        var current = getSvgPoint(event.clientX, event.clientY);
        if (!current) return;

        dragState.started = true;
        dragState.currentDx = current.x - dragState.startSvg.x;
        dragState.currentDy = current.y - dragState.startSvg.y;

        dragState.ids.forEach(function (id) {
            var el = svgContent.querySelector("#" + CSS.escape(id));
            if (!el) return;
            var original = dragState.originalTransforms[id];
            var translate = "translate(" + dragState.currentDx.toFixed(2) + " " + dragState.currentDy.toFixed(2) + ")";
            if (original) el.setAttribute("transform", original + " " + translate);
            else el.setAttribute("transform", translate);
            el.classList.add("svg-drag-preview");
        });
    }

    function finishDrag() {
        if (!dragState.active) return false;

        var applied = dragState.started &&
            EditorLogic &&
            (Math.abs(dragState.currentDx) >= 1 || Math.abs(dragState.currentDy) >= 1);

        if (applied) {
            var offsets = getCurrentPreviewOffsets();
            dragState.ids.forEach(function (id) {
                var existing = offsets[id] || { dx: 0, dy: 0 };
                offsets[id] = {
                    dx: (Number(existing.dx) || 0) + dragState.currentDx,
                    dy: (Number(existing.dy) || 0) + dragState.currentDy
                };
            });
            updateMergedAnnotationForCurrentTarget();
            suppressNextElementClick = true;
            window.setTimeout(function () {
                suppressNextElementClick = false;
            }, 50);
        }

        clearDragPreview(applied);
        resetDragState();
        if (applied) {
            applyPreviewOffsetsForCurrentSlide();
        }
        return applied;
    }

    // ================================================================
    //  1.  loadSlides  -- GET /api/slides
    // ================================================================
    function loadSlides() {
        return fetch("/api/slides")
            .then(function (res) { return res.json(); })
            .then(function (data) {
                slideListEl.innerHTML = "";
                var slides = data.slides || [];
                slideNames = slides.map(function (s) { return s.name; });

                if (slides.length === 0) {
                    var empty = document.createElement("div");
                    empty.className = "slide-list-empty";
                    empty.textContent = liveMode
                        ? t("empty_waiting_slides")
                        : t("empty_no_slides");
                    slideListEl.appendChild(empty);
                    if (!currentSlide) {
                        svgPlaceholder.style.display = "block";
                        svgPlaceholder.textContent = liveMode
                            ? t("placeholder_live_ready")
                            : t("empty_no_slides");
                        svgContent.style.display = "none";
                    }
                    updateNavLabel();
                    return;
                }

                var currentExists = false;
                slides.forEach(function (s) {
                    if (s.name === currentSlide) currentExists = true;
                    var item = document.createElement("div");
                    item.className = "slide-item" + (s.name === currentSlide ? " active" : "");
                    item.setAttribute("data-name", s.name);

                    var nameSpan = document.createElement("span");
                    nameSpan.className = "slide-name";
                    nameSpan.textContent = s.name;
                    item.appendChild(nameSpan);

                    if (s.annotation_count > 0) {
                        var badge = document.createElement("span");
                        badge.className = "badge";
                        badge.textContent = s.annotation_count;
                        item.appendChild(badge);
                    }

                    item.addEventListener("click", function () {
                        selectSlide(s.name, item);
                    });
                    slideListEl.appendChild(item);
                });

                if (!currentSlide || !currentExists) {
                    selectSlide(slides[0].name);
                }
                updateNavLabel();
            })
            .catch(function (err) {
                console.error("loadSlides:", err);
                showError(t("err_load_slides") + err.message);
            });
    }

    // ================================================================
    //  2.  selectSlide  -- GET /api/slide/{name}
    // ================================================================
    function selectSlide(name, el) {
        // Update active class in sidebar
        document.querySelectorAll(".slide-item").forEach(function (it) {
            it.classList.remove("active");
        });
        if (el) el.classList.add("active");

        currentSlide = name;
        selectedElementIds.clear();
        slideAnnotations = {};
        currentLayoutIssues = [];
        resetSelectionModeState();
        updateNavLabel();

        // Reset right panel and rubber band
        clearDragPreview();
        resetDragState();
        clearScaleHandles();
        resetScaleState();
        cancelRubberBand();
        clearSelection();

        fetch("/api/slide/" + encodeURIComponent(name))
            .then(function (res) { return res.json(); })
            .then(function (data) {
                if (data.error) {
                    console.error("selectSlide:", data.error);
                    if (liveMode) {
                        currentSlide = null;
                        svgPlaceholder.style.display = "block";
                        svgPlaceholder.textContent = t("placeholder_slide_writing");
                        svgContent.style.display = "none";
                    }
                    return;
                }
                // Render SVG
                svgPlaceholder.style.display = "none";
                svgContent.style.display = "block";
                svgContent.innerHTML = sanitizeSvg(data.content);

                // Build annotations map from response
                (data.annotations || []).forEach(function (a) {
                    slideAnnotations[a.element_id] = a.annotation;
                });

                setupSvgInteraction();
                markPreviewBaseTransforms();
                applyPreviewOffsetsForCurrentSlide();
                refreshAnnotationVisuals();
                updateAnnotationList();
                renderLayoutIssuesForSelection();
            })
            .catch(function (err) {
                console.error("selectSlide:", err);
                showError(t("err_load_slide") + err.message);
            });
    }

    // ================================================================
    //  3.  setupSvgInteraction
    // ================================================================
    var SKIP_TAGS = ["defs", "style", "title", "desc"];

    function resolveSelectionTarget(el) {
        if (!el) return null;
        if (selectionMode === "child" && activeGroupId) {
            var groupEl = svgContent.querySelector("#" + CSS.escape(activeGroupId));
            if (groupEl && groupEl.contains && groupEl.contains(el)) {
                return isEditableChildElement(el) ? el : null;
            }
        }

        var groupAncestor = findNearestGroupAncestor(el);
        if (groupAncestor) {
            return groupAncestor;
        }
        return el;
    }

    function setupSvgInteraction() {
        var svg = svgContent.querySelector("svg");
        if (!svg) return;

        var allEls = svg.querySelectorAll("*");
        allEls.forEach(function (el) {
            var tag = el.tagName.toLowerCase();
            if (SKIP_TAGS.indexOf(tag) !== -1) return;
            if (el === svg) return;

            el.classList.add("svg-selectable");

            el.addEventListener("click", function (e) {
                if (suppressNextElementClick) {
                    e.stopPropagation();
                    e.preventDefault();
                    suppressNextElementClick = false;
                    return;
                }
                e.stopPropagation();
                var target = resolveSelectionTarget(el);
                if (target) {
                    selectElement(target, e.ctrlKey || e.metaKey);
                }
            });

            el.addEventListener("mousedown", function (e) {
                if (e.button !== 0) return;
                var target = resolveSelectionTarget(el);
                if (target) {
                    beginDrag(target, e);
                }
            });
        });

        // Click on blank area clears selection (skip the synthetic click after rubber band)
        svg.addEventListener("click", function (e) {
            if (suppressNextSvgClick) {
                suppressNextSvgClick = false;
                return;
            }
            if (e.target === svg) clearSelection();
        });
    }

    // ================================================================
    //  4.  selectElement
    // ================================================================
    function selectElement(elem, addToSelection) {
        var eid = elem.id;
        if (!eid) return;
        var tag = elem.tagName.toLowerCase();

        if (addToSelection) {
            // Ctrl+click: toggle this element
            if (selectedElementIds.has(eid)) {
                selectedElementIds.delete(eid);
                elem.classList.remove("svg-selected");
            } else {
                selectedElementIds.add(eid);
                elem.classList.add("svg-selected");
            }
        } else {
            // Normal click: clear others, select only this one
            selectedElementIds.forEach(function (id) {
                if (id !== eid) {
                    var old = svgContent.querySelector("#" + CSS.escape(id));
                    if (old) old.classList.remove("svg-selected");
                }
            });
            selectedElementIds.clear();
            selectedElementIds.add(eid);
            elem.classList.add("svg-selected");
        }

        if (selectionMode === "child") {
            activeChildId = eid;
            if (!activeGroupId) {
                var parentGroup = findNearestGroupAncestor(elem);
                activeGroupId = parentGroup ? parentGroup.id : null;
            }
        } else {
            activeChildId = null;
            activeGroupId = tag === "g" ? eid : null;
        }

        updateSelectionPanel();
    }

    // ================================================================
    //  5.  clearSelection
    // ================================================================
    function clearSelection() {
        clearDragPreview();
        resetDragState();
        clearScaleHandles();
        resetScaleState();
        selectedElementIds.forEach(function (id) {
            var el = svgContent.querySelector("#" + CSS.escape(id));
            if (el) el.classList.remove("svg-selected");
        });
        selectedElementIds.clear();
        clearLayoutIssueVisuals();
        currentLayoutIssues = [];
        resetSelectionModeState();
        updateSelectionPanel();
    }

    function enterChildSelectionMode() {
        if (!activeGroupId) return;
        var groupEl = svgContent.querySelector("#" + CSS.escape(activeGroupId));
        if (!groupEl) return;
        var editableChildren = getEditableChildren(groupEl);
        if (!editableChildren.length) return;
        selectionMode = "child";
        activeChildId = editableChildren[0].id;
        selectElement(editableChildren[0], false);
    }

    function returnToGroupSelectionMode() {
        if (!activeGroupId) return;
        var groupEl = svgContent.querySelector("#" + CSS.escape(activeGroupId));
        selectionMode = "group";
        activeChildId = null;
        if (groupEl) {
            selectElement(groupEl, false);
        } else {
            updateSelectionPanel();
        }
    }

    function updateSelectionModeControls(selectedEl) {
        if (!selectionActionsEl || !btnToggleSelectionMode || !selectionPathEl || !selectedElementHelpEl) return;

        selectionActionsEl.style.display = "none";
        selectionPathEl.style.display = "none";
        selectionPathEl.textContent = "";
        selectedElementHelpEl.textContent = t("selected_help_drag");

        if (!selectedEl || selectedElementIds.size !== 1) return;

        if (selectionMode === "child" && activeGroupId && activeChildId) {
            selectionActionsEl.style.display = "block";
            btnToggleSelectionMode.textContent = t("btn_return_group_mode");
            selectionPathEl.style.display = "block";
            selectionPathEl.textContent = t("selection_path_label") + activeGroupId + " > " + activeChildId;
            selectedElementHelpEl.textContent = t("selected_help_drag");
            return;
        }

        if (selectedEl.tagName.toLowerCase() === "g" && getEditableChildren(selectedEl).length > 0) {
            selectionActionsEl.style.display = "block";
            btnToggleSelectionMode.textContent = t("btn_enter_child_mode");
            selectedElementHelpEl.textContent = t("selected_help_group");
        }
    }

    function updateSelectionPanel() {
        var propsEl = elementPropsEl;
        var count = selectedElementIds.size;

        if (count === 0) {
            selectedElementEl.classList.add("empty");
            selectedElementEl.textContent = t("empty_selected_element");
            annotationInput.style.display = "none";
            annotationText.value = "";
            propsEl.style.display = "none";
            propsEl.innerHTML = "";
            layoutIssuesEl.style.display = "none";
            layoutIssuesListEl.innerHTML = "";
            layoutIssuesActionsEl.innerHTML = "";
            selectionActionsEl.style.display = "none";
            selectionPathEl.style.display = "none";
            selectionPathEl.textContent = "";
            selectedElementHelpEl.textContent = t("selected_help_drag");
            return;
        }

        selectedElementEl.classList.remove("empty");
        propsEl.style.display = "block";
        var currentEl = null;

        if (count === 1) {
            var eid = selectedElementIds.values().next().value;
            var el = svgContent.querySelector("#" + CSS.escape(eid));
            currentEl = el;
            if (el) {
                var tag = el.tagName.toLowerCase();
                selectedElementEl.innerHTML =
                    '<span class="el-tag">&lt;' + escapeHtml(tag) + '&gt;</span>' +
                    '<span class="el-id">' + escapeHtml(eid) + '</span>';
                propsEl.innerHTML = renderPropertyTable(getElementProperties(el));
            }
        } else {
            selectedElementEl.innerHTML =
                '<span class="multi-count">' + escapeHtml(t("multi_selected", { count: count })) + '</span>';
            propsEl.innerHTML = renderMultiSelectSummary(Array.from(selectedElementIds));
        }

        annotationInput.style.display = "block";
        annotationText.placeholder = count > 1
            ? t("placeholder_annotation_multi", { count: count })
            : t("placeholder_annotation");
        if (count === 1) {
            var targetId = selectedElementIds.values().next().value;
            annotationText.value = getMergedAnnotationForTarget(targetId) || slideAnnotations[targetId] || "";
        } else {
            annotationText.value = "";
        }
        updateSelectionModeControls(currentEl);
        renderLayoutIssuesForSelection();
        renderScaleHandles();
    }

    // ---- Rubber band selection ----
    var rubberBandEl = null;
    var rubberBandStart = null;
    var rubberBandUsed = false;
    var suppressNextSvgClick = false;
    var RUBBER_BAND_THRESHOLD = 5;

    function initRubberBand() {
        var overlay = document.getElementById("rubber-band-overlay");
        var container = document.getElementById("svg-container");

        container.addEventListener("mousedown", function (e) {
            // Only left mouse button
            if (e.button !== 0) return;
            if (e.target && isSelectableElement(e.target)) return;

            // Always start tracking — rubber band only activates when
            // mousemove exceeds the threshold. This allows clicking on any
            // element (including SVG background rects) to still trigger
            // the element's click handler for selection.
            rubberBandStart = { x: e.clientX, y: e.clientY };
            rubberBandUsed = false;
        });

        document.addEventListener("mousemove", function (e) {
            if (scaleState.active) {
                updateScalePreview(e);
                return;
            }
            if (dragState.active) {
                updateDragPreview(e);
                return;
            }
            if (!rubberBandStart) return;

            var dx = e.clientX - rubberBandStart.x;
            var dy = e.clientY - rubberBandStart.y;
            var dist = Math.sqrt(dx * dx + dy * dy);

            if (dist < RUBBER_BAND_THRESHOLD) {
                return;
            }

            // Threshold exceeded — this is a drag, not a click
            if (!rubberBandUsed) {
                rubberBandUsed = true;
                overlay.classList.add("active");
            }

            if (!rubberBandEl) {
                rubberBandEl = document.createElement("div");
                rubberBandEl.id = "rubber-band";
                document.body.appendChild(rubberBandEl);
            }

            var x = Math.min(rubberBandStart.x, e.clientX);
            var y = Math.min(rubberBandStart.y, e.clientY);
            var w = Math.abs(dx);
            var h = Math.abs(dy);

            rubberBandEl.style.left = x + "px";
            rubberBandEl.style.top = y + "px";
            rubberBandEl.style.width = w + "px";
            rubberBandEl.style.height = h + "px";
        });

        document.addEventListener("mouseup", function (e) {
            if (scaleState.active) {
                finishScale();
                return;
            }
            if (dragState.active) {
                finishDrag();
                return;
            }
            if (!rubberBandStart) return;

            overlay.classList.remove("active");

            var dx = e.clientX - rubberBandStart.x;
            var dy = e.clientY - rubberBandStart.y;
            var dist = Math.sqrt(dx * dx + dy * dy);

            if (rubberBandEl) {
                rubberBandEl.remove();
                rubberBandEl = null;
            }

            // Only process if drag was beyond threshold
            if (dist >= RUBBER_BAND_THRESHOLD) {
                var rect = {
                    left: Math.min(rubberBandStart.x, e.clientX),
                    top: Math.min(rubberBandStart.y, e.clientY),
                    right: Math.max(rubberBandStart.x, e.clientX),
                    bottom: Math.max(rubberBandStart.y, e.clientY)
                };

                if (!e.ctrlKey && !e.metaKey) {
                    clearSelection();
                }

                selectByRubberBand(rect);
                suppressNextSvgClick = true;
                window.setTimeout(function () {
                    suppressNextSvgClick = false;
                }, 50);
            } else {
                // Below threshold: treat as click on empty space
                if (!e.ctrlKey && !e.metaKey) {
                    clearSelection();
                }
            }

            rubberBandStart = null;
        });

    }

    function cancelRubberBand() {
        rubberBandStart = null;
        if (rubberBandEl) {
            rubberBandEl.remove();
            rubberBandEl = null;
        }
        var ov = document.getElementById("rubber-band-overlay");
        if (ov) ov.classList.remove("active");
        suppressNextSvgClick = false;
        clearDragPreview();
        resetDragState();
    }

    function selectByRubberBand(screenRect) {
        var svg = svgContent.querySelector("svg");
        if (!svg) return;

        var selectableEls = svg.querySelectorAll(".svg-selectable");
        selectableEls.forEach(function (el) {
            try {
                var bbox = el.getBBox();
                var ctm = el.getScreenCTM();
                if (!ctm) return;

                // Transform bbox corners to screen coordinates
                var corners = [
                    { x: bbox.x, y: bbox.y },
                    { x: bbox.x + bbox.width, y: bbox.y },
                    { x: bbox.x, y: bbox.y + bbox.height },
                    { x: bbox.x + bbox.width, y: bbox.y + bbox.height }
                ];

                var minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
                corners.forEach(function (c) {
                    var sx = c.x * ctm.a + c.y * ctm.c + ctm.e;
                    var sy = c.x * ctm.b + c.y * ctm.d + ctm.f;
                    if (sx < minX) minX = sx;
                    if (sy < minY) minY = sy;
                    if (sx > maxX) maxX = sx;
                    if (sy > maxY) maxY = sy;
                });

                // AABB intersection
                if (minX < screenRect.right && maxX > screenRect.left &&
                    minY < screenRect.bottom && maxY > screenRect.top) {
                    var eid = el.id;
                    if (eid) {
                        selectedElementIds.add(eid);
                        el.classList.add("svg-selected");
                    }
                }
            } catch (err) {
                // getBBox can throw for elements with no geometry
            }
        });

        updateSelectionPanel();
    }

    // ================================================================
    //  Keyboard shortcuts
    // ================================================================
    function initKeyboardShortcuts() {
        document.addEventListener("keydown", function (e) {
            // Ctrl+A / Cmd+A: select all elements
            if ((e.ctrlKey || e.metaKey) && e.key === "a") {
                // Don't intercept if focus is in textarea
                if (document.activeElement === annotationText) return;

                e.preventDefault();
                var svg = svgContent.querySelector("svg");
                if (!svg) return;

                svg.querySelectorAll(".svg-selectable").forEach(function (el) {
                    var eid = el.id;
                    if (eid) {
                        selectedElementIds.add(eid);
                        el.classList.add("svg-selected");
                    }
                });
                updateSelectionPanel();
            }

            // Escape: clear selection (skip if textarea is focused)
            if (e.key === "Escape") {
                if (document.activeElement === annotationText) return;
                clearSelection();
            }

            // Slide navigation: ArrowLeft/Right + Home/End (skip while typing)
            if (document.activeElement === annotationText) return;
            if (e.ctrlKey || e.metaKey || e.altKey) return;
            if (slideNames.length === 0) return;

            if (e.key === "ArrowLeft") {
                e.preventDefault();
                gotoSlideIndex(currentSlideIndex() - 1);
            } else if (e.key === "ArrowRight") {
                e.preventDefault();
                gotoSlideIndex(currentSlideIndex() + 1);
            } else if (e.key === "Home") {
                e.preventDefault();
                gotoSlideIndex(0);
            } else if (e.key === "End") {
                e.preventDefault();
                gotoSlideIndex(slideNames.length - 1);
            }
        });
    }

    function initSlideNav() {
        if (navFirstBtn) navFirstBtn.addEventListener("click", function () { gotoSlideIndex(0); });
        if (navPrevBtn)  navPrevBtn.addEventListener("click", function ()  { gotoSlideIndex(currentSlideIndex() - 1); });
        if (navNextBtn)  navNextBtn.addEventListener("click", function ()  { gotoSlideIndex(currentSlideIndex() + 1); });
        if (navLastBtn)  navLastBtn.addEventListener("click", function ()  { gotoSlideIndex(slideNames.length - 1); });
    }

    if (btnResetPreview) {
        btnResetPreview.addEventListener("click", function () {
            clearDragPreview();
            resetDragState();
            clearScaleHandles();
            resetScaleState();
            resetPreviewOffsets(true);
            renderLayoutIssuesForSelection();
            renderScaleHandles();
        });
    }

    if (btnToggleSelectionMode) {
        btnToggleSelectionMode.addEventListener("click", function () {
            if (selectionMode === "group") {
                enterChildSelectionMode();
            } else {
                returnToGroupSelectionMode();
            }
        });
    }

    // ================================================================
    //  6.  Add annotation  -- POST /api/slide/{name}/annotate
    // ================================================================
    btnAddAnnotation.addEventListener("click", function () {
        if (!currentSlide || selectedElementIds.size === 0) return;

        var text = annotationText.value.trim();
        if (!text) return;

        var ids = Array.from(selectedElementIds);
        var promises = ids.map(function (eid) {
            return fetch("/api/slide/" + encodeURIComponent(currentSlide) + "/annotate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ element_id: eid, annotation: text })
            }).then(jsonOrThrow);
        });

        Promise.all(promises)
            .then(function () {
                ids.forEach(function (eid) {
                    slideAnnotations[eid] = text;
                });
                refreshAnnotationVisuals();
                updateAnnotationList();
                annotationText.value = "";
                loadSlides();
            })
            .catch(function (err) {
                console.error("addAnnotation:", err);
                showError(t("err_add_annotation") + err.message);
            });
    });

    // ================================================================
    //  7.  removeAnnotation  -- DELETE /api/slide/{name}/annotate/{id}
    // ================================================================
    function removeAnnotation(elementId) {
        if (!currentSlide) return;

        fetch("/api/slide/" + encodeURIComponent(currentSlide) + "/annotate/" + encodeURIComponent(elementId), {
            method: "DELETE"
        })
            .then(function (res) { return res.json(); })
            .then(function () {
                delete slideAnnotations[elementId];
                refreshAnnotationVisuals();
                updateAnnotationList();
                loadSlides();
            })
            .catch(function (err) {
                console.error("removeAnnotation:", err);
                showError(t("err_remove_annotation") + err.message);
            });
    }

    function clearLayoutIssueVisuals() {
        svgContent.querySelectorAll(".svg-layout-warning").forEach(function (el) {
            el.classList.remove("svg-layout-warning");
        });
    }

    function elementBBoxSafe(el) {
        try {
            return el.getBBox();
        } catch (e) {
            return null;
        }
    }

    function findLikelyContainerForText(textEl) {
        var textBox = elementBBoxSafe(textEl);
        if (!textBox) return null;

        var candidates = Array.from(svgContent.querySelectorAll("rect,image"));
        var best = null;
        var bestArea = Infinity;

        candidates.forEach(function (candidate) {
            if (candidate === textEl) return;
            var box = elementBBoxSafe(candidate);
            if (!box || box.width <= 0 || box.height <= 0) return;
            var contains =
                textBox.x >= box.x - 2 &&
                textBox.y >= box.y - 2 &&
                textBox.x + textBox.width <= box.x + box.width + 2 &&
                textBox.y + textBox.height <= box.y + box.height + 2;
            if (!contains) return;
            var area = box.width * box.height;
            if (area < bestArea) {
                best = { element: candidate, box: box };
                bestArea = area;
            }
        });

        return best;
    }

    function collectTextLayoutIssues(el) {
        if (!EditorLogic || !el) return [];
        var box = elementBBoxSafe(el);
        if (!box) return [];
        var style = window.getComputedStyle(el);
        var fontSizePx = parseFloat(style.fontSize || el.getAttribute("font-size") || "0") || 0;
        var container = findLikelyContainerForText(el);
        return EditorLogic.detectTextLayoutIssues({
            fontSizePx: fontSizePx,
            textLength: (el.textContent || "").trim().length,
            textBox: { width: box.width, height: box.height },
            containerBox: container ? { width: container.box.width, height: container.box.height } : null,
            containerTolerance: 2
        });
    }

    function issueTitle(issue) {
        if (issue.kind === "overflow") return LANG === "zh" ? "文字可能溢出" : "Possible overflow";
        if (issue.kind === "font_too_small") return LANG === "zh" ? "字号可能过小" : "Font may be too small";
        if (issue.kind === "font_too_large") return LANG === "zh" ? "字号可能过大" : "Font may be too large";
        return LANG === "zh" ? "排版问题" : "Layout issue";
    }

    function suggestionForIssue(issue) {
        return LANG === "zh" ? (issue.suggestion_zh || issue.message) : (issue.suggestion_en || issue.message);
    }

    function renderLayoutIssuesForSelection() {
        clearLayoutIssueVisuals();
        currentLayoutIssues = [];

        if (selectedElementIds.size !== 1) {
            layoutIssuesEl.style.display = "none";
            layoutIssuesListEl.innerHTML = "";
            layoutIssuesActionsEl.innerHTML = "";
            return;
        }

        var eid = selectedElementIds.values().next().value;
        var el = svgContent.querySelector("#" + CSS.escape(eid));
        if (!el) {
            layoutIssuesEl.style.display = "none";
            return;
        }

        var tag = el.tagName.toLowerCase();
        if (tag !== "text" && tag !== "tspan") {
            layoutIssuesEl.style.display = "none";
            layoutIssuesListEl.innerHTML = "";
            layoutIssuesActionsEl.innerHTML = "";
            return;
        }

        currentLayoutIssues = collectTextLayoutIssues(el);
        if (!currentLayoutIssues.length) {
            layoutIssuesEl.style.display = "none";
            layoutIssuesListEl.innerHTML = "";
            layoutIssuesActionsEl.innerHTML = "";
            return;
        }

        el.classList.add("svg-layout-warning");
        layoutIssuesEl.style.display = "block";
        layoutIssuesListEl.innerHTML = "";
        layoutIssuesActionsEl.innerHTML = "";

        currentLayoutIssues.forEach(function (issue, idx) {
            var item = document.createElement("div");
            item.className = "layout-issue";
            item.innerHTML =
                '<div class="layout-issue-title">' + escapeHtml(issueTitle(issue)) + '</div>' +
                '<div class="layout-issue-text">' + escapeHtml(issue.message) + '</div>';
            layoutIssuesListEl.appendChild(item);

            var action = document.createElement("button");
            action.type = "button";
            action.className = "layout-issue-action";
            action.textContent = LANG === "zh" ? ("生成建议批注 " + (idx + 1)) : ("Suggest annotation " + (idx + 1));
            action.addEventListener("click", function () {
                var targetId = getCurrentTargetId();
                if (targetId) {
                    getCurrentPreviewTextHints()[targetId] = [suggestionForIssue(issue)];
                    updateMergedAnnotationForCurrentTarget();
                } else {
                    annotationInput.style.display = "block";
                    annotationText.value = suggestionForIssue(issue);
                }
                annotationText.focus();
            });
            layoutIssuesActionsEl.appendChild(action);
        });
    }

    // ================================================================
    //  8.  refreshAnnotationVisuals
    // ================================================================
    function refreshAnnotationVisuals() {
        // Clear all annotated marks
        svgContent.querySelectorAll(".svg-annotated").forEach(function (el) {
            el.classList.remove("svg-annotated");
        });
        // Apply marks
        Object.keys(slideAnnotations).forEach(function (eid) {
            var el = svgContent.querySelector("#" + CSS.escape(eid));
            if (el) el.classList.add("svg-annotated");
        });
    }

    // ================================================================
    //  9.  updateAnnotationList
    // ================================================================
    function updateAnnotationList() {
        annotationsEl.innerHTML = "";

        var ids = Object.keys(slideAnnotations);
        if (ids.length === 0) {
            annotationsEl.innerHTML = '<div class="annotations-empty">' + escapeHtml(t("empty_annotations")) + '</div>';
            return;
        }

        ids.forEach(function (eid) {
            var item = document.createElement("div");
            item.className = "annotation-item";

            // Try to resolve tag from live SVG
            var tag = "";
            var el = svgContent.querySelector("#" + CSS.escape(eid));
            if (el) tag = el.tagName.toLowerCase();

            var header = document.createElement("div");
            header.className = "ann-header";

            var leftSpan = document.createElement("span");
            if (tag) {
                var tagSpan = document.createElement("span");
                tagSpan.className = "ann-tag";
                tagSpan.textContent = "<" + tag + ">";
                leftSpan.appendChild(tagSpan);
            }
            var idSpan = document.createElement("span");
            idSpan.className = "ann-id";
            idSpan.textContent = eid;
            leftSpan.appendChild(idSpan);

            header.appendChild(leftSpan);

            var removeBtn = document.createElement("button");
            removeBtn.className = "ann-remove";
            removeBtn.innerHTML = "&times;";
            removeBtn.title = t("tooltip_remove_annotation");
            removeBtn.addEventListener("click", function () {
                removeAnnotation(eid);
            });
            header.appendChild(removeBtn);

            item.appendChild(header);

            var textDiv = document.createElement("div");
            textDiv.className = "ann-text";
            textDiv.textContent = slideAnnotations[eid];
            item.appendChild(textDiv);

            annotationsEl.appendChild(item);
        });
    }

    // ================================================================
    // 10.  Save all  -- two-step: confirm then save
    // ================================================================
    btnSave.addEventListener("click", function () {
        pendingModalAction = "submit";
        modalMessage.textContent = t("modal_confirm_submit");
        modalConfirm.textContent = t("modal_submit");
        modalConfirm.style.display = "";
        modalCancel.style.display = "";
        modalOverlay.style.display = "flex";
    });

    btnExitPreview.addEventListener("click", function () {
        pendingModalAction = "exit";
        modalMessage.textContent = t("modal_confirm_exit");
        modalConfirm.textContent = t("btn_exit_preview");
        modalConfirm.style.display = "";
        modalCancel.style.display = "";
        modalOverlay.style.display = "flex";
    });

    modalConfirm.addEventListener("click", function () {
        if (pendingModalAction === "exit") {
            modalConfirm.style.display = "none";
            modalCancel.style.display = "none";
            modalMessage.textContent = t("modal_stopping");
            fetch("/api/shutdown", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ reason: "exit-preview" })
            })
                .then(function () {
                    modalMessage.textContent = t("modal_success_exit");
                })
                .catch(function () {
                    modalMessage.textContent = t("modal_success_exit");
                });
            return;
        }

        // Step 2: save annotations. Service lifetime is controlled only by Exit preview.
        modalConfirm.style.display = "none";
        modalCancel.style.display = "none";

        fetch("/api/save-all", { method: "POST" })
            .then(function (res) { return res.json(); })
            .then(function (data) {
                if (data.error) {
                    modalMessage.textContent = t("err_save") + data.error;
                } else {
                    resetPreviewOffsets(true);
                    modalMessage.textContent = t("modal_success_submit");
                    loadSlides();
                }
            })
            .catch(function (err) {
                modalMessage.textContent = t("err_save") + err;
            });
    });

    modalCancel.addEventListener("click", function () {
        modalConfirm.textContent = t("modal_submit");
        modalOverlay.style.display = "none";
    });

    // Close modal on overlay click
    modalOverlay.addEventListener("click", function (e) {
            if (e.target === modalOverlay) {
                modalConfirm.textContent = t("modal_submit");
                modalOverlay.style.display = "none";
            }
        });

    // ================================================================
    //  Utility
    // ================================================================
    function sanitizeSvg(svgString) {
        var doc = new DOMParser().parseFromString(svgString, "image/svg+xml");
        doc.querySelectorAll("script,foreignObject").forEach(function (el) { el.remove(); });
        doc.querySelectorAll("*").forEach(function (el) {
            Array.from(el.attributes).forEach(function (attr) {
                if (attr.name.indexOf("on") === 0) el.removeAttribute(attr.name);
                // Strip dangerous URI protocols from href/xlink:href
                if ((attr.name === "href" || attr.name === "xlink:href") &&
                    (/^\s*javascript\s*:/i.test(attr.value) ||
                     /^\s*data\s*:/i.test(attr.value))) {
                    el.removeAttribute(attr.name);
                }
            });
        });
        return new XMLSerializer().serializeToString(doc.documentElement);
    }

    function showError(msg) {
        var banner = document.createElement("div");
        banner.style.cssText = "position:fixed;top:0;left:0;right:0;padding:10px 16px;background:#ef4444;color:#fff;font-size:13px;text-align:center;z-index:999;cursor:pointer;";
        banner.textContent = msg;
        banner.onclick = function () { banner.remove(); };
        document.body.appendChild(banner);
        setTimeout(function () { banner.remove(); }, 5000);
    }

    function escapeHtml(str) {
        var d = document.createElement("div");
        d.appendChild(document.createTextNode(str));
        return d.innerHTML;
    }

    function jsonOrThrow(res) {
        return res.json().then(function (data) {
            if (!res.ok || data.error) {
                throw new Error(data.error || ("Request failed with status " + res.status));
            }
            return data;
        });
    }

    function loadConfig() {
        return fetch("/api/config")
            .then(function (res) { return res.json(); })
            .then(function (data) {
                liveMode = !!data.live;
            })
            .catch(function () {
                liveMode = false;
            });
    }

    function startSlidePolling() {
        if (!liveMode || slidePollTimer) return;
        slidePollTimer = window.setInterval(function () {
            loadSlides();
        }, 2000);
    }

    // ================================================================
    //  Property extraction & rendering
    // ================================================================
    function getElementProperties(elem) {
        var props = {};
        var tag = elem.tagName.toLowerCase();
        var style = window.getComputedStyle(elem);

        // Position (common to all)
        try {
            var bbox = elem.getBBox();
            props["position"] = Math.round(bbox.x) + ", " + Math.round(bbox.y);
            props["size"] = Math.round(bbox.width) + " x " + Math.round(bbox.height);
        } catch (e) {
            // no geometry
        }

        if (tag === "text" || tag === "tspan") {
            props["font"] = style.fontFamily || elem.getAttribute("font-family") || "";
            props["font-size"] = style.fontSize || elem.getAttribute("font-size") || "";
            props["font-weight"] = style.fontWeight || elem.getAttribute("font-weight") || "";
            props["fill"] = style.fill || elem.getAttribute("fill") || "";
            props["anchor"] = elem.getAttribute("text-anchor") || style.textAnchor || "";
            var text = elem.textContent || "";
            if (text.length > 50) text = text.substring(0, 50) + "...";
            props["content"] = text;
        } else if (tag === "rect") {
            props["fill"] = elem.getAttribute("fill") || style.fill || "";
            props["stroke"] = elem.getAttribute("stroke") || style.stroke || "";
        } else if (tag === "circle") {
            props["r"] = elem.getAttribute("r") || "";
            props["fill"] = elem.getAttribute("fill") || style.fill || "";
            props["stroke"] = elem.getAttribute("stroke") || style.stroke || "";
        } else if (tag === "ellipse") {
            props["rx"] = elem.getAttribute("rx") || "";
            props["ry"] = elem.getAttribute("ry") || "";
            props["fill"] = elem.getAttribute("fill") || style.fill || "";
        } else if (tag === "image") {
            var href = elem.getAttribute("href") || elem.getAttribute("xlink:href") || "";
            var parts = href.split("/");
            props["file"] = parts[parts.length - 1] || href;
        } else if (tag === "path") {
            props["fill"] = elem.getAttribute("fill") || style.fill || "";
            props["stroke"] = elem.getAttribute("stroke") || style.stroke || "";
        }

        return props;
    }

    function isSafeColor(val) {
        // Only allow values that look like CSS colors (hex, rgb, rgba, hsl, named).
        // Reject anything with ; : url @ \ to prevent CSS injection.
        return val.length < 100 && !/[;:@\\]|url\s*\(/i.test(val);
    }

    function renderPropertyTable(props) {
        var html = '<table class="prop-table">';
        Object.keys(props).forEach(function (key) {
            var val = props[key];
            if (!val) return;
            html += '<tr><td class="prop-key">' + escapeHtml(key) + '</td><td class="prop-val">';
            if ((key === "fill" || key === "stroke") && isSafeColor(val)) {
                html += '<span class="prop-color" style="background:' + escapeHtml(val) + ';"></span>';
            }
            html += escapeHtml(val) + '</td></tr>';
        });
        html += '</table>';
        return html;
    }

    function renderMultiSelectSummary(ids) {
        var typeCounts = {};
        var sharedFontSize = null;
        var allHaveFontSize = true;

        ids.forEach(function (eid) {
            var el = svgContent.querySelector("#" + CSS.escape(eid));
            if (!el) return;
            var tag = el.tagName.toLowerCase();
            typeCounts[tag] = (typeCounts[tag] || 0) + 1;

            if (tag === "text" || tag === "tspan") {
                var fs = window.getComputedStyle(el).fontSize || el.getAttribute("font-size") || "";
                if (sharedFontSize === null) {
                    sharedFontSize = fs;
                } else if (sharedFontSize !== fs) {
                    sharedFontSize = "mixed";
                }
            } else {
                allHaveFontSize = false;
            }
        });

        var summary = '<div class="multi-summary">';
        var parts = [];
        Object.keys(typeCounts).forEach(function (tag) {
            parts.push(typeCounts[tag] + " " + tag);
        });
        summary += parts.join(", ");

        if (allHaveFontSize && sharedFontSize && sharedFontSize !== "mixed") {
            summary += ' | font-size: ' + escapeHtml(sharedFontSize);
        } else if (allHaveFontSize && sharedFontSize === "mixed") {
            summary += ' | font-size: ' + escapeHtml(t("multi_mixed"));
        }
        summary += '</div>';

        // Element list
        summary += '<div class="multi-el-list">';
        ids.forEach(function (eid) {
            var el = svgContent.querySelector("#" + CSS.escape(eid));
            if (!el) return;
            var tag = el.tagName.toLowerCase();
            summary += '<div class="multi-el-item"><span class="el-tag">&lt;' +
                escapeHtml(tag) + '&gt;</span>' + escapeHtml(eid) + '</div>';
        });
        summary += '</div>';

        return summary;
    }

    // ================================================================
    //  Boot
    // ================================================================
    applyI18n();
    var langToggleBtn = document.getElementById("btn-lang-toggle");
    if (langToggleBtn) {
        langToggleBtn.textContent = LANG === "zh" ? "EN" : "中";
        langToggleBtn.title = t("lang_toggle_title");
        langToggleBtn.addEventListener("click", function () {
            setLang(LANG === "zh" ? "en" : "zh");
        });
    }

    loadConfig().then(function () {
        loadSlides();
        startSlidePolling();
    });
    initRubberBand();
    initKeyboardShortcuts();
    initSlideNav();
})();
