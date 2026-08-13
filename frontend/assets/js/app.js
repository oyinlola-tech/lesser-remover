import "./background-remover.js";
import "./compressor.js";
import { openSupport } from "./support-popup.js";

const fabSupport = document.querySelector("#fab-support");
const footerSupport = document.querySelector("#footer-support-button");

if (fabSupport) {
  fabSupport.addEventListener("click", () => {
    openSupport();
  });
}

if (footerSupport) {
  footerSupport.addEventListener("click", () => {
    openSupport();
  });
}

