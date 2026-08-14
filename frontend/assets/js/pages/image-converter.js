import { initToolPage, setupUpload, renderImageResult } from "./tool-kit.js";
import { apiUpload } from "../api.js";

const kit = await initToolPage("image-converter");
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
            kit.banner.show("Choose an image first.");
            return;
        }
        kit.banner.hide();
        kit.setBusy(true, "Converting your image...");
        try {
            const result = await apiUpload("/tools/image/convert", {
                files: [{ name: "file", file: currentFile }],
                fields: { output_format: document.querySelector("#format").value },
            });
            kit.setBusy(false);
            renderImageResult(document.querySelector("#tool-results"), result, {
                originalSize: currentFile.size,
            });
            if (result.details && result.details.flattened) {
                kit.banner.show("Note: the image had transparency, which was flattened onto a white background for JPG output.");
            }
        } catch (error) {
            kit.setBusy(false);
            kit.banner.show(error.message);
        }
    });
}
