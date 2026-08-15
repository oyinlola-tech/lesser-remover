import {
    CATEGORY_META,
    CATEGORY_ORDER,
    loadCapabilities,
    toolsByCategory,
} from "./capabilities.js";
import { toolIconHtml, iconHtml } from "./icons.js";

function renderToolCard(tool) {
    if (tool.status === "available") {
        const card = document.createElement("a");
        card.className = "tool-card";
        card.href = `/tools/${tool.id}`;
        card.innerHTML = `
            <div class="tool-card-top">
                <span class="tool-card-icon" aria-hidden="true">${toolIconHtml(tool.id)}</span>
                <span class="tool-card-arrow" aria-hidden="true">${iconHtml("arrow-right")}</span>
            </div>
            <div>
                <span class="tool-card-label">${tool.category} tool</span>
                <h3>${tool.name}</h3>
                <p>${tool.description}</p>
            </div>
            <span class="tool-card-action">Open tool</span>`;
        return card;
    }

    const card = document.createElement("div");
    card.className = "tool-card tool-card-planned";
    const actionLabel =
        tool.status === "planned"
            ? "Coming soon"
            : "Unavailable in this environment";
    card.innerHTML = `
        <div class="tool-card-top">
            <span class="tool-card-icon" aria-hidden="true">${toolIconHtml(tool.id)}</span>
        </div>
        <div>
            <span class="tool-card-label">${tool.category} tool</span>
            <h3>${tool.name}</h3>
            <p>${tool.description}</p>
        </div>
        <span class="tool-card-action">${actionLabel}</span>`;
    return card;
}

function renderFeaturedTools() {
    const host = document.querySelector("#featured-tools");
    if (!host) {
        return;
    }
    host.innerHTML = "";
    const available = [];
    for (const category of CATEGORY_ORDER) {
        const tools = toolsByCategory(category).filter(
            (tool) => tool.featured && tool.status === "available"
        );
        for (const tool of tools) {
            available.push(tool);
        }
    }
    if (!available.length) {
        host.innerHTML = `<p class="catalog-loading">No featured tools available.</p>`;
        return;
    }
    for (const tool of available) {
        host.appendChild(renderToolCard(tool));
    }
}

async function initLanding() {
    const featuredHost = document.querySelector("#featured-tools");
    try {
        await loadCapabilities();
    } catch (error) {
        if (featuredHost) {
            featuredHost.innerHTML = `<p class="catalog-error" role="alert">
                Could not load the tool list. Start the local server and try again.
            </p>`;
        }
        return;
    }
    renderFeaturedTools();
}

initLanding();
