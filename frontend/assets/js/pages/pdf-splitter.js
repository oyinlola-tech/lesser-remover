import { initToolPage, setupUpload, renderFileResult } from "./tool-kit.js";
import { apiUpload } from "../api.js";

const kit = await initToolPage("pdf-splitter");
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
        kit.setBusy(true, "Splitting PDF into pages...");
        try {
            const result = await apiUpload("/tools/pdf/split", {
                files: [{ name: "file", file: currentFile }],
            });
            kit.setBusy(false);
            const meta = document.createElement("p");
            meta.className = "file-hint";
            meta.textContent = `${result.details.page_count} single-page PDFs inside the ZIP archive.`;
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
