export function formatBytes(bytes) {
    if (bytes < 1024) {
        return `${bytes} B`;
    }
    if (bytes < 1024 * 1024) {
        return `${(bytes / 1024).toFixed(1)} KB`;
    }
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}
export function showElement(element) {
    if (!element) return;
    element.classList.remove("hidden");
}
export function hideElement(element) {
    if (!element) return;
    element.classList.add("hidden");
}
