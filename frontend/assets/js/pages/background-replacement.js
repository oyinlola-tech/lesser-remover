import { initToolPage, setupUpload, renderImageResult } from "./tool-kit.js";
import { apiUpload } from "../api.js";
import { showElement, hideElement } from "../utils.js";

const kit = await initToolPage("background-replacement");
if (!kit.available) {
    setupUpload({ onFiles: () => {} });
} else {
    let currentFile = null;
    let backgroundImageFile = null;
    setupUpload({
        onFiles: (files) => {
            currentFile = files[0];
        },
    });

    let backgroundType = "color";
    const typeSelect = document.querySelector("#background-type");
    typeSelect.addEventListener("change", () => {
        backgroundType = typeSelect.value;
        hideElement(document.querySelector("#background-color-field"));
        hideElement(document.querySelector("#background-image-field"));
        hideElement(document.querySelector("#background-blur-field"));
        if (backgroundType === "color") {
            showElement(document.querySelector("#background-color-field"));
        } else if (backgroundType === "image") {
            showElement(document.querySelector("#background-image-field"));
        } else {
            showElement(document.querySelector("#background-blur-field"));
        }
    });

    document
        .querySelector("#background-image")
        .addEventListener("change", (event) => {
            backgroundImageFile = event.target.files[0] || null;
        });

    const blurInput = document.querySelector("#background-blur");
    blurInput.addEventListener("input", () => {
        document.querySelector("#background-blur-value").textContent =
            blurInput.value;
    });

    document.querySelector("#tool-run").addEventListener("click", async () => {
        if (!currentFile) {
            kit.banner.show("Choose an image first.");
            return;
        }
        if (backgroundType === "image" && !backgroundImageFile) {
            kit.banner.show("Choose a background image.");
            return;
        }
        kit.banner.hide();
        const fields = {
            output_format: document.querySelector("#background-format").value,
            blur: backgroundType === "blur" ? blurInput.value : 0,
        };
        const files = [{ name: "file", file: currentFile }];
        if (backgroundType === "color") {
            fields.color = document.querySelector("#background-color").value;
        } else if (backgroundType === "image") {
            files.push({ name: "background_image", file: backgroundImageFile });
        }
        kit.setBusy(true, "Replacing background...");
        try {
            const data = await apiUpload("/background/replace", {
                files,
                fields,
            });
            kit.setBusy(false);
            renderImageResult(
                document.querySelector("#tool-results"),
                data.result,
                { originalSize: currentFile.size }
            );
        } catch (error) {
            kit.setBusy(false);
            kit.banner.show(error.message);
        }
    });
}
