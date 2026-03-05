# postlibertarian.com — Developer Context

## What this is
A **static site** exported from a WordPress installation using the [Simply Static](https://wordpress.org/plugins/simply-static/) plugin. It is **not** a live WordPress install — all pages are pre-rendered HTML files. No PHP, no database, no server-side processing.

## Deployment
- Hosted on **GitHub Pages** from the `main` branch, custom domain `postlibertarian.com` (set via `CNAME` file).
- No CI/CD pipeline. Deploying = committing to main and pushing.
- `git push origin main` → live within seconds/minutes via GitHub Pages.

## Site structure
```
/                         → index.html (homepage)
/YYYY/MM/DD/post-slug/    → individual post pages
/category/slug/           → category archive pages
/tag/slug/                → tag archive pages
/author/slug/             → author archive pages
/page/N/                  → paginated index pages
/wp-content/uploads/      → locally hosted images and media
/wp-content/themes/       → twentyfifteen-child theme CSS/JS
/wp-includes/             → WordPress core CSS/JS (static copies)
/pagefind/                → Pagefind search index and JS
/search.html              → search page (uses Pagefind)
```

## Theme
`twentyfifteen-child` — a child theme of WordPress's Twenty Fifteen. CSS customizations live in `wp-content/themes/twentyfifteen-child/`.

## Maintenance scripts
These Python scripts live at the site root and are run manually when needed:

| Script | Purpose |
|---|---|
| `fix_sidebar.py` | Patches sidebar widgets across all HTML files (removes email widget, adds Threads link, adds Calibrations to blogroll, removes Meta section) |
| `fix_photon_urls.py` | Rewrites Jetpack Photon CDN URLs (`i*.wp.com`) to direct source URLs. Self-hosted images become local paths; Substack/external images become direct HTTPS URLs. Run this after any new Simply Static export. |
| `generate_archives.py` | Generates monthly archive index pages |

## Re-exporting from WordPress
If the WordPress source is ever updated and a new static export is needed:
1. Run Simply Static in WordPress to export
2. Copy output here
3. Run `fix_sidebar.py` to restore sidebar customizations
4. Run `fix_photon_urls.py` to fix Jetpack Photon CDN URLs
5. Run `generate_archives.py` if new months have posts
6. Commit and push

## Known issues / notes
- **Tweet embeds**: Two patterns exist in the HTML:
  - `<blockquote class="twitter-tweet">` **with** `<script src="https://platform.twitter.com/widgets.js">` inline — these render as live X.com embed cards (~46 instances).
  - `<blockquote class="twitter-tweet">` **without** widgets.js — these show as plain blockquotes (~20 instances in individual post pages). WordPress used to inject the script server-side; the static export didn't preserve it. Fix: add widgets.js to those pages.
- **Substack cross-posts**: Images from Substack are served directly from `substack-post-media.s3.amazonaws.com` after the Photon fix. These are external URLs and could theoretically break if Substack changes their CDN.
- **Pagefind search**: The `/pagefind/` index was built at export time. If new posts are added, the index needs to be rebuilt with `npx pagefind --site .` from the site root.

## Content
Blog by @postlibertarian. Topics: libertarianism, politics, economics, technology, prediction markets. Has a companion Substack at calibrations.blog. Some posts are cross-posted from Substack.
