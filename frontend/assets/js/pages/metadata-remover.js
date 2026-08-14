import { initToolPage, setupUpload, renderImageResult } from "./tool-kit.js";
import { apiUpload } from "../api.js";

const kit = await initToolPage("metadata-remover");
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
        kit.setBusy(true, "Stripping metadata...");
        try {
            const result = await apiUpload("/tools/image/remove-metadata", {
                files: [{ name: "file", file: currentFile }],
            });
            kit.setBusy(false);
            renderImageResult(document.querySelector("#tool-results"), result, {
                originalSize: currentFile.size,
            });
            const removed = result.details.removed_metadata || [];
            if (removed.length) {
                kit.banner.show(`Removed metadata fields: ${removed.join(", ")}.`);
            } else {
                kit.banner.show("No embedded metadata was found; the image was re-encoded cleanly.");
            }
        } catch (error) {
            kit.setBusy(false);
            kit.banner.show(error.message);
        }
    });
}
