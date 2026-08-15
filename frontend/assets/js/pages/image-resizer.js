import { initToolPage } from "./tool-kit.js";
import { apiUpload, apiGet } from "../api.js";
import { formatBytes } from "../utils.js";
import { UploadZone } from "../components/ui.js";

const kit = await initToolPage("image-resizer");

const DIMENSIONS_PRESETS = [
    { width: 1920, height: 1080, label: "1920 × 1080" },
    { width: 1600, height: 900, label: "1600 × 900" },
    { width: 1280, height: 720, label: "1280 × 720" },
    { width: 1080, height: 1080, label: "1080 × 1080" },
    { width: 1080, height: 1350, label: "1080 × 1350" },
    { width: 1080, height: 1920, label: "1080 × 1920" },
    { width: 1200, height: 630, label: "1200 × 630" },
];

const ASPECT_LOCKED_KEY = "aspect-locked";
const ASPECT_UNLOCKED_KEY = "aspect-unlocked";

let currentFiles = [];
let isAspectLocked = true;
let currentMode = "aspect";

function $(id) {
    return document.getElementById(id);
}

function setupModeButtons() {
    const buttons = document.querySelectorAll("#resize-mode button");
    buttons.forEach((button) => {
        button.addEventListener("click", () => {
            buttons.forEach((item) => item.classList.remove("active"));
            button.classList.add("active");
            currentMode = button.dataset.mode;
            updateModeFields();
        });
    });
}

function updateModeFields() {
    const modes = ["percent", "exact", "max", "aspect"];
    modes.forEach((mode) => {
        const el = $(`field-${mode}`);
        if (el) {
            el.classList.toggle("hidden", currentMode !== mode && mode !== "aspect");
        }
    });

    if (currentMode === "percent") {
        showField("field-percent");
        hideField("field-dimensions");
        hideField("field-max");
    } else if (currentMode === "exact") {
        showField("field-dimensions");
        hideField("field-percent");
        hideField("field-max");
    } else if (currentMode === "max") {
        showField("field-max");
        hideField("field-percent");
        hideField("field-dimensions");
    } else {
        showField("field-dimensions");
        hideField("field-percent");
        hideField("field-max");
    }

    updateQualityVisibility();
}

function showField(id) {
    const el = $(id);
    if (el) el.classList.remove("hidden");
}

function hideField(id) {
    const el = $(id);
    if (el) el.classList.add("hidden");
}

function updateQualityVisibility() {
    const format = $("resize-format").value;
    const qualityField = $("quality-field");
    if (qualityField) {
        qualityField.classList.toggle("hidden", format === "png");
    }
    updateBackgroundHint();
}

function updateBackgroundHint() {
    const format = $("resize-format").value;
    const hint = $("transparency-hint");
    const bgField = $("field-background");
    if (hint) {
        if (format === "jpg") {
            hint.textContent =
                "JPEG cannot preserve transparency. Transparent areas will be filled with the background color.";
        } else {
            hint.textContent =
                "Transparency is preserved for PNG and WebP output.";
        }
    }
    if (bgField) {
        bgField.classList.toggle("hidden", format !== "jpg" && format !== "jpeg");
    }
}

function setupDimensionInputs() {
    const widthInput = $("width-input");
    const heightInput = $("height-input");
    const lockButton = $("aspect-lock");

    widthInput.addEventListener("input", () => {
        if (isAspectLocked && currentMode === "aspect" && widthInput.value) {
            const w = parseInt(widthInput.value, 10);
            const ratio = originalRatio;
            if (ratio && !isNaN(w) && w > 0) {
                heightInput.value = Math.round(w / ratio);
            }
        }
    });

    heightInput.addEventListener("input", () => {
        if (isAspectLocked && currentMode === "aspect" && heightInput.value) {
            const h = parseInt(heightInput.value, 10);
            const ratio = originalRatio;
            if (ratio && !isNaN(h) && h > 0) {
                widthInput.value = Math.round(h * ratio);
            }
        }
    });

    lockButton.addEventListener("click", () => {
        isAspectLocked = !isAspectLocked;
        lockButton.setAttribute(
            "aria-label",
            isAspectLocked ? "Unlock aspect ratio" : "Lock aspect ratio",
        );
        const icon = lockButton.querySelector(".aspect-lock-icon");
        const text = lockButton.querySelector(".aspect-lock-text");
        if (icon) icon.textContent = isAspectLocked ? "🔗" : "🔓";
        if (text) text.textContent = isAspectLocked ? "Locked" : "Unlocked";
    });
}

function setupPresetButtons() {
    const standardContainer = $("standard-presets");
    if (standardContainer) {
        standardContainer.innerHTML = "";
        DIMENSIONS_PRESETS.forEach((preset) => {
            const button = document.createElement("button");
            button.type = "button";
            button.className = "preset-button";
            button.dataset.width = preset.width;
            button.dataset.height = preset.height;
            button.textContent = preset.label;
            button.addEventListener("click", () => {
                applyPreset(preset.width, preset.height);
            });
            standardContainer.appendChild(button);
        });
    }
}

