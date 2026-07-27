# Deploying the portfolio to MagicRedDeer.github.io

The site is a GitHub **user site**, so it must live in a repo named exactly
**`MagicRedDeer.github.io`** and is served at `https://magicreddeer.github.io/`.
Deployment is automated by `.github/workflows/deploy.yml` (build with Astro → publish to Pages).

## One-time setup

### 1. Create the repo
On GitHub, create a new **empty** repository: `MagicRedDeer/MagicRedDeer.github.io`
(no README/license — keep it empty so the first push is clean).

### 2. Push this folder as the repo root
From `D:\Talha\resume-cv\portfolio`:

```bash
git init
git branch -M main
git add .
git commit -m "Portfolio: Astro site, projects, and OpenUSD pipeline writing"
git remote add origin https://github.com/MagicRedDeer/MagicRedDeer.github.io.git
git push -u origin main
```

> The `.gitignore` already excludes `node_modules/`, `dist/`, and `.astro/`.

### 3. Turn on Pages via Actions
On GitHub: **Settings → Pages → Build and deployment → Source = GitHub Actions**.
(That's it — no branch to pick; the workflow handles publishing.)

### 4. Watch the deploy
The **Actions** tab shows the "Deploy to GitHub Pages" run. When it's green, the site is live at
<https://magicreddeer.github.io/>.

## Updating the site later

```bash
# edit content in src/content/... then:
git add -A
git commit -m "New post: <title>"
git push
```

Every push to `main` rebuilds and redeploys automatically. To preview before pushing:

```bash
npm run dev       # http://localhost:4321
```

## If you'd rather I do it via the gh CLI

If your `gh` CLI is logged in as `MagicRedDeer`, I can create the repo, push, and enable Pages for
you — just say the word and I'll run it (I'll confirm before the push, since it acts on your
GitHub account).

## Custom domain (optional, later)

To use a custom domain, add a `public/CNAME` file containing the domain and configure it in
Settings → Pages. Not needed for the `magicreddeer.github.io` address.
