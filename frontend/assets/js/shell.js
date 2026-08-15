import { openSupport } from "./support-popup.js";
import { injectIcons, iconHtml } from "./icons.js";
import {
    CATEGORY_ORDER,
    loadCapabilities,
    toolsByCategory,
} from "./capabilities.js";

const GITHUB_URL = "https://github.com/oyinlola-tech/utils-tools";
const SITE_URL = "https://tools.oyinlola.site/";

const STAR_ICON = iconHtml("github");
const HEART_ICON = iconHtml("heart");

const NAV_ITEMS = [
    { href: "/tools", label: "Tools" },
    { href: "/about", label: "About" },
    { href: "/#how-it-works", label: "How it works" },
    { href: "/#faq", label: "FAQ" },
];

function renderHeader() {
    const links = NAV_ITEMS.map(
        (item) =>
            `<a href="${item.href}" class="nav-link" data-shell-nav-link>${item.label}</a>`
    ).join("");
    const mobileLinks = NAV_ITEMS.map(
        (item) =>
            `<a href="${item.href}" class="mobile-nav-link" data-shell-nav-link>${item.label}</a>`
    ).join("");

    return `
<header class="site-header" data-shell-header role="banner">
  <div class="container header-inner">
    <a href="/" class="brand" aria-label="Utils-tool — home">
      <img src="/static/assets/brand/logo.svg" alt="" width="32" height="32" loading="eager" decoding="async" />
      <span>Utils-tool</span>
    </a>
    <nav class="header-nav" aria-label="Main navigation">
      ${links}
    </nav>
    <div class="header-actions">
      <a href="${GITHUB_URL}" target="_blank" rel="noopener noreferrer" class="header-star-button" aria-label="View and star this project on GitHub">
        ${STAR_ICON}
        <span>Star</span>
      </a>
      <button type="button" class="header-menu-toggle" data-shell-menu-toggle aria-label="Open menu" aria-expanded="false" aria-controls="mobile-nav">
        ${iconHtml("bars")}
      </button>
    </div>
  </div>
  <nav id="mobile-nav" class="mobile-nav" aria-label="Mobile navigation" hidden>
    <div class="container mobile-nav-inner">
      ${mobileLinks}
      <div class="mobile-nav-actions">
        <a href="${GITHUB_URL}" target="_blank" rel="noopener noreferrer" class="header-star-button">
          ${STAR_ICON}
          <span>Star on GitHub</span>
        </a>
      </div>
    </div>
  </nav>
</header>`;
}

function renderFooter() {
    return `
<footer class="site-footer" data-shell-footer role="contentinfo">
  <div class="container">
    <div class="footer-top">
      <div class="footer-brand-section">
        <a href="/" class="footer-brand" aria-label="Utils-tool — home">
          <img src="/static/assets/brand/logo.svg" alt="" width="28" height="28" loading="lazy" decoding="async" />
          <span>Utils-tool</span>
        </a>
        <p class="footer-tagline">
          Private by default. Fast, calm, and precise file tools.
        </p>
        <div class="footer-actions">
          <a href="${GITHUB_URL}" target="_blank" rel="noopener noreferrer" class="footer-star-button" aria-label="View and star this project on GitHub">
            ${STAR_ICON}
            <span>Star</span>
          </a>
          <button type="button" class="footer-support-button" data-shell-support>Support this project</button>
        </div>
      </div>
      <div class="footer-columns" data-footer-categories>
        <div class="footer-column">
          <h4 class="footer-heading">Product</h4>
          <a href="/tools">All tools</a>
          <a href="/about">About</a>
          <a href="/#how-it-works">How it works</a>
          <a href="/#faq">FAQ</a>
        </div>
        <div class="footer-column" data-footer-popular>
          <h4 class="footer-heading">Popular tools</h4>
        </div>
        <div class="footer-column">
          <h4 class="footer-heading">Connect</h4>
          <a href="${SITE_URL}" target="_blank" rel="noopener noreferrer">oyinlola.site</a>
          <a href="${GITHUB_URL}" target="_blank" rel="noopener noreferrer">GitHub</a>
        </div>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© <span data-shell-year>2026</span> Oluwayemi Oyinlola.</span>
      <span class="footer-meta">
        <span>Open source</span>
        <span class="footer-divider">·</span>
        <span>Local-first</span>
        <span class="footer-divider">·</span>
        <span>No tracking</span>
      </span>
    </div>
  </div>
</footer>
<button type="button" class="fab-support" data-shell-fab aria-label="Support this project">
  ${HEART_ICON}
</button>`;
}

