import { initToolPage, setupUpload, renderFileResult } from "./tool-kit.js";
import { apiUpload } from "../api.js";

const kit = await initToolPage("image-to-pdf");
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
            kit.banner.show("Choose at least one image.");
            return;
        }
        kit.banner.hide();
        kit.setBusy(true, "Creating PDF from images...");
        try {
            const result = await apiUpload("/tools/pdf/from-images", {
                files: files.map((file) => ({ name: "files", file })),
            });
            kit.setBusy(false);
            const meta = document.createElement("p");
            meta.className = "file-hint";
            meta.textContent = `${result.details.page_count} page PDF created.`;
            const host = document.querySelector("#tool-results");
            host.innerHTML = "";
            host.appendChild(meta);
            renderFileResult(host, result, {
                originalSize: files.reduce((sum, file) => sum + file.size, 0),
            });
        } catch (error) {
            kit.setBusy(false);
            kit.banner.show(error.message);
        }
    });
}
