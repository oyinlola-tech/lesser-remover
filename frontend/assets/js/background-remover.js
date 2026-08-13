import { startBackgroundRemoval } from "./api.js";
import { hideElement, showElement, formatBytes } from "./utils.js";
import { registerUse } from "./support-popup.js";

const dropZone = document.querySelector("#bg-drop-zone");
const fileInput = document.querySelector("#bg-file-input");
const processing = document.querySelector("#bg-processing");
const result = document.querySelector("#bg-result");
const errorMessage = document.querySelector("#bg-error-message");
const originalPreview = document.querySelector("#original-preview");
const processedPreview = document.querySelector("#processed-preview");
const processedPreviewContainer = document.querySelector("#processed-preview-container");
const comparisonDivider = document.querySelector("#comparison-divider");
const comparisonSlider = document.querySelector("#comparison-slider");
const resultMeta = document.querySelector("#bg-result-meta");
const variantGrid = document.querySelector("#bg-variant-grid");
const newImageButton = document.querySelector("#bg-new-image-button");
const outputOptions = document.querySelectorAll(".output-option");

let originalObjectUrl = null;
let selectedOutputFormat = "webp";

outputOptions.forEach((option) => {
    option.addEventListener("click", () => {
        outputOptions.forEach((other) => {
            other.classList.remove("active");
        });
        option.classList.add("active");
        selectedOutputFormat = option.dataset.format || "webp";
    });
});

function resetUI() {
    hideElement(processing);
    hideElement(result);
    hideElement(errorMessage);
    const badge = document.querySelector("#bg-success-badge");
    if (badge) hideElement(badge);
    dropZone.classList.remove("hidden");
    if (originalObjectUrl) {
        URL.revokeObjectURL(originalObjectUrl);
        originalObjectUrl = null;
    }
    originalPreview.removeAttribute("src");
    processedPreview.removeAttribute("src");
    resultMeta.textContent = "";
    variantGrid.innerHTML = "";
    fileInput.value = "";
}

function showError(message) {
    hideElement(processing);
    hideElement(result);
    dropZone.classList.remove("hidden");
    errorMessage.textContent = message;
    showElement(errorMessage);
}

function showResult(data) {
    hideElement(dropZone);
    hideElement(processing);
    hideElement(errorMessage);

    resultMeta.textContent = `${data.width} × ${data.height} · ${data.format.toUpperCase()}`;
    processedPreview.src = data.download_url;
    processedPreview.alt = `Processed image (${data.format})`;

    variantGrid.innerHTML = "";
    const card = document.createElement("div");
    card.className = "variant";
    card.innerHTML = `
        <h3>${String(data.format).toUpperCase()}</h3>
        <div class="variant-size">${formatBytes(Number(data.size_bytes || 0))}</div>
        <p class="variant-description">Transparent background, original resolution.</p>
        <a class="primary-button" href="${data.download_url}" download="${data.filename}">Download ${String(data.format).toUpperCase()}</a>
    `;
    variantGrid.appendChild(card);

    comparisonSlider.value = 50;
    updateComparison(50);

    showElement(result);
    const badge = document.querySelector("#bg-success-badge");
    if (badge) showElement(badge);
    
    result.style.animation = "none";
    result.offsetHeight;
    result.style.animation = "fadeIn 400ms ease-out";
    
    try {
        registerUse();
    } catch (e) {
        // ignore popup errors
    }
}

async function processFile(file) {
    if (!file) {
        return;
    }
    if (!file.type || !file.type.startsWith("image/")) {
        showError("Please choose a valid image file.");
        return;
    }

    hideElement(dropZone);
    hideElement(result);
    hideElement(errorMessage);
    showElement(processing);

    try {
        if (originalObjectUrl) {
            URL.revokeObjectURL(originalObjectUrl);
        }
        originalObjectUrl = URL.createObjectURL(file);
        originalPreview.src = originalObjectUrl;
        originalPreview.alt = file.name || "Original image";

        const data = await startBackgroundRemoval(file, selectedOutputFormat);
        showResult(data.result);
    } catch (error) {
        showError(error.message || "Something went wrong while processing the image.");
    }
}

fileInput.addEventListener("change", () => {
    const file = fileInput.files?.[0];
    processFile(file);
});

dropZone.addEventListener("dragover", (event) => {
    event.preventDefault();
    dropZone.classList.add("dragging");
});

dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("dragging");
});

dropZone.addEventListener("drop", (event) => {
    event.preventDefault();
    dropZone.classList.remove("dragging");
    const file = event.dataTransfer.files?.[0];
    processFile(file);
});

newImageButton.addEventListener("click", resetUI);

function updateComparison(value) {
    const percentage = Number(value);
    processedPreviewContainer.style.clipPath = `inset(0 0 0 ${percentage}%)`;
    comparisonDivider.style.left = `${percentage}%`;
}

comparisonSlider.addEventListener("input", () => {
    updateComparison(comparisonSlider.value);
});

updateComparison(50);

window.addEventListener("beforeunload", () => {
    if (originalObjectUrl) {
        try {
            URL.revokeObjectURL(originalObjectUrl);
        } catch (e) {}
        originalObjectUrl = null;
    }
});
