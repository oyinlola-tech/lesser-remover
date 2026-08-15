import { initToolPage, setupUpload, renderImageResult } from "./tool-kit.js";
import { apiUpload, apiGet } from "../api.js";

const kit = await initToolPage("social-media-resizer");
if (!kit.available) {
    setupUpload({ onFiles: () => {} });
} else {
    let presets = [];
    let selectedPreset = null;
    let currentFile = null;

    setupUpload({
        onFiles: (files) => {
            currentFile = files[0];
        },
    });

    async function loadPresets() {
        const select = document.querySelector("#preset-select");
        try {
            const data = await apiGet("/tools/image/social-presets");
            presets = data.presets || [];
            select.innerHTML = '<option value="">Select a platform preset…</option>';
            for (const preset of presets) {
                const option = document.createElement("option");
                option.value = String(presets.indexOf(preset));
                option.textContent = `${preset.name} (${preset.width}×${preset.height})`;
                option.title = preset.description;
                select.appendChild(option);
            }
            select.addEventListener("change", () => {
                const index = Number(select.value);
                selectedPreset = presets[index] || null;
            });
        } catch {
            select.innerHTML = '<option value="">Unable to load presets</option>';
        }
    }
    loadPresets();

    document.querySelector("#tool-run").addEventListener("click", async () => {
        if (!currentFile) {
            kit.banner.show("Choose an image first.");
            return;
        }
        if (!selectedPreset) {
            kit.banner.show("Choose a platform preset.");
            return;
        }
        kit.banner.hide();
        kit.setBusy(true, "Resizing for the selected preset...");
        try {
            const result = await apiUpload("/tools/image/resize", {
                files: [{ name: "file", file: currentFile }],
                fields: {
                    width: selectedPreset.width,
                    height: selectedPreset.height,
                    cover: true,
                    output_format: document.querySelector("#social-format").value,
                },
            });
            kit.setBusy(false);
            const meta = document.createElement("p");
            meta.className = "file-hint";
            meta.textContent = `${selectedPreset.name} · ${selectedPreset.width}×${selectedPreset.height}px`;
            const host = document.querySelector("#tool-results");
            host.innerHTML = "";
            host.appendChild(meta);
            renderImageResult(host, result, { originalSize: currentFile.size });
        } catch (error) {
            kit.setBusy(false);
            kit.banner.show(error.message);
        }
    });
}
