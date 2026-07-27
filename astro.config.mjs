// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// MagicRedDeer.github.io is a GitHub *user* site → served at the domain root,
// so no `base` path is needed. If this ever becomes a project site, set
// `base: '/repo-name'` and update the deploy workflow accordingly.
export default defineConfig({
  site: 'https://magicreddeer.github.io',
  integrations: [sitemap()],
  markdown: {
    shikiConfig: {
      theme: 'github-dark-dimmed',
      wrap: true,
    },
  },
});
