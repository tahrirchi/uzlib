// UzLiB leaderboard — client logic (no build step, no dependencies)
const state = { rows: [], sortKey: "all", sortDir: -1, q: "", org: "", hideBase: false };

const $ = (id) => document.getElementById(id);
const esc = (s) =>
  String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const pct = (v) => (v == null ? "—" : (v * 100).toFixed(2) + "%");
const short = (v) => (v == null ? "—" : (v * 100).toFixed(2));

const COLS = ["all", "correct_word", "meaning", "meaning_in_context", "fill_in"];

async function load() {
  try {
    const [lb, meta] = await Promise.all([
      fetch("./leaderboard.json").then((r) => r.json()),
      fetch("./meta.json").then((r) => r.json()),
    ]);
    state.rows = lb;
    // overall rank by "all" desc (non-baseline only)
    const ranked = [...lb].filter((m) => !m.baseline).sort((a, b) => (b.all ?? -1) - (a.all ?? -1));
    ranked.forEach((m, i) => (m._rank = i + 1));
    renderStats(meta, ranked[0]);
    renderOrgs(lb);
    renderCats(meta);
    renderSpot(lb);
    bindToolbar();
    render();
  } catch (e) {
    $("rows").innerHTML = `<tr><td colspan="8" class="muted">Ma'lumot yuklanmadi. Internet aloqasini tekshirib, sahifani yangilang.</td></tr>`;
  }
}

function renderStats(meta, best) {
  $("st-models").textContent = meta.total_models;
  $("st-questions").textContent = meta.total_questions;
  $("st-best").textContent = best ? `${short(best.all)}% · ${best.name}` : "—";
  $("st-updated").textContent = meta.generated || "—";
}

function renderOrgs(rows) {
  const orgs = [...new Set(rows.map((r) => r.org).filter((o) => o && o !== "-"))].sort();
  const sel = $("org");
  for (const o of orgs) {
    const opt = document.createElement("option");
    opt.value = o;
    opt.textContent = o;
    sel.appendChild(opt);
  }
}

const CAT_INFO = {
  correct_word: ["To'g'ri so'z", "Imlo va to'g'ri yozuv shakllari"],
  meaning: ["Ma'no", "So'z ma'nolarini bilish"],
  meaning_in_context: ["Kontekstda ma'no", "Gap ichida ma'no farqlash"],
  fill_in: ["To'ldirish", "Bo'sh o'rinni to'ldirish"],
};

function renderCats(meta) {
  const box = $("cat-cards");
  box.innerHTML = Object.entries(meta.categories || {})
    .map(
      ([k, n]) => `<div class="card"><h3>${esc(CAT_INFO[k]?.[0] ?? k)}</h3>
        <div class="score">${n}</div>
        <div class="sub">${esc(CAT_INFO[k]?.[1] ?? "")} savol</div></div>`
    )
    .join("");
}

function renderSpot(rows) {
  const box = $("spot-cards");
  const items = [...rows]
    .filter((r) => !r.baseline)
    .sort((a, b) => (b.all ?? 0) - (a.all ?? 0))
    .slice(0, 3);
  const medal = ["🥇", "🥈", "🥉"];
  box.innerHTML = items
    .map((m, i) => {
      const name = m.url
        ? `<a class="model-link" href="${esc(m.url)}" target="_blank" rel="noopener">${esc(m.name)}</a>`
        : esc(m.name);
      return `<div class="card"><h3>${medal[i]} ${name}</h3>
        <div class="score">${pct(m.all)}</div>
        <div class="sub">${esc(m.org)}</div></div>`;
    })
    .join("");
}

function bindToolbar() {
  const qEl = $("q");
  const onQ = (e) => { state.q = e.target.value.toLowerCase(); render(); };
  qEl.addEventListener("input", onQ);
  qEl.addEventListener("search", onQ);
  $("org").addEventListener("change", (e) => { state.org = e.target.value; render(); });
  $("hideBase").addEventListener("change", (e) => { state.hideBase = e.target.checked; render(); });
  $("csvBtn").addEventListener("click", downloadCSV);
  document.querySelectorAll("#board thead th").forEach((th) => {
    th.addEventListener("click", () => {
      const k = th.dataset.k;
      if (!k || k === "rank") return;
      if (state.sortKey === k) state.sortDir *= -1;
      else { state.sortKey = k; state.sortDir = k === "name" || k === "org" ? 1 : -1; }
      document.querySelectorAll("#board thead th").forEach((h) => h.classList.remove("sel", "asc"));
      th.classList.add("sel");
      if (state.sortDir === 1) th.classList.add("asc");
      render();
    });
  });
}

function filtered() {
  let rows = [...state.rows];
  if (state.hideBase) rows = rows.filter((r) => !r.baseline);
  if (state.org) rows = rows.filter((r) => r.org === state.org);
  if (state.q) rows = rows.filter((r) => (r.name + " " + r.org).toLowerCase().includes(state.q));
  const k = state.sortKey, d = state.sortDir;
  rows.sort((a, b) => {
    let x = a[k], y = b[k];
    if (x == null) return 1;
    if (y == null) return -1;
    if (typeof x === "string") return d * x.localeCompare(y);
    return d * (x - y);
  });
  return rows;
}

function render() {
  const rows = filtered();
  const tb = $("rows");
  tb.innerHTML = rows
    .map((m) => {
      const cls = [m.baseline ? "is-base" : "", m._rank === 1 ? "top1" : "", m._rank === 2 || m._rank === 3 ? "top23" : ""].join(" ");
      const name = m.url
        ? `<a class="model-link" href="${esc(m.url)}" target="_blank" rel="noopener">${esc(m.name)}</a>`
        : esc(m.name);
      const rest = COLS.slice(1).map((c) =>
        `<td class="num">${short(m[c])}<div class="bar"><i style="width:${(m[c] ?? 0) * 100}%"></i></div></td>`
      ).join("");
      return `<tr class="${cls}"><td>${m._rank ?? "—"}</td><td>${name}</td><td>${esc(m.org)}</td>
        <td class="num"><b>${short(m.all)}</b><div class="bar"><i style="width:${(m.all ?? 0) * 100}%"></i></div></td>${rest}</tr>`;
    })
    .join("");
  const total = state.rows.filter((r) => !r.baseline).length;
  $("count").textContent = `${rows.length} qator ko'rsatilmoqda (jami model: ${total}) · Saralash: ${label(state.sortKey)} ${state.sortDir === 1 ? "↑" : "↓"}`;
}

function label(k) {
  return { name: "nom", org: "tashkilot", all: "umumiy", correct_word: "to'g'ri so'z", meaning: "ma'no", meaning_in_context: "kontekstda ma'no", fill_in: "to'ldirish" }[k] || k;
}

function downloadCSV() {
  const head = ["rank", "model", "org", "all", "correct_word", "meaning", "meaning_in_context", "fill_in", "url"];
  const lines = [head.join(",")];
  for (const m of filtered()) {
    lines.push([m._rank ?? "", `"${(m.name || "").replace(/"/g, '""')}"`, `"${(m.org || "").replace(/"/g, '""')}"`,
      m.all ?? "", m.correct_word ?? "", m.meaning ?? "", m.meaning_in_context ?? "", m.fill_in ?? "", m.url || ""].join(","));
  }
  const blob = new Blob(["\ufeff" + lines.join("\n")], { type: "text/csv;charset=utf-8" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "uzlib-leaderboard.csv";
  a.click();
  URL.revokeObjectURL(a.href);
}

load();
