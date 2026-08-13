import "./background-remover.js";
import "./compressor.js";
import { openSupport } from "./support-popup.js";

const headerSupport = document.querySelector("#header-support-button");
const footerSupport = document.querySelector("#footer-support-button");

if (headerSupport) {
  headerSupport.addEventListener("click", () => {
    openSupport();
  });
}

if (footerSupport) {
  footerSupport.addEventListener("click", () => {
    openSupport();
  });
}

