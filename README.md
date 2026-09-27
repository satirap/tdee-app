# TDEE Tracker — ต้น & พัช

A mini web app for fat loss: record weight, calculate current TDEE (−500 kcal), and track results as a graph.
Static site on GitHub Pages + Firebase (Google login + Firestore).

## Firebase setup (one-time)

1. Go to https://console.firebase.google.com → **Add project** (Google Analytics is not needed)
2. **Build → Authentication → Get started → Sign-in method → Google → Enable**
3. **Build → Firestore Database → Create database** → choose region `asia-southeast1` (Singapore) → **Production mode**
4. **Firestore → Rules** tab → copy the contents of `firestore.rules`, replace
   `YOUR_EMAIL@gmail.com` with the Gmail of the person who records for both → **Publish**
   (only this account can log in; to add people later, change `==` to `in ['a@gmail.com', 'b@gmail.com']`)
5. **Project settings (⚙️) → Your apps → Web (`</>`)** → register an app (Hosting not needed)
   → copy the `firebaseConfig` values into `firebase-config.js`
6. **Authentication → Settings → Authorized domains → Add domain** → `<your-github-username>.github.io`

## Deploy to GitHub Pages

1. Create a new **public** repo on github.com (e.g. `tdee-app`) — don't add a README
2. Push this code (`git push -u origin main`)
3. Repo → **Settings → Pages → Source: Deploy from a branch → `main` / `(root)`** → Save
4. Wait ~1 minute → open `https://<username>.github.io/tdee-app/`

## Local testing

Open via a local server (ES modules won't run from `file://`):

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000 (`localhost` is already an authorized domain in Firebase).

## Data

- `people/ton` and `people/pach` in Firestore — profile, goals, activities, weight entries
- Use the Export button at the bottom of the page to back up to JSON periodically
