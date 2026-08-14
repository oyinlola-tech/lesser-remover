import { initToolPage, setupUpload, renderFileResult } from "./tool-kit.js";
import { apiUpload } from "../api.js";

const kit = await initToolPage("pdf-to-image");
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
            kit.banner.show("Choose a PDF file.");
            return;
        }
        kit.banner.hide();
        kit.setBusy(true, "Rasterizing PDF pages...");
        try {
            const result = await apiUpload("/tools/pdf/to-images", {
                files: [{ name: "file", file: currentFile }],
                fields: {
                    image_format: document.querySelector("#image-format").value,
                    dpi: document.querySelector("#dpi").value,
                },
            });
            kit.setBusy(false);
            const meta = document.createElement("p");
            meta.className = "file-hint";
            meta.textContent = `${result.details.page_count} page images at ${result.details.dpi} DPI inside the ZIP archive.`;
            const host = document.querySelector("#tool-results");
            host.innerHTML = "";
            host.appendChild(meta);
            renderFileResult(host, result, { originalSize: currentFile.size });
        } catch (error) {
            kit.setBusy(false);
            kit.banner.show(error.message);
        }
    });
}
