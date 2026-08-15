import { formatBytes, showElement, hideElement } from "../utils.js";

const MIME_EXTENSION_MAP = {
    "image/": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif", ".bmp", ".svg", ".ico", ".tiff", ".tif"],
    "application/pdf": [".pdf"],
};


export class UploadZone {
    constructor(host, options = {}) {
        this.host = host;
        this.options = options;
        this.accept = options.accept || "";
        this.multiple = options.multiple !== false;
        this.maxFiles = options.maxFiles || 20;
        this.maxSizeMb = options.maxSizeMb || 100;
        this.onFiles = options.onFiles || (() => {});
        this.onError = options.onError || (() => {});
        this.hint = options.hint || "";
        this.buttonLabel = options.buttonLabel || "Choose file";
        this.title = options.title || (this.multiple ? "Drop your files here" : "Drop a file here");
        this.acceptList = this.accept
            .split(",")
            .map((item) => item.trim())
            .filter(Boolean);
        this.render();
        this.wire();
    }

    render() {
        const inputId = `file-input-${Math.random().toString(36).slice(2, 9)}`;
        this.host.innerHTML = `
            <div class="drop-zone" tabindex="0" role="button" aria-label="${this.multiple ? "Upload files" : "Upload a file"}">
                <div class="upload-icon" aria-hidden="true"><i class="fa-solid fa-cloud-arrow-up"></i></div>
                <h2>${this.title}</h2>
                <p>Or choose ${this.multiple ? "files" : "a file"} from your computer</p>
                <label for="${inputId}" class="primary-button">${this.buttonLabel}</label>
                <input id="${inputId}" type="file" ${this.accept ? `accept="${this.accept}"` : ""} ${this.multiple ? "multiple" : ""} class="visually-hidden" />
                ${this.hint ? `<p class="file-hint">${this.hint}</p>` : ""}
            </div>
            <div class="error-message hidden" role="alert"></div>`;
        this.dropZone = this.host.querySelector(".drop-zone");
        this.input = this.host.querySelector("input[type=file]");
        this.errorEl = this.host.querySelector(".error-message");
    }

    wire() {
        this.input.addEventListener("change", () => {
            const selected = Array.from(this.input.files || []);
            this.input.value = "";
            this.handleFiles(selected);
        });

        this.dropZone.addEventListener("dragover", (event) => {
            event.preventDefault();
            this.dropZone.classList.add("dragging");
        });

        this.dropZone.addEventListener("dragleave", () => {
            this.dropZone.classList.remove("dragging");
        });

        this.dropZone.addEventListener("drop", (event) => {
            event.preventDefault();
            this.dropZone.classList.remove("dragging");
            this.handleFiles(Array.from(event.dataTransfer.files || []));
        });

        this.dropZone.addEventListener("keydown", (event) => {
            if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                this.input.click();
            }
        });
    }

    handleFiles(files) {
        this.clearError();
        if (!files.length) {
            return;
        }
        if (!this.multiple) {
            files = files.slice(0, 1);
        }
        if (files.length > this.maxFiles) {
            this.showError(`You can upload a maximum of ${this.maxFiles} files at once.`);
            return;
        }
        const valid = [];
        const rejected = [];
        for (const file of files) {
            const error = this.validate(file);
            if (error) {
                rejected.push({ file, error });
            } else {
                valid.push(file);
            }
        }
        if (rejected.length) {
            const first = rejected[0];
            this.showError(`${first.file.name}: ${first.error}`);
            return;
        }
        this.onFiles(valid);
    }

    validate(file) {
        if (this.acceptList.length) {
            const allowedExt = [];
            const allowedMime = [];
            for (const entry of this.acceptList) {
                if (entry.startsWith(".")) {
                    allowedExt.push(entry.toLowerCase());
                } else if (entry.includes("/")) {
                    allowedMime.push(entry);
                }
            }
            const fileName = file.name.toLowerCase();
            const matchesExtension = allowedExt.some((ext) =>
                fileName.endsWith(ext)
            );
            const matchesMime = allowedMime.some((entry) => {
                if (entry.endsWith("/*")) {
                    return file.type.startsWith(entry.slice(0, -1));
                }
                return file.type === entry;
            });
            let matchesExtensionFallback = false;
            if (!file.type && !matchesExtension) {
                matchesExtensionFallback = allowedMime.some((entry) => {
                    const prefix = entry.endsWith("/*") ? entry.slice(0, -1) : entry;
                    const exts = MIME_EXTENSION_MAP[prefix];
                    if (exts) {
                        return exts.some((ext) => fileName.endsWith(ext));
                    }
                    return false;
                });
            }
            if (!matchesExtension && !matchesMime && !matchesExtensionFallback) {
                return "This file type is not supported.";
            }
        }
        if (file.size <= 0) {
            return "This file is empty.";
        }
        if (file.size > this.maxSizeMb * 1024 * 1024) {
            return `File is too large. Maximum size is ${this.maxSizeMb} MB.`;
        }
        return null;
    }

    showError(message) {
        this.errorEl.textContent = message;
        showElement(this.errorEl);
        this.onError(message);
    }

    clearError() {
        hideElement(this.errorEl);
    }
}


export class ProcessingPanel {
    constructor(host, options = {}) {
        this.host = host;
        this.title = options.title || "Processing your file";
        this.render();
        this.hide();
    }

    render() {
        this.host.innerHTML = `
            <div class="processing">
                <div class="processing-content">
                    <div class="spinner" role="status" aria-label="Processing"></div>
                    <h2>${this.title}</h2>
                    <p class="processing-message" role="status" aria-live="polite">Preparing your file...</p>
                    <div class="progress-bar" aria-hidden="true">
                        <div class="progress-bar-value progress-indeterminate"></div>
                    </div>
                </div>
            </div>`;
        this.message = this.host.querySelector(".processing-message");
    }

    setMessage(message) {
        if (this.message) {
            this.message.textContent = message;
        }
    }

    show() {
        showElement(this.host);
    }

    hide() {
        hideElement(this.host);
    }
}


export class ErrorBanner {
    constructor(host) {
        this.host = host;
        this.host.classList.add("error-message");
        this.host.setAttribute("role", "alert");
        hideElement(this.host);
    }

    show(message) {
        this.host.textContent = message;
        showElement(this.host);
    }

    hide() {
        hideElement(this.host);
    }
}


export function createDownloadCard({
    filename,
    originalSize,
    resultSize,
    downloadUrl,
    label,
}) {
    const element = document.createElement("div");
    element.className = "completed-file";

    const info = document.createElement("div");
    info.className = "completed-file-info";

    const name = document.createElement("strong");
    name.className = "completed-file-name";
    name.textContent = filename;
    name.title = filename;

    const meta = document.createElement("div");
    meta.className = "completed-file-meta";

    if (originalSize != null && resultSize != null) {
        const sizeText = document.createElement("div");
        sizeText.className = "completed-file-size";
        sizeText.textContent = `${formatBytes(originalSize)} → ${formatBytes(resultSize)}`;
        meta.appendChild(sizeText);
    }

    info.appendChild(name);
    info.appendChild(meta);
    element.appendChild(info);

    const download = document.createElement("a");
    download.className = "completed-file-download";
    download.href = downloadUrl;
    download.download = filename;
    download.textContent = label || "Download";
    element.appendChild(download);

    return element;
}
