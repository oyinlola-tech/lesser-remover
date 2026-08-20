/**
 * vercel-analytics.js
 * Loads Vercel Web Analytics + Speed Insights only when running on Vercel.
 * On localhost the scripts simply don't exist, so we skip them silently.
 */
(function () {
  const isVercel =
    window.location.hostname !== "localhost" &&
    window.location.hostname !== "127.0.0.1" &&
    !window.location.hostname.startsWith("192.168.") &&
    !window.location.hostname.startsWith("10.");

  if (!isVercel) return;

  // Vercel Web Analytics
  window.va =
    window.va ||
    function () {
      (window.vaq = window.vaq || []).push(arguments);
    };
  var vaScript = document.createElement("script");
  vaScript.defer = true;
  vaScript.src = "/_vercel/insights/script.js";
  document.head.appendChild(vaScript);

  // Vercel Speed Insights
  window.si =
    window.si ||
    function () {
      (window.siq = window.siq || []).push(arguments);
    };
  var siScript = document.createElement("script");
  siScript.defer = true;
  siScript.src = "/_vercel/speed-insights/script.js";
  document.head.appendChild(siScript);
})();
