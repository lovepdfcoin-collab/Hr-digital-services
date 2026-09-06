import React, { useRef, useEffect } from "react";
import { FaBold, FaItalic, FaListUl, FaLink, FaUnlink } from "react-icons/fa";

/**
 * Lightweight rich-text editor (contentEditable + execCommand) that outputs
 * HTML. Supports Bold, Italic, H2/H3 headings, bullet lists and links.
 * Controlled via `value` (HTML string) / `onChange(html)`.
 */
const RichTextEditor = ({ value, onChange, placeholder = "" }) => {
  const ref = useRef(null);
  const inited = useRef(false);

  // Initialise the DOM from `value` exactly ONCE (first mount / first non-empty
  // load). After that the contentEditable DOM is the single source of truth —
  // we never write innerHTML again, so re-renders can't wipe the user's typing.
  useEffect(() => {
    if (!ref.current || inited.current) return;
    ref.current.innerHTML = value || "";
    inited.current = true;
  }, [value]);

  const emit = () => {
    onChange?.(ref.current?.innerHTML || "");
  };

  const exec = (cmd, arg = null) => {
    document.execCommand(cmd, false, arg);
    ref.current?.focus();
    emit();
  };

  const heading = (tag) => exec("formatBlock", `<${tag}>`);

  const addLink = () => {
    const url = window.prompt("Link URL (https://...)");
    if (!url) return;
    const href = /^https?:\/\//i.test(url) ? url : `https://${url}`;
    exec("createLink", href);
  };

  const Btn = ({ onClick, title, children, testid }) => (
    <button
      type="button"
      title={title}
      onMouseDown={(e) => e.preventDefault()} /* keep text selection */
      onClick={onClick}
      className="px-2.5 py-2 rounded hover:bg-slate-200 text-slate-600 text-sm font-bold min-w-[34px]"
      data-testid={testid}
    >
      {children}
    </button>
  );

  return (
    <div className="mt-1 rounded-lg border border-slate-300 bg-white overflow-hidden focus-within:border-emerald-500">
      <div className="flex items-center gap-0.5 flex-wrap border-b border-slate-200 px-2 py-1.5 bg-slate-50">
        <Btn onClick={() => exec("bold")} title="Bold" testid="rte-bold"><FaBold /></Btn>
        <Btn onClick={() => exec("italic")} title="Italic" testid="rte-italic"><FaItalic /></Btn>
        <span className="w-px h-5 bg-slate-300 mx-1" />
        <Btn onClick={() => heading("h2")} title="Heading 2" testid="rte-h2">H2</Btn>
        <Btn onClick={() => heading("h3")} title="Heading 3" testid="rte-h3">H3</Btn>
        <Btn onClick={() => exec("formatBlock", "<p>")} title="Normal text" testid="rte-p">P</Btn>
        <span className="w-px h-5 bg-slate-300 mx-1" />
        <Btn onClick={() => exec("insertUnorderedList")} title="Bullet list" testid="rte-ul"><FaListUl /></Btn>
        <Btn onClick={addLink} title="Insert link" testid="rte-link"><FaLink /></Btn>
        <Btn onClick={() => exec("unlink")} title="Remove link" testid="rte-unlink"><FaUnlink /></Btn>
      </div>
      <div
        ref={ref}
        contentEditable
        suppressContentEditableWarning
        onInput={emit}
        onBlur={emit}
        data-placeholder={placeholder}
        className="rte-content min-h-[180px] max-h-[420px] overflow-y-auto px-3 py-2 text-sm text-slate-900 outline-none leading-relaxed"
        data-testid="rte-editor"
      />
    </div>
  );
};

export default RichTextEditor;
