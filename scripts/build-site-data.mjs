#!/usr/bin/env node
// LEADERBOARD.md -> docs/leaderboard.json + docs/meta.json
// Sayt ma'lumoti FAQAT repo'dagi rasmiy LEADERBOARD.md dan olinadi —
// merge qilinmagan lokal natijalar saytga tushmasligi uchun.
// Ishlatish: `node scripts/build-site-data.mjs [kirish.md]`
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { join, dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const input = resolve(root, process.argv[2] || "LEADERBOARD.md");

const strip = (c) =>
  c.trim().replace(/^\*\*|\*\*$/g, "").replace(/^\*|\*$/g, "").trim();
const num = (v) => {
  const n = parseFloat(strip(v));
  return Number.isNaN(n) ? null : n;
};

const src = readFileSync(input, "utf8");
const rows = src
  .split("\n")
  .filter((l) => l.trim().startsWith("|"))
  .slice(2);

const models = [];
for (const r of rows) {
  const p = r.split("|").slice(1, -1).map((s) => s.trim());
  if (p.length < 7) continue;
  const m = p[0].match(/\[([^\]]+)\]\(([^)]+)\)/);
  const name = m ? m[1].trim() : strip(p[0]);
  const url = m ? m[2].trim() : null;
  const org = strip(p[1]);
  const isBaseline =
    org === "-" || /baseline/i.test(name) || /human voters/i.test(name);
  models.push({
    name,
    url,
    org,
    all: num(p[2]),
    correct_word: num(p[3]),
    meaning: num(p[4]),
    meaning_in_context: num(p[5]),
    fill_in: num(p[6]),
    baseline: isBaseline,
  });
}

mkdirSync(join(root, "docs"), { recursive: true });
writeFileSync(
  join(root, "docs", "leaderboard.json"),
  JSON.stringify(models, null, 1) + "\n"
);

const ranked = models
  .filter((m) => !m.baseline)
  .sort((a, b) => (b.all ?? -1) - (a.all ?? -1));
const meta = {
  generated: new Date().toISOString().slice(0, 10),
  source_file: process.argv[2] || "LEADERBOARD.md",
  total_models: ranked.length,
  total_questions: 1861,
  categories: {
    correct_word: 1501,
    meaning: 236,
    meaning_in_context: 72,
    fill_in: 52,
  },
  best: ranked.length
    ? { name: ranked[0].name, all: ranked[0].all, org: ranked[0].org }
    : null,
  source: {
    dataset: "https://huggingface.co/datasets/tahrirchi/uzlib",
    repo: "https://github.com/tahrirchi/uzlib",
    blog: "https://tilmoch.ai/uz/uzlib-ozbekcha-lingvistik-benchmark",
  },
};
writeFileSync(
  join(root, "docs", "meta.json"),
  JSON.stringify(meta, null, 1) + "\n"
);
console.log(`OK: ${models.length} qator (${input}) -> docs/leaderboard.json + docs/meta.json`);
