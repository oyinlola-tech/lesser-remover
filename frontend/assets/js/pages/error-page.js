import { renderShell } from "../shell.js";

renderShell();

const detailHost = document.querySelector("#error-detail");
if (detailHost) {
    const params = new URLSearchParams(window.location.search);
    const detail =
        params.get("detail") ||
        sessionStorage.getItem("utils-error-detail") ||
        "";
    if (detail) {
        detailHost.textContent = detail;
        detailHost.style.display = "block";
        sessionStorage.removeItem("utils-error-detail");
    }
}
