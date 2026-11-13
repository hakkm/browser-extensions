# Local browser extensions

One Git repository for the local extensions used on both laptops. Each project
lives under `extensions/`, including any native helpers and its own instructions.
Extension manifests are the index; no separate list needs updating.

## Set up each laptop

1. Put this repository in a permanent location, preferably
   `~/work/browser-extensions` on both laptops. Move it there before loading any
   extensions. Avoid loading from a temporary scratch directory.
2. Run `python3 scripts/list.py` to list the names and absolute load paths.
3. Open `brave://extensions` (or `chrome://extensions`), enable **Developer mode**,
   and select **Load unpacked** for each path printed. This is a one-time step
   per extension and browser profile.
4. Follow each project's README for native helper installation where required.

The included projects were copied from `~/work/tries/config` as starting points.
The originals and the current browser setup have not been changed. After loading
these copies, edit the versions in this repository going forward. The device
setup bundle still contains its old copies; do not use it to overwrite newer
extension code from this repository.

### Included extensions

- `extensions/youtube-music-control`: load this folder. Its desktop helper
  currently uses the existing device setup bundle; see its README. Loading the
  extension here alone does not relocate the desktop shortcut or register a host.
- `extensions/native-messaging-demo`: load its `extension/` subfolder, then run
  `python3 extensions/native-messaging-demo/register.py EXTENSION_ID` on each
  laptop to register its local helper. See its README for details.

Do not enable an old and new copy of the same extension together. For an extension
with native messaging, keep its manifest key if present and follow its host setup
instructions when changing paths.

## Sync changes

This repository is public. Add its Git remote once on this laptop:

```sh
git remote add origin YOUR_REPOSITORY_URL
git add .
git commit -m "Organize local browser extensions"
git push -u origin main
```

On the second laptop:

```sh
git clone YOUR_REPOSITORY_URL ~/work/browser-extensions
cd ~/work/browser-extensions
python3 scripts/list.py
```

Before editing on either laptop, run `git pull --ff-only`. After editing:

```sh
git add extensions
git commit -m "Describe the extension change"
git push
```

On the other laptop, run `git pull --ff-only`, then click **Reload** on each
changed extension's card. Finish pushing on one laptop before editing on the
other. If a pull reports diverged history, resolve it before continuing; do not
force push over the other laptop's changes.

## Add another extension

Put its source in `extensions/short-descriptive-name/`, run
`python3 scripts/list.py`, then commit and push. Load it once on each laptop.
For projects with a build step, follow their README and load the built folder;
keep only one manifest intended for loading in the source tree where practical.

Git syncs source files. Browser registration, extension storage/settings,
permissions, native-host registrations and desktop shortcuts are per laptop.
Keep browser profiles, account data and private signing keys out of this repo.
No custom sync service, background daemon or browser-profile copying is needed.