async function loadSocialPresets() {
    const container = $("social-presets");
    if (!container) return;

    try {
        const data = await apiGet("/tools/image/social-presets");
        if (data.presets && data.presets.length) {
            container.innerHTML = "";
            data.presets.forEach((preset) => {
                const button = document.createElement("button");
                button.type = "button";
                button.className = "preset-button";
                button.dataset.width = preset.width;
                button.dataset.height = preset.height;
                button.textContent = `${preset.name} (${preset.width} × ${preset.height})`;
                button.title = preset.description;
                button.addEventListener("click", () => {
                    applyPreset(preset.width, preset.height);
                });
                container.appendChild(button);
            });
        }
    } catch (error) {
        container.innerHTML = '<span class="file-hint">Presets unavailable</span>';
    }
}

function applyPreset(width, height) {
    $("width-input").value = width;
    $("height-input").value = height;
    if (currentMode !== "exact") {
        const buttons = document.querySelectorAll("#resize-mode button");
        buttons.forEach((item) => item.classList.remove("active"));
        const exactButton = document.querySelector('#resize-mode button[data-mode="exact"]');
        exactButton.classList.add("active");
        exactButton.click();
    }
}

function updateOriginalRatio(file) {
    if (!file) {
        originalRatio = null;
        return;
    }
    const url = URL.createObjectURL(file);
    const img = new Image();
    img.onload = () => {
        originalRatio = img.naturalWidth / img.naturalHeight;
        URL.revokeObjectURL(url);
    };
    img.src = url;
}

let originalRatio = null;

function setupUpload() {
    const upload = new UploadZone(document.querySelector("#tool-upload"), {
        accept: "image/jpeg,image/png,image/webp,image/jpg",
        multiple: true,
        maxFiles: 50,
        maxSizeMb: 25,
        hint: "JPG, PNG, WebP up to 25 MB",
        onFiles: (files) => {
            currentFiles = files;
            kit.banner.hide();
            if (files.length === 1) {
                updateOriginalRatio(files[0]);
            } else {
                originalRatio = null;
            }
            updateFileSummary();
        },
    });
    return upload;
}

function updateFileSummary() {
    const upload = document.querySelector("#tool-upload");
    const hint = upload.querySelector(".file-hint");
    if (currentFiles.length === 0) {
        if (hint) hint.textContent = "JPG, PNG, WebP up to 25 MB";
    } else {
        if (hint) hint.textContent = `${currentFiles.length} image(s) ready`;
    }
}

async function handleResize() {
    if (!currentFiles.length) {
        kit.banner.show("Choose at least one image first.");
        return;
    }

    kit.banner.hide();

    const fields = {
        resize_mode: currentMode,
        maintain_aspect_ratio: document.querySelector("#maintain-aspect").checked,
        allow_upscale: document.querySelector("#allow-upscale").checked,
        output_format: $("resize-format").value,
        remove_metadata: document.querySelector("#remove-metadata").checked,
    };

    if (currentMode === "percent") {
        fields.percent = $("percent-input").value;
    } else if (currentMode === "exact" || currentMode === "aspect") {
        const w = $("width-input").value;
        const h = $("height-input").value;
        if (w) fields.width = w;
        if (h) fields.height = h;
        if (!w && !h) {
            kit.banner.show("Provide at least width or height.");
            return;
        }
    } else if (currentMode === "max") {
        const mw = $("max-width-input").value;
        const mh = $("max-height-input").value;
        if (mw) fields.max_width = mw;
        if (mh) fields.max_height = mh;
        if (!mw && !mh) {
            kit.banner.show("Provide at least a maximum width or height.");
            return;
        }
    }

    const format = fields.output_format;
    if (format !== "auto" && (format === "jpg" || format === "jpeg")) {
        fields.background_color = $("background-color").value || "#ffffff";
    } else {
        fields.background_color = $("background-color").value;
    }

    const quality = $("quality-input").value;
    if (quality && (format === "jpg" || format === "jpeg" || format === "webp" || format === "auto")) {
        fields.quality = quality;
    }

    kit.setBusy(true, `Resizing ${currentFiles.length} image(s)...`);

    try {
        const result = await apiUpload("/images/resize", {
            files: currentFiles.map((file) => ({ name: "files", file })),
            fields,
        });

        kit.setBusy(false);
        renderBatchResult(result);
    } catch (error) {
        kit.setBusy(false);
        kit.banner.show(error.message);
    }
}

