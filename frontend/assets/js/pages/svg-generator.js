import { initToolPage, setupUpload, triggerDownload } from "./tool-kit.js";
import { apiDownload } from "../api.js";
import { formatBytes } from "../utils.js";

const kit = await initToolPage("svg-generator");
if (!kit.available) {
    setupUpload({ onFiles: () => {} });
} else {
    let currentFile = null;
    setupUpload({
        onFiles: (files) => {
            currentFile = files[0];
        },
    });

    const thresholdInput = document.getElementById("threshold-input");
    const thresholdSlider = document.getElementById("threshold-slider");
    [thresholdInput, thresholdSlider].forEach((el) => {
        el.addEventListener("input", () => {
            const val = Number(el.value);
            thresholdInput.value = val;
            thresholdSlider.value = val;
        });
    });

    let selectedBg = "white";
    let selectedFg = "black";
    let customBg = "";
    let customFg = "";

    document.querySelectorAll("#background-selector .format-option").forEach((btn) => {
        btn.addEventListener("click", () => {
            document.querySelectorAll("#background-selector .format-option")
                .forEach((b) => b.classList.remove("active"));
            btn.classList.add("active");
            selectedBg = btn.dataset.color;
            if (selectedBg === "transparent") {
                customBg = "transparent";
            }
            toggleCustomFields();
        });
    });

    document.querySelectorAll("#foreground-selector .format-option").forEach((btn) => {
        btn.addEventListener("click", () => {
            document.querySelectorAll("#foreground-selector .format-option")
                .forEach((b) => b.classList.remove("active"));
            btn.classList.add("active");
            selectedFg = btn.dataset.color;
            toggleCustomFields();
        });
    });

    function toggleCustomFields() {
        const bgField = document.getElementById("field-custom-bg");
        const fgField = document.getElementById("field-custom-fg");
        const isCustomBg = ["white", "black", "transparent"].includes(selectedBg) === false;
        const isCustomFg = ["black", "white"].includes(selectedFg) === false;
        bgField.classList.toggle("hidden", !isCustomBg);
        fgField.classList.toggle("hidden", !isCustomFg);
    }

    document.getElementById("background-color").addEventListener("input", (e) => {
        customBg = e.target.value.trim();
        if (customBg) selectedBg = customBg;
    });
    document.getElementById("foreground-color-input").addEventListener("input", (e) => {
        customFg = e.target.value.trim();
        if (customFg) selectedFg = customFg;
    });

    document.getElementById("tool-run").addEventListener("click", async () => {
        if (!currentFile) {
            kit.banner.show("Choose an image file.");
            return;
        }
        kit.banner.hide();
        kit.setBusy(true, "Generating SVG...");
        try {
            const { blob, filename, contentType } = await apiDownload(
                "/tools/dev/svg-generate",
                {
                    files: [{ name: "image", file: currentFile }],
                    fields: {
                        threshold: thresholdSlider.value,
                        background_color: selectedBg,
                        foreground_color: selectedFg,
                    },
                },
            );
            kit.setBusy(false);

            const host = document.querySelector("#tool-results");
            host.innerHTML = "";

            const preview = document.createElement("div");
            preview.className = "result-actions";
            const svgUrl = URL.createObjectURL(blob);
            const imgEl = document.createElement("img");
            imgEl.src = svgUrl;
            imgEl.style.maxWidth = "100%";
            imgEl.alt = "SVG preview";
            preview.appendChild(imgEl);
            setTimeout(() => URL.revokeObjectURL(svgUrl), 4000);

            const meta = document.createElement("p");
            meta.className = "file-hint";
            meta.textContent = `Generated ${formatBytes(blob.size)} SVG from ${formatBytes(currentFile.size)} image.`;

            const download = document.createElement("button");
            download.type = "button";
            download.className = "primary-button";
            download.textContent = "Download SVG";
            download.addEventListener("click", () => triggerDownload(blob, filename));

            host.appendChild(meta);
            host.appendChild(preview);
            host.appendChild(download);
            kit.showResult();
        } catch (error) {
            kit.setBusy(false);
            kit.banner.show(error.message);
        }
    });
}
