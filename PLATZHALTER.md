# Platzhalter & offene Angaben – vor Veröffentlichung prüfen/ersetzen

Keine dieser Angaben wurde erfunden oder „aufgefüllt". Jeder Platzhalter ist im
Code zentral geführt und/oder im sichtbaren Entwurf klar gekennzeichnet.

## Platzhalter-Liste (Fundstellen)

| ID | Angabe | Fundstellen im Code |
|---|---|---|
| **PH-01** | Exakte Firmierung laut Handelsregister (`legalName`) | `src/config/site.ts` · Footer · Impressum · Datenschutz · Kontakt · Schema.org (`Schema.astro`) |
| **PH-02** | Handelsregisternummer + Registergericht | `src/pages/impressum.astro` (markierter Platzhalter) |
| **PH-03** | Umsatzsteuer-ID (falls vorhanden) | `src/pages/impressum.astro` (markierter Platzhalter) |
| **PH-04** | Vollständiger Datenschutztext (fachlich prüfen) | `src/pages/datenschutz.astro` (Gliederung + Entwurfshinweis) |
| **PH-05** | Impressum vollständig (fachlich prüfen) | `src/pages/impressum.astro` (Entwurfshinweis) |
| **PH-06** | Logo-Datei (SVG/PNG) + exakte Markenfarben; Favicon; OG-Bild | `src/components/Header.astro`, `Footer.astro` (Wortmarke) · `public/favicon.svg` (Platzhalter) · `@font-face` in `src/styles/base.css` |
| **PH-07** | Alle Foto-/Videoassets gemäß Medienmanifest | Überall via `MediaPlaceholder` (Hero, Leistungsseiten, Über uns) · `public/assets/README.md` |
| **PH-08** | Hosting-Entscheidung → Formular-Endpunkt | `src/config/site.ts` (`formEndpoint`, `features.formLive`) · `src/pages/kontakt.astro` (sichtbarer Hinweis) · `server/php/config.php.example` |
| **PH-09** | Zweite Telefonnummer 0157 57831464 – Verwendung klären | `src/config/site.ts` (`phoneSecondary…`, `phoneSecondaryConfirmed: false`). **Nicht sichtbar verwendet.** |
| **PH-10** | Foto/Portrait Nadim Sawan (optional) | `src/pages/ueber-uns.astro` (`MediaPlaceholder`) |
| **PH-11** | E-Mail-Empfängeradresse für Formulareingänge | `server/php/config.php.example` (`recipient`) – nicht im Repo |
| **PH-12** | OG-Vorschaubild (1200×630) | `src/layouts/Base.astro` (og:image bewusst weggelassen) · `public/assets/README.md` |

## Bestätigte Angaben (verbindlich, kein Platzhalter)

- Marke: **SANI Trocknung**
- Adresse: **Ulmenstraße 6a, 13467 Berlin**
- Hauptnummer (sichtbar): **+49 157 57209238** / `tel:+4915757209238`
- E-Mail: **info@sani-trocknung.de**
- Erreichbarkeit: **24/7-Notdienst** (bestätigt)
- WhatsApp: gleiche Nummer wie Notruf (`wa.me/4915757209238`)
- Ansprechpartner: **Nadim Sawan**, Geschäftsführer und Inhaber

## Bewusst NICHT verwendet (nicht erfunden)

- Keine Zertifikate, Mitgliedschaften, Bewertungen, Referenzen, Kundenstimmen.
- Kein Gründungsjahr / keine Tätigkeitsdauer.
- Keine Social-Media-Profile (nicht vorhanden → nicht verlinkt).
- Keine `aggregateRating`/`review` im Schema.
- Keine externen Schriften, Karten, Videos oder Trackingdienste.

## Checkliste vor Veröffentlichung (Kap. 21)

1. [ ] PH-01/02/03/05 – Impressum vollständig + fachlich geprüft
2. [ ] PH-04 – Datenschutzerklärung erstellt/geprüft (Hosting, Formular, WhatsApp)
3. [ ] PH-06 – Logo eingebunden (Header/Footer/Favicon/OG), Farbwerte abgeglichen
4. [ ] PH-07 – Alle Medien ersetzt, komprimiert (AVIF/WebP, Video ≤ 6 MB), Alt-Texte
5. [ ] PH-08 – Hosting entschieden; Formular-Endpunkt konfiguriert und real getestet; `formLive: true`
6. [ ] PH-09 – Zweitnummer geklärt (verwenden oder endgültig entfernen)
7. [ ] PH-11 – Empfängeradresse Formular gesetzt (nicht im Repo)
8. [ ] PH-12 – OG-Bild erstellt und verlinkt
9. [ ] `baseUrl`/Canonical-Domain final, Redirects (https, www-Schema) aktiv
10. [ ] Sicherheits-Header gesetzt, HTTPS erzwungen
11. [ ] Lokale Schriften (WOFF2) eingebunden oder System-Stack final bestätigt
12. [ ] „Entwurf"-Hinweise auf Impressum/Datenschutz entfernt
13. [ ] Volltext-Check: keine unbestätigten Aussagen
14. [ ] 404-Test mit zufälliger URL auf Live-Domain
