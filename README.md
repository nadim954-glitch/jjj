# SANI Trocknung – Website

Produktionsnahe, statische Unternehmenswebsite für **SANI Trocknung**
(Wasserschadensanierung, Bautrocknung, Leckageortung u. a. in Berlin und Umland).

- **Stack:** [Astro 5](https://astro.build), statische Ausgabe (reines HTML/CSS,
  minimales JS), hostingunabhängig.
- **Designrichtung:** „Tiefenwasser Editorial" – ruhig, hochwertig, vertrauenswürdig.
- **Datensparsam:** keine externen Requests im Auslieferungszustand (Schriften
  lokal/System, keine Google Fonts, keine Maps, kein Tracking).

## Schnellstart

```bash
npm ci
npm run dev       # Entwicklungsserver → http://localhost:4321
npm run build     # Produktions-Build → dist/
npm run preview   # Build lokal ansehen
npm run check     # Astro Typ-/Diagnose-Check
```

## Struktur

```
src/
├─ config/site.ts        ZENTRALE Konfiguration (Kontaktdaten, Feature-Flags)
├─ layouts/Base.astro    <head>, Meta/OG/Schema, Header, Footer, Sticky-Leiste
├─ components/           Header, MobileNav, Footer, StickyBar, Icon, Button,
│                        ServiceCard, FaqAccordion, MediaPlaceholder, AreaMap,
│                        Breadcrumb, CtaSection, Schema
├─ data/                 nav.ts, services.ts, faq.ts (Inhalte)
├─ styles/               tokens · base · layout · components (eine CSS-Ausgabe)
├─ scripts/main.js       Nav, Dropdown, Akkordeon, Reveal-Observer, Formular-UX
└─ pages/                16 Seiten (Start, Leistungen + 7 Details, Über uns,
                         Einsatzgebiete, FAQ, Kontakt, Impressum, Datenschutz, 404)
public/                  robots.txt, favicon (Platzhalter), assets/ (Medienordner)
server/php/              optionaler Mailhandler (nur bei PHP-Hosting)
```

## Wichtige Dateien

- **`src/config/site.ts`** – einzige Quelle für Kontaktdaten. Telefonnummer,
  E-Mail, Adresse, Formular-Endpunkt und Feature-Flags hier ändern.
- **`PLATZHALTER.md`** – alle offenen Angaben (PH-01 … PH-12) mit Fundstellen und
  Veröffentlichungs-Checkliste.
- **`PLAN.md`** – Umsetzungsweg und getroffene Entscheidungen.

## Vor Veröffentlichung

Mehrere Angaben sind bewusst als Platzhalter geführt und **vor dem Livegang zu
ersetzen/prüfen** (Impressum, Datenschutz, Logo/Medien, Hosting/Formular-Endpunkt,
Zweitnummer). Details in `PLATZHALTER.md`. Rechtstexte durch eine fachkundige
Stelle prüfen lassen.

## Deployment

`npm run build` erzeugt `dist/` (rein statisch) für beliebiges Webhosting
(HTTPS, HTTP/2, eigene 404-Zuweisung, Redirect auf kanonisches Schema).
Optionaler Formularversand per PHP: siehe `server/php/README.md`.
