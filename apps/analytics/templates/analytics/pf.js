(function () {
  const pf_id_key = "pf_id";

  function uuidv4() {
    return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
      const r = (Math.random() * 16) | 0,
        v = c === "x" ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  }

  function getPFID() {
    let id = localStorage.getItem(pf_id_key);
    if (!id) {
      id = uuidv4();
      localStorage.setItem(pf_id_key, id);
    }
    return id;
  }

  function collectData(siteId) {
    const endpoint = "{{ site_url }}api/collect/";
    const data = {
      pf_id: getPFID(),
      site_id: siteId,
      url: location.href,
      referrer: document.referrer || null,
      title: document.title,
      ua: navigator.userAgent,
      width: window.innerWidth,
      height: window.innerHeight,
      ts: new Date().toISOString(),
    };

    const blob = new Blob([JSON.stringify(data)], { type: "application/json" });
    navigator.sendBeacon(endpoint, blob);
  }

  function runAnalytics() {
    const scriptTag = document.querySelector('script[data-site]');
    const siteId = scriptTag?.getAttribute("data-site");
    if (!siteId) {
      console.warn("[PingFox] Missing data-site attribute in script tag.");
      return;
    }
    collectData(siteId);
  }

  // Initial run
  if (document.readyState === "complete" || document.readyState === "interactive") {
    runAnalytics();
  } else {
    window.addEventListener("DOMContentLoaded", runAnalytics);
  }

  // Handle HTMX page navigation (hx-boost)
  document.body.addEventListener("htmx:afterSettle", runAnalytics);
})();
