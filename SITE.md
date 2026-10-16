# UzLiB saytini nashr qilish (GitHub Pages)

Sayt — `docs/` papkasidagi statik fayllar (`index.html`, `styles.css`, `app.js`,
`leaderboard.json`, `meta.json`). Server, build yoki API kalit kerak emas.

## 1. Ma'lumotni yangilash

`LEADERBOARD.md` ga yangi model qo'shilganda (rasmiy fayl — merge qilinmagan
lokal natijalar saytga tushmasligi kerak):

```bash
node scripts/build-site-data.mjs
```

Bu `docs/leaderboard.json` va `docs/meta.json` ni qayta yaratadi.

## 2. GitHub Pages ni yoqish

1. GitHub repo sahifasida **Settings → Pages** ga kiring.
2. **Source** sifatida **Deploy from a branch** ni tanlang.
3. **Branch**: `main`, papka: `/docs` → **Save**.
4. 1–2 daqiqadan keyin sayt ushbu manzilda ochiladi:
   `https://<username>.github.io/uzlib/`

## 3. Mahalliy ko'rish

```bash
npx serve docs
# yoki
python -m http.server -d docs 8000
```

## Fayllar

| Fayl | Vazifa |
|---|---|
| `docs/index.html` | Sahifa tuzilmasi (hero, reyting, kategoriyalar, metodologiya) |
| `docs/styles.css` | Dizayn (responsive, mobilgacha) |
| `docs/app.js` | Qidiruv, tashkilot filtri, ustun bo'yicha saralash, CSV yuklash |
| `docs/leaderboard.json` | Jadval ma'lumoti (avto-generatsiya) |
| `docs/meta.json` | Statistika: model/savol soni, eng yaxshi natija, sana |
| `scripts/build-site-data.mjs` | `LEADERBOARD.md` → JSON generator |
