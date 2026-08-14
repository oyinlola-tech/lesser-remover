import { initToolPage, setupUpload, triggerDownload } from "./tool-kit.js";
import { apiDownload } from "../api.js";
import { formatBytes } from "../utils.js";

const kit = await initToolPage("svg-optimizer");
if (!kit.available) {
    setupUpload({ onFiles: () => {} });
} else {
    let currentFile = null;
    setupUpload({
        onFiles: (files) => {
            currentFile = files[0];
        },
    });

    document.querySelector("#tool-run").addEventListener("click", async () => {
        if (!currentFile) {
            kit.banner.show("Choose an SVG file.");
            return;
        }
        kit.banner.hide();
        kit.setBusy(true, "Optimizing SVG...");
        try {
            const { blob, filename } = await apiDownload("/tools/dev/svg-optimize", {
                files: [{ name: "file", file: currentFile }],
                fields: {
                    precision: document.querySelector("#precision").value,
                },
            });
            kit.setBusy(false);
            const saved = Math.max(0, currentFile.size - blob.size);
            const percent = currentFile.size
                ? Math.round((saved / currentFile.size) * 100)
                : 0;
            const host = document.querySelector("#tool-results");
            host.innerHTML = "";
            const meta = document.createElement("p");
            meta.className = "file-hint";
            meta.textContent = `Reduced from ${formatBytes(currentFile.size)} to ${formatBytes(blob.size)} (${percent}% saved).`;
            const actions = document.createElement("div");
            actions.className = "result-actions";
            const download = document.createElement("button");
            download.type = "button";
            download.className = "primary-button";
            download.textContent = "Download optimized SVG";
            download.addEventListener("click", () => triggerDownload(blob, filename));
            actions.appendChild(download);
            host.appendChild(meta);
            host.appendChild(actions);
            kit.showResult();
        } catch (error) {
            kit.setBusy(false);
            kit.banner.show(error.message);
        }
    });
}
