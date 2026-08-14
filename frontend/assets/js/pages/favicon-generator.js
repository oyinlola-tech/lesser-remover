import { initToolPage, setupUpload, triggerDownload } from "./tool-kit.js";
import { apiDownload } from "../api.js";

const kit = await initToolPage("favicon-generator");
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
        kit.setBusy(true, "Generating favicon set...");
        try {
            const { blob, filename } = await apiDownload("/tools/dev/favicon", {
                files: [{ name: "image", file: currentFile }],
                fields: {
                    size: document.querySelector("#favicon-size").value,
                    add_padding: document.querySelector("#favicon-padding").value,
                },
            });
            kit.setBusy(false);
            triggerDownload(blob, filename);
            const done = document.createElement("p");
            done.className = "file-hint";
            done.textContent =
                "Your favicon set (favicon.ico + PNG) has been downloaded.";
            const host = document.querySelector("#tool-results");
            host.innerHTML = "";
            host.appendChild(done);
            kit.showResult();
        } catch (error) {
            kit.setBusy(false);
            kit.banner.show(error.message);
        }
    });
}
