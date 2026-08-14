import { initToolPage, setupUpload } from "./tool-kit.js";

const kit = await initToolPage("image-to-base64");
if (!kit.available) {
    setupUpload({ onFiles: () => {} });
} else {
    let currentBase64 = null;
    setupUpload({
        onFiles: (files) => {
            const file = files[0];
            kit.banner.hide();
            const reader = new FileReader();
            reader.onload = () => {
                currentBase64 = reader.result;
                renderOutput();
            };
            reader.onerror = () => {
                kit.banner.show("Unable to read the selected file.");
            };
            reader.readAsDataURL(file);
        },
    });

    function outputType() {
        return document.querySelector("#base64-type .active").dataset.type;
    }

    function renderOutput() {
        if (!currentBase64) {
            return;
        }
        const textarea = document.querySelector("#base64-output");
        if (outputType() === "raw") {
            textarea.value = currentBase64.split(",")[1] || "";
        } else {
            textarea.value = currentBase64;
        }
    }

    document.querySelectorAll("#base64-type button").forEach((button) => {
        button.addEventListener("click", () => {
            document
                .querySelectorAll("#base64-type button")
                .forEach((item) => item.classList.remove("active"));
            button.classList.add("active");
            renderOutput();
        });
    });

    document.querySelector("#base64-copy").addEventListener("click", async () => {
        const textarea = document.querySelector("#base64-output");
        if (!textarea.value) {
            kit.banner.show("Choose an image first.");
            return;
        }
        try {
            await navigator.clipboard.writeText(textarea.value);
            kit.banner.show("Copied to clipboard.");
        } catch {
            textarea.select();
            document.execCommand("copy");
            kit.banner.show("Copied to clipboard.");
        }
    });
}
