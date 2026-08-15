import {
    CATEGORY_META,
    CATEGORY_ORDER,
    loadCapabilities,
    toolsByCategory,
} from "../capabilities.js";

function renderToolCard(tool) {
    const icon = tool.icon || tool.name.charAt(0);
    if (tool.status === "available") {
        const card = document.createElement("a");
        card.className = "tool-card";
        card.href = `/tools/${tool.id}`;
        card.innerHTML = `
            <div class="tool-card-top">
                <span class="tool-card-icon" aria-hidden="true">${icon}</span>
                <span class="tool-card-arrow" aria-hidden="true">↗</span>
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
    card.innerHTML = `
        <div class="tool-card-top">
            <span class="tool-card-icon" aria-hidden="true">${icon}</span>
        </div>
        <div>
            <span class="tool-card-label">${tool.category} tool</span>
            <h3>${tool.name}</h3>
            <p>${tool.description}</p>
        </div>
        <span class="tool-card-action">Coming soon</span>`;
    return card;
}

function renderCatalog() {
    const host = document.querySelector("#tool-catalog");
    if (!host) {
        return;
    }
    host.innerHTML = "";
    for (const category of CATEGORY_ORDER) {
        const meta = CATEGORY_META[category];
        if (!meta) {
            continue;
        }
        const tools = toolsByCategory(category);
        if (!tools.length) {
            continue;
        }
        const section = document.createElement("section");
        section.className = "catalog-category";
        section.id = `category-${category}`;

        const heading = document.createElement("div");
        heading.className = "catalog-category-heading";
        heading.innerHTML = `
            <h3>${meta.title}</h3>
            <p>${meta.description}</p>`;
        section.appendChild(heading);

        const grid = document.createElement("div");
        grid.className = "tool-grid catalog-grid";
        for (const tool of tools) {
            grid.appendChild(renderToolCard(tool));
        }
        section.appendChild(grid);
        host.appendChild(section);
    }
}

async function initToolsPage() {
    const host = document.querySelector("#tool-catalog");
    if (!host) {
        return;
    }
    try {
        await loadCapabilities();
    } catch (error) {
        host.innerHTML = `<p class="catalog-error" role="alert">
            Could not load the tool list. Start the local server and try again.
        </p>`;
        return;
    }
    renderCatalog();
}

initToolsPage();
