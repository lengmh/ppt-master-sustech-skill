(function () {
    "use strict";

    var state = {
        enabled: false,
        model: null,
        review_decisions: { artifact_type: "ppt_text_normalize_review_decisions", schema_version: "0.1", review_model: "review_model.json", decisions: [] },
        undoStack: [],
        selectedBlockId: null,
        selectedIds: [],
        svgRoot: null
    };

    var USER_GROUP_PALETTE = ["#A855F7", "#F97316", "#14B8A6", "#E11D48", "#84CC16", "#0EA5E9"];

    function el(id) { return document.getElementById(id); }

    function init(config) {
        state.enabled = !!(config && config.enabled);
        var panel = el("normalization-review-panel");
        if (!panel) return;
        panel.style.display = state.enabled ? "block" : "none";
        var panelRight = el("panel-right");
        if (panelRight) panelRight.classList.toggle("normalization-review-enabled", state.enabled);
        if (!state.enabled) return;
        Promise.all([
            fetchJson("/api/normalization-review/model"),
            fetchJson("/api/normalization-review/decisions")
        ]).then(function (items) {
            state.model = items[0];
            state.review_decisions = items[1];
            state.undoStack = [];
            renderSummary();
            populateGroups();
            bindActions();
            updateUndoButton();
            applyAllDecisionOverlays();
        }).catch(function (err) {
            setStatus("审阅模型加载失败：" + err.message, true);
        });
    }

    function fetchJson(url) {
        return fetch(url).then(function (res) {
            return res.json().then(function (data) {
                if (!res.ok || data.error) throw new Error(data.error || ("HTTP " + res.status));
                return data;
            });
        });
    }

    function bindActions() {
        var btn = el("normalization-review-apply");
        if (btn && !btn.dataset.bound) {
            btn.dataset.bound = "1";
            btn.addEventListener("click", saveDecisionForSelected);
        }
        var undoBtn = el("normalization-review-undo");
        if (undoBtn && !undoBtn.dataset.bound) {
            undoBtn.dataset.bound = "1";
            undoBtn.addEventListener("click", undoLastDecision);
        }
        var groupSelect = el("normalization-review-group");
        if (groupSelect && !groupSelect.dataset.bound) {
            groupSelect.dataset.bound = "1";
            groupSelect.addEventListener("change", refreshFieldAvailability);
        }
        document.querySelectorAll('input[name="normalization-review-action"]').forEach(function (radio) {
            if (radio.dataset.bound) return;
            radio.dataset.bound = "1";
            radio.addEventListener("change", refreshFieldAvailability);
        });
        var override = el("normalization-review-override");
        if (override && !override.dataset.bound) {
            override.dataset.bound = "1";
            override.addEventListener("change", refreshFieldAvailability);
        }
    }

    function renderSummary() {
        var summary = el("normalization-review-summary");
        if (!summary || !state.model) return;
        var blocks = state.model.blocks || [];
        var groups = state.model.groups || [];
        summary.textContent = "共 " + blocks.length + " 个文本块，" + groups.length + " 个分组。浏览器只保存 review_decisions.json。";
    }

    function populateGroups() {
        var select = el("normalization-review-group");
        if (!select || !state.model) return;
        select.innerHTML = "";
        var selectedValue = select.value;
        allGroups().forEach(function (group) {
            var opt = document.createElement("option");
            opt.value = group.group_id;
            opt.textContent = groupDisplayName(group);
            opt.title = group.group_id;
            select.appendChild(opt);
        });
        if (selectedValue && groupById(selectedValue)) select.value = selectedValue;
    }

    function onSlideLoaded(svgRoot) {
        state.svgRoot = svgRoot || null;
        applyAllDecisionOverlays();
    }

    function allGroups() {
        return (state.model ? (state.model.groups || []) : []).concat(userGroupsFromDecisions());
    }

    function onSelectionChange(ids, svgRoot) {
        state.selectedIds = ids || [];
        state.selectedBlockId = null;
        state.svgRoot = svgRoot || state.svgRoot;
        applyAllDecisionOverlays();
        if (!state.enabled || !svgRoot || !state.selectedIds.length) {
            renderCurrent(null);
            return;
        }
        for (var i = 0; i < state.selectedIds.length; i++) {
            var selected = svgRoot.querySelector("#" + CSS.escape(state.selectedIds[i]));
            var holder = findReviewHolder(selected);
            if (holder) {
                state.selectedBlockId = holder.getAttribute("data-review-block-id");
                break;
            }
        }
        renderCurrent(blockById(state.selectedBlockId));
    }

    function findReviewHolder(node) {
        var current = node;
        while (current && current.getAttribute) {
            if (current.getAttribute("data-review-block-id")) return current;
            current = current.parentNode;
        }
        return null;
    }

    function blockById(blockId) {
        if (!blockId || !state.model) return null;
        return (state.model.blocks || []).find(function (b) { return b.block_id === blockId; }) || null;
    }

    function renderCurrent(block) {
        var current = el("normalization-review-current");
        if (!current) return;
        if (!block) {
            current.innerHTML = '<div class="review-muted">请选择一个文本规范化覆盖框。</div>';
            updateFieldAvailability(null);
            return;
        }
        current.innerHTML = "<strong>" + escapeHtml(block.block_id) + "</strong>"
            + "<div>状态：" + escapeHtml(statusLabel(block.status)) + "</div>"
            + "<div>自动分组：" + escapeHtml(groupLabelById(block.auto_group_id) || "无") + "</div>"
            + "<div>计划字段：" + escapeHtml(fieldListLabel(block.planned_fields || [])) + "</div>"
            + "<div>文本预览：" + escapeHtml(block.text_preview || "") + "</div>";
        var groupSelect = el("normalization-review-group");
        if (groupSelect && block.planned_group_id && groupById(block.planned_group_id)) groupSelect.value = block.planned_group_id;
        applyDecisionToForm(existingDecision(block.block_id), block);
    }

    function applyDecisionToForm(decision, block) {
        var action = (decision && decision.action) || "keep_auto";
        var radio = document.querySelector('input[name="normalization-review-action"][value="' + action + '"]');
        if (radio) radio.checked = true;
        var groupSelect = el("normalization-review-group");
        if (groupSelect && decision && decision.group_id && groupById(decision.group_id)) groupSelect.value = decision.group_id;
        var nameInput = el("normalization-review-new-group-name");
        if (nameInput) {
            nameInput.value = decision && decision.action === "create_group"
                ? (decision.label || "")
                : "";
        }
        var fields = decision && Array.isArray(decision.fields)
            ? decision.fields
            : (Array.isArray(block.planned_fields) && block.planned_fields.length ? block.planned_fields : defaultFieldsForBlock(block));
        document.querySelectorAll(".normalization-review-field").forEach(function (box) {
            box.checked = fields.indexOf(box.value) !== -1;
        });
        var override = el("normalization-review-override");
        if (override) override.checked = !!(decision && decision.override_frozen_skip);
        updateFieldAvailability(block);
    }

    function existingDecision(blockId) {
        var decisions = Array.isArray(state.review_decisions.decisions) ? state.review_decisions.decisions : [];
        return decisions.find(function (item) { return item.block_id === blockId; }) || null;
    }

    function selectedAction() {
        var radio = document.querySelector('input[name="normalization-review-action"]:checked');
        return radio ? radio.value : "keep_auto";
    }

    function selectedFields() {
        var out = [];
        document.querySelectorAll(".normalization-review-field:checked").forEach(function (box) {
            if (box.disabled) return;
            if (["font_family", "bold", "color"].indexOf(box.value) !== -1) out.push(box.value);
        });
        return out;
    }

    function refreshFieldAvailability() {
        updateFieldAvailability(blockById(state.selectedBlockId));
    }

    function updateFieldAvailability(block) {
        var boxes = Array.from(document.querySelectorAll(".normalization-review-field"));
        var hint = el("normalization-review-field-hint");
        if (!boxes.length) return;
        if (!block) {
            boxes.forEach(function (box) {
                setFieldBoxAvailability(box, false, "");
                box.checked = false;
            });
            if (hint) hint.textContent = "请选择文本块后再选择字段。";
            return;
        }
        var action = selectedAction();
        if (action === "exclude") {
            boxes.forEach(function (box) {
                setFieldBoxAvailability(box, false, "排除时不需要选择字段");
                box.checked = false;
            });
            if (hint) hint.textContent = "排除 / 跳过不会修改字段。";
            return;
        }
        var allowed = allowedFieldsForDecision(block, action);
        var allowedSet = {};
        allowed.forEach(function (field) { allowedSet[field] = true; });
        var disabledLabels = [];
        boxes.forEach(function (box) {
            var enabled = !!allowedSet[box.value];
            setFieldBoxAvailability(box, enabled, enabled ? "" : "当前文本块或分组不允许修改此字段");
            if (!enabled) {
                if (box.checked) box.checked = false;
                disabledLabels.push(fieldLabel(box.value));
            }
        });
        if (!boxes.some(function (box) { return box.checked && !box.disabled; })) {
            defaultFieldsForAllowed(allowed).forEach(function (field) {
                var box = boxes.find(function (item) { return item.value === field; });
                if (box && !box.disabled) box.checked = true;
            });
        }
        if (hint) {
            hint.textContent = disabledLabels.length
                ? "不可用字段：" + disabledLabels.join("、") + "。"
                : "当前字段均可用于所选处理方式。";
        }
    }

    function setFieldBoxAvailability(box, enabled, reason) {
        box.disabled = !enabled;
        box.title = reason || "";
        var label = box.closest ? box.closest("label") : box.parentNode;
        if (label && label.classList) {
            label.classList.toggle("review-field-disabled", !enabled);
            label.title = reason || "";
        }
    }

    function allowedFieldsForDecision(block, action) {
        var blockAllowed = allowedFieldsFromBlock(block);
        var groupAllowed = null;
        if (action === "keep_auto") {
            groupAllowed = allowedFieldsFromGroup(groupById(block.planned_group_id || block.auto_group_id));
        } else if (action === "use_group") {
            groupAllowed = allowedFieldsFromGroup(groupById((el("normalization-review-group") || {}).value));
        }
        if (!groupAllowed) return blockAllowed;
        return intersectFields(blockAllowed, groupAllowed);
    }

    function allowedFieldsFromBlock(block) {
        if (!block) return [];
        if (Array.isArray(block.allowed_fields)) return normalizeFieldList(block.allowed_fields);
        if (Array.isArray(block.planned_fields)) return normalizeFieldList(block.planned_fields);
        return ["font_family", "bold", "color"];
    }

    function allowedFieldsFromGroup(group) {
        if (!group) return null;
        if (Array.isArray(group.allowed_fields)) return normalizeFieldList(group.allowed_fields);
        if (Array.isArray(group.fields)) return normalizeFieldList(group.fields);
        return normalizeFieldList([].concat(group.default_fields || [], group.optional_fields || []));
    }

    function normalizeFieldList(fields) {
        var out = [];
        (fields || []).forEach(function (field) {
            if (["font_family", "bold", "color"].indexOf(field) !== -1 && out.indexOf(field) === -1) out.push(field);
        });
        return out;
    }

    function intersectFields(left, right) {
        var rightSet = {};
        (right || []).forEach(function (field) { rightSet[field] = true; });
        return (left || []).filter(function (field) { return !!rightSet[field]; });
    }

    function defaultFieldsForBlock(block) {
        return defaultFieldsForAllowed(allowedFieldsFromBlock(block));
    }

    function defaultFieldsForAllowed(allowed) {
        var allowedSet = {};
        (allowed || []).forEach(function (field) { allowedSet[field] = true; });
        var preferred = ["font_family", "bold"];
        var out = preferred.filter(function (field) { return !!allowedSet[field]; });
        if (!out.length && allowed && allowed.length) out.push(allowed[0]);
        return out;
    }

    function fieldLabel(field) {
        var labels = {
            font_family: "字体",
            east_asia_font_family: "中文字体",
            bold: "粗体",
            color: "颜色",
            font_size_pt: "字号"
        };
        return labels[field] || field;
    }

    function saveDecisionForSelected() {
        var block = blockById(state.selectedBlockId);
        if (!block) {
            setStatus("未选中文本规范化块。", true);
            return;
        }
        var previousPayload = cloneReviewDecisions();
        var action = selectedAction();
        var fields = selectedFields();
        if (action !== "exclude" && fields.length === 0) {
            setStatus("请选择至少一个允许修改字段，或选择“排除 / 跳过”。", true);
            return;
        }
        var decision = { block_id: block.block_id, action: action };
        if (action === "use_group") {
            decision.group_id = (el("normalization-review-group") || {}).value || block.planned_group_id || block.auto_group_id;
            decision.fields = fields;
        } else if (action === "create_group") {
            decision.new_group_id = userGroupIdForBlock(block);
            decision.label = selectedNewGroupLabel(block);
            decision.reference_block_id = block.block_id;
            decision.fields = fields;
        } else if (action === "keep_auto") {
            decision.fields = fields;
        } else if (action === "exclude") {
            decision.reason = "visual_review_excluded";
        }
        var override = el("normalization-review-override");
        if (override && override.checked && action !== "exclude") decision.override_frozen_skip = true;
        var nextPayload = cloneReviewDecisions();
        nextPayload.decisions = effectiveDecisionsFrom(previousPayload).filter(function (item) { return item.block_id !== block.block_id; });
        nextPayload.decisions.push(decision);
        nextPayload.updated_at = new Date().toISOString();
        state.review_decisions = nextPayload;
        postCurrentDecisions(function () {
            state.undoStack.push(previousPayload);
            populateGroups();
            updateUndoButton();
            applyAllDecisionOverlays();
            setStatus("已保存当前块决策：" + block.block_id, false);
            renderCurrent(block);
        }, function (err) {
            state.review_decisions = previousPayload;
            populateGroups();
            updateUndoButton();
            applyAllDecisionOverlays();
            setStatus("保存失败：" + err.message, true);
            renderCurrent(block);
        });
    }

    function undoLastDecision() {
        var currentPayload = cloneReviewDecisions();
        var previousPayload = state.undoStack.pop();
        var fallbackRemoved = null;
        if (!previousPayload) {
            var decisions = effectiveDecisionsFrom(currentPayload);
            if (!decisions.length) {
                setStatus("没有可撤销的决策。", true);
                updateUndoButton();
                return;
            }
            fallbackRemoved = decisions[decisions.length - 1];
            previousPayload = cloneReviewDecisions();
            previousPayload.decisions = decisions.slice(0, decisions.length - 1);
        }
        previousPayload.updated_at = new Date().toISOString();
        state.review_decisions = previousPayload;
        postCurrentDecisions(function () {
            populateGroups();
            updateUndoButton();
            applyAllDecisionOverlays();
            var restored = blockById(state.selectedBlockId);
            renderCurrent(restored);
            setStatus(fallbackRemoved ? ("已撤销最近决策：" + fallbackRemoved.block_id) : "已撤销最近一次保存。", false);
        }, function (err) {
            state.review_decisions = currentPayload;
            if (!fallbackRemoved) state.undoStack.push(previousPayload);
            populateGroups();
            updateUndoButton();
            applyAllDecisionOverlays();
            renderCurrent(blockById(state.selectedBlockId));
            setStatus("撤销失败：" + err.message, true);
        });
    }

    function postCurrentDecisions(onSuccess, onError) {
        fetch("/api/normalization-review/decisions", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(state.review_decisions)
        }).then(function (res) { return res.json(); })
            .then(function (data) {
                if (data.error) throw new Error(data.error);
                if (onSuccess) onSuccess(data);
            })
            .catch(function (err) {
                if (onError) onError(err);
            });
    }

    function effectiveDecisions() {
        return effectiveDecisionsFrom(state.review_decisions);
    }

    function effectiveDecisionsFrom(payload) {
        return payload && Array.isArray(payload.decisions) ? payload.decisions : [];
    }

    function cloneReviewDecisions() {
        return JSON.parse(JSON.stringify(state.review_decisions || {
            artifact_type: "ppt_text_normalize_review_decisions",
            schema_version: "0.1",
            review_model: "review_model.json",
            decisions: []
        }));
    }

    function updateUndoButton() {
        var undoBtn = el("normalization-review-undo");
        if (!undoBtn) return;
        undoBtn.disabled = state.undoStack.length === 0 && effectiveDecisions().length === 0;
    }

    function userGroupsFromDecisions() {
        var seen = {};
        effectiveDecisions().forEach(function (decision) {
            if (!decision || decision.action !== "create_group" || !decision.new_group_id) return;
            seen[decision.new_group_id] = {
                group_id: decision.new_group_id,
                label: decision.label || ("自定义分组：" + decision.reference_block_id),
                source: "user_review",
                reference_block_id: decision.reference_block_id,
                fields: normalizeFieldList(decision.fields || ["font_family", "bold"]),
                allowed_fields: normalizeFieldList(decision.fields || ["font_family", "bold"]),
                color: userGroupColor(decision.new_group_id)
            };
        });
        return Object.keys(seen).sort().map(function (groupId) { return seen[groupId]; });
    }

    function selectedNewGroupLabel(block) {
        var input = el("normalization-review-new-group-name");
        var label = input ? String(input.value || "").trim() : "";
        return label || ("自定义分组：" + block.block_id);
    }

    function userGroupIdForBlock(block) {
        return "user_group_" + block.block_id.replace(/[^A-Za-z0-9_-]/g, "_");
    }

    function userGroupColor(groupId) {
        var groups = userGroupsFromDecisionIds();
        var index = groups.indexOf(groupId);
        if (index < 0) index = groups.length;
        return USER_GROUP_PALETTE[index % USER_GROUP_PALETTE.length];
    }

    function userGroupsFromDecisionIds() {
        var out = [];
        effectiveDecisions().forEach(function (decision) {
            if (decision && decision.action === "create_group" && decision.new_group_id && out.indexOf(decision.new_group_id) === -1) {
                out.push(decision.new_group_id);
            }
        });
        return out.sort();
    }

    function applyAllDecisionOverlays() {
        if (!state.enabled || !state.svgRoot || !state.model) return;
        (state.model.blocks || []).forEach(function (block) {
            resetOverlayForBlock(block);
        });
        effectiveDecisions().forEach(function (decision) {
            updateOverlayForDecision(decision);
        });
    }

    function updateOverlayForDecision(decision) {
        if (!decision || !decision.block_id) return;
        var block = blockById(decision.block_id);
        var holder = reviewHolderByBlockId(decision.block_id);
        if (!block || !holder) return;
        var rect = holder.querySelector("rect");
        if (!rect) return;
        holder.classList.remove("review-decision-applied", "review-decision-excluded");
        if (decision.action === "exclude") {
            rect.setAttribute("fill", "#D1D5DB");
            rect.setAttribute("fill-opacity", "0.14");
            rect.setAttribute("stroke", "#9CA3AF");
            rect.setAttribute("stroke-dasharray", "6 4");
            holder.classList.add("review-decision-excluded");
            return;
        }
        var groupId = decision.group_id || decision.new_group_id || block.planned_group_id || block.auto_group_id;
        var color = groupColor(groupId);
        rect.setAttribute("fill", color);
        rect.setAttribute("fill-opacity", "0.26");
        rect.setAttribute("stroke", color);
        rect.removeAttribute("stroke-dasharray");
        holder.classList.add("review-decision-applied");
    }

    function resetOverlayForBlock(block) {
        var holder = reviewHolderByBlockId(block.block_id);
        if (!holder) return;
        var rect = holder.querySelector("rect");
        if (!rect) return;
        var status = block.status || "skipped";
        var groupId = block.planned_group_id || block.auto_group_id;
        var color = groupColor(groupId);
        holder.classList.remove("review-decision-applied", "review-decision-excluded");
        rect.setAttribute("fill", status === "planned_change" ? color : "#D1D5DB");
        rect.setAttribute("fill-opacity", status === "planned_change" ? "0.22" : "0.14");
        rect.setAttribute("stroke", color);
        if (["unchanged_selectable", "frozen", "skipped", "unsupported"].indexOf(status) !== -1) {
            rect.setAttribute("stroke-dasharray", "6 4");
        } else {
            rect.removeAttribute("stroke-dasharray");
        }
    }

    function reviewHolderByBlockId(blockId) {
        if (!state.svgRoot || !blockId) return null;
        var holders = state.svgRoot.querySelectorAll(".normalization-review-overlay");
        for (var i = 0; i < holders.length; i++) {
            if (holders[i].getAttribute("data-review-block-id") === blockId) return holders[i];
        }
        return null;
    }

    function groupColor(groupId) {
        var group = groupById(groupId);
        return (group && group.color) || "#9CA3AF";
    }

    function setStatus(message, isError) {
        var status = el("normalization-review-status");
        if (!status) return;
        status.textContent = message;
        status.className = isError ? "review-error" : "review-muted";
    }

    function escapeHtml(value) {
        var div = document.createElement("div");
        div.appendChild(document.createTextNode(String(value == null ? "" : value)));
        return div.innerHTML;
    }

    function groupById(groupId) {
        if (!groupId || !state.model) return null;
        return allGroups().find(function (group) { return group.group_id === groupId; }) || null;
    }

    function groupLabelById(groupId) {
        var group = groupById(groupId);
        if (group) return groupDisplayName(group);
        return groupId || "";
    }

    function groupDisplayName(group) {
        if (group.source === "user_review") {
            return group.label || group.group_id || "自定义分组";
        }
        var key = group.canonical_key || {};
        if (key.page_type || key.object_slot || key.slot_variant) {
            return [
                pageTypeLabel(key.page_type),
                slotLabel(key.object_slot),
                variantLabel(key.slot_variant, key.object_slot),
                profileLabel(group.permission_profile)
            ].filter(Boolean).join(" / ");
        }
        if (group.label) return localizeGroupLabel(group.label);
        return group.group_id || "未命名分组";
    }

    function localizeGroupLabel(label) {
        return String(label || "")
            .split("/")
            .map(function (part) { return tokenLabel(part.trim()); })
            .join(" / ");
    }

    function tokenLabel(token) {
        return pageTypeLabel(token) || slotLabel(token) || variantLabel(token) || profileLabel(token) || token;
    }

    function pageTypeLabel(value) {
        var labels = {
            cover: "封面页",
            toc: "目录页",
            content: "内容页",
            chapter: "章节页",
            divider: "分隔页",
            unknown: "未知页面"
        };
        return labels[value] || "";
    }

    function slotLabel(value) {
        var labels = {
            page_title: "页面标题",
            footer: "页脚",
            toc_title: "目录标题",
            toc_item: "目录项",
            content_stat: "数据指标",
            content_caption: "内容说明",
            content_label: "内容标签",
            chapter_marker: "章节编号",
            chapter_title: "章节标题",
            hero: "主视觉",
            body: "正文",
            unknown: "未知对象"
        };
        return labels[value] || "";
    }

    function variantLabel(value, objectSlot) {
        if (!value) return "";
        var suffix = String(value);
        if (objectSlot && suffix.indexOf(objectSlot + "@") === 0) suffix = suffix.slice(String(objectSlot).length + 1);
        var labels = {
            "default": "默认样式",
            "standard_top": "标准顶部",
            "primary": "主标题",
            "secondary": "副标题",
            "org_name": "机构名称",
            "page_num": "页码",
            "note": "注释",
            "uniform_grid_title": "统一网格标题"
        };
        return labels[suffix] || ("变体：" + suffix.replace(/_/g, " "));
    }

    function profileLabel(value) {
        var labels = {
            typography_only: "仅字体",
            conservative_text: "保守文本",
            slot_standard: "标准槽位",
            list_standard: "标准列表",
            series_standard: "系列文本",
            frozen: "冻结"
        };
        return labels[value] || "";
    }

    function statusLabel(value) {
        var labels = {
            planned_change: "计划修改",
            unchanged_selectable: "无变化，可选择",
            unsupported: "不支持",
            skipped: "已跳过",
            frozen: "已冻结"
        };
        return labels[value] || (value || "未知");
    }

    function fieldListLabel(fields) {
        if (!fields || !fields.length) return "无";
        return fields.map(fieldLabel).join("、");
    }

    window.PptTextNormalizeReview = {
        init: init,
        onSlideLoaded: onSlideLoaded,
        onSelectionChange: onSelectionChange
    };
})();