function renderBatchResult(result) {
    const host = $("tool-results");
    host.innerHTML = "";

    if (result.successful_files === result.total_files && result.failed_files === 0) {
        const header = document.createElement("div");
        header.className = "result-header";
        header.innerHTML = `
            <h2>${result.successful_files} image(s) resized</h2>
            <div class="result-meta">${formatBytes(getTotalSize(result.results))}</div>
        `;
        host.appendChild(header);

        const grid = document.createElement("div");
        grid.className = "result-grid";

        result.results.forEach((item) => {
            const card = renderResizeResult(item);
            grid.appendChild(card);
        });
        host.appendChild(grid);

        const actions = document.createElement("div");
        actions.className = "result-actions";
        const again = document.createElement("button");
        again.type = "button";
        again.className = "secondary-button";
        again.textContent = "Resize another";
        again.addEventListener("click", () => {
            host.innerHTML = "";
            currentFiles = [];
            updateFileSummary();
            window.scrollTo({ top: 0, behavior: "smooth" });
        });
        actions.appendChild(again);
        host.appendChild(actions);
    } else {
        const header = document.createElement("div");
        header.className = "result-header";
        const statusText = `${result.successful_files} of ${result.total_files} images resized`;
        header.innerHTML = `
            <div>
                <h2>${statusText}</h2>
                ${result.failed_files > 0
                    ? `<p class="file-hint">${result.failed_files} image(s) could not be processed</p>`
                    : ""}
            </div>
        `;
        host.appendChild(header);

        if (result.results && result.results.length) {
            const grid = document.createElement("div");
            grid.className = "result-grid";
            result.results.forEach((item) => {
                const card = renderResizeResult(item);
                grid.appendChild(card);
            });
            host.appendChild(grid);
        }

        if (result.failures && result.failures.length) {
            const failSection = document.createElement("div");
            failSection.className = "failed-files";
            result.failures.forEach((failure) => {
                const failCard = document.createElement("div");
                failCard.className = "failed-file-item";
                failCard.textContent = `${failure.filename}: ${failure.error}`;
                failSection.appendChild(failCard);
            });
            host.appendChild(failSection);
        }

        const actions = document.createElement("div");
        actions.className = "result-actions";
        const again = document.createElement("button");
        again.type = "button";
        again.className = "secondary-button";
        again.textContent = "Try again";
        again.addEventListener("click", () => {
            host.innerHTML = "";
            window.scrollTo({ top: 0, behavior: "smooth" });
        });
        actions.appendChild(again);
        host.appendChild(actions);
    }

    kit.showResult();
}

function getTotalSize(results) {
    return results.reduce((sum, r) => sum + (r.size_bytes || 0), 0);
}

function renderResizeResult(item) {
    const card = document.createElement("div");
    card.className = "completed-file";

    const info = document.createElement("div");
    info.className = "completed-file-info";

    const name = document.createElement("strong");
    name.className = "completed-file-name";
    name.textContent = item.original_filename;
    name.title = item.original_filename;

    const meta = document.createElement("div");
    meta.className = "completed-file-meta";

    const origSize = item.original_size_bytes;
    const newSize = item.size_bytes;
    const sizeChanged = origSize !== newSize;
    const sizeText = document.createElement("div");
    sizeText.className = "completed-file-size";

    if (sizeChanged) {
        const direction = newSize > origSize
            ? "Size increased"
            : "Size reduced";
        sizeText.textContent = `${formatBytes(origSize)} → ${formatBytes(newSize)} (${direction})`;
    } else {
        sizeText.textContent = `${formatBytes(origSize)} (unchanged)`;
    }
    meta.appendChild(sizeText);

    const dimText = document.createElement("div");
    dimText.className = "completed-file-dimensions";
    dimText.textContent = `${item.original_width} × ${item.original_height} → ${item.width} × ${item.height}`;
    meta.appendChild(dimText);

    const fmtText = document.createElement("div");
    fmtText.className = "completed-file-format";
    fmtText.textContent = `${item.input_format} → ${item.output_format.toUpperCase()}`;
    if (item.details && item.details.flattened) {
        fmtText.textContent += " (transparency flattened)";
    }
    meta.appendChild(fmtText);

    info.appendChild(name);
    info.appendChild(meta);
    card.appendChild(info);

    const preview = document.createElement("div");
    preview.className = "completed-file-preview";
    const img = document.createElement("img");
    img.src = item.download_url;
    img.alt = item.original_filename;
    img.loading = "lazy";
    preview.appendChild(img);
    card.appendChild(preview);

    const download = document.createElement("a");
    download.className = "completed-file-download";
    download.href = item.download_url;
    download.download = item.output_filename;
    download.textContent = "Download";
    card.appendChild(download);

    return card;
}

function initPage() {
    kit.banner.hide();
    setupModeButtons();
    setupDimensionInputs();
    setupPresetButtons();
    loadSocialPresets();
    updateQualityVisibility();

    $("resize-format").addEventListener("change", updateQualityVisibility);

    $("tool-run").addEventListener("click", handleResize);
}

if (kit.available) {
    initPage();
}
