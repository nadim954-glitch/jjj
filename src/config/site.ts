// ============================================================================
// ZENTRALE KONFIGURATION – einzige Quelle für Kontakt- und Unternehmensdaten.
// KEINE Kontaktdaten irgendwo anders hart codieren.
// [PH-xx] markiert Platzhalter/Prüfwerte gemäß Masterdokument Kap. 2.2 / 21.
// ============================================================================

export const site = {
  // --- Marke / Firmierung -------------------------------------------------
  brand: 'SANI Trocknung',
  // [PH-01] Exakte Firmierung laut Handelsregister vor Veröffentlichung prüfen:
  legalName: 'SANI Trocknung GmbH',

  // --- Telefon ------------------------------------------------------------
  // Bestätigte Hauptnummer (verbindlich, sichtbar auf der Website):
  phoneDisplay: '+49 157 57209238',
  phoneLink: '+4915757209238',
  // [PH-09] Zweite Nummer 0157 57831464 – Verwendung noch NICHT geklärt.
  // Bleibt als zentraler Prüfwert dokumentiert, wird NICHT sichtbar ausgegeben.
  phoneSecondaryDisplay: '+49 157 57831464', // PRÜFWERT – nicht rendern
  phoneSecondaryLink: '+4915757831464', // PRÜFWERT – nicht rendern
  phoneSecondaryConfirmed: false, // solange false: nirgends sichtbar verwenden

  // --- WhatsApp / E-Mail --------------------------------------------------
  whatsapp: '4915757209238', // gleiche Nummer wie Notruf
  email: 'info@sani-trocknung.de',

  // --- Adresse ------------------------------------------------------------
  address: { street: 'Ulmenstraße 6a', zip: '13467', city: 'Berlin', country: 'DE' },

  // --- Erreichbarkeit (bestätigt) ----------------------------------------
  hours: '24/7-Notdienst – rund um die Uhr erreichbar',

  // --- Ansprechpartner ----------------------------------------------------
  owner: 'Nadim Sawan',
  ownerRole: 'Geschäftsführer und Inhaber',

  // --- Technik / URLs -----------------------------------------------------
  // [vor Launch prüfen] finale Domain / Canonical-Schema:
  baseUrl: 'https://www.sani-trocknung.de',
  // [PH-08] Formular-Endpunkt je nach Hosting (PHP-Handler oder Dienst):
  formEndpoint: '/server/php/contact.php',

  // --- Social Media -------------------------------------------------------
  // Nicht vorhanden – NICHT verlinken (Masterdokument Kap. 2.1).
  social: {} as Record<string, string>,

  // --- Feature-Flags (Erweiterungen, deaktiviert) -------------------------
  features: {
    reviews: false, // TrustReviews-Slot vorbereitet, aus
    blog: false,
    upload: false, // Bild-Upload nicht im Launch-Umfang
    formLive: false, // [PH-08] Formularversand erst nach Hosting-Klärung aktivieren
  },
} as const;

export type Site = typeof site;
