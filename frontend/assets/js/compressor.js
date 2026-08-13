import { compressFiles, cancelJob, getJob } from "./api.js";
import { hideElement, showElement, formatBytes } from "./utils.js";

const show = showElement;
const hide = hideElement;

const dropZone = document.querySelector(
    "#compressor-drop-zone"
);
const fileInput = document.querySelector(
    "#compressor-file-input"
);
const workspace = document.querySelector(
    "#compressor-workspace"
);
const fileQueue = document.querySelector("#file-queue");
const processing = document.querySelector(
    "#compression-processing"
);
const result = document.querySelector(
    "#compression-result"
);
const errorMessage = document.querySelector(
    "#compression-error"
);
const compressButton = document.querySelector(
    "#compress-button"
);
const clearFilesButton = document.querySelector(
    "#clear-files"
);
const qualityOptions = document.querySelectorAll(
    ".quality-option"
);
const outputFormat = document.querySelector(
    "#output-format"
);
const pdfQuality = document.querySelector(
    "#pdf-quality"
);
const originalSize = document.querySelector(
    "#original-size"
);
const compressedSize = document.querySelector(
    "#compressed-size"
);
const savingsPercent = document.querySelector(
    "#savings-percent"
);
const downloadButton = document.querySelector(
    "#compression-download"
);
const compressAnotherButton =
    document.querySelector(
        "#compress-another"
    );
const processingMessage =
    document.querySelector(
        "#processing-message"
    );
const processingProgress =
    document.querySelector(
        "#processing-progress"
    );
const processingCount =
    document.querySelector(
        "#processing-count"
    );
const cancelCompressionButton =
    document.querySelector(
        "#cancel-compression"
    );
const resultMeta =
    document.querySelector(
        "#compression-result-meta"
    );
const completedFiles = document.querySelector(
    "#completed-files"
);

let files = [];
let selectedQuality = 85;
let activeJobId = null;
let cancelling = false;

// use formatBytes, showElement, hideElement from utils

function isSupportedFile(file) {
    const isImage = file.type.startsWith("image/");
    const isPdf =
        file.type === "application/pdf" ||
        file.name.toLowerCase().endsWith(".pdf");
    return isImage || isPdf;
}

function isPdf(file) {
    return (
        file.type === "application/pdf" ||
        file.name.toLowerCase().endsWith(".pdf")
    );
}

function createFileId(file) {
    return [file.name, file.size, file.lastModified].join("-");
}

