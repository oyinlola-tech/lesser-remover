import { initToolPage, setupUpload, triggerDownload } from "./tool-kit.js";

const kit = await initToolPage("image-cropper");
if (!kit.available) {
    setupUpload({ onFiles: () => {} });
} else {
    const MAX_PREVIEW = 900;
    let source = null; 
    let rotation = 0;
    let flipH = false;
    let flipV = false;
    let ratio = 0; 
    let crop = null; 
    let dragging = null;

    const frame = document.querySelector("#crop-canvas-frame");
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
    frame.appendChild(canvas);

    function transformedSize() {
        let w = source.width;
        let h = source.height;
        if (rotation % 180 !== 0) {
            [w, h] = [h, w];
        }
        return { w, h };
    }

    function previewScale() {
        const { w, h } = transformedSize();
        return Math.min(MAX_PREVIEW / w, MAX_PREVIEW / h, 1);
    }

    function drawTransformed() {
        const { w, h } = transformedSize();
        const scale = previewScale();
        canvas.width = Math.round(w * scale);
        canvas.height = Math.round(h * scale);
        ctx.save();
        ctx.fillStyle = "#ffffff";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.translate(canvas.width / 2, canvas.height / 2);
        if (flipH) {
            ctx.scale(-1, 1);
        }
        if (flipV) {
            ctx.scale(1, -1);
        }
        ctx.rotate((rotation * Math.PI) / 180);
        ctx.drawImage(
            source,
            -w / 2 * (flipH ? 1 : 1),
            -h / 2 * (flipV ? 1 : 1),
            w,
            h
        );
        ctx.restore();
    }

    function initCrop() {
        const pad = Math.round(canvas.width * 0.05);
        crop = {
            x: pad,
            y: pad,
            w: canvas.width - pad * 2,
            h: canvas.height - pad * 2,
        };
        applyRatio();
    }

    function applyRatio() {
        if (!crop) {
            return;
        }
        if (ratio > 0) {
            const target = crop.w / crop.h;
            if (target > ratio) {
                crop.w = crop.h * ratio;
            } else {
                crop.h = crop.w / ratio;
            }
            crop.x = Math.max(0, (canvas.width - crop.w) / 2);
            crop.y = Math.max(0, (canvas.height - crop.h) / 2);
        }
    }

    function drawCropOverlay() {
        drawTransformed();
        if (!crop) {
            return;
        }
        ctx.save();
        ctx.fillStyle = "rgba(0, 0, 0, 0.45)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.clearRect(crop.x, crop.y, crop.w, crop.h);
        ctx.strokeStyle = "#9fe870";
        ctx.lineWidth = 2;
        ctx.strokeRect(crop.x, crop.y, crop.w, crop.h);
        ctx.fillStyle = "#163300";
        ctx.fillRect(crop.x + crop.w - 8, crop.y + crop.h - 8, 16, 16);
        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 2;
        ctx.strokeRect(crop.x + crop.w - 8, crop.y + crop.h - 8, 16, 16);
        ctx.restore();
    }

    function canvasPoint(event) {
        const rect = canvas.getBoundingClientRect();
        return {
            x: ((event.clientX - rect.left) * canvas.width) / rect.width,
            y: ((event.clientY - rect.top) * canvas.height) / rect.height,
        };
    }

    canvas.addEventListener("pointerdown", (event) => {
        if (!crop) {
            return;
        }
        const point = canvasPoint(event);
        const handleSize = 24;
        if (
            point.x >= crop.x + crop.w - handleSize &&
            point.y >= crop.y + crop.h - handleSize
        ) {
            dragging = "resize";
        } else if (
            point.x >= crop.x &&
            point.x <= crop.x + crop.w &&
            point.y >= crop.y &&
            point.y <= crop.y + crop.h
        ) {
            dragging = "move";
            dragging = {
                type: "move",
                offsetX: point.x - crop.x,
                offsetY: point.y - crop.y,
            };
        } else {
            dragging = null;
        }
        canvas.setPointerCapture(event.pointerId);
    });

    canvas.addEventListener("pointermove", (event) => {
        if (!crop || !dragging) {
            return;
        }
        const point = canvasPoint(event);
        if (dragging === "resize") {
            let w = point.x - crop.x;
            let h = point.y - crop.y;
            if (ratio > 0) {
                if (w / ratio >= h) {
                    h = w / ratio;
                } else {
                    w = h * ratio;
                }
            }
            crop.w = Math.max(24, Math.min(w, canvas.width - crop.x));
            if (ratio > 0) {
                crop.h = crop.w / ratio;
                if (crop.y + crop.h > canvas.height) {
                    crop.h = Math.max(24, canvas.height - crop.y);
                    crop.w = crop.h * ratio;
                }
            } else {
                crop.h = Math.max(24, Math.min(h, canvas.height - crop.y));
            }
        } else if (dragging.type === "move") {
            crop.x = Math.min(
                Math.max(0, point.x - dragging.offsetX),
                canvas.width - crop.w
            );
            crop.y = Math.min(
                Math.max(0, point.y - dragging.offsetY),
                canvas.height - crop.h
            );
        }
        drawCropOverlay();
    });

    canvas.addEventListener("pointerup", () => {
        dragging = null;
    });

    const ratioSelect = document.querySelector("#crop-ratio");
    if (ratioSelect) {
        ratioSelect.addEventListener("change", () => {
            const value = ratioSelect.value;
            if (value === "free") {
                ratio = 0;
            } else {
                const [rw, rh] = value.split(":").map(Number);
                ratio = rw / rh;
            }
            if (crop) {
                applyRatio();
                drawCropOverlay();
            }
        });
    }

    function reflow() {
        initCrop();
        drawCropOverlay();
    }

    document.querySelector("#rotate-left").addEventListener("click", () => {
        rotation = (rotation - 90 + 360) % 360;
        reflow();
    });
    document.querySelector("#rotate-right").addEventListener("click", () => {
        rotation = (rotation + 90) % 360;
        reflow();
    });
    document.querySelector("#flip-h").addEventListener("click", () => {
        flipH = !flipH;
        reflow();
    });
    document.querySelector("#flip-v").addEventListener("click", () => {
        flipV = !flipV;
        reflow();
    });

    setupUpload({
        onFiles: (files) => {
            const file = files[0];
            const url = URL.createObjectURL(file);
            const image = new Image();
            image.onload = () => {
                URL.revokeObjectURL(url);
                source = image;
                rotation = 0;
                flipH = false;
                flipV = false;
                reflow();
            };
            image.src = url;
        },
    });

    document.querySelector("#tool-run").addEventListener("click", () => {
        if (!source || !crop) {
            kit.banner.show("Choose an image first.");
            return;
        }
        kit.banner.hide();
        const { w, h } = transformedSize();
        const scale = w / canvas.width;
        const outCanvas = document.createElement("canvas");
        const outCtx = outCanvas.getContext("2d");
        outCanvas.width = Math.max(1, Math.round(crop.w * scale));
        outCanvas.height = Math.max(1, Math.round(crop.h * scale));
        outCtx.save();
        outCtx.translate(-crop.x * scale, -crop.y * scale);
        outCtx.translate(w / 2, h / 2);
        if (flipH) {
            outCtx.scale(-1, 1);
        }
        if (flipV) {
            outCtx.scale(1, -1);
        }
        outCtx.rotate((rotation * Math.PI) / 180);
        outCtx.drawImage(source, -w / 2, -h / 2, w, h);
        outCtx.restore();
        outCanvas.toBlob((blob) => {
            const base = (source.currentSrc || source.src || "image").split("/").pop() || "image";
            const name = `${base.replace(/\.[^.]+$/, "")}-cropped.png`;
            triggerDownload(blob, name);
        }, "image/png");
    });
}
