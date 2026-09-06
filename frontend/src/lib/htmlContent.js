/**
 * Makes admin-authored HTML content safe & useful for display:
 *  - Converts inline/block Markdown (**bold**, # heading, *italic*, `code`, [x](url))
 *    to HTML automatically — no toolbar needed.
 *  - Auto-links bare URLs (http/https/www...) that aren't already inside an <a>.
 *  - Forces every <a> to open in a new tab with safe rel attributes.
 * Runs in the browser via DOMParser (falls back to the raw html on the server).
 */
const HEADING_TAG = { 1: "h2", 2: "h3", 3: "h4", 4: "h4" };

function escapeHtml(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// Convert inline Markdown tokens in a plain string into HTML.
function inlineMarkdown(text) {
  let s = escapeHtml(text);
  s = s.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2">$1</a>'); // [label](url)
  s = s.replace(/\*\*([^*]+?)\*\*/g, "<strong>$1</strong>"); // **bold**
  s = s.replace(/__([^_]+?)__/g, "<strong>$1</strong>"); // __bold__
  s = s.replace(/(^|[^*])\*(?!\s)([^*]+?)\*(?!\*)/g, "$1<em>$2</em>"); // *italic*
  s = s.replace(/(^|[^_\w])_(?!\s)([^_]+?)_(?![_\w])/g, "$1<em>$2</em>"); // _italic_
  s = s.replace(/`([^`]+?)`/g, "<code>$1</code>"); // `code`
  return s;
}

function hasInlineMd(text) {
  return /\*\*[^*]+\*\*|__[^_]+__|\*[^*\s][^*]*\*|`[^`]+`|\[[^\]]+\]\(https?:\/\//.test(text);
}

// Convert Markdown embedded in the parsed HTML DOM (block headings + inline).
function applyMarkdown(root, doc) {
  // Block-level headings: a P/DIV line OR a bare text-node line whose text
  // starts with #, ##, ### ... (contentEditable often leaves the first line
  // as a bare text node, so we must handle both cases).
  const headingRe = /^\s*(#{1,4})\s+(.+?)\s*$/;
  Array.from(root.childNodes).forEach((node) => {
    if (node.nodeType === 1 && ["P", "DIV"].includes(node.tagName) && !node.querySelector("*")) {
      const m = node.textContent.match(headingRe);
      if (!m) return;
      const h = doc.createElement(HEADING_TAG[m[1].length] || "h4");
      h.innerHTML = inlineMarkdown(m[2]);
      node.replaceWith(h);
    } else if (node.nodeType === 3) {
      const m = node.nodeValue.match(headingRe);
      if (!m) return;
      const h = doc.createElement(HEADING_TAG[m[1].length] || "h4");
      h.innerHTML = inlineMarkdown(m[2]);
      node.replaceWith(h);
    }
  });

  // Inline Markdown on remaining plain text nodes.
  const walker = doc.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  const nodes = [];
  while (walker.nextNode()) nodes.push(walker.currentNode);
  nodes.forEach((node) => {
    const p = node.parentElement;
    if (!p || p.closest("a, code, pre, strong, em, h1, h2, h3, h4")) return;
    const text = node.nodeValue;
    if (!text || !hasInlineMd(text)) return;
    const html = inlineMarkdown(text);
    if (html === escapeHtml(text)) return;
    const span = doc.createElement("span");
    span.innerHTML = html;
    node.replaceWith(...Array.from(span.childNodes));
  });
}

export function enhanceHtml(html) {
  if (!html) return "";
  if (typeof window === "undefined" || typeof DOMParser === "undefined") return html;
  try {
    const doc = new DOMParser().parseFromString(`<div id="__root">${html}</div>`, "text/html");
    const root = doc.getElementById("__root");
    if (!root) return html;

    // 0) Markdown → HTML (bold / headings / italic / code / links).
    applyMarkdown(root, doc);

    // 0b) Strip baked-in inline text colours/backgrounds so the site theme
    // controls contrast. Scraped/pasted content often carries dark inline
    // colours that become invisible in dark mode.
    root.querySelectorAll("[style]").forEach((el) => {
      el.style.removeProperty("color");
      el.style.removeProperty("background");
      el.style.removeProperty("background-color");
      if (!el.getAttribute("style") || !el.getAttribute("style").trim()) {
        el.removeAttribute("style");
      }
    });
    root.querySelectorAll("font[color]").forEach((el) => el.removeAttribute("color"));
    root.querySelectorAll("font[bgcolor]").forEach((el) => el.removeAttribute("bgcolor"));

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