function escapeHtml(value) {
    return value
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

async function getImageDimensions(file) {
    if (!file.type.startsWith("image/")) {
        return null;
    }

    return new Promise((resolve) => {
        const url = URL.createObjectURL(file);

        const image = new Image();

        image.onload = () => {
            const dimensions = `${image.naturalWidth} × ${image.naturalHeight}`;

            URL.revokeObjectURL(url);

            resolve(dimensions);
        };

        image.onerror = () => {
            URL.revokeObjectURL(url);

            resolve(null);
        };

        image.src = url;
    });
}

async function addFiles(newFiles) {
    for (const file of newFiles) {
        if (!isSupportedFile(file)) {
            continue;
        }

        const id = createFileId(file);

        const alreadyExists = files.some((item) => item.id === id);

        if (alreadyExists) {
            continue;
        }

        let previewUrl = null;

        if (file.type.startsWith("image/")) {
            previewUrl = URL.createObjectURL(file);
        }

        const dimensions = await getImageDimensions(file);

        files.push({
            id,
            file,
            status: "waiting",
            result: null,
            previewUrl,
            dimensions,
        });
    }

    renderQueue();
}

function removeFile(id) {
    const item = files.find((file) => file.id === id);

    if (item?.previewUrl) {
        URL.revokeObjectURL(item.previewUrl);
    }

    files = files.filter((item) => item.id !== id);

    renderQueue();
}

function clearFiles() {
    for (const item of files) {
        if (item.previewUrl) {
            URL.revokeObjectURL(item.previewUrl);
        }
    }

    files = [];

    fileInput.value = "";

    hide(workspace);

    show(dropZone);
}

function renderQueue() {
    fileQueue.innerHTML = "";

    if (!files.length) {
        hide(workspace);
        show(dropZone);
        return;
    }

    hide(dropZone);
    show(workspace);

    for (const item of files) {
        const element = document.createElement("div");

        element.className = "file-queue-item";

        const pdf = isPdf(item.file);

        const statusClass = `status-${item.status}`;

        const preview = document.createElement("div");

        preview.className = "file-preview";

        if (!pdf && item.previewUrl) {
            const image = document.createElement("img");

            image.src = item.previewUrl;

            image.alt = "";

            preview.appendChild(image);
        } else {
            const pdfLabel = document.createElement("span");

            pdfLabel.className = "file-preview-pdf";

            pdfLabel.textContent = "PDF";

            preview.appendChild(pdfLabel);
        }

        const main = document.createElement("div");

        main.className = "file-queue-main";

        const details = document.createElement("div");

        details.className = "file-queue-details";

        const name = document.createElement("strong");

        name.className = "file-queue-name";

        name.textContent = item.file.name;

        name.title = item.file.name;

        const meta = document.createElement("div");

        meta.className = "file-queue-meta";

        const size = document.createElement("span");

        size.textContent = formatBytes(item.file.size);

        meta.appendChild(size);

        if (item.dimensions) {
            const dimensions = document.createElement("span");

            dimensions.textContent = item.dimensions;

            meta.appendChild(dimensions);
        }

        details.appendChild(name);
        details.appendChild(meta);

        main.appendChild(preview);
        main.appendChild(details);

        const status = document.createElement("span");

        status.className = `file-queue-status ${statusClass}`;

        status.textContent = getStatusLabel(item);

        const actions = document.createElement("div");

        actions.className = "file-queue-actions";

        if (item.status === "completed" && item.result?.download_url) {
            const download = document.createElement("a");

            download.className = "file-queue-download";

            download.href = item.result.download_url;

            download.download = item.result.output_filename;

            download.textContent = "Download";

            actions.appendChild(download);
        }

        if (item.status !== "processing") {
            const remove = document.createElement("button");

            remove.type = "button";

            remove.className = "file-queue-remove";

            remove.dataset.fileId = item.id;

            remove.setAttribute("aria-label", `Remove ${item.file.name}`);

            remove.textContent = "×";

            actions.appendChild(remove);
        }

        element.appendChild(main);
        element.appendChild(status);
        element.appendChild(actions);

        fileQueue.appendChild(element);
    }

    document.querySelectorAll(".file-queue-remove").forEach((button) => {
        button.addEventListener("click", () => {
            removeFile(button.dataset.fileId);
        });
    });
}

function getStatusLabel(item) {
    if (item.status === "waiting") {
        return "Ready";
    }

    if (item.status === "processing") {
        return "Compressing";
    }

    if (item.status === "completed") {
        if (item.result) {
            return `Saved ${item.result.savings_percent}%`;
        }

        return "Done";
    }

    if (item.status === "failed") {
        return "Failed";
    }

    return item.status;
}

function syncJobToFiles(job) {
    if (!job.files) {
        return;
    }

    for (const serverFile of job.files) {
        const localFile = files.find((item) => item.file.name === serverFile.filename);

        if (!localFile) {
            continue;
        }

        localFile.status = serverFile.status;

        if (serverFile.status === "completed") {
            localFile.result = {
                output_filename: serverFile.output_filename,
                download_url: serverFile.download_url,
                compressed_size_bytes: serverFile.compressed_size_bytes,
                original_size_bytes: serverFile.original_size_bytes,
                savings_percent: serverFile.savings_percent,
            };
        }

        if (serverFile.status === "failed") {
            localFile.result = {
                error: serverFile.error,
            };
        }
    }
}

function renderCompletedFiles(job) {
    if (!completedFiles) return;

    completedFiles.innerHTML = "";

    if (!job.files) return;

    for (const file of job.files) {
        if (file.status !== "completed") {
            continue;
        }

        const element = document.createElement("div");

        element.className = "completed-file";

        const info = document.createElement("div");

        info.className = "completed-file-info";

        const name = document.createElement("strong");

        name.className = "completed-file-name";

        name.textContent = file.filename;

        const meta = document.createElement("span");

        meta.className = "completed-file-meta";

        meta.textContent = `${formatBytes(file.original_size_bytes)} → ${formatBytes(file.compressed_size_bytes)} · Saved ${file.savings_percent}%`;

        info.appendChild(name);
        info.appendChild(meta);

        const download = document.createElement("a");

        download.className = "completed-file-download";

        download.href = file.download_url;

        download.download = file.output_filename;

        download.textContent = "Download";

        element.appendChild(info);

        element.appendChild(download);

        completedFiles.appendChild(element);
    }
}

qualityOptions.forEach((option) => {
    option.addEventListener("click", () => {
        qualityOptions.forEach((btn) => {
            btn.classList.remove("active");
        });
        option.classList.add("active");
        selectedQuality = Number(option.dataset.quality) || 85;
    });
});

fileInput.addEventListener("change", () => {
    addFiles(Array.from(fileInput.files || []));
    fileInput.value = "";
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
    addFiles(Array.from(event.dataTransfer.files));
});

clearFilesButton.addEventListener("click", clearFiles);

async function waitForJob(jobId) {
    while (true) {
        const job = await getJob(jobId);

        syncJobToFiles(job);

        updateProcessingUI(job);

        renderQueue();

        if (job.status === "completed") {
            renderCompletedFiles(job);
            return job;
        }

        if (job.status === "failed") {
            throw new Error("Compression failed.");
        }

        if (job.status === "cancelled") {
            throw new Error("Compression was cancelled.");
        }

        await new Promise((resolve) => setTimeout(resolve, 500));
    }
}

function updateProcessingUI(job) {
    const completed = job.completed_files || 0;
    const failed = job.failed_files || 0;
    const total = job.total_files || 0;
    const finished = completed + failed;
    const percentage = total > 0 ? (finished / total) * 100 : 0;

    processingProgress.style.width = `${percentage}%`;
    processingCount.textContent = `${finished} of ${total} completed`;

    const currentFile = job.files?.find(
        (file) => file.status === "processing"
    );
    if (currentFile) {
        processingMessage.textContent = `Compressing ${currentFile.filename}`;
    } else if (job.status === "completed") {
        processingMessage.textContent = "All files have been processed.";
    } else {
        processingMessage.textContent = "Preparing your files...";
    }
}

compressButton.addEventListener("click", async () => {
    if (!files.length || activeJobId) {
        return;
    }
    compressButton.disabled = true;
    hide(workspace);
    hide(result);
    hide(errorMessage);
    show(processing);

    processingProgress.style.width = "0%";
    processingCount.textContent = `0 of ${files.length} completed`;

    const abortController = new AbortController();

    try {
        const startResult = await compressFiles({
            files: files.map((item) => item.file),
            imageOutputFormat: outputFormat.value,
            imageQuality: selectedQuality,
            pdfQuality: pdfQuality.value,
        });

        activeJobId = startResult.job_id;
        cancelCompressionButton.disabled = false;
        cancelCompressionButton.textContent = "Cancel";

        const job = await waitForJob(
            startResult.job_id,
            abortController.signal
        );

        if (!job.download_url) {
            throw new Error(
                "No downloadable archive was created."
            );
        }

        originalSize.textContent = formatBytes(
            Number(job.original_size_bytes || 0)
        );
        compressedSize.textContent = formatBytes(
            Number(job.compressed_size_bytes || 0)
        );
        const savings =
            Number(job.original_size_bytes || 0) > 0
                ? (1 - (Number(job.compressed_size_bytes || 0) / Number(job.original_size_bytes || 1))) * 100
                : 0;
        savingsPercent.textContent = `${savings.toFixed(2)}%`;

        const failedCount = Number(job.failed_files || 0);
        if (failedCount > 0) {
            resultMeta.textContent = `${job.completed_files} completed · ${failedCount} failed`;
        } else {
            resultMeta.textContent = `${job.completed_files} files compressed`;
        }

        downloadButton.href = job.download_url;
        downloadButton.textContent = "Download all";

        hide(processing);
        show(result);
    } catch (error) {
        hide(processing);
        show(workspace);
        show(errorMessage);
        errorMessage.textContent =
            error.message || "Compression failed.";
    } finally {
        abortController.abort();
        activeJobId = null;
        cancelling = false;
        compressButton.disabled = false;
        cancelCompressionButton.disabled = false;
        cancelCompressionButton.textContent = "Cancel";
    }
});

cancelCompressionButton.addEventListener("click", async () => {
    if (!activeJobId || cancelling) {
        return;
    }
    cancelling = true;
    cancelCompressionButton.disabled = true;
    cancelCompressionButton.textContent = "Cancelling...";

    try {
        await cancelJob(activeJobId);
    } catch (error) {
        console.error(error);
    } finally {
        cancelling = false;
    }
});

compressAnotherButton.addEventListener("click", () => {
    clearFiles();
    hide(result);
    hide(errorMessage);
    show(dropZone);
});
