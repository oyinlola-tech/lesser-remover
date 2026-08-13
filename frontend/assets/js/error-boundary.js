const ERROR_STATE = {
    boundary: null,
    init() {
        this.boundary = document.querySelector("#js-error-boundary");
        if (!this.boundary) {
            this.boundary = document.createElement("div");
            this.boundary.id = "js-error-boundary";
            this.boundary.style.cssText = "display:none;position:fixed;inset:0;z-index:9999;background:#f7f7f2;padding:24px;overflow:auto;";
            document.body.appendChild(this.boundary);
        }
        window.addEventListener("error", (event) => {
            this.show(event.message || "Unexpected error", event.filename, event.lineno);
        }, true);
        window.addEventListener("unhandledrejection", (event) => {
            const reason = event.reason?.message || event.reason || "Promise rejected";
            this.show(reason, "", 0);
        });
    },
    show(message, file = "", line = 0) {
        if (!this.boundary) return;
        const fileInfo = file ? `<div style="margin-top:8px;color:#55634f;font-size:14px;">${this.escape(file)}${line ? `:${line}` : ""}</div>` : "";
        this.boundary.innerHTML = `
            <div style="max-width:560px;margin:80px auto;text-align:center;">
                <div style="font-size:48px;margin-bottom:16px;">⚠️</div>
                <h1 style="font-size:24px;margin:0 0 12px;letter-spacing:-0.03em;">Something went wrong</h1>
                <p style="color:#55634f;margin:0 0 24px;">The app hit an unexpected error. You can try refreshing the page.</p>
                <div style="background:#fff;border:1px solid #deded6;border-radius:12px;padding:16px;text-align:left;font-family:monospace;font-size:13px;word-break:break-word;">${this.escape(message)}${fileInfo}</div>
                <button onclick="location.reload()" style="margin-top:24px;padding:12px 24px;border-radius:999px;background:#9fe870;color:#163300;font-weight:800;border:0;cursor:pointer;">Refresh page</button>
            </div>
        `;
        this.boundary.style.display = "block";
        document.querySelectorAll(".site-header, main, footer").forEach((el) => { el.style.display = "none"; });
    },
    escape(value) {
        return String(value).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    }
};

ERROR_STATE.init();
