import { initToolPage, triggerDownload } from "./tool-kit.js";
import { apiDownload } from "../api.js";

const kit = await initToolPage("barcode-generator");
if (!kit.available) {
    document.querySelector("#tool-run").addEventListener("click", () => {});
} else {
    let previewUrl = null;
    async function run() {
        const content = document.querySelector("#barcode-content").value.trim();
        if (!content) {
            kit.banner.show("Enter content for the barcode.");
            return;
        }
        kit.banner.hide();
        kit.setBusy(true, "Generating barcode...");
        try {
            const { blob, filename } = await apiDownload("/tools/dev/barcode", {
                fields: {
                    content,
                    code_type: document.querySelector("#barcode-type").value,
                    output_format: document.querySelector("#barcode-format").value,
                },
            });
            kit.setBusy(false);
            const host = document.querySelector("#tool-results");
            host.innerHTML = "";
            const preview = document.createElement("div");
            preview.className = "result-preview";
            if (previewUrl) {
                URL.revokeObjectURL(previewUrl);
            }
            previewUrl = URL.createObjectURL(blob);
            const viewer = document.createElement("div");
            viewer.className = "result-viewer";
            const img = document.createElement("img");
            img.src = previewUrl;
            img.alt = "Barcode preview";
            viewer.appendChild(img);
            const name = document.createElement("div");
            name.className = "result-name";
            name.textContent = filename;
            const actions = document.createElement("div");
            actions.className = "result-actions";
            const download = document.createElement("button");
            download.type = "button";
            download.className = "primary-button";
            download.textContent = "Download";
            download.addEventListener("click", () => triggerDownload(blob, filename));
            actions.appendChild(download);
            const again = document.createElement("button");
            again.type = "button";
            again.className = "secondary-button";
            again.textContent = "Generate again";
            again.addEventListener("click", run);
            actions.appendChild(again);
            preview.appendChild(viewer);
            preview.appendChild(name);
            preview.appendChild(actions);
            host.appendChild(preview);
            kit.showResult();
        } catch (error) {
            kit.setBusy(false);
            kit.banner.show(error.message);
        }
    }

    document.querySelector("#tool-run").addEventListener("click", run);
}
