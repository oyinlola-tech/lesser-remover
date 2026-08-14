import { openSupport } from "./support-popup.js";
import {
    CATEGORY_META,
    CATEGORY_ORDER,
    loadCapabilities,
} from "./capabilities.js";

const GITHUB_URL = "https://github.com/oyinlola-tech/utils-tools";
const SITE_URL = "https://www.oyinlola.site/";

const STAR_ICON = `
<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round" aria-hidden="true">
  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26"></polygon>
</svg>`;

const HEART_ICON = `
<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
  <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
</svg>`;

function renderHeader() {
    return `
<header class="site-header">
  <div class="container header-inner">
    <a href="/" class="brand" aria-label="Utils-tool home">
      <img src="/static/assets/brand/logo.svg" alt="" width="32" height="32" style="display:block;" />
      <span>Utils-tool</span>
    </a>
    <nav class="header-nav" aria-label="Main navigation">
      <a href="/#tools">Tools</a>
      <a href="/#categories">Categories</a>
    </nav>
    <div class="header-actions">
      <a href="${GITHUB_URL}" target="_blank" rel="noopener noreferrer" class="header-star-button" aria-label="Star this project on GitHub">
        ${STAR_ICON}
        <span>Star</span>
      </a>
    </div>
  </div>
</header>`;
}

function renderFooter() {
    return `
<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand-section">
        <div class="footer-brand">
          <img src="/static/assets/brand/logo.svg" alt="" width="28" height="28" />
          <span>Utils-tool</span>
        </div>
        <p class="footer-tagline">
          Private by default. Fast, calm, and precise file tools that run in your browser.
        </p>
        <div class="footer-actions">
          <a href="${GITHUB_URL}" target="_blank" rel="noopener noreferrer" class="footer-star-button" aria-label="Star this project on GitHub">
            ${STAR_ICON}
            Star
          </a>
          <button type="button" class="footer-support-button" data-shell-support>Support this project</button>
        </div>
      </div>
      <div class="footer-links" data-footer-categories>
        <div class="footer-column">
          <h4 class="footer-heading">Product</h4>
          <a href="/#tools">All tools</a>
          <a href="/#categories">Categories</a>
        </div>
        <div class="footer-column">
          <h4 class="footer-heading">Connect</h4>
          <a href="${SITE_URL}" target="_blank" rel="noopener noreferrer">oyinlola.site</a>
          <a href="${GITHUB_URL}" target="_blank" rel="noopener noreferrer">GitHub</a>
        </div>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© <span data-shell-year>2026</span> Oluwayemi Oyinlola. All rights reserved.</span>
      <span class="footer-divider">·</span>
      <span>Built with care. Runs locally in your browser.</span>
    </div>
  </div>
</footer>
<button type="button" class="fab-support" data-shell-fab aria-label="Support this project">
  ${HEART_ICON}
</button>`;
}

export function renderShell() {
    const headerHost = document.querySelector("#site-header");
    const footerHost = document.querySelector("#site-footer");

    if (headerHost) {
        headerHost.innerHTML = renderHeader();
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

    const activeLink = footerHost
        ? footerHost.querySelector(".footer-star-button")
        : null;
    if (activeLink) {
        const toolId = document.body.dataset.toolId;
        const headerNav = headerHost ? headerHost.querySelector(".header-nav") : null;
        if (toolId && headerNav) {
            const toolsLink = headerNav.querySelector('a[href="/#tools"]');
            if (toolsLink) {
                toolsLink.setAttribute("href", "/tools");
            }
        }
    }
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
    const available = new Set(
        tools.filter((tool) => tool.status === "available").map((tool) => tool.id)
    );
    const columns = CATEGORY_ORDER.map((category) => {
        const meta = CATEGORY_META[category];
        if (!meta) {
            return "";
        }
        const links = tools
            .filter((tool) => tool.category === category)
            .map((tool) => {
                if (available.has(tool.id)) {
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
