import { initToolPage, setupUpload, renderFileResult } from "./tool-kit.js";
import { apiUpload } from "../api.js";

const kit = await initToolPage("pdf-rotator");
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
        kit.setBusy(true, "Rotating pages...");
        try {
            const result = await apiUpload("/tools/pdf/rotate", {
                files: [{ name: "file", file: currentFile }],
                fields: {
                    angle: document.querySelector("#angle").value,
                    pages: document.querySelector("#rotate-pages").value,
                },
            });
            kit.setBusy(false);
            renderFileResult(document.querySelector("#tool-results"), result, {
                originalSize: currentFile.size,
            });
        } catch (error) {
            kit.setBusy(false);
            kit.banner.show(error.message);
        }
    });
}
