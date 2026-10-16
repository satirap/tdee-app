# TDEE Tracker (ต้น & พัช)

Fat-loss tracker for two people. Static web app on GitHub Pages: https://satirap.github.io/tdee-app/ (repo satirap/tdee-app, branch `main`, deploy = push). The user writes in Thai; answer in Thai.

## Files
- `index.html` – the whole app (HTML + CSS + one ES module, ~2.8k lines). Firebase JS SDK 10.12.2 (gstatic), Chart.js 4.4.1 (cdnjs), Anthropic SDK 0.128.0 (jsdelivr, loaded only for AI).
- `foods-th.js` – `STD_FOODS` reference foods. `firebase-config.js` – public Firebase config. `firestore.rules`.
- `VERSION`, `CHANGELOG.md`, `stamp.sh` – version/build stamp.
- `backups/` – local Firestore backups (gitignored). PIN and backup commands: `CLAUDE.local.md`.

## Data (Firestore `vault/{PIN}/…`)
- `people/{ton|patt}`: profile, goals, `activities`, `entries[]` (weigh-ins), `log{date:[items]}`, `days{date:{kcal,target}}`.
- Log item: `id, foodId?, name, p,c,f,kcal (per serving), qty, amount, unit, unitName, meal ('b'|'l'|'d'), pct?, adj?{p,c,f}, parts?[]` (parts = lines combined into one 🍱 set). Effective values via `eff(x)`.
- `people/{id}` also: `dayType{date:'badminton'|'weights'|'rest'}`, `typeKcal{type:kcal}`, `days[d].est` (planned target when Health replaced it).
- `health/{ton|patt}`: `days{date:{active,resting,at}}` written only by the iPhone Shortcut (REST PATCH, updateMask `days.`date``); the app only reads it.
- `shared/foods`: `foods{id:…, last?{amount,unit}}`, `meals{id:{name,items}}`, `uses`, `hidden`.
- `backups/{date}`: automatic daily copy written by the app.
- Meals are breakfast/lunch/dinner only; old 's' (snack) lines show under "ไม่ระบุมื้อ".

## Version + build date (mandatory, every change)
- Version lives in `VERSION` (semver; bump patch=fix, minor=feature, major=breaking). Add a `CHANGELOG.md` entry `## <version> — <YYYY-MM-DD>` (Thai bullets).
- Run `./stamp.sh` before every commit: it writes `APP_VERSION`/`APP_BUILD` into `index.html`; the footer shows `v… · build …`.
- After the Pages deploy, curl the live page and confirm the stamped version; end the reply with "ตอนนี้เป็น vX · build …".

## Hard rules
- **Never delete or overwrite stored data.** Use the `data-safety` skill: back up → change → compare counts, for every deploy and any data write. Field-level writes only (`updateDoc` / REST `updateMask`).
- **Diagnose before fixing** reported problems (`diagnose-before-fix` skill).
- Keep the UI minimal (no hint texts, search-first). Phone = native-app feel (bottom tab bar, sheets); desktop = standard web layout.
- Wording: above target but under TDEE = "ยังลดอยู่", above TDEE = "พักลด"; amber, not red. Never "เกิน" for kcal. Exception (user, 2026-10-16): calorie chart bars are green inside target ±tol, orange below, red above.

## Test → deploy workflow
1. Copy `index.html foods-th.js firebase-config.js *.png` to the scratchpad `site/`, then stub **every** write: `setDoc(personDoc…)`, `setDoc(backupDoc…)`, shared seed `setDoc(sharedDoc…)`, `sharedWrite`, import `setDoc`. Expose `window.__S`/`__render`. Grep that no `setDoc|updateDoc|deleteDoc(` remains.
2. `preview_start` name `tdee` (port 8000), test with `javascript_tool` at mobile 375×812 and desktop, then a full tab sweep (all tabs × sub-tabs, charts present, no errors).
3. Backup → `git commit` (author `satirap <paritas.ton@gmail.com>`) → push → poll Pages with curl/grep → backup again → `compare`. Report any count change with item names and timestamps.

## Token-saving habits
- Read only the needed lines of `index.html` (grep first, then `sed -n` ranges); never read the whole file.
- Batch browser steps in one `browser_batch`; prefer `javascript_tool` text checks over screenshots; use `zoom` / scale 0.5 when a picture is needed.
- Keep reports short: what changed, how it was tested, data check.
