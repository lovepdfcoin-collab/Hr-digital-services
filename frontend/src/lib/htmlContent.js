/**
 * Makes admin-authored HTML content safe & useful for display:
 *  - Auto-links bare URLs (http/https/www...) that aren't already inside an <a>.
 *  - Forces every <a> to open in a new tab with safe rel attributes.
 * Runs in the browser via DOMParser (falls back to the raw html on the server).
 */
export function enhanceHtml(html) {
  if (!html) return "";
  if (typeof window === "undefined" || typeof DOMParser === "undefined") return html;
  try {
    const doc = new DOMParser().parseFromString(`<div id="__root">${html}</div>`, "text/html");
    const root = doc.getElementById("__root");
    if (!root) return html;

    const urlRe = /((?:https?:\/\/|www\.)[^\s<]+[^\s<.,;:)"'!?\]])/gi;

    // 1) Linkify bare URLs inside plain text nodes only.
    const walker = doc.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    const textNodes = [];
    while (walker.nextNode()) textNodes.push(walker.currentNode);

    textNodes.forEach((node) => {
      // Skip text already inside an anchor.
      if (node.parentElement && node.parentElement.closest("a")) return;
      const text = node.nodeValue;
      if (!text || !urlRe.test(text)) return;
      urlRe.lastIndex = 0;

      const frag = doc.createDocumentFragment();
      let last = 0;
      let m;
      while ((m = urlRe.exec(text))) {
        const before = text.slice(last, m.index);
        if (before) frag.appendChild(doc.createTextNode(before));
        const raw = m[0];
        const a = doc.createElement("a");
        a.href = /^https?:\/\//i.test(raw) ? raw : `https://${raw}`;
        a.textContent = raw;
        frag.appendChild(a);
        last = m.index + raw.length;
      }
      const after = text.slice(last);
      if (after) frag.appendChild(doc.createTextNode(after));
      node.parentNode.replaceChild(frag, node);
    });

    // 2) Make every anchor open safely in a new tab.
    root.querySelectorAll("a").forEach((a) => {
      const href = a.getAttribute("href") || "";
      if (href && !/^https?:\/\//i.test(href) && !href.startsWith("/") && !href.startsWith("#")) {
        a.setAttribute("href", `https://${href}`);
      }
      a.setAttribute("target", "_blank");
      a.setAttribute("rel", "noreferrer nofollow");
    });

    return root.innerHTML;
  } catch {
    return html;
  }
}
