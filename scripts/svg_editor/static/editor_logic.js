(function (root, factory) {
    if (typeof module === "object" && module.exports) {
        module.exports = factory();
    } else {
        root.PptSvgEditorLogic = factory();
    }
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
    "use strict";

    function _num(value) {
        var n = Number(value);
        return Number.isFinite(n) ? n : 0;
    }

    function _absRoundedPx(value) {
        return String(Math.round(Math.abs(_num(value)))) + "px";
    }

    function _movementParts(dx, dy, lang) {
        var parts = [];
        dx = _num(dx);
        dy = _num(dy);

        if (dx > 0) parts.push(lang === "zh" ? (_absRoundedPx(dx) + "向右") : (_absRoundedPx(dx) + " right"));
        if (dx < 0) parts.push(lang === "zh" ? (_absRoundedPx(dx) + "向左") : (_absRoundedPx(dx) + " left"));
        if (dy > 0) parts.push(lang === "zh" ? (_absRoundedPx(dy) + "向下") : (_absRoundedPx(dy) + " down"));
        if (dy < 0) parts.push(lang === "zh" ? (_absRoundedPx(dy) + "向上") : (_absRoundedPx(dy) + " up"));

        return parts;
    }

    function generateMoveAnnotation(opts) {
        opts = opts || {};
        var dx = _num(opts.dx);
        var dy = _num(opts.dy);
        var count = Math.max(1, _num(opts.count) || 1);
        var lang = opts.lang === "zh" ? "zh" : "en";
        var parts = _movementParts(dx, dy, lang);

        if (!parts.length) {
            return lang === "zh"
                ? "本次拖拽位移过小，可忽略。"
                : "This drag is too small to apply.";
        }

        if (lang === "zh") {
            return count > 1
                ? ("将这些已选元素作为一组移动：" + parts.join("，") + "。保持它们之间的相对间距不变。")
                : ("将该元素移动：" + parts.join("，") + "。保持当前视觉层级。");
        }

        return count > 1
            ? ("Move these selected elements " + parts.join(" and ") + " as a group. Keep their internal spacing unchanged.")
            : ("Move this element " + parts.join(" and ") + ". Preserve its visual hierarchy.");
    }

    function _percent(value) {
        return Math.round(_num(value) * 100);
    }

    function generateScaleAnnotation(opts) {
        opts = opts || {};
        var scaleX = _num(opts.scaleX || 1);
        var scaleY = _num(opts.scaleY || 1);
        var count = Math.max(1, _num(opts.count) || 1);
        var lang = opts.lang === "zh" ? "zh" : "en";

        if (Math.abs(scaleX - 1) < 0.01 && Math.abs(scaleY - 1) < 0.01) {
            return lang === "zh" ? "当前缩放变化过小，可忽略。" : "This scale change is too small to apply.";
        }

        if (Math.abs(scaleX - scaleY) < 0.02) {
            var pct = _percent(scaleX);
            if (lang === "zh") {
                return count > 1
                    ? ("将这些已选元素整体缩放到 " + pct + "%，保持它们之间的相对间距不变。")
                    : ("将该元素缩放到 " + pct + "%，保持当前视觉层级。");
            }
            return count > 1
                ? ("Scale these selected elements to " + pct + "% as a group. Keep their internal spacing unchanged.")
                : ("Scale this element to " + pct + "%. Preserve its visual hierarchy.");
        }

        if (lang === "zh") {
            return count > 1
                ? ("将这些已选元素横向缩放到 " + _percent(scaleX) + "%、纵向缩放到 " + _percent(scaleY) + "%，保持它们之间的相对间距不变。")
                : ("将该元素横向缩放到 " + _percent(scaleX) + "%、纵向缩放到 " + _percent(scaleY) + "%，保持当前视觉层级。");
        }
        return count > 1
            ? ("Scale these selected elements to " + _percent(scaleX) + "% width and " + _percent(scaleY) + "% height as a group. Keep their internal spacing unchanged.")
            : ("Scale this element to " + _percent(scaleX) + "% width and " + _percent(scaleY) + "% height. Preserve its visual hierarchy.");
    }

    function _joinClauses(clauses, lang) {
        clauses = clauses.filter(Boolean);
        if (!clauses.length) return "";
        if (clauses.length === 1) return clauses[0];
        if (lang === "zh") return clauses.join("，并");
        return clauses.join(", and ");
    }

    function _stripClosingHierarchyClause(text, lang) {
        text = String(text || "").trim();
        if (!text) return "";
        if (lang === "zh") {
            return text
                .replace(/[，。]保持当前视觉层级。?$/u, "")
                .replace(/[，。；]+$/u, "")
                .trim();
        }
        return text
            .replace(/\. Preserve (its|their) visual hierarchy\.?$/i, "")
            .replace(/[,.;\s]+$/i, "")
            .trim();
    }

    function _normalizeHintText(text, lang) {
        text = String(text || "").trim();
        if (!text) return "";
        if (lang === "zh") {
            return text.replace(/[，。；]+$/u, "").trim();
        }
        return text.replace(/[,.;\s]+$/i, "").trim();
    }

    function generateMergedAnnotation(opts) {
        opts = opts || {};
        var lang = opts.lang === "zh" ? "zh" : "en";
        var count = Math.max(1, _num(opts.count) || 1);
        var clauses = [];
        var dx = _num(opts.dx);
        var dy = _num(opts.dy);
        var sx = _num(opts.scaleX || 1);
        var sy = _num(opts.scaleY || 1);
        var textHints = Array.isArray(opts.textHints) ? opts.textHints.filter(Boolean) : [];

        if (Math.abs(dx) >= 1 || Math.abs(dy) >= 1) {
            clauses.push(_stripClosingHierarchyClause(
                generateMoveAnnotation({ dx: dx, dy: dy, count: count, lang: lang }),
                lang
            ));
        }

        if (Math.abs(sx - 1) >= 0.01 || Math.abs(sy - 1) >= 0.01) {
            clauses.push(_stripClosingHierarchyClause(
                generateScaleAnnotation({ scaleX: sx, scaleY: sy, count: count, lang: lang }),
                lang
            ));
        }

        if (textHints.length) {
            clauses.push(textHints.map(function (hint) {
                return _normalizeHintText(hint, lang);
            }).filter(Boolean).join(lang === "zh" ? "；" : ". "));
        }

        var merged = _joinClauses(clauses, lang);
        if (!merged) return "";
        if (lang === "zh") {
            return merged + "。保持当前视觉层级。";
        }
        return merged + ". Preserve its visual hierarchy.";
    }

    function _issue(kind, message, suggestionEn, suggestionZh) {
        return {
            kind: kind,
            severity: "warning",
            message: message,
            suggestion_en: suggestionEn,
            suggestion_zh: suggestionZh
        };
    }

    function detectTextLayoutIssues(opts) {
        opts = opts || {};
        var issues = [];
        var fontSizePx = _num(opts.fontSizePx);
        var textLength = Math.max(0, _num(opts.textLength));
        var textBox = opts.textBox || null;
        var containerBox = opts.containerBox || null;
        var containerTolerance = _num(opts.containerTolerance || 2);

        if (fontSizePx > 0 && fontSizePx < 12) {
            issues.push(_issue(
                "font_too_small",
                "Font size appears too small for comfortable reading.",
                "This text appears too small for comfortable reading. Increase the font size while preserving the current hierarchy, then rebalance nearby spacing if needed.",
                "这段文字看起来过小，影响阅读。请在保持当前层级关系的前提下适当增大字号，必要时再微调周边间距。"
            ));
        }

        if (fontSizePx > 72) {
            issues.push(_issue(
                "font_too_large",
                "Font size appears oversized relative to common slide text usage.",
                "This text appears oversized relative to its container. Reduce the font size slightly or expand the title area while preserving hierarchy.",
                "这段文字看起来偏大。请在保持层级关系的前提下适当减小字号，或扩展标题区域。"
            ));
        }

        if (textBox && containerBox) {
            var overflowX = _num(textBox.width) > (_num(containerBox.width) + containerTolerance);
            var overflowY = _num(textBox.height) > (_num(containerBox.height) + containerTolerance);
            if (overflowX || overflowY) {
                issues.push(_issue(
                    "overflow",
                    "Text likely overflows its inferred container.",
                    "This text appears to overflow its container. Reflow the text first; if needed, allow one more line before shrinking the font.",
                    "这段文字看起来已超出容器。请先重新排布换行，必要时优先增加一行，再考虑缩小字号。"
                ));
            }

            if (fontSizePx > 24 && _num(textBox.height) > _num(containerBox.height) * 0.4) {
                issues.push(_issue(
                    "font_too_large",
                    "Text height dominates too much of its inferred container.",
                    "This text appears oversized relative to its container. Reduce the font size slightly or expand the title area while preserving hierarchy.",
                    "这段文字占据容器高度过多。请适当减小字号，或扩展标题区域，同时保持层级关系。"
                ));
            }

            if (fontSizePx >= 12 &&
                fontSizePx < 14 &&
                textLength > 40 &&
                _num(textBox.height) > _num(containerBox.height) * 0.7) {
                issues.push(_issue(
                    "font_too_small",
                    "Text may have been compressed too far to fit the container.",
                    "This text may have been compressed too far to fit the container. Increase readability first, then rebalance the surrounding layout.",
                    "这段文字可能为了塞进容器被压得过小。请优先恢复可读性，再重新平衡周边布局。"
                ));
            }
        }

        return issues;
    }

    return {
        generateMoveAnnotation: generateMoveAnnotation,
        generateScaleAnnotation: generateScaleAnnotation,
        generateMergedAnnotation: generateMergedAnnotation,
        detectTextLayoutIssues: detectTextLayoutIssues
    };
});
