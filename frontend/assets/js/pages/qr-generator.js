import { initToolPage, triggerDownload } from "./tool-kit.js";
import { apiDownload } from "../api.js";

const kit = await initToolPage("qr-generator");
if (!kit.available) {
    document.querySelector("#tool-run").addEventListener("click", () => {});
} else {
    let logoFile = null;
    document.querySelector("#qr-logo").addEventListener("change", (event) => {
        logoFile = event.target.files[0] || null;
    });

    const sizeInput = document.querySelector("#qr-size");
    sizeInput.addEventListener("input", () => {
        document.querySelector("#qr-size-value").textContent =
            sizeInput.value >= 14 ? "Large" : sizeInput.value >= 8 ? "Medium" : "Small";
    });

    let previewUrl = null;
    async function run() {
        const content = document.querySelector("#qr-content").value.trim();
        if (!content) {
            kit.banner.show("Enter content for the QR code.");
            return;
        }
        kit.banner.hide();
        kit.setBusy(true, "Generating QR code...");
        try {
            const { blob, filename, contentType } = await apiDownload("/tools/dev/qr", {
                files: logoFile ? [{ name: "logo", file: logoFile }] : [],
                fields: {
                    content,
                    box_size: sizeInput.value,
                    fill_color: document.querySelector("#qr-fill").value,
                    back_color: document.querySelector("#qr-back").value,
                    output_format: document.querySelector("#qr-format").value,
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
            const img = document.createElement("img");
            img.src = previewUrl;
            img.alt = "QR code preview";
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
            preview.appendChild(img);
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
