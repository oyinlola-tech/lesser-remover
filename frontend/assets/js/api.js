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

export async function removeBackground(file) {
    const formData = new FormData();
    formData.append("file", file);
    const response = await fetch(
        `${API_BASE_URL}/background/remove`,
        {
            method: "POST",
            body: formData,
        }
    );
    const data = await parseJsonResponse(response);
    if (!response.ok) {
        throw new Error(
            data?.detail || "Unable to process image."
        );
    }
    return data;
}
export async function compressFile({
    file,
    imageOutputFormat = "webp",
    imageQuality = 85,
    pdfQuality = "ebook",
    targetSizeKb = null,
}) {
    const formData = new FormData();
    formData.append("file", file);
    const params = new URLSearchParams();
    params.set(
        "image_output_format",
        imageOutputFormat
    );
    params.set(
        "image_quality",
        String(imageQuality)
    );
    params.set(
        "pdf_quality",
        pdfQuality
    );
    if (
        targetSizeKb !== null &&
        targetSizeKb !== ""
    ) {
        params.set(
            "target_size_kb",
            String(targetSizeKb)
        );
    }
    const response = await fetch(
        `${API_BASE_URL}/compression?${params.toString()}`,
        {
            method: "POST",
            body: formData,
        }
    );
    const data = await parseJsonResponse(response);
    if (!response.ok) {
        throw new Error(
            data?.detail || "Unable to compress file."
        );
    }
    return data;
}
export async function compressFiles({
    files,
    imageOutputFormat = "webp",
    imageQuality = 85,
    pdfQuality = "ebook",
}) {
    const formData = new FormData();
    for (const file of files) {
        formData.append("files", file);
    }
    const params = new URLSearchParams();
    params.set(
        "image_output_format",
        imageOutputFormat
    );
    params.set(
        "image_quality",
        String(imageQuality)
    );
    params.set(
        "pdf_quality",
        pdfQuality
    );
    const response = await fetch(
        `${API_BASE_URL}/compression/batch?${params.toString()}`,
        {
            method: "POST",
            body: formData,
        }
    );
    const data = await parseJsonResponse(response);
    if (!response.ok) {
        throw new Error(
            data?.detail || "Unable to compress files."
        );
    }
    return data;
}
export async function cancelJob(jobId) {
    const response = await fetch(
        `/api/jobs/${jobId}`,
        {
            method: "DELETE",
        }
    );
    const data = await parseJsonResponse(response);
    if (!response.ok) {
        throw new Error(
            data?.detail || "Unable to cancel job."
        );
    }
    return data;
}
export async function getJob(jobId) {
    const response = await fetch(`/api/jobs/${jobId}`);
    const data = await parseJsonResponse(response);
    if (!response.ok) {
        throw new Error(data?.detail || "Unable to load job.");
    }
    return data;
}

export async function getJob(jobId) {
    const response = await fetch(`/api/jobs/${jobId}`);
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.detail || "Unable to fetch job.");
    }
    return data;
}
