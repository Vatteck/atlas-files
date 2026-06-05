#!/usr/bin/env python3
"""Generate arch/aur_discovery.json — the AUR discovery buckets consumed by Atlas's Browse view.

The AUR has no category taxonomy and no "browse all / sort by votes" RPC endpoint, so Atlas can't
build discovery buckets from the names index it normally fetches. Instead we precompute them here
from the full metadata dump (packages-meta-ext-v1.json.gz) and Atlas fetches the small result.

Each bucket entry keeps the AUR-RPC-shaped capitalized keys (Name/Version/Description/NumVotes/…) so
Atlas can map them with its existing AURDataMapper — no special-casing on the client.

Stdlib only. Run by .github/workflows/aur-discovery.yml (daily) or by hand:

    python3 arch/generate_aur_discovery.py
"""
import gzip
import json
import os
import urllib.request
from datetime import datetime, timezone

DUMP_URL = 'https://aur.archlinux.org/packages-meta-ext-v1.json.gz'
OUT_PATH = os.path.join(os.path.dirname(__file__), 'aur_discovery.json')

TOP_N = 60
VCS_SUFFIXES = ('-git', '-svn', '-hg', '-bzr', '-cvs', '-darcs')
RECENT_MIN_VOTES = 5  # keep "recently updated" meaningful — the raw feed is dominated by VCS churn

# The fields we keep per entry (RPC-shaped). Anything else in the dump is dropped to stay small.
KEEP_FIELDS = ('Name', 'Version', 'Description', 'NumVotes', 'Popularity',
               'Maintainer', 'OutOfDate', 'LastModified', 'FirstSubmitted', 'URL', 'PackageBase')


def fetch_dump(url=DUMP_URL):
    """Download + gunzip + parse the meta-ext dump into a list of package dicts."""
    req = urllib.request.Request(url, headers={'User-Agent': 'atlas-files-aur-discovery'})
    with urllib.request.urlopen(req, timeout=120) as resp:
        raw = resp.read()
    return json.loads(gzip.decompress(raw))


def slim(pkg):
    return {k: pkg.get(k) for k in KEEP_FIELDS if pkg.get(k) is not None}


def _pop(pkg):
    return pkg.get('Popularity') or 0


def _mtime(pkg):
    return pkg.get('LastModified') or 0


def _votes(pkg):
    return pkg.get('NumVotes') or 0


def build_buckets(pkgs):
    """Compute the discovery buckets from the full package list."""
    name = lambda p: (p.get('Name') or '')

    popular = sorted(pkgs, key=_pop, reverse=True)[:TOP_N]

    recent = sorted((p for p in pkgs if _votes(p) >= RECENT_MIN_VOTES),
                    key=_mtime, reverse=True)[:TOP_N]

    vcs = sorted((p for p in pkgs if name(p).endswith(VCS_SUFFIXES)),
                 key=_pop, reverse=True)[:TOP_N]

    binary = sorted((p for p in pkgs if name(p).endswith('-bin')),
                    key=_pop, reverse=True)[:TOP_N]

    return {
        'popular': [slim(p) for p in popular],
        'recently_updated': [slim(p) for p in recent],
        'vcs': [slim(p) for p in vcs],
        'bin': [slim(p) for p in binary],
    }


def main():
    print(f'Downloading {DUMP_URL} …')
    pkgs = fetch_dump()
    print(f'  {len(pkgs)} AUR packages')
    buckets = build_buckets(pkgs)
    for key, items in buckets.items():
        print(f'  {key}: {len(items)}')
    out = {
        'generated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'source': DUMP_URL,
        'buckets': buckets,
    }
    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write('\n')
    print(f'Wrote {OUT_PATH}')


if __name__ == '__main__':
    main()
