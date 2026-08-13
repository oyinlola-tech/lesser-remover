const API_BASE_URL = "/api";

async function parseJsonResponse(response) {
    const text = await response.text();
    if (!text) {
        return null;
    }
    try {
        return JSON.parse(text);
    } catch {
        return null;
    }
}

async function safeFetch(url, options = {}) {
    const controller = new AbortController();
    const timeout = options.timeout || 0;
    let timeoutId;
    if (timeout > 0) {
        timeoutId = setTimeout(() => controller.abort(), timeout);
    }
    try {
        const response = await fetch(url, {
            ...options,
            signal: controller.signal,
        });
        return response;
    } catch (error) {
        if (error.name === "AbortError") {
            throw new Error("Request timed out. Please check your connection and try again.");
        }
        if (!navigator.onLine) {
            throw new Error("You appear to be offline. Please check your internet connection.");
        }
        throw new Error("Network error. Please try again.");
    } finally {
        if (timeoutId) clearTimeout(timeoutId);
    }
}

export async function startBackgroundRemoval(file, outputFormat = "webp") {
    const formData = new FormData();
    formData.append("file", file);

    const params = new URLSearchParams();
    params.set("output_format", outputFormat);

    const response = await safeFetch(
        `${API_BASE_URL}/background/start?${params.toString()}`,
        {
            method: "POST",
            body: formData,
        }
    );

    const data = await parseJsonResponse(response);
    if (!response.ok) {
        throw new Error(data?.detail || "Unable to process image.");
    }
    return data;
}

export async function startBatchCompression({
    files,
    imageOutputFormat = "webp",
    compressionPreset = "balanced",
    maxDimension = null,
    targetSizeKb = null,
    stripMetadata = true,
}) {
    const formData = new FormData();
    for (const file of files) {
        formData.append("files", file);
    }

    const params = new URLSearchParams();
    params.set("image_output_format", imageOutputFormat);
    params.set("compression_preset", compressionPreset);

    if (maxDimension !== null && maxDimension !== "") {
        params.set("max_dimension", String(maxDimension));
    }

    if (targetSizeKb !== null && targetSizeKb !== "") {
        params.set("target_size_kb", String(targetSizeKb));
    }

    params.set("strip_metadata", String(stripMetadata));

    const response = await safeFetch(
        `${API_BASE_URL}/compression/batch/start?${params.toString()}`,
        {
            method: "POST",
            body: formData,
        }
    );

    const data = await parseJsonResponse(response);
    if (!response.ok) {
        throw new Error(data?.detail || "Unable to compress files.");
    }
    return data;
}

export async function cancelJob(jobId) {
    const response = await safeFetch(`/api/jobs/${jobId}`, {
        method: "DELETE",
    });
    const data = await parseJsonResponse(response);
    if (!response.ok) {
        throw new Error(data?.detail || "Unable to cancel job.");
    }
    return data;
}

export async function getJob(jobId) {
    const response = await safeFetch(`/api/jobs/${jobId}`);
    const data = await parseJsonResponse(response);
    if (!response.ok) {
        throw new Error(data?.detail || "Unable to load job.");
    }
    return data;
}
