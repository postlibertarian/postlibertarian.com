#!/usr/bin/env python3
"""Replace Jetpack Photon CDN URLs (i*.wp.com) with direct source URLs.

URL patterns handled:
  1. Self-hosted: i0.wp.com/postlibertarian.com/wp-content/... → /wp-content/...
  2. Substack:    i0.wp.com/substackcdn.com/image/fetch/{params}/https%3A//... → decoded S3 URL
  3. External:    i0.wp.com/{host}/{path}?resize=... → https://{host}/{path}

Photon query params (?w=, ?resize=, ?fit=, ?zoom=, ?ssl=, &ssl=, &w=) are stripped.
HTML-encoded ampersands (&amp;) in URLs are handled correctly.
"""

import glob
import os
import re
from urllib.parse import unquote

SITE_DIR = "/home/melgart/dev/postlibertarian.com"

# Matches i0/i1/i2.wp.com URLs, capturing everything after the host.
# Handles both plain & and HTML-entity &amp; in query strings.
PHOTON_RE = re.compile(
    r'https://i[0-2]\.wp\.com/([^"\'<>\s)]+)',
    re.IGNORECASE,
)

# Photon-only query params to strip (others might be meaningful, so we only
# strip the known Photon resize/ssl params).
PHOTON_PARAMS = re.compile(
    r'[?&](w|h|resize|fit|zoom|ssl|strip|quality|amp)=[^&"\'<>\s)]*',
    re.IGNORECASE,
)


def extract_source_url(photon_path: str) -> str:
    """Given the path portion after i*.wp.com/, return the real source URL."""

    # Decode HTML entities so we work with the raw URL text.
    path = photon_path.replace('&amp;', '&')

    # Case 1: self-hosted image
    if path.startswith('postlibertarian.com/'):
        # Strip host, keep path, drop Photon query params
        local = '/' + path[len('postlibertarian.com/'):]
        local = local.split('?')[0]   # drop all query params
        return local

    # Case 2: Substack CDN — the real URL is URL-encoded at the end of the path
    # Pattern: substackcdn.com/image/fetch/{transform}/https%3A//...
    substack_match = re.match(
        r'substackcdn\.com/image/fetch/[^/]+/(https%3A.+?)(?:\?|$)',
        path,
        re.IGNORECASE,
    )
    if substack_match:
        return unquote(substack_match.group(1))

    # Also handle substackcdn without transform params:
    # substackcdn.com/image/fetch/https%3A//...
    substack_match2 = re.match(
        r'substackcdn\.com/image/fetch/(https%3A.+?)(?:\?|$)',
        path,
        re.IGNORECASE,
    )
    if substack_match2:
        return unquote(substack_match2.group(1))

    # Case 3: any other external image — strip Photon host and resize params
    # path = "{host}/{rest}?{photon-params}"
    # Split off query string
    if '?' in path:
        path_part, query = path.split('?', 1)
    else:
        path_part, query = path, ''

    # Reconstruct as https:// URL without Photon resize params
    source = 'https://' + path_part

    # Keep any query params that aren't Photon-specific
    if query:
        remaining = []
        for param in query.split('&'):
            key = param.split('=')[0].lower()
            if key not in ('w', 'h', 'resize', 'fit', 'zoom', 'ssl', 'strip', 'quality'):
                remaining.append(param)
        if remaining:
            source += '?' + '&'.join(remaining)

    return source


def replace_photon(match: re.Match) -> str:
    photon_path = match.group(1)
    return extract_source_url(photon_path)


html_files = glob.glob(os.path.join(SITE_DIR, "**/*.html"), recursive=True)
print(f"Found {len(html_files)} HTML files")

modified = 0
skipped = 0
replacements_total = 0

for path in html_files:
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    original = content

    new_content, count = PHOTON_RE.subn(replace_photon, content)

    if new_content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        modified += 1
        replacements_total += count
    else:
        skipped += 1

print(f"Modified:    {modified} files")
print(f"Unchanged:   {skipped} files")
print(f"Replacements:{replacements_total} URLs rewritten")
