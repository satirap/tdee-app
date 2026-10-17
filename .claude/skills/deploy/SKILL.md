---
name: deploy
description: Test and deploy the TDEE app (index.html etc.) to GitHub Pages. Use before any commit to main / deploy, or when asked to test the app in a browser.
---

# Deploy TDEE app

## 0. Where am I?
- `CLAUDE.local.md` exists (user's machine) → full flow below.
- Not found (cloud session) → do steps 1–2 with Playwright (Chromium at `/opt/pw-browsers`), then commit + push the session branch only. **No backup, no data write, no push to `main`.** Tell the user to deploy from their machine.

## 1. Build a safe test copy
- Copy `index.html foods-th.js firebase-config.js *.png` to the scratchpad `site/`.
- Stub **every** write: `setDoc(personDoc…)`, `setDoc(backupDoc…)`, shared seed `setDoc(sharedDoc…)`, `sharedWrite`, import `setDoc`.
- Expose `window.__S` / `__render`.
- `grep -nE 'setDoc|updateDoc|deleteDoc\(' site/index.html` → must be no live write left.

## 2. Test
- Desktop app: `preview_start` name `tdee` (port 8000), check with `javascript_tool`. Cloud: `python3 -m http.server 8000` + Playwright.
- Mobile 375×812 and desktop.
- Full tab sweep: all tabs × sub-tabs, charts present, no console errors.
- Batch steps; prefer text checks over screenshots.

## 3. Deploy (user's machine only)
1. Backup (commands in `CLAUDE.local.md`, `data-safety` skill).
2. Bump `VERSION` + `CHANGELOG.md`, run `./stamp.sh`.
3. `git commit` (author `satirap <paritas.ton@gmail.com>`) → push `main`.
4. Poll https://satirap.github.io/tdee-app/ with curl/grep until the stamped version shows.
5. Backup again → `compare`. Report any count change with item names and timestamps.
6. End the reply with "ตอนนี้เป็น vX · build …".
