import {
    CATEGORY_META,
    CATEGORY_ORDER,
    loadCapabilities,
    toolsByCategory,
} from "./capabilities.js";

function renderToolCard(tool) {
    if (tool.status === "available") {
        const card = document.createElement("a");
        card.className = "tool-card";
        card.href = `/tools/${tool.id}`;
        card.innerHTML = `
            <div class="tool-card-top">
                <span class="tool-card-icon" aria-hidden="true">${tool.name.charAt(0)}</span>
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
            <span class="tool-card-icon" aria-hidden="true">${tool.name.charAt(0)}</span>
        </div>
        <div>
            <span class="tool-card-label">${tool.category} tool</span>
            <h3>${tool.name}</h3>
            <p>${tool.description}</p>
        </div>
        <span class="tool-card-action">Coming soon</span>`;
    return card;
}

function renderCategory(category) {
    const meta = CATEGORY_META[category];
    if (!meta) {
        return "";
    }
    const tools = toolsByCategory(category);
    if (!tools.length) {
        return "";
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
    return section;
}

async function renderCatalog() {
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
    for (const category of CATEGORY_ORDER) {
        const section = renderCategory(category);
        if (section) {
            host.appendChild(section);
        }
    }
}

renderCatalog();
