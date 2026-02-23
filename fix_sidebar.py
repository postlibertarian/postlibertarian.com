#!/usr/bin/env python3
"""Fix sidebar widgets across all HTML files:
  Task 1: Remove email subscription widget (blog_subscription-2)
  Task 2: Replace Twitter widget with Threads link (custom_html-2)
  Task 3: Add Calibrations link to Blogroll (linkcat-20)
  Task 4: Remove Meta sidebar section (meta-2)
"""

import os
import re
import glob

SITE_DIR = "/home/melgart/dev/postlibertarian.com"

THREADS_WIDGET = (
    '<aside id="custom_html-2" class="widget_text widget widget_custom_html">'
    '<div class="textwidget custom-html-widget">'
    '<a href="https://www.threads.com/@postlibertarian">Follow @postlibertarian on Threads</a>'
    '</div></aside>'
)

CALIBRATIONS_LI = '<li><a href="https://www.calibrations.blog/" title="Calibrations blog">Calibrations</a></li>\n'

modified = 0
skipped = 0

html_files = glob.glob(os.path.join(SITE_DIR, "**/*.html"), recursive=True)
print(f"Found {len(html_files)} HTML files")

for path in html_files:
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    original = content

    # Task 1: Remove email subscription widget
    content = re.sub(
        r'<aside id="blog_subscription-2".*?</aside>',
        '',
        content,
        flags=re.DOTALL
    )

    # Task 2: Replace Twitter widget with Threads link
    content = re.sub(
        r'<aside id="custom_html-2".*?</aside>',
        THREADS_WIDGET,
        content,
        flags=re.DOTALL
    )

    # Task 3: Add Calibrations as first item in Blogroll
    content = content.replace(
        '<ul class="xoxo blogroll">\n',
        '<ul class="xoxo blogroll">\n' + CALIBRATIONS_LI
    )

    # Task 4: Remove Meta sidebar section
    content = re.sub(
        r'<aside id="meta-2".*?</aside>',
        '',
        content,
        flags=re.DOTALL
    )

    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        modified += 1
    else:
        skipped += 1

print(f"Modified: {modified} files")
print(f"Unchanged: {skipped} files")
