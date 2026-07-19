// ============================================================================
// Leistungsinhalte – Texte 1:1 aus Masterdokument Kap. 9.4–9.10 / 9.0.
// Interne Links im Fließtext als <a>-Tags (eigener, vertrauenswürdiger Inhalt).
// Medien: lokale Platzhalter gemäß Medienmanifest Kap. 13 (PH-07).
// ============================================================================

export interface ServiceFaq {
  q: string;
  a: string; // darf interne <a>-Links enthalten
}

export interface Service {
  slug: string;
  label: string;
  group: 1 | 2 | 3 | 4;
  icon: string;
  metaTitle: string;
  metaDescription: string;
  h1: string;
  intro: string;
  cardText: string;
  image: { file: string; alt: string };
  situations: string[];
  approachTitle: string;
  approach: string;
  ownServices?: string[]; // nur Wiederherstellung
  coordination?: { title: string; text: string }; // nur Wiederherstellung
  advantagesTitle: string;
  advantages: string[];
  steps: string[];
  faqs: ServiceFaq[];
  related: { label: string; slug: string }[];
}

export const servicesData: Service[] = [
  {
    slug: 'leckageortung',
    label: 'Leckageortung',
    group: 1,
    icon: 'leckageortung',
    metaTitle: 'Leckageortung Berlin – zerstörungsarm | SANI Trocknung',
    metaDescription:
      'Versteckte Leckage? Wir orten Wasserschäden in Berlin mit moderner Messtechnik – möglichst zerstörungsarm. 24/7 erreichbar.',
    h1: 'Leckageortung in Berlin: die Ursache finden, bevor der Schaden wächst.',
    intro:
      'Feuchte Flecken, ein steigender Wasserzähler, muffiger Geruch – oft liegt die Ursache verdeckt in Wand, Boden oder Leitung. Wir lokalisieren Leckagen mit moderner Messtechnik und arbeiten dabei möglichst zerstörungsarm.',
    cardText:
      'Versteckte Leckagen möglichst zerstörungsarm finden, bevor der Schaden wächst.',
    image: { file: 'leistung-leckageortung', alt: 'Leckageortung mit Messgerät an einer Wand' },
    situations: [
      'Feuchte Flecken an Wand oder Decke ohne erkennbare Ursache',
      'Wasserzähler läuft, obwohl kein Wasser entnommen wird',
      'Muffiger Geruch in einzelnen Räumen',
      'Nasse Stellen am Boden oder aufquellender Belag',
      'Druckverlust in der Heizungsanlage',
      'Wasserschaden beim Nachbarn mit unklarer Herkunft',
    ],
    approachTitle: 'Unsere Vorgehensweise',
    approach:
      'Wir grenzen die Ursache Ihres Feuchtigkeitsschadens systematisch ein. Dazu kombinieren wir je nach Situation geeignete moderne Messmethoden und untersuchen die betroffenen Bereiche möglichst zerstörungsarm – Öffnungen erfolgen nur dort, wo sie wirklich nötig sind. Das Ergebnis besprechen wir verständlich mit Ihnen und dokumentieren es für die weiteren Schritte, etwa gegenüber Versicherung oder Hausverwaltung.',
    advantagesTitle: 'Ihre Vorteile',
    advantages: [
      'Möglichst zerstörungsarme Untersuchung',
      'Moderne Messmethoden statt Verdachtsöffnungen',
      'Klare Eingrenzung der Schadenursache',
      'Verständliche Erklärung und Dokumentation',
      'Direkte Anbindung an Trocknung und Sanierung aus einer Hand',
    ],
    steps: [
      'Kontakt und Schilderung der Situation',
      'Termin – bei akuten Schäden kurzfristig',
      'Messung und Eingrenzung vor Ort',
      'Ergebnisbesprechung und Empfehlung',
      'Auf Wunsch: direkte Einleitung der nächsten Schritte',
    ],
    faqs: [
      {
        q: 'Wie wird eine versteckte Leckage gefunden?',
        a: 'Mit einer Kombination moderner Messverfahren grenzen wir den Bereich schrittweise ein – von der großflächigen Feuchtemessung bis zur punktgenauen Ortung. Welche Methode passt, hängt von Bauweise und Schadenbild ab.',
      },
      {
        q: 'Muss dafür die Wand oder der Boden geöffnet werden?',
        a: 'Nicht zwingend. Wir arbeiten möglichst zerstörungsarm. Ob und wo eine Öffnung nötig ist, zeigt sich erst nach der Eingrenzung – und wird vorher mit Ihnen besprochen.',
      },
      {
        q: 'Was passiert nach der Ortung?',
        a: 'Sie erhalten eine klare Empfehlung. Auf Wunsch übernehmen wir direkt die weiteren Schritte – von der <a href="/leistungen/bautrocknung/">Bautrocknung</a> bis zur <a href="/leistungen/wiederherstellung/">Wiederherstellung</a>.',
      },
    ],
    related: [
      { label: 'Feuchtemessung', slug: 'feuchtemessung' },
      { label: 'Bautrocknung', slug: 'bautrocknung' },
      { label: 'Wasserschadensanierung', slug: 'wasserschadensanierung' },
    ],
  },
  {
    slug: 'feuchtemessung',
    label: 'Feuchtemessung',
    group: 1,
    icon: 'feuchtemessung',
    metaTitle: 'Feuchtemessung Berlin – Wände & Böden | SANI Trocknung',
    metaDescription:
      'Feuchtigkeit in Wand, Boden oder Decke? Wir messen mit moderner Technik und beurteilen Ursache und Ausmaß. Jetzt Termin anfragen.',
    h1: 'Feuchtemessung: Klarheit über Ursache und Ausmaß.',
    intro:
      'Ist die Wand wirklich feucht – und wenn ja, wie tief? Mit moderner Messtechnik erfassen wir Feuchtigkeit in Wänden, Böden, Decken, Estrich und weiteren Bauteilen und schaffen die Grundlage für die richtigen Maßnahmen.',
    cardText: 'Feuchtigkeit in Wänden, Böden und Decken präzise erfassen und beurteilen.',
    image: { file: 'leistung-feuchtemessung', alt: 'Feuchtemessung an einem Estrichboden' },
    situations: [
      'Verdacht auf Feuchtigkeit nach einem Wasserschaden',
      'Dunkle Flecken oder abplatzende Farbe',
      'Kontrolle vor oder nach einer Trocknung',
      'Feuchteverdacht beim Immobilienkauf oder Mieterwechsel',
      'Klärung, ob Estrich oder Dämmschicht betroffen sind',
    ],
    approachTitle: 'Unsere Vorgehensweise',
    approach:
      'Wir messen die betroffenen Bauteile mit geeigneten Verfahren, beurteilen Ursache und Ausmaß und leiten daraus die passenden Maßnahmen ab – ob gezielte Trocknung, weitergehende Ortung oder Entwarnung. Die Ergebnisse erklären wir Ihnen verständlich.',
    advantagesTitle: 'Ihre Vorteile',
    advantages: [
      'Belastbare Grundlage statt Vermutungen',
      'Messung an Wänden, Böden, Decken und Estrich',
      'Verständliche Einordnung der Ergebnisse',
      'Konkrete Maßnahmenempfehlung',
      'Direkter Übergang zu Trocknung oder Ortung, falls nötig',
    ],
    steps: [
      'Anfrage und Terminvereinbarung',
      'Messung der betroffenen Bauteile vor Ort',
      'Beurteilung von Ursache und Ausmaß',
      'Empfehlung der nächsten Schritte',
    ],
    faqs: [
      {
        q: 'Wie erkenne ich Feuchtigkeit in der Wand?',
        a: 'Mögliche Anzeichen sind dunkle Flecken, abblätternde Farbe, sich lösende Tapeten, muffiger Geruch oder ein spürbar kaltes, feuchtes Wandgefühl. Gewissheit gibt erst eine Messung.',
      },
      {
        q: 'Reicht eine einzelne Messung aus?',
        a: 'Das hängt vom Ziel ab. Für eine erste Einschätzung oft ja; zur Kontrolle einer Trocknung können mehrere Messungen im Verlauf sinnvoll sein. Wir empfehlen nur, was das Schadenbild erfordert.',
      },
      {
        q: 'Was kostet eine Feuchtemessung?',
        a: 'Der Aufwand hängt von Objekt und Fragestellung ab. Schildern Sie uns die Situation – Sie erhalten vorab eine klare Auskunft zum Vorgehen.',
      },
    ],
    related: [
      { label: 'Leckageortung', slug: 'leckageortung' },
      { label: 'Bautrocknung', slug: 'bautrocknung' },
      { label: 'Schimmelbeseitigung', slug: 'schimmelbeseitigung' },
    ],
  },
  {
    slug: 'bautrocknung',
    label: 'Bautrocknung',
    group: 2,
    icon: 'bautrocknung',
    metaTitle: 'Bautrocknung Berlin – technische Trocknung | SANI Trocknung',
    metaDescription:
      'Technische Bautrocknung nach Wasserschäden in Berlin und Umland. Geeignete Geräte, kontrolliertes Vorgehen, ein Ansprechpartner.',
    h1: 'Bautrocknung: Feuchtigkeit kontrolliert reduzieren.',
    intro:
      'Nach einem Wasser- oder Feuchtigkeitsschaden kommt es darauf an, die Feuchtigkeit kontrolliert aus den Bauteilen zu bekommen – mit geeigneten Geräten und einem Verfahren, das zum Schadenbild passt. Genau das ist technische Bautrocknung.',
    cardText: 'Technische Trocknung mit geeigneten Geräten – kontrolliert und nachvollziehbar.',
    image: { file: 'leistung-bautrocknung', alt: 'Bautrockner im Einsatz in einem Wohnraum' },
    situations: [
      'Nach Rohrbruch oder Leitungsschaden',
      'Durchfeuchteter Estrich oder Dämmschicht',
      'Wasserschaden durch Unwetter oder Rückstau',
      'Feuchte Wände nach einer Leckage',
      'Neubaufeuchte oder Restfeuchte vor weiteren Arbeiten',
    ],
    approachTitle: 'Unsere Vorgehensweise',
    approach:
      'Auf Basis der Messergebnisse wählen wir geeignete Trocknungsgeräte und -verfahren aus, stellen sie fachgerecht auf und stimmen die Trocknung auf das Schadenbild ab. Ziel ist, die Feuchtigkeit kontrolliert zu reduzieren und Folgeschäden wie Schimmelbildung zu vermeiden. Den Fortschritt kontrollieren wir durch begleitende Messungen und stimmen das Ende der Trocknung mit Ihnen ab.',
    advantagesTitle: 'Ihre Vorteile',
    advantages: [
      'Geeignete Geräte und Verfahren je nach Schadenbild',
      'Kontrollierte Reduzierung der Feuchtigkeit',
      'Vermeidung von Folgeschäden',
      'Begleitende Kontrolle durch Messungen',
      'Ein Ansprechpartner – auch für die Schritte davor und danach',
    ],
    steps: [
      'Schadenaufnahme und Feuchtemessung',
      'Auswahl von Geräten und Verfahren',
      'Aufbau und Inbetriebnahme der Trocknung',
      'Kontrolle des Trocknungsfortschritts',
      'Abbau und Abstimmung der nächsten Schritte',
    ],
    faqs: [
      {
        q: 'Wie lange dauert eine Bautrocknung?',
        a: 'Das hängt von Durchfeuchtungsgrad, Bauteilen, Materialien und Umgebungsbedingungen ab – von wenigen Tagen bis zu mehreren Wochen. Nach der ersten Messung können wir die Dauer besser einschätzen.',
      },
      {
        q: 'Wie schnell sollte mit der Trocknung begonnen werden?',
        a: 'Möglichst zeitnah. Je früher Feuchtigkeit kontrolliert reduziert wird, desto besser lassen sich Folgeschäden begrenzen.',
      },
      {
        q: 'Kann ich während der Trocknung in der Wohnung bleiben?',
        a: 'In vielen Fällen ja. Wir besprechen mit Ihnen, welche Räume betroffen sind, wie laut die Geräte sind und worauf Sie achten sollten.',
      },
    ],
    related: [
      { label: 'Feuchtemessung', slug: 'feuchtemessung' },
      { label: 'Wasserschadensanierung', slug: 'wasserschadensanierung' },
      { label: 'Wiederherstellung', slug: 'wiederherstellung' },
    ],
  },
  {
    slug: 'wasserschadensanierung',
    label: 'Wasserschadensanierung',
    group: 2,
    icon: 'sanierung',
    metaTitle: 'Wasserschadensanierung Berlin – 24/7 | SANI Trocknung',
    metaDescription:
      'Wasserschadensanierung in Berlin: Schadenaufnahme, Trocknung, Sanierung und Wiederherstellung koordiniert aus einer Hand. 24/7-Notdienst.',
    h1: 'Wasserschadensanierung: koordiniert von der Aufnahme bis zur Übergabe.',
    intro:
      'Ein Wasserschaden bedeutet viele Einzelschritte – Aufnahme, Sicherung, Trocknung, Rückbau, Wiederherstellung. Wir koordinieren diese Schritte für Sie und führen sie aus einer Hand aus, abgestimmt auf Schadenbild und Auftrag.',
    cardText: 'Vom ersten Schritt bis zur Übergabe: koordinierte Sanierung Ihres Schadens.',
    image: { file: 'leistung-sanierung', alt: 'Schadenaufnahme bei einer Wasserschadensanierung' },
    situations: [
      'Rohrbruch in Wohnung oder Haus',
      'Wasserschaden durch defekte Geräte (z. B. Wasch- oder Spülmaschine)',
      'Schaden über mehrere Etagen oder Einheiten',
      'Wasserschaden in vermieteten Objekten',
      'Versicherter Schadenfall mit Abstimmungsbedarf',
    ],
    approachTitle: 'Unsere Vorgehensweise',
    approach:
      'Wir nehmen den Schaden strukturiert auf, sichern betroffene Bereiche und bewerten beschädigte Materialien. Darauf aufbauend koordinieren wir Trocknungs- und Sanierungsmaßnahmen, binden wo nötig Fachgewerke ein und bereiten die Wiederherstellung vor – oder führen sie direkt durch. Sie erhalten in jedem Schritt eine klare, transparente Abstimmung; die Dokumentation unterstützt Sie auch gegenüber Versicherung oder Hausverwaltung.',
    advantagesTitle: 'Ihre Vorteile',
    advantages: [
      'Ein Ansprechpartner für den gesamten Schaden',
      'Strukturierte Schadenaufnahme und Dokumentation',
      'Koordination aller erforderlichen Schritte und Fachgewerke',
      'Saubere Arbeitsweise, auch in bewohnten Objekten',
      'Nahtloser Übergang bis zur Wiederherstellung',
    ],
    steps: [
      'Schaden melden – 24/7',
      'Schadenaufnahme und Sicherung vor Ort',
      'Ortung, Messung und Maßnahmenplan',
      'Trocknung, Rückbau und Sanierung',
      'Wiederherstellung und Übergabe',
    ],
    faqs: [
      {
        q: 'Übernimmt die Versicherung die Kosten?',
        a: 'Das hängt vom Schadenfall, Ihrem Vertrag und dem Versicherer ab – eine pauschale Zusage ist nicht möglich. Unsere Schadendokumentation unterstützt Sie bei der Abwicklung; klären Sie den Umfang direkt mit Ihrer Versicherung.',
      },
      {
        q: 'Was sollte ich unmittelbar nach einem Wasserschaden tun?',
        a: 'Wenn möglich: Wasserzufuhr stoppen (Absperrhahn), Strom in betroffenen Bereichen abschalten lassen, Wertsachen aus dem Nassbereich bringen und den Schaden mit Fotos festhalten. Danach: melden – wir besprechen die nächsten Schritte.',
      },
      {
        q: 'Arbeiten Sie mit Hausverwaltungen zusammen?',
        a: 'Ja. Wir stimmen uns eng mit Verwaltungen, Eigentümern und Mietern ab und halten alle Beteiligten auf dem Laufenden.',
      },
    ],
    related: [
      { label: 'Leckageortung', slug: 'leckageortung' },
      { label: 'Bautrocknung', slug: 'bautrocknung' },
      { label: 'Rückbau & Abriss', slug: 'rueckbau-abriss' },
      { label: 'Wiederherstellung', slug: 'wiederherstellung' },
    ],
  },
  {
    slug: 'schimmelbeseitigung',
    label: 'Schimmelbeseitigung',
    group: 2,
    icon: 'schimmel',
    metaTitle: 'Schimmelbeseitigung Berlin | SANI Trocknung',
    metaDescription:
      'Fachgerechte Schimmelsanierung in Berlin: Ursache beheben, betroffene Bereiche behandeln oder entfernen. Sprechen Sie mit uns.',
    h1: 'Schimmelbeseitigung: erst die Ursache, dann die Fläche.',
    intro:
      'Schimmel ist meist ein Folgeproblem – von Feuchtigkeit, die nicht dorthin gehört. Deshalb beheben wir zuerst die Ursache und behandeln oder entfernen anschließend die betroffenen Bereiche fachgerecht.',
    cardText: 'Ursache beheben, betroffene Bereiche fachgerecht behandeln oder entfernen.',
    image: {
      file: 'leistung-schimmel',
      alt: 'Fachgerechte Behandlung einer von Schimmel betroffenen Wand',
    },
    situations: [
      'Schimmel nach einem Wasserschaden',
      'Dunkle Flecken an Außenwänden oder hinter Möbeln',
      'Muffiger Geruch trotz Lüften',
      'Schimmel im Bad oder an Fensterlaibungen',
      'Befall nach unentdeckter Leckage',
    ],
    approachTitle: 'Unsere Vorgehensweise',
    approach:
      'Wir klären zunächst die Feuchtigkeitsursache – etwa durch Feuchtemessung oder Leckageortung. Erst danach behandeln wir betroffene Bereiche oder entfernen betroffene Materialien fachgerecht; eine rein kosmetische Überdeckung löst das Problem nicht. Bei umfangreichem Befall weisen wir Sie auf eine notwendige weitergehende Fachbewertung hin.',
    advantagesTitle: 'Ihre Vorteile',
    advantages: [
      'Ursachenbehebung vor kosmetischer Behandlung',
      'Fachgerechte Entfernung oder Behandlung betroffener Materialien',
      'Ehrliche Einschätzung – auch, wenn eine weitergehende Bewertung nötig ist',
      'Anbindung an Trocknung, Rückbau und Wiederherstellung aus einer Hand',
    ],
    steps: [
      'Besichtigung und Ursachenklärung',
      'Maßnahmenempfehlung',
      'Fachgerechte Behandlung oder Entfernung',
      'Ursachenbeseitigung (z. B. Trocknung)',
      'Wiederherstellung der Flächen',
    ],
    faqs: [
      {
        q: 'Wann kann nach einem Wasserschaden Schimmel entstehen?',
        a: 'Bei anhaltender Feuchtigkeit kann sich Schimmel bereits innerhalb weniger Tage bilden. Deshalb ist eine zeitnahe, kontrollierte Trocknung wichtig.',
      },
      {
        q: 'Reicht Anti-Schimmel-Spray aus dem Baumarkt?',
        a: 'Bei oberflächlichem, kleinflächigem Befall kann eine Behandlung genügen – solange die Ursache behoben ist. Bleibt die Feuchtigkeit, kommt der Schimmel wieder. Im Zweifel: einschätzen lassen.',
      },
      {
        q: 'Ist Schimmel gesundheitsschädlich?',
        a: 'Schimmelbefall in Innenräumen sollte grundsätzlich beseitigt und die Ursache behoben werden. Medizinische Fragen klären Sie bitte mit einer Ärztin oder einem Arzt – wir kümmern uns um die bauliche Seite.',
      },
    ],
    related: [
      { label: 'Feuchtemessung', slug: 'feuchtemessung' },
      { label: 'Bautrocknung', slug: 'bautrocknung' },
      { label: 'Rückbau & Abriss', slug: 'rueckbau-abriss' },
    ],
  },
  {
    slug: 'rueckbau-abriss',
    label: 'Rückbau & Abriss',
    group: 3,
    icon: 'rueckbau',
    metaTitle: 'Rückbau & Abrissarbeiten Berlin | SANI Trocknung',
    metaDescription:
      'Kontrollierter Rückbau, Demontage und Entkernung nach Wasserschäden in Berlin – sauber, koordiniert und gut vorbereitet.',
    h1: 'Rückbau und Abrissarbeiten: kontrolliert, sauber, gut vorbereitet.',
    intro:
      'Manche Materialien lassen sich nach einem Wasserschaden nicht retten. Dann bauen wir beschädigte Bereiche kontrolliert aus, legen betroffene Bauteile frei und bereiten die Flächen für Trocknung oder Wiederherstellung vor.',
    cardText: 'Beschädigte Materialien kontrolliert ausbauen und Flächen sauber vorbereiten.',
    image: { file: 'leistung-rueckbau', alt: 'Kontrollierter Rückbau mit Staubschutz' },
    situations: [
      'Durchfeuchteter Estrich oder Bodenaufbau',
      'Beschädigter Trockenbau oder Wandverkleidungen',
      'Aufgequollene Böden und Beläge',
      'Entkernung einzelner Räume nach großflächigem Schaden',
      'Demontage von Einbauten vor der Sanierung',
    ],
    approachTitle: 'Unsere Vorgehensweise',
    approach:
      'Wir planen den Rückbau so, dass nur entfernt wird, was entfernt werden muss. Demontage-, Rückbau-, Abriss- und Entkernungsarbeiten führen wir kontrolliert und sauber aus – mit Staubschutz, geordneter Baustelle und klarer Abstimmung über Entsorgung und nächste Schritte.',
    advantagesTitle: 'Ihre Vorteile',
    advantages: [
      'Kontrollierter Ausbau statt pauschalem Abriss',
      'Saubere, koordinierte Arbeitsweise',
      'Freilegen betroffener Bauteile für eine wirksame Trocknung',
      'Direkte Vorbereitung der Wiederherstellung',
      'Abstimmung aller Schritte aus einer Hand',
    ],
    steps: [
      'Bewertung der betroffenen Materialien',
      'Abstimmung des Rückbauumfangs',
      'Schutzmaßnahmen und Demontage',
      'Rückbau und geordnete Entsorgung',
      'Übergabe an Trocknung oder Wiederherstellung',
    ],
    faqs: [
      {
        q: 'Muss bei einem Wasserschaden immer der Boden geöffnet werden?',
        a: 'Nein. Ob eine Öffnung nötig ist, hängt vom Aufbau und vom Messergebnis ab. Wir öffnen nur, wo es für Trocknung oder Sanierung erforderlich ist – und besprechen das vorher mit Ihnen.',
      },
      {
        q: 'Wie schützen Sie die übrigen Räume?',
        a: 'Mit Abdeckungen, Staubschutz und einer geordneten Baustelleneinrichtung. Saubere Arbeit gehört bei uns zum Standard – gerade in bewohnten Objekten.',
      },
      {
        q: 'Übernehmen Sie auch die Entsorgung?',
        a: 'Die geordnete Entsorgung der ausgebauten Materialien stimmen wir im Rahmen des Auftrags mit Ihnen ab.',
      },
    ],
    related: [
      { label: 'Wasserschadensanierung', slug: 'wasserschadensanierung' },
      { label: 'Bautrocknung', slug: 'bautrocknung' },
      { label: 'Wiederherstellung', slug: 'wiederherstellung' },
    ],
  },
  {
    slug: 'wiederherstellung',
    label: 'Wiederherstellung',
    group: 4,
    icon: 'wiederherstellung',
    metaTitle: 'Wiederherstellung nach Wasserschaden | SANI Trocknung',
    metaDescription:
      'Räume wieder nutzbar machen: Trockenbau, Maler-, Boden- und weitere Arbeiten – eigene Leistungen und koordinierte Fachgewerke.',
    h1: 'Wiederherstellung: Ihre Räume wieder nutzbar machen.',
    intro:
      'Nach Trocknung und Sanierung folgt der Schritt, auf den Sie warten: Ihre Räume kommen zurück in den nutzbaren Zustand. Mit eigenen Leistungen und koordinierten Fachgewerken begleiten wir Sie bis zur Übergabe.',
    cardText: 'Räume wieder nutzbar machen – mit eigenen Leistungen und koordinierten Fachgewerken.',
    image: {
      file: 'leistung-wiederherstellung',
      alt: 'Wiederhergestellter Wohnraum nach einer Sanierung',
    },
    situations: [
      'Neuaufbau von Böden nach Estrich-Trocknung',
      'Wand- und Deckenflächen nach Rückbau',
      'Malerarbeiten nach Feuchteschaden',
      'Wiedereinbau von Türen und Zargen',
      'Komplette Raum-Wiederherstellung nach größerem Schaden',
    ],
    approachTitle: 'Unsere Leistungen',
    approach:
      'Je nach Schadenbild und Auftrag gehören dazu insbesondere: Trockenbauarbeiten, Putzarbeiten, Malerarbeiten, Bodenbelagsarbeiten, Estricharbeiten, Fliesenarbeiten, Tischlerarbeiten, Türen- und Zargenarbeiten, Montagearbeiten und Reinigungsarbeiten.',
    ownServices: [
      'Trockenbauarbeiten',
      'Putzarbeiten',
      'Malerarbeiten',
      'Bodenbelagsarbeiten',
      'Estricharbeiten',
      'Fliesenarbeiten',
      'Tischlerarbeiten',
      'Türen- und Zargenarbeiten',
      'Montagearbeiten',
      'Reinigungsarbeiten',
    ],
    coordination: {
      title: 'Technische Gewerke und Koordination',
      text: 'Elektro-, Sanitär-, Klempner-, Heizungs- und Installationsarbeiten binden wir als koordinierte Fachgewerke ein. Wir stimmen alle Sanierungs- und Wiederherstellungsschritte aufeinander ab – Sie behalten einen Ansprechpartner.',
    },
    advantagesTitle: 'Ihre Vorteile',
    advantages: [
      'Wiederherstellung im Anschluss an die Sanierung – ohne neue Anbieter-Suche',
      'Breites Leistungsspektrum plus koordinierte Fachgewerke',
      'Aufeinander abgestimmte Reihenfolge der Gewerke',
      'Saubere Übergabe inklusive Endreinigung',
    ],
    steps: [
      'Aufnahme des Wiederherstellungsumfangs',
      'Abstimmung von Materialien und Reihenfolge',
      'Ausführung der Gewerke – eigenes Team und koordinierte Fachbetriebe',
      'Endkontrolle und Reinigung',
      'Übergabe der fertigen Räume',
    ],
    faqs: [
      {
        q: 'Führen Sie auch Wiederherstellungsarbeiten durch?',
        a: 'Ja – von Trockenbau über Maler- bis zu Bodenarbeiten. Der konkrete Umfang richtet sich nach Schadenbild und Auftrag; einzelne Leistungen übernehmen koordinierte Fachgewerke.',
      },
      {
        q: 'Kann ich Materialien selbst auswählen?',
        a: 'Ja. Bodenbeläge, Farben oder Fliesen stimmen wir gemeinsam mit Ihnen ab – im Rahmen dessen, was der Auftrag vorsieht.',
      },
      {
        q: 'Was ist, wenn zusätzlich Elektro- oder Sanitärarbeiten nötig sind?',
        a: 'Dann binden wir die passenden Fachgewerke ein und koordinieren die Termine – Sie müssen nichts selbst organisieren.',
      },
    ],
    related: [
      { label: 'Wasserschadensanierung', slug: 'wasserschadensanierung' },
      { label: 'Rückbau & Abriss', slug: 'rueckbau-abriss' },
      { label: 'Alle Leistungen', slug: '' },
    ],
  },
];

export function getService(slug: string): Service | undefined {
  return servicesData.find((s) => s.slug === slug);
}
