import { initToolPage } from "./tool-kit.js";
import { apiJsonPost } from "../api.js";

const kit = await initToolPage("word-counter");

const textArea = document.querySelector("#text-input");
const statWords = document.querySelector("#stat-words");
const statChars = document.querySelector("#stat-chars");
const statSentences = document.querySelector("#stat-sentences");
const statLines = document.querySelector("#stat-lines");
const statTime = document.querySelector("#stat-time");

async function updateStats() {
    const text = textArea.value;
    try {
        const res = await apiJsonPost("/tools/text/word-counter", { text });
        if (res && res.data) {
            statWords.textContent = res.data.words;
            statChars.textContent = res.data.characters;
            statSentences.textContent = res.data.sentences;
            statLines.textContent = res.data.lines;
            statTime.textContent = `${res.data.reading_time_minutes} min`;
        }
    } catch {
        // Fallback live calculation if offline/network error
    }
}

textArea.addEventListener("input", updateStats);
