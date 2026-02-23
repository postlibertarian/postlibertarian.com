#!/usr/bin/env python3
"""Generate index.html for all year/month archive directories.

Scans posts, extracts title/date, then writes a themed monthly listing page
for each year/month combination that lacks one.
"""

import os
import re
import glob
import calendar
from datetime import datetime

SITE_DIR = "/home/melgart/dev/postlibertarian.com"
TEMPLATE_FILE = os.path.join(SITE_DIR, "archives/index.html")

# ── Load template ────────────────────────────────────────────────────────────

with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
    template = f.read()

# Split into before-article and after-article sections.
# "before" = everything up to and including the <main> tag
# "after"  = everything from </main> to end of file

main_open = '<main id="main" class="site-main">'
main_close_marker = '</main><!-- .site-main -->'

before_main = template[:template.index(main_open) + len(main_open)]
after_main = template[template.index(main_close_marker):]

# ── Scan posts ────────────────────────────────────────────────────────────────

# Map (year, month) -> list of {title, date, url}
month_posts: dict[tuple, list] = {}

title_re = re.compile(r'<h\d[^>]*entry-title[^>]*>(.*?)</h\d>', re.DOTALL)
datetime_re = re.compile(r'<time[^>]*entry-date[^>]*datetime="([^"]+)"')

# Post paths look like: SITE_DIR/YYYY/MM/DD/slug/index.html
pattern = os.path.join(SITE_DIR, "20[0-9][0-9]/[0-9][0-9]/[0-9][0-9]/*/index.html")

for post_path in glob.glob(pattern):
    rel = os.path.relpath(post_path, SITE_DIR)
    parts = rel.split(os.sep)  # ['YYYY', 'MM', 'DD', 'slug', 'index.html']
    if len(parts) != 5:
        continue
    year, month, day, slug = parts[0], parts[1], parts[2], parts[3]

    with open(post_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    title_m = title_re.search(content)
    dt_m = datetime_re.search(content)

    if not title_m or not dt_m:
        print(f"  SKIP (no title/date): {rel}")
        continue

    title = title_m.group(1).strip()
    dt_str = dt_m.group(1)[:10]  # "YYYY-MM-DD"
    url = f"/{year}/{month}/{day}/{slug}/"

    key = (year, month)
    month_posts.setdefault(key, []).append({
        "title": title,
        "date": dt_str,
        "url": url,
    })

# ── Generate archive pages ────────────────────────────────────────────────────

month_names = list(calendar.month_name)  # index 0 is '', 1 = 'January', etc.

generated = 0
skipped = 0

for (year, month), posts in sorted(month_posts.items()):
    out_dir = os.path.join(SITE_DIR, year, month)
    out_file = os.path.join(out_dir, "index.html")

    if os.path.exists(out_file):
        skipped += 1
        continue

    month_int = int(month)
    month_name = month_names[month_int]
    heading = f"{month_name} {year}"

    # Sort posts newest-first
    posts_sorted = sorted(posts, key=lambda p: p["date"], reverse=True)

    # Build post list HTML
    items = "\n".join(
        f'      <li><a href="{p["url"]}">{p["title"]}</a> — {p["date"]}</li>'
        for p in posts_sorted
    )

    article = f"""


<article class="page type-page status-publish hentry">
	<header class="entry-header">
		<h1 class="entry-title">{heading}</h1>
	</header><!-- .entry-header -->

	<div class="entry-content">
		<ul>
{items}
		</ul>
	</div><!-- .entry-content -->

</article>

"""

    # Build page: replace title, slot in the article
    page = before_main.replace(
        "<title>Archives</title>",
        f"<title>{heading}</title>"
    ) + article + after_main

    os.makedirs(out_dir, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(page)
    generated += 1

print(f"Generated: {generated} archive pages")
print(f"Skipped (already existed): {skipped}")
