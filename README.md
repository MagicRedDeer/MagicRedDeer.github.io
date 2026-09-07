# MagicRedDeer.github.io — portfolio

Personal portfolio for Talha Ahmed (Pipeline & Automation Engineer · Technical Artist), built with
[Astro](https://astro.build). Clean, ATS-adjacent, fast, dark/light.

## Local development

```bash
npm install
npm run dev       # http://localhost:4321
npm run build     # outputs to ./dist
npm run preview   # preview the production build locally
```

## Content

- **Projects** — `src/content/projects/*.md` (frontmatter: title, description, order, featured, role, period, tech[], links[])
- **Writing** — `src/content/blog/*.md` (frontmatter: title, description, date, tags[], draft, series, seriesOrder)
  - Set `draft: true` to keep a post out of the production build.
- **Résumé PDFs** — `public/resume/` (`Talha_Ahmed_Resume.pdf`, `Talha_Ahmed_Resume_SoftwareEngineer.pdf`).
  Regenerate from `../resume/resume-cg-pipeline.typ` and `../resume/resume-swe.typ` and copy them here.

## Deploying to GitHub Pages

This repo is intended to be the **user site** `MagicRedDeer.github.io`, served at the domain root.

1. Create the repo `MagicRedDeer/MagicRedDeer.github.io` on GitHub.
2. In **Settings → Pages**, set **Source = GitHub Actions**.
3. Push to `main`. The workflow in `.github/workflows/deploy.yml` builds and deploys automatically.

See `DEPLOY.md` in the parent folder for the exact first-push commands.

## NDA note

The five articles in the "Engineering an OpenUSD asset pipeline" series describe the **Epic Games
(Quixel) Megascans → OpenUSD** work in full. **NDA cleared 2026-09-06**: product name and exact
counts (20,637 assets, ~92%, six material types, ~110 QA rules, 30+ asset classes, 78.7% → 98.9%)
are fine to publish. Do not soften them back into generalized posture unless the user records a
new NDA decision in `evidence-bank.md`.
