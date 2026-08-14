import { getCapabilities } from "./api.js";

let cachePromise = null;
let cache = null;

export async function loadCapabilities() {
    if (cache) {
        return cache;
    }
    if (!cachePromise) {
        cachePromise = getCapabilities()
            .then((data) => {
                cache = data;
                return data;
            })
            .catch((error) => {
                cachePromise = null;
                throw error;
            });
    }
    return cachePromise;
}

export function getTool(toolId) {
    if (!cache) {
        return null;
    }
    return cache.tools.find((tool) => tool.id === toolId) || null;
}

export function isAvailable(toolId) {
    const tool = getTool(toolId);
    return Boolean(tool && tool.status === "available");
}

export function availableTools() {
    if (!cache) {
        return [];
    }
    return cache.tools.filter((tool) => tool.status === "available");
}

export function toolsByCategory(category) {
    if (!cache) {
        return [];
    }
    return cache.tools.filter((tool) => tool.category === category);
}

export function getAppInfo() {
    return cache ? cache.app : null;
}