function currentPath() {
    const path = window.location.pathname;
    if (path === "/about") {
        return "/about";
    }
    if (path === "/tools" || path.startsWith("/tools/")) {
        return "/tools";
    }
    return "/";
}

function markCurrentNav() {
    const current = currentPath();
    document.querySelectorAll("[data-shell-nav-link]").forEach((link) => {
        const href = link.getAttribute("href").split("#")[0];
        if (href && href === current) {
            link.setAttribute("aria-current", "page");
        } else {
            link.removeAttribute("aria-current");
        }
    });
}

function setupMobileMenu() {
    const toggle = document.querySelector("[data-shell-menu-toggle]");
    const panel = document.querySelector("#mobile-nav");
    if (!toggle || !panel) {
        return;
    }

    const setOpen = (open) => {
        panel.hidden = !open;
        panel.classList.toggle("is-open", open);
        toggle.setAttribute("aria-expanded", String(open));
        toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
        toggle.innerHTML = iconHtml(open ? "xmark" : "bars");
    };

    toggle.addEventListener("click", () => {
        const open = toggle.getAttribute("aria-expanded") !== "true";
        setOpen(open);
        if (open) {
            const first = panel.querySelector(".mobile-nav-link");
            if (first) {
                first.focus();
            }
        } else {
            toggle.focus();
        }
    });

    panel.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            setOpen(false);
            toggle.focus();
        }
    });

    panel.querySelectorAll("a").forEach((link) => {
        link.addEventListener("click", () => setOpen(false));
    });

    document.addEventListener("click", (event) => {
        const inHeader = event.target.closest(".site-header");
        if (!inHeader && toggle.getAttribute("aria-expanded") === "true") {
            setOpen(false);
        }
    });

    window.addEventListener("resize", () => {
        if (window.innerWidth > 700) {
            setOpen(false);
        }
    });
}

async function renderFooterPopular() {
    const host = document.querySelector("[data-footer-popular]");
    if (!host) {
        return;
    }
    let tools;
    try {
        const data = await loadCapabilities();
        tools = data.tools;
    } catch (error) {
        return;
    }
    const popular = [];
    for (const category of CATEGORY_ORDER) {
        const tool = toolsByCategory(category).find(
            (item) => item.status === "available" && item.featured
        );
        if (tool) {
            popular.push(tool);
        }
    }
    for (const tool of popular.slice(0, 4)) {
        const link = document.createElement("a");
        link.href = `/tools/${tool.id}`;
        link.textContent = tool.name;
        host.appendChild(link);
    }
}

export function renderShell() {
    injectIcons();

    const headerHost = document.querySelector("#site-header");
    const footerHost = document.querySelector("#site-footer");

    if (headerHost) {
        headerHost.innerHTML = renderHeader();
        const headerHeight = headerHost.querySelector(".site-header");
        if (headerHeight) {
            document.documentElement.style.setProperty(
                "--header-height",
                `${headerHeight.offsetHeight}px`
            );
        }
    }
    if (footerHost) {
        footerHost.innerHTML = renderFooter();
        const year = footerHost.querySelector("[data-shell-year]");
        if (year) {
            year.textContent = String(new Date().getFullYear());
        }
        renderFooterPopular();
    }

    const main = document.querySelector("main");
    if (main && !main.id) {
        main.id = "main";
    }

    const skipLink = document.createElement("a");
    skipLink.className = "skip-link";
    skipLink.href = "#main";
    skipLink.textContent = "Skip to content";
    document.body.prepend(skipLink);

    markCurrentNav();
    setupMobileMenu();

    document.querySelectorAll("[data-shell-fab], [data-shell-support]").forEach((button) => {
        button.addEventListener("click", () => openSupport());
    });
}
