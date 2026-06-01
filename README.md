# atlas-files

Runtime data for **[Atlas](https://github.com/Vatteck/atlas)** — the suggestion lists,
category maps, AppImage database, and Web-app environment that Atlas downloads while it
runs. Atlas fetches these from the **`main`** branch via `raw.githubusercontent.com`.

This repo is a fork of [bauh-files](https://github.com/vinifmor/bauh-files); some folders
are legacy data kept for the sources Atlas disables by default (Snap, Debian, Web).

## What Atlas uses

Atlas is Arch-focused, so the actively-curated data is for **Arch, AUR, Flatpak, and
AppImage**:

| Path | Used by | Purpose |
|------|---------|---------|
| [`arch/suggestions.txt`](arch/suggestions.txt) | Arch gem | suggested apps (one per line, `priority=name`, 3 = top). **Official-repo names only** — Atlas filters suggestions against the repos, so AUR-only names won't appear. |
| [`arch/categories.txt`](arch/categories.txt) | Arch gem | category mapping for Arch packages |
| [`flatpak/suggestions.txt`](flatpak/suggestions.txt) | Flatpak gem | suggested Flatpak apps (`priority=app.id`) |
| [`appimage/suggestions.txt`](appimage/suggestions.txt) | AppImage gem | suggested AppImages (`priority=name`) |
| [`appimage/dbs.tar.gz`](appimage) · [`appimage/apps.txt`](appimage/apps.txt) | AppImage gem | the AppImage database (from [appimage.github.io](https://appimage.github.io)) and its app-name index |

## Legacy / optional (sources off by default in Atlas)

- `snap/` — `suggestions.txt`, `categories.txt`
- `debian/` — `suggestions.txt`, `suggestions_v1.txt`
- `web/` — `env/v2/environment.yml`, `env/v2/suggestions.yml`, and per-site `fix/` scripts
  for the Electron/Nativefier web-app runtime
- `aur/`, `arch/aur_suggestions.txt`, `arch/gpgservers.txt` — inherited from bauh-files;
  not consumed by the current Atlas code paths

## Suggestion file format

Plain text, one entry per line, `priority=name`:

```
3=firefox     # highest priority (shown first / weighted most)
2=gimp
1=blender
0=remmina     # lowest
```

Flatpak entries use the application id (e.g. `3=com.spotify.Client`); Arch/AppImage use the
package/app name.

## Editing

Edit the relevant file, commit, and push to `main`. Atlas caches downloads under
`~/.cache/atlaspm/<gem>/`, so to see changes immediately, delete the cached copy
(`rm ~/.cache/atlaspm/*/suggestions.*`) or wait for the cache to expire.

Licensed under zlib/libpng; see [LICENSE](LICENSE).
