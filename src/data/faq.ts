// FAQ-Inhalte 1:1 aus Masterdokument Kap. 9.13, thematisch gruppiert.
// Antworten dürfen interne <a>-Links enthalten.
export interface FaqItem {
  q: string;
  a: string;
}
export interface FaqGroup {
  title: string;
  items: FaqItem[];
}

export const faqGroups: FaqGroup[] = [
  {
    title: 'Im Notfall',
    items: [
      {
        q: 'Was sollte ich unmittelbar nach einem Wasserschaden tun?',
        a: 'Wenn möglich: Wasserzufuhr am Absperrhahn stoppen, Strom in den betroffenen Bereichen abschalten lassen, Möbel und Wertsachen aus dem Nassbereich bringen und den Schaden mit Fotos dokumentieren. Melden Sie den Schaden anschließend – wir besprechen mit Ihnen die nächsten Schritte.',
      },
      {
        q: 'Wen rufe ich bei einem Wasserschaden zuerst an?',
        a: 'Bei akutem Wasseraustritt zuerst: Wasser abstellen. Danach hängt es von der Situation ab: Als Mieter informieren Sie Vermieter oder Hausverwaltung, als Eigentümer Ihre Versicherung. Uns können Sie in jedem Fall rund um die Uhr anrufen – wir helfen Ihnen, die Lage einzuordnen und die richtigen Schritte einzuleiten.',
      },
      {
        q: 'Wie schnell sollte mit der Trocknung begonnen werden?',
        a: 'Möglichst zeitnah. Je länger Feuchtigkeit in Bauteilen bleibt, desto größer das Risiko von Folgeschäden wie Schimmelbildung. Eine frühe Messung schafft Klarheit, ob und wie getrocknet werden muss.',
      },
    ],
  },
  {
    title: 'Ablauf und Dauer',
    items: [
      {
        q: 'Wie wird eine versteckte Leckage gefunden?',
        a: 'Mit einer Kombination moderner Messverfahren grenzen wir den betroffenen Bereich schrittweise ein – möglichst zerstörungsarm. Mehr dazu: <a href="/leistungen/leckageortung/">Leckageortung</a>.',
      },
      {
        q: 'Wie lange dauert eine Bautrocknung?',
        a: 'Je nach Durchfeuchtung, Bauteilen und Bedingungen von wenigen Tagen bis zu mehreren Wochen. Nach der ersten Messung lässt sich die Dauer besser einschätzen. Mehr dazu: <a href="/leistungen/bautrocknung/">Bautrocknung</a>.',
      },
      {
        q: 'Muss bei einem Wasserschaden immer der Boden geöffnet werden?',
        a: 'Nein. Ob eine Öffnung nötig ist, hängt vom Bodenaufbau und den Messergebnissen ab. Wir öffnen nur, wo es erforderlich ist – und stimmen das vorher mit Ihnen ab.',
      },
      {
        q: 'Führen Sie auch Wiederherstellungsarbeiten durch?',
        a: 'Ja – von Trockenbau- über Maler- bis zu Bodenarbeiten, ergänzt um koordinierte Fachgewerke. Mehr dazu: <a href="/leistungen/wiederherstellung/">Wiederherstellung</a>.',
      },
    ],
  },
  {
    title: 'Feuchtigkeit und Schimmel',
    items: [
      {
        q: 'Wie erkenne ich Feuchtigkeit in der Wand?',
        a: 'Anzeichen sind dunkle Flecken, abblätternde Farbe, sich lösende Tapeten, muffiger Geruch oder aufquellende Bodenbeläge. Gewissheit gibt eine <a href="/leistungen/feuchtemessung/">Feuchtemessung</a>.',
      },
      {
        q: 'Wann kann nach einem Wasserschaden Schimmel entstehen?',
        a: 'Bei anhaltender Feuchtigkeit teils schon innerhalb weniger Tage. Deshalb ist eine zeitnahe, kontrollierte Trocknung so wichtig.',
      },
    ],
  },
  {
    title: 'Versicherung und Zusammenarbeit',
    items: [
      {
        q: 'Übernimmt die Versicherung die Kosten?',
        a: 'Das hängt vom konkreten Schadenfall, Ihrem Vertrag und dem Versicherer ab – pauschal lässt sich das nicht zusagen. Unsere Dokumentation des Schadens unterstützt Sie bei der Abwicklung; den Leistungsumfang klären Sie direkt mit Ihrer Versicherung.',
      },
      {
        q: 'Arbeiten Sie mit Hausverwaltungen zusammen?',
        a: 'Ja, regelmäßig. Wir stimmen uns mit Verwaltung, Eigentümern und Mietern ab, halten alle Beteiligten auf dem Laufenden und dokumentieren die Maßnahmen nachvollziehbar.',
      },
      {
        q: 'Sind Sie in ganz Berlin tätig?',
        a: 'Ja – in allen Berliner Bezirken und im näheren Umland, von Potsdam bis Bernau. Alle Orte: <a href="/einsatzgebiete/">Einsatzgebiete</a>.',
      },
    ],
  },
];

// Startseiten-Vorschau: 6 Fragen (Kap. 9.2) – reiner Text ohne Links.
export const faqPreview: FaqItem[] = [
  faqGroups[0].items[0],
  faqGroups[0].items[1],
  faqGroups[0].items[2],
  {
    q: 'Muss bei einem Wasserschaden immer der Boden geöffnet werden?',
    a: 'Nein. Ob eine Öffnung nötig ist, hängt vom Bodenaufbau und den Messergebnissen ab. Wir öffnen nur, wo es erforderlich ist – und stimmen das vorher mit Ihnen ab.',
  },
  {
    q: 'Übernimmt die Versicherung die Kosten?',
    a: 'Das hängt vom konkreten Schadenfall, Ihrem Vertrag und dem Versicherer ab. Unsere Schadendokumentation unterstützt Sie bei der Abwicklung; den Umfang klären Sie direkt mit Ihrer Versicherung.',
  },
  {
    q: 'Sind Sie in ganz Berlin tätig?',
    a: 'Ja – in allen Berliner Bezirken und im näheren Umland, von Potsdam bis Bernau.',
  },
];
