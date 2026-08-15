import { initToolPage, setupUpload, renderFileResult, showResultBox } from "./tool-kit.js";
import { apiUpload } from "../api.js";
import { formatBytes } from "../utils.js";

const kit = await initToolPage("pdf-to-image");
if (!kit.available) {
    setupUpload({ onFiles: () => {} });
} else {
    let currentFile = null;
    setupUpload({
        onFiles: (files) => {
            currentFile = files[0];
        },
    });

    function renderPages(host, result) {
        host.innerHTML = "";
        const ext = result.image_format === "png" ? "PNG" : "JPG";
        const header = document.createElement("div");
        header.className = "result-header";
        header.innerHTML = `
            <h2>${result.page_count} page image${result.page_count === 1 ? "" : "s"} (${ext})</h2>
            <div class="result-meta">${result.dpi} DPI</div>
        `;
        host.appendChild(header);

        const grid = document.createElement("div");
        grid.className = "result-grid";
        result.pages.forEach((page) => {
            const card = document.createElement("div");
            card.className = "completed-file";

            const info = document.createElement("div");
            info.className = "completed-file-info";

            const name = document.createElement("strong");
            name.className = "completed-file-name";
            name.textContent = page.filename;
            name.title = page.filename;

            const meta = document.createElement("div");
            meta.className = "completed-file-meta";
            const sizeText = document.createElement("div");
            sizeText.className = "completed-file-size";
            sizeText.textContent = formatBytes(page.size_bytes);
            meta.appendChild(sizeText);
            const pageText = document.createElement("div");
            pageText.className = "completed-file-dimensions";
            pageText.textContent = `Page ${page.page}`;
            meta.appendChild(pageText);

            info.appendChild(name);
            info.appendChild(meta);
            card.appendChild(info);

            const preview = document.createElement("div");
            preview.className = "completed-file-preview";
            const img = document.createElement("img");
            img.src = page.download_url;
            img.alt = page.filename;
            img.loading = "lazy";
            preview.appendChild(img);
            card.appendChild(preview);

            const download = document.createElement("a");
            download.className = "completed-file-download";
            download.href = page.download_url;
            download.download = page.filename;
            download.textContent = "Download";
            card.appendChild(download);

            grid.appendChild(card);
        });
        host.appendChild(grid);
        showResultBox(host);
    }

    document.querySelector("#tool-run").addEventListener("click", async () => {
        if (!currentFile) {
            kit.banner.show("Choose a PDF file.");
            return;
        }
        kit.banner.hide();
        kit.setBusy(true, "Rasterizing PDF pages...");
        try {
            const result = await apiUpload("/tools/pdf/to-images", {
                files: [{ name: "file", file: currentFile }],
                fields: {
                    image_format: document.querySelector("#image-format").value,
                    dpi: document.querySelector("#dpi").value,
                    as_zip: document.querySelector("#as-zip").checked,
                },
            });
            kit.setBusy(false);
            const host = document.querySelector("#tool-results");
            if (result.as_zip) {
                const meta = document.createElement("p");
                meta.className = "file-hint";
                meta.textContent = `${result.details.page_count} page images at ${result.details.dpi} DPI inside the ZIP archive.`;
                host.innerHTML = "";
                host.appendChild(meta);
                renderFileResult(host, result, { originalSize: currentFile.size });
            } else {
                renderPages(host, result);
            }
        } catch (error) {
            kit.setBusy(false);
            kit.banner.show(error.message);
        }
    });
}
