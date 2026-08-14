import { initToolPage, setupUpload } from "./tool-kit.js";
import { apiUpload } from "../api.js";
import { formatBytes, showElement } from "../utils.js";

const kit = await initToolPage("duplicate-finder");
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
            kit.banner.show("Choose files to compare.");
            return;
        }
        kit.banner.hide();
        kit.setBusy(true, "Hashing files...");
        try {
            const groups = await apiUpload("/tools/file/duplicates", {
                files: files.map((file) => ({ name: "files", file })),
            });
            kit.setBusy(false);
            const host = document.querySelector("#tool-results");
            host.innerHTML = "";
            if (!groups.length) {
                const none = document.createElement("p");
                none.className = "file-hint";
                none.textContent =
                    "No duplicates found - every file in this batch is unique.";
                host.appendChild(none);
                showElement(host);
                return;
            }
            for (const group of groups) {
                const wrapper = document.createElement("div");
                wrapper.className = "duplicate-group";
                const title = document.createElement("strong");
                title.textContent = `${group.filenames.length} identical copies (${formatBytes(group.size_bytes)} each)`;
                const list = document.createElement("ul");
                for (const name of group.filenames) {
                    const item = document.createElement("li");
                    item.textContent = name;
                    list.appendChild(item);
                }
                const hash = document.createElement("div");
                hash.className = "result-meta";
                hash.textContent = `SHA-256: ${group.hash.slice(0, 24)}…`;
                wrapper.appendChild(title);
                wrapper.appendChild(list);
                wrapper.appendChild(hash);
                host.appendChild(wrapper);
            }
            showElement(host);
        } catch (error) {
            kit.setBusy(false);
            kit.banner.show(error.message);
        }
    });
}
