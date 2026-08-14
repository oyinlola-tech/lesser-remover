import { initToolPage, triggerDownload } from "./tool-kit.js";

const kit = await initToolPage("base64-to-image");

function parseBase64(input) {
    let data = input.trim();
    if (!data) {
        throw new Error("Paste some Base64 data first.");
    }
    let mime = null;
    const dataUriMatch = data.match(/^data:([^;,]+);base64,(.+)$/s);
    if (dataUriMatch) {
        mime = dataUriMatch[1];
        data = dataUriMatch[2];
    }
    data = data.replace(/\s+/g, "");
    if (!/^[A-Za-z0-9+/=]+$/.test(data)) {
        throw new Error("This does not look like valid Base64 data.");
    }
    return { data, mime };
}

async function run() {
    const input = document.querySelector("#base64-input").value;
    kit.banner.hide();
    try {
        const { data, mime } = parseBase64(input);
        const binary = atob(data);
        const bytes = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) {
            bytes[i] = binary.charCodeAt(i);
        }
        let extension = "png";
        if (mime) {
            const match = mime.match(/^image\/(\w+)/);
            if (match) {
                extension = match[1] === "jpeg" ? "jpg" : match[1];
            }
        }
        const blob = new Blob([bytes], { type: mime || "image/png" });
        const url = URL.createObjectURL(blob);
        const host = document.querySelector("#tool-results");
        host.innerHTML = "";
        const preview = document.createElement("div");
        preview.className = "result-preview";
        const img = document.createElement("img");
        img.src = url;
        img.alt = "Decoded image";
        const name = document.createElement("div");
        name.className = "result-name";
        name.textContent = `decoded-image.${extension}`;
        const actions = document.createElement("div");
        actions.className = "result-actions";
        const download = document.createElement("button");
        download.type = "button";
        download.className = "primary-button";
        download.textContent = "Download";
        download.addEventListener("click", () =>
            triggerDownload(blob, `decoded-image.${extension}`)
        );
        actions.appendChild(download);
        preview.appendChild(img);
        preview.appendChild(name);
        preview.appendChild(actions);
        host.appendChild(preview);
        kit.showResult();
    } catch (error) {
        kit.banner.show(error.message);
    }
}

document.querySelector("#base64-decode").addEventListener("click", run);
