import { initToolPage, setupUpload, renderFileResult } from "./tool-kit.js";
import { apiUpload } from "../api.js";

const kit = await initToolPage("zip-creator");
if (!kit.available) {
    setupUpload({ onFiles: () => {} });
} else {
    let files = [];
    setupUpload({
        onFiles: (selected) => {
            files = selected;
        },
    });

    document.querySelector("#tool-run").addEventListener("click", async () => {
        if (!files.length) {
            kit.banner.show("Choose files to package.");
            return;
        }
        kit.banner.hide();
        kit.setBusy(true, "Creating ZIP archive...");
        try {
            const result = await apiUpload("/tools/file/zip", {
                files: files.map((file) => ({ name: "files", file })),
            });
            kit.setBusy(false);
            renderFileResult(document.querySelector("#tool-results"), result, {
                originalSize: files.reduce((sum, file) => sum + file.size, 0),
            });
        } catch (error) {
            kit.setBusy(false);
            kit.banner.show(error.message);
        }
    });
}
