import { initToolPage, setupUpload, renderImageResult } from "./tool-kit.js";
import { apiUpload } from "../api.js";
import { hideElement, showElement } from "../utils.js";

const kit = await initToolPage("image-resizer");
if (!kit.available) {
    setupUpload({ onFiles: () => {} });
} else {
    let currentFile = null;
    setupUpload({
        onFiles: (files) => {
            currentFile = files[0];
        },
    });

    let mode = "percent";
    const modeButtons = document.querySelectorAll("#resize-mode button");
    modeButtons.forEach((button) => {
        button.addEventListener("click", () => {
            modeButtons.forEach((item) => item.classList.remove("active"));
            button.classList.add("active");
            mode = button.dataset.mode;
            hideElement(document.querySelector("#field-percent"));
            hideElement(document.querySelector("#field-dimensions"));
            hideElement(document.querySelector("#field-height"));
            hideElement(document.querySelector("#field-max"));
            if (mode === "percent") {
                showElement(document.querySelector("#field-percent"));
            } else if (mode === "dimensions") {
                showElement(document.querySelector("#field-dimensions"));
                showElement(document.querySelector("#field-height"));
            } else {
                showElement(document.querySelector("#field-max"));
            }
        });
    });

    document.querySelector("#tool-run").addEventListener("click", async () => {
        if (!currentFile) {
            kit.banner.show("Choose an image first.");
            return;
        }
        kit.banner.hide();
        const fields = {
            output_format: document.querySelector("#resize-format").value,
        };
        if (mode === "percent") {
            fields.percent = document.querySelector("#percent").value;
        } else if (mode === "dimensions") {
            fields.width = document.querySelector("#width").value;
            fields.height = document.querySelector("#height").value;
        } else {
            fields.max_dimension = document.querySelector("#max-dimension").value;
        }
        kit.setBusy(true, "Resizing your image...");
        try {
            const result = await apiUpload("/tools/image/resize", {
                files: [{ name: "file", file: currentFile }],
                fields,
            });
            kit.setBusy(false);
            renderImageResult(document.querySelector("#tool-results"), result, {
                originalSize: currentFile.size,
            });
        } catch (error) {
            kit.setBusy(false);
            kit.banner.show(error.message);
        }
    });
}
