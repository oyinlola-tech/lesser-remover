import { openSupport } from "./support-popup.js";
import { injectIcons } from "./icons.js";
import {
    CATEGORY_META,
    CATEGORY_ORDER,
    loadCapabilities,
} from "./capabilities.js";

const GITHUB_URL = "https://github.com/oyinlola-tech/utils-tools";
const SITE_URL = "https://tools.oyinlola.site/";

const STAR_ICON = '<i class="fa-brands fa-github" aria-hidden="true"></i>';
const HEART_ICON = '<i class="fa-solid fa-heart" aria-hidden="true"></i>';

function renderHeader() {
    return `
<header class="site-header" data-shell-header role="banner">
  <div class="container header-inner">
    <a href="/" class="brand" aria-label="Utils-tool — home">
      <img src="/static/assets/brand/logo.svg" alt="" width="32" height="32" style="display:block;" />
      <span>Utils-tool</span>
    </a>
    <nav class="header-nav" aria-label="Main navigation">
      <a href="/tools" class="nav-link">Tools</a>
      <a href="/about" class="nav-link">About</a>
      <a href="/#how-it-works" class="nav-link">How it works</a>
      <a href="/#faq" class="nav-link">FAQ</a>
    </nav>
    <div class="header-actions">
      <a href="${GITHUB_URL}" target="_blank" rel="noopener noreferrer" class="header-star-button" aria-label="View and star this project on GitHub">
        ${STAR_ICON}
        <span>Star</span>
      </a>
    </div>
  </div>
</header>`;
}

function renderFooter() {
    return `
<footer class="site-footer" data-shell-footer role="contentinfo">
  <div class="container footer-inner">
    <div class="footer-brand-section">
      <a href="/" class="footer-brand" aria-label="Utils-tool — home">
        <img src="/static/assets/brand/logo.svg" alt="" width="28" height="28" />
        <span>Utils-tool</span>
      </a>
      <p class="footer-tagline">
        Private by default. Fast, calm, and precise file tools.
      </p>
      <div class="footer-actions">
        <a href="${GITHUB_URL}" target="_blank" rel="noopener noreferrer" class="footer-star-button" aria-label="View and star this project on GitHub">
          ${STAR_ICON}
          Star
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
      <div class="footer-column">
        <h4 class="footer-heading">Connect</h4>
        <a href="${SITE_URL}" target="_blank" rel="noopener noreferrer">oyinlola.site</a>
        <a href="${GITHUB_URL}" target="_blank" rel="noopener noreferrer">GitHub</a>
      </div>
    </div>
  </div>
  <div class="footer-bottom">
    <span>© <span data-shell-year>2026</span> Oluwayemi Oyinlola.</span>
    <span class="footer-divider">·</span>
    <span>Open source · Local-first</span>
  </div>
</footer>
<button type="button" class="fab-support" data-shell-fab aria-label="Support this project">
  ${HEART_ICON}
</button>`;
}

export function renderShell() {
    injectIcons();

    const headerHost = document.querySelector("#site-header");
    const footerHost = document.querySelector("#site-footer");

    if (headerHost) {
        headerHost.innerHTML = renderHeader();
        const headerHeight = headerHost.querySelector(".site-header");
        if (headerHeight) {
            document.documentElement.style.setProperty("--header-height", `${headerHeight.offsetHeight}px`);
        }
    }
    if (footerHost) {
        footerHost.innerHTML = renderFooter();
        const year = footerHost.querySelector("[data-shell-year]");
        if (year) {
            year.textContent = String(new Date().getFullYear());
        }
        renderFooterCategories(footerHost);
    }

    document.querySelectorAll("[data-shell-fab], [data-shell-support]").forEach((button) => {
        button.addEventListener("click", () => openSupport());
    });
}

async function renderFooterCategories(footerHost) {
    const host = footerHost.querySelector("[data-footer-categories]");
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

    const columns = CATEGORY_ORDER.map((category) => {
        const meta = CATEGORY_META[category];
        if (!meta) {
            return "";
        }
        const links = tools
            .filter((tool) => tool.category === category)
            .map((tool) => {
                if (tool.status === "available") {
                    return `<a href="/tools/${tool.id}">${tool.name}</a>`;
                }
                return `<a href="/tools/${tool.id}" aria-disabled="true">${tool.name}</a>`;
            })
            .join("");
        if (!links) {
            return "";
        }
        return `
            <div class="footer-column">
                <h4 class="footer-heading">${meta.title}</h4>
                ${links}
            </div>`;
    }).join("");
    host.insertAdjacentHTML("afterbegin", columns);
}
