// Navigationsstruktur (zentral). Reihenfolge gemäß Masterdokument Kap. 7.2.
export const services = [
  { slug: 'leckageortung', label: 'Leckageortung' },
  { slug: 'feuchtemessung', label: 'Feuchtemessung' },
  { slug: 'bautrocknung', label: 'Bautrocknung' },
  { slug: 'wasserschadensanierung', label: 'Wasserschadensanierung' },
  { slug: 'schimmelbeseitigung', label: 'Schimmelbeseitigung' },
  { slug: 'rueckbau-abriss', label: 'Rückbau & Abriss' },
  { slug: 'wiederherstellung', label: 'Wiederherstellung' },
] as const;

export const mainNav = [
  {
    label: 'Leistungen',
    href: '/leistungen/',
    children: [
      { label: 'Alle Leistungen', href: '/leistungen/' },
      ...services.map((s) => ({ label: s.label, href: `/leistungen/${s.slug}/` })),
    ],
  },
  { label: 'Einsatzgebiete', href: '/einsatzgebiete/' },
  { label: 'Über uns', href: '/ueber-uns/' },
  { label: 'FAQ', href: '/faq/' },
  { label: 'Kontakt', href: '/kontakt/' },
] as const;
