/* niche-lab UI auditor. Runs in the page; returns [{inv, key, detail}].
   Invariants I1–I10b of docs/CORRECTIVE-PLAN-v2.1.md §3.1. Pure read except I10b, which scrolls and restores. */
(opts) => {
  opts = opts || {};
  const vw = document.documentElement.clientWidth, narrow = vw < 860, out = [];
  const seen = new Set();
  const ctx = e => { const f = e.closest && e.closest("[data-fig]"); if (f) return "fig:" + f.dataset.fig;
    const a = e.closest && e.closest("[data-act]"); const sec = e.closest && e.closest("section[id]");
    return (a ? "act:" + a.dataset.act : "") + (sec ? (a ? "/" : "") + "sec:" + sec.id : "") || "body"; };
  const sel = e => { const c = (typeof e.className === "string" ? e.className : e.className?.baseVal || "").trim().split(/\s+/).filter(Boolean)[0];
    return e.tagName.toLowerCase() + (c ? "." + c : ""); };
  const add = (inv, e, detail) => { const key = `${inv} ${ctx(e)} ${sel(e)}`; if (seen.has(key)) return; seen.add(key);
    out.push({ inv, key, detail: (detail || "") + ' "' + (e.textContent || "").trim().replace(/\s+/g, " ").slice(0, 50) + '"' }); };
  const shown = e => { if (!e.getClientRects().length) return false; for (let p = e; p && p.nodeType === 1; p = p.parentElement) {
      const cs = getComputedStyle(p); if (cs.visibility === "hidden" || cs.opacity === "0" || cs.display === "none") return false;
      if (p.getAttribute && (p.getAttribute("role") === "tooltip" || p.hasAttribute("data-audit-ignore"))) return false; } return true; };
  const boxesOf = e => { const out = []; for (let p = e; p && p !== document.body; p = p.parentElement) { const d = getComputedStyle(p).display;
      if (d === "inline" || d === "contents") continue; out.push(p); if (!/^inline/.test(d)) break; } return out; };
  const clipOf = e => { for (let p = e.parentElement; p; p = p.parentElement) { const o = getComputedStyle(p).overflowX; if (o !== "visible") return p; } return null; };

  /* I1 */
  if (document.documentElement.scrollWidth > vw) out.push({ inv: "I1", key: "I1 page", detail: `document ${document.documentElement.scrollWidth} > ${vw}` });

  const all = [...document.body.querySelectorAll("*")];
  for (const e of all) {
    if (e.closest("svg") && e.tagName.toLowerCase() !== "svg") continue;
    const cs = getComputedStyle(e);
    /* I2 */
    if ((cs.overflowX === "auto" || cs.overflowX === "scroll") && e.scrollWidth > e.clientWidth + 1 && shown(e)) add("I2", e, `scroll ${e.scrollWidth}>${e.clientWidth}`);
    /* I5 (css) */
    if (cs.textOverflow === "ellipsis" && shown(e)) add("I5", e, "text-overflow: ellipsis");
  }

  /* I3, I5, I9 on text nodes */
  const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let t; (t = tw.nextNode());) {
    const s = t.nodeValue; if (!s.trim()) continue; const e = t.parentElement; if (!e || e.closest("svg,script,style,textarea,option")) continue;
    if (!shown(e)) continue;
    const r = document.createRange(); r.selectNodeContents(t); const rects = [...r.getClientRects()].filter(x => x.width > 0); if (!rects.length) continue;
    const L = Math.min(...rects.map(x => x.left)), Rr = Math.max(...rects.map(x => x.right));
    let bad = false; for (const b of boxesOf(e)) { const box = b.getBoundingClientRect(); if (Rr > box.right + 1.5 || L < box.left - 1.5) { add("I3", e, `text ${Math.round(L)}..${Math.round(Rr)} outside ${sel(b)} ${Math.round(box.left)}..${Math.round(box.right)}`); bad = true; break; } }
    if (!bad) { const c = clipOf(e); if (c) { const cr = c.getBoundingClientRect(); if (Rr > cr.right + 1.5 || L < cr.left - 1.5) add("I3", e, "text cut by overflow container"); } }
    if (Rr > vw + 1 || L < -1) add("I3", e, "text outside viewport");
    const fs = parseFloat(getComputedStyle(e).fontSize); if (fs < 11.95) add("I9", e, `font ${fs}px`);
    if (/…\s*$/.test(s) && !e.closest("p,li,pre,blockquote,.prose")) add("I5", e, "ends in …");
    if (narrow && e.closest("p,li") && !e.closest("nav,table,figcaption,.legend,.meta,.tag,.st") && fs < 13.95) add("I9", e.closest("p,li"), `body copy ${fs}px under 860 (min 14)`);
  }
  for (const f of document.querySelectorAll("input:not([type=checkbox]):not([type=radio]),select,textarea")) if (shown(f) && narrow && parseFloat(getComputedStyle(f).fontSize) < 15.95) add("I9", f, "form control under 16px");

  /* I4 and I5 in SVG */
  for (const svg of document.querySelectorAll("svg")) { if (!shown(svg)) continue; const sr = svg.getBoundingClientRect(); if (!sr.width) continue;
    const scale = sr.width / (svg.viewBox?.baseVal?.width || sr.width); const boxes = [];
    for (const t of svg.querySelectorAll("text")) { const r = t.getBoundingClientRect(); if (!r.width || !shown(t)) continue;
      if (r.left < sr.left - 2 || r.right > sr.right + 2 || r.top < sr.top - 2 || r.bottom > sr.bottom + 2) add("I4", svg, `label "${t.textContent.slice(0, 30)}" outside its chart`);
      if (r.left < -1 || r.right > vw + 1) add("I4", svg, "label outside viewport");
      if (/…\s*$/.test(t.textContent)) add("I5", svg, "SVG label ends in …");
      if (parseFloat(getComputedStyle(t).fontSize) * scale < 11.95) add("I9", svg, "SVG text under 12px");
      if (!t.closest("[data-decor]")) boxes.push([r, t]); }
    for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) { const [a] = boxes[i], [b] = boxes[j];
      const ox = Math.min(a.right, b.right) - Math.max(a.left, b.left), oy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
      if (ox > 2 && oy > 2) { add("I4", svg, `labels overlap: "${boxes[i][1].textContent.slice(0, 20)}" / "${boxes[j][1].textContent.slice(0, 20)}"`); i = boxes.length; break; } } }

  /* I6 */
  for (const g of document.querySelectorAll("[data-btn-group]")) { if (!shown(g)) continue;
    const kids = [...g.children].filter(shown).map(k => k.getBoundingClientRect()); if (kids.length < 2) continue;
    const ws = kids.map(k => k.width); if (Math.max(...ws) - Math.min(...ws) > 1) add("I6", g, `widths ${[...new Set(ws.map(Math.round))].join("/")}`);
    const rows = {}; kids.forEach(k => { const key = Object.keys(rows).find(t => Math.abs(t - k.top) < 4) ?? k.top; (rows[key] = rows[key] || []).push(k); });
    for (const row of Object.values(rows)) { const hs = row.map(k => k.height); if (Math.max(...hs) - Math.min(...hs) > 1) add("I6", g, "heights differ in a row");
      const ts = row.map(k => k.top); if (Math.max(...ts) - Math.min(...ts) > 1) add("I6", g, "tops differ in a row"); }
    const cols = {}; kids.forEach(k => { const key = Object.keys(cols).find(l => Math.abs(l - k.left) < 4) ?? k.left; cols[key] = 1; });
    if (Object.keys(rows).length > 1 && Object.keys(cols).length > Object.values(rows)[0].length) add("I6", g, "columns not aligned across rows"); }

  /* I7 */
  const ctl = [...document.querySelectorAll("button,[role=tab],summary,select,input,textarea,a[href]")].filter(shown);
  for (const c of ctl) { let t = c; const tag = c.tagName.toLowerCase();
    if (tag === "input" && /checkbox|radio/.test(c.type)) t = c.closest("label") || c;
    if (tag === "a") { const blk = c.closest("p,li,td,dd,.prose"); if (blk && (blk.textContent.trim().length > c.textContent.trim().length + 20)) continue; }
    const r = t.getBoundingClientRect();
    if (narrow ? (r.height < 43.5 || r.width < 43.5) : (tag !== "a" && !(tag === "input" && /checkbox|radio/.test(c.type)) && r.height < 35.5)) add("I7", c, `target ${Math.round(r.width)}x${Math.round(r.height)}`); }

  /* I8 + caps */
  const solos = document.querySelectorAll("[data-btn-solo]").length, decor = document.querySelectorAll("[data-decor]").length, ign = document.querySelectorAll("[data-audit-ignore]").length;
  if (solos > 3) out.push({ inv: "I8", key: "I8 caps solo", detail: `${solos} solo buttons > 3` });
  if (decor > 4) out.push({ inv: "I8", key: "I8 caps decor", detail: `${decor} decor > 4` });
  if (ign > 0) out.push({ inv: "I8", key: "I8 caps ignore", detail: `${ign} audit-ignore` });
  const byAct = {};
  for (const b of document.querySelectorAll("button")) { if (!shown(b)) continue;
    if (b.closest("[data-btn-group]") || b.hasAttribute("data-btn-solo")) continue;
    const a = b.getAttribute("data-action"); if (!a) { add("I8", b, "button outside any group, action or solo"); continue; }
    (byAct[a] = byAct[a] || []).push(b); }
  for (const [a, bs] of Object.entries(byAct)) { const ws = bs.map(b => b.getBoundingClientRect().width); if (Math.max(...ws) - Math.min(...ws) > 1) add("I8", bs[0], `action ${a} widths differ`);
    const lists = new Map(); bs.forEach(b => { const l = b.closest("[data-list]") || b.parentElement.parentElement; if (!lists.has(l)) lists.set(l, []); lists.get(l).push(b.getBoundingClientRect().right); });
    for (const rs of lists.values()) if (rs.length > 1 && Math.max(...rs) - Math.min(...rs) > 1) add("I8", bs[0], `action ${a} right edges differ`); }

  /* I11: act length budgets in viewports (only once acts exist) */
  if (opts.budgets) for (const a of document.querySelectorAll("[data-act]")) { const b = opts.budgets[a.dataset.act]; if (!b) continue;
    const h = a.getBoundingClientRect().height / innerHeight; if (h > b + 0.05) out.push({ inv: "I11", key: "I11 act:" + a.dataset.act, detail: `${h.toFixed(1)} screens > ${b}` });
    const figs = [...a.querySelectorAll("[data-fig]")].filter(f => shown(f) && !f.closest("details:not([open])") && !f.parentElement.closest("[data-fig]")).length;
    if (figs > 5) out.push({ inv: "I11", key: "I11 figs act:" + a.dataset.act, detail: `${figs} figures outside expanders > 5` }); }

  /* I10b: nothing interactive hidden under fixed or sticky chrome */
  if (opts.occlusion) { const y0 = scrollY; const fixed = [...document.querySelectorAll("body *")].filter(e => { const p = getComputedStyle(e).position; return (p === "fixed" || p === "sticky") && shown(e) && e.id !== "tip"; });
    if (fixed.length) for (const c of ctl) { if (fixed.some(f => f.contains(c))) continue; c.scrollIntoView({ block: "center" });
      const r = c.getBoundingClientRect(); if (r.width < 1 || r.height < 1) continue; const x = Math.min(vw - 2, Math.max(1, r.left + r.width / 2)), y = r.top + r.height / 2;
      if (y < 0 || y > innerHeight) continue; const hit = document.elementFromPoint(x, y);
      if (hit && hit !== c && !c.contains(hit) && !hit.contains(c) && fixed.some(f => f.contains(hit))) add("I10b", c, "covered by fixed chrome"); }
    scrollTo(0, y0); }
  return out;
}
