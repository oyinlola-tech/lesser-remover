import { removeBackground } from "./api.js";
import { hideElement, showElement, formatBytes } from "./utils.js";
const dropZone = document.querySelector("#bg-drop-zone");
const fileInput = document.querySelector("#bg-file-input");
const processing = document.querySelector("#bg-processing");
const result = document.querySelector("#bg-result");
const errorMessage = document.querySelector("#bg-error-message");
const previewImage = document.querySelector("#bg-preview-image");
const resultMeta = document.querySelector("#bg-result-meta");
const variantGrid = document.querySelector("#bg-variant-grid");
const newImageButton =
    document.querySelector("#bg-new-image-button");
function resetUI() {
    hideElement(processing);
    hideElement(result);
    hideElement(errorMessage);
    dropZone.classList.remove("hidden");
    previewImage.removeAttribute("src");
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
function escapeAttribute(value) {
    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/"/g, "&quot;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
}

function createVariantCard(variant) {
    const card = document.createElement("div");
    card.className = "variant";

    const title = document.createElement("h3");
    title.textContent = String(variant.format).toUpperCase();

    const size = document.createElement("div");
    size.className = "variant-size";
    size.textContent = formatBytes(Number(variant.size_bytes || 0));

    const link = document.createElement("a");
    link.className = "primary-button";
    link.href = String(variant.download_url || "#");
    link.download = String(variant.filename || "download");
    link.textContent = `Download ${String(variant.format).toUpperCase()}`;

    card.append(title, size, link);
    return card;
}
function showResult(data) {
    hideElement(dropZone);
    hideElement(processing);
    hideElement(errorMessage);
    resultMeta.textContent =
        `${data.width} × ${data.height} · ` +
        `${data.variants.length} formats available`;
    variantGrid.innerHTML = "";
    for (const variant of data.variants) {
        variantGrid.appendChild(
            createVariantCard(variant)
        );
    }
    const webpVariant = data.variants.find(
        (variant) =>
            variant.format.toLowerCase() === "webp"
    );
    if (webpVariant) {
        previewImage.src =
            webpVariant.download_url;
    } else {
        previewImage.src =
            data.variants[0].download_url;
    }
    showElement(result);
}
async function processFile(file) {
    if (!file) {
        return;
    }
    if (!file || !file.type || !file.type.startsWith("image/")) {
        showError(
            "Please choose a valid image file."
        );
        return;
    }
    hideElement(dropZone);
    hideElement(result);
    hideElement(errorMessage);
    showElement(processing);
    try {
        const data = await removeBackground(file);
        showResult(data);
    } catch (error) {
        showError(
            error.message ||
            "Something went wrong while processing the image."
        );
    }
}
fileInput.addEventListener(
    "change",
    () => {
        const file = fileInput.files?.[0];
        processFile(file);
    }
);
dropZone.addEventListener(
    "dragover",
    (event) => {
        event.preventDefault();
        dropZone.classList.add("dragging");
    }
);
dropZone.addEventListener(
    "dragleave",
    () => {
        dropZone.classList.remove("dragging");
    }
);
dropZone.addEventListener(
    "drop",
    (event) => {
        event.preventDefault();
        dropZone.classList.remove("dragging");
        const file =
            event.dataTransfer.files?.[0];
        processFile(file);
    }
);
newImageButton.addEventListener(
    "click",
    resetUI
);
