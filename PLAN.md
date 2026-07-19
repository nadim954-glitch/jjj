# Umsetzungsplan – SANI Trocknung Website

Stand: Juli 2026 · Stack: **Astro 5, statische Ausgabe** · Design: **„Tiefenwasser Editorial"**

Dieses Dokument hält den Umsetzungsweg und die eigenständig getroffenen
Entscheidungen fest. Inhaltlich/strukturell maßgeblich ist das
Masterdokument; die **gestalterische Ausführung** wurde auf ausdrücklichen
Wunsch vollständig neu entwickelt (der vorhandene Prototyp war nicht
freigegeben und lag zudem nicht vor).

## Phasen

1. **Bestandsanalyse** – Masterdokument vollständig ausgewertet; Prototyp
   nicht vorhanden (Repo enthielt ein unverwandtes Projekt). Inhalte, Fakten,
   Platzhalter und technische Risiken erfasst.
2. **Designrichtung** – drei Richtungen entworfen (Tiefenwasser Editorial /
   Klare Werkstatt / Immersiv Tiefblau). Auswahl: **Tiefenwasser Editorial** –
   ruhig, hochwertig, maximale Lesbarkeit für gestresste Akutnutzer, starke
   CTA-Kontraste, markendistinkt durch das Signaturelement „Messlinie".
3. **Designsystem** – `src/styles/tokens.css` (Farben, Typo, Abstände, Radien,
   Schatten, Breakpoints), `base.css`, `layout.css`, `components.css`.
   Verfeinerte, premium wirkende Palette (Ausgangspunkt: Kap. 10.2), Rollen
   beibehalten. Hochwertiger System-Font-Stack; lokale WOFF2 vorbereitet.
4. **Umsetzung** – Astro-Projekt mit 16 Seiten, zentraler Konfiguration
   (`src/config/site.ts`), Komponenten, Schema.org, Sitemap, optionalem
   PHP-Mailhandler.
5. **Qualität** – `astro check` (0 Fehler), Produktions-Build (16 Seiten),
   Screenshot-Prüfung Desktop/Tablet/Mobil, Kontrolle: keine externen Requests,
   Telefonnummer nur aus Konfiguration, ein H1/Seite, Schema korrekt.

## Eigenständige Entscheidungen

- **Gestalterische Neuentwicklung** statt wörtlicher Übernahme der Tokens aus
  Kap. 10.2 – auf ausdrücklichen Wunsch. Semantische Rollen und Kontrastregeln
  wurden beibehalten, die Hex-Werte premium-orientiert verfeinert (wärmeres
  Papier, tieferes Navy, ein kontrollierter Wasser-Akzent).
- **System-Font-Stack** statt Manrope/Inter-Einbindung, da keine externen
  Schriften geladen werden dürfen und keine lokalen WOFF2 vorlagen. `@font-face`
  liegt in `base.css` auskommentiert bereit (PH-06/Produktion).
- **FAQPage-Schema nur auf `/faq/`** (Kap. 15 / 8.4) – auf den Leistungsseiten
  bleibt das sichtbare Akkordeon, aber ohne Duplikat-Markup.
- **Zweite Telefonnummer (PH-09)** nur als zentraler Prüfwert in `site.ts`
  (`phoneSecondary…`, `phoneSecondaryConfirmed: false`) – **nicht** sichtbar.
- **Formularversand nicht produktiv** (`features.formLive: false`); sichtbarer
  Hinweis auf der Kontaktseite; PHP-Handler im `dev_mode` (sendet keine Mail).
- **Medien** ausschließlich als lokale, klar beschriftete Platzhalter (PH-07).
- **Berlin-Karte** als eigene, bewusst abstrahierte SVG (keine Kartendaten
  Dritter, keine Google Maps).

## Struktur (16 Seiten)

`/` · `/leistungen/` · 7 × `/leistungen/<slug>/` · `/ueber-uns/` ·
`/einsatzgebiete/` · `/faq/` · `/kontakt/` · `/impressum/` · `/datenschutz/` ·
`/404`.

## Build & Deployment

```bash
npm ci
npm run build      # → dist/ (rein statisch)
```

`dist/` auf beliebiges Webhosting laden (HTTPS, HTTP/2, eigene 404-Zuweisung).
Optionaler PHP-Mailhandler: siehe `server/php/README.md`. Endpunkt/Domain
zentral in `src/config/site.ts`.
