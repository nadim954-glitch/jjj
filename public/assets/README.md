# Medien-Assets (PH-07)

Alle Bilder/Videos sind derzeit **lokale Platzhalter** (im Code als
`MediaPlaceholder` gerendert). Vor Veröffentlichung gemäß Medienmanifest
(Masterdokument Kap. 13) ersetzen.

## Ordner

- `images/` – Foto-Assets (AVIF + WebP, `srcset` 480/768/1200/1800w)
- `video/` – Hero-Video (`hero-trocknung.webm` + `.mp4`, ≤ 6 MB, nur Desktop)
- `icons/` – zusätzliche SVG-Icons (Basis-Icons sind inline in `Icon.astro`)
- `fonts/` – lokale WOFF2 (Manrope/Inter). `@font-face` liegt in
  `src/styles/base.css` vorbereitet und ist auskommentiert.

## Benötigte Dateien (Auszug)

| Datei | Verwendung | Ratio | Max. Größe |
|---|---|---|---|
| `hero-poster.avif/.webp` | Hero-Poster / Mobil-Hero | 16:9 | 1920×1080 |
| `leistung-leckageortung.*` | Leckageortung | 4:3 | 1200×900 |
| `leistung-feuchtemessung.*` | Feuchtemessung | 4:3 | 1200×900 |
| `leistung-bautrocknung.*` | Bautrocknung | 4:3 | 1200×900 |
| `leistung-sanierung.*` | Wasserschadensanierung | 4:3 | 1200×900 |
| `leistung-schimmel.*` | Schimmelbeseitigung | 4:3 | 1200×900 |
| `leistung-rueckbau.*` | Rückbau & Abriss | 4:3 | 1200×900 |
| `leistung-wiederherstellung.*` | Wiederherstellung | 4:3 | 1200×900 |
| `ansprechpartner-sawan.*` (PH-10) | Über uns | 1:1 | 800×800 |
| `og-default.jpg` (PH-12) | Social Preview | 1.91:1 | 1200×630 |

Keine Fremdbilder ohne geklärte Lizenz einbinden.
