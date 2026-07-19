# PHP-Mailhandler (optionales Modul)

Verarbeitet das Kontaktformular serverseitig. **Nur nötig, wenn PHP-Hosting
gewählt wird** (PH-08). Bei statischem Hosting stattdessen `formEndpoint` in
`src/config/site.ts` auf einen datenschutzkonform geprüften Formulardienst oder
eine Serverless-Funktion umstellen.

## Installation

1. `dist/` (Build-Ausgabe) auf das Hosting hochladen.
2. Ordner `server/php/` mit hochladen (oder an eine Stelle legen, die unter
   `/server/php/contact.php` erreichbar ist – passend zu `formEndpoint`).
3. `config.php.example` nach `config.php` kopieren und ausfüllen:
   - `recipient` – Empfängeradresse (PH-11)
   - `from` – fester Domain-Absender (SPF/DKIM einrichten)
   - `allowed_host` – eigene Domain
   - `dev_mode` – für Produktion auf `false` setzen
4. Testversand durchführen (echte Testmail empfangen).
5. `config.php` **nicht** ins Repository aufnehmen.

## Sicherheit

- Nur POST von eigener Domain (Origin/Referer-Plausibilität), Content-Length-Limit.
- Serverseitige Validierung identisch zum Frontend (Pflichtlogik, Whitelists, Längen).
- Spam-Schutz: Honeypot, Zeitfalle (< 3 s), Rate-Limit je IP – kein reCAPTCHA, kein Tracking.
- Header-Injection verhindert (CR/LF entfernt); `From` fest, Nutzer-Mail nur als `Reply-To`.
- Keine Protokollierung von Formularinhalten; nur generische Fehlercodes.

## Antwortformat

- JS/fetch: `{ "ok": true }` bzw. `{ "ok": false, "errors": { "feld": "meldung" } }`
- No-JS-POST: Redirect auf `/kontakt/?status=ok` bzw. `?status=fehler`

> Hinweis: Impressum, Datenschutz, Absenderadresse und Aufbewahrungsfristen sind
> vor Veröffentlichung durch eine fachkundige Stelle zu prüfen.
