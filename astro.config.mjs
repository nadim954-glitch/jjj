import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { site } from './src/config/site.ts';

// Statische Ausgabe (reines HTML/CSS + minimales JS), hostingunabhängig.
// baseUrl ist zentral konfiguriert und vor Launch zu prüfen (PH-08 / Domain).
export default defineConfig({
  site: site.baseUrl,
  output: 'static',
  trailingSlash: 'always',
  build: {
    format: 'directory',
  },
  integrations: [
    sitemap({
      // 404 nicht in die Sitemap aufnehmen
      filter: (page) => !page.includes('/404'),
    }),
  ],
  // Kein externes CSS/JS, keine Fremd-CDNs – Datensparsamkeit im Auslieferungszustand.
});
