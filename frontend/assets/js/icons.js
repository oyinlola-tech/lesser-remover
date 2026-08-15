const FA_CSS = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css";

let injected = false;

export function injectIcons() {
    if (injected) {
        return;
    }
    const existing = document.querySelector('link[data-fa-icons]');
    if (existing) {
        injected = true;
        return;
    }
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = FA_CSS;
    link.setAttribute("data-fa-icons", "true");
    link.media = "print";
    link.onload = () => {
        link.media = "all";
    };
    document.head.appendChild(link);
    injected = true;
}

export function icon(name) {
    const span = document.createElement("span");
    span.className = `fa-solid fa-${name}`;
    span.setAttribute("aria-hidden", "true");
    return span;
}
