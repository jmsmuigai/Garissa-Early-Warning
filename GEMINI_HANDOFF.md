# Hand-off to Gemini – publish CSG Portal v2

The live site for this repo (GitHub Pages, https://jmsmuigai.github.io/Garissa-Early-Warning/) must now serve the
**Garissa County Steering Group portal v2** built by Claude. Do not regenerate or overwrite it with
5_generate_dashboard.py output.

## What is where
| Path | Content |
|---|---|
| `portal/` | The built v2 website (static, works on GitHub Pages). This is what visitors see. |
| `index.html` (root) | Redirects to `portal/` and retires the old GEWAS service worker. |
| `sw.js` | Self-unregistering worker so returning visitors stop getting the cached old page. |
| `legacy/` | The previous GEWAS dashboard, kept for reference. |
| `csg_portal_v2/source/csg-portal/` | Full source: React/Vite frontend, FastAPI backend (Gemini agent), data pipeline, docs. |

## Your task (Gemini)
1. `git add index.html sw.js portal legacy csg_portal_v2/source GEMINI_HANDOFF.md`
2. `git commit -m "Publish Garissa CSG portal v2"` (skip if already committed) and `git push origin main`.
3. Check GitHub → Settings → Pages: source = branch `main`, folder `/ (root)`.
4. After ~2 minutes open https://jmsmuigai.github.io/Garissa-Early-Warning/ and confirm the CSG portal loads
   (header "Garissa County Steering Group", red county boundary on the map, pages Risk map … Report emergency).
5. Do not edit files under `portal/` by hand. To change the site, edit `csg_portal_v2/source/csg-portal/frontend/src`,
   run `npm install && npm run build` in that `frontend` folder, then copy `frontend/dist/*` into `portal/`.
6. Do not commit `.env` or any API key. The Gemini key belongs only in the backend's `.env` on the server.

On GitHub Pages the portal runs in static mode (models from `portal/data/api/*.json`, live weather from Open-Meteo,
built-in assistant). The Gemini assistant, AI translation and stored reports need the backend:
`csg_portal_v2/source/csg-portal/start_portal.command`.
