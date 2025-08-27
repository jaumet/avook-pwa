# ✅ Roadmap Audiovook — Monorepo `avook-pwa` (Frontend + Backend + Infra)

> **Objectiu:** PWA en React + API FastAPI + PostgreSQL + S3/MinIO, tot al mateix repositori i aixecat amb Docker Compose.

## 📁 Estructura del repo
- [ ] `/frontend/` — PWA (React).
- [ ] `/backend/` — API (FastAPI).
- [ ] `/infra/` — compose, init, scripts locals.
- [ ] `/docs/` — arxiu tècnic, fluxos, UX copies.
- [ ] `README.md` — arrencada en local amb Docker.
- [ ] `CHECKLIST.md` — aquest fitxer.

## 🔧 Serveis (ports locals suggerits)
- [ ] **frontend** (5173) — parla amb `http://api:8000`.
- [ ] **api** (8000) — FastAPI.
- [ ] **db** (5432) — PostgreSQL (volum de dades).
- [ ] **object-store** (9000/9001) — MinIO S3.
- [ ] **proxy** (8080) — NGINX per HLS/CORS/Range.

## 🌱 Fase A — Bootstrap del monorepo
- [x] Crear carpetes i fitxers base (README, CHECKLIST, docs).
- [x] `.env.example` per `frontend`, `backend`, `infra`.
- [x] Docker Compose amb serveis (sense codi d’app encara).
- [x] Health checks bàsics per serveis.
**DoD:** `docker compose up` aixeca tots els contenidors i responen ping/health.

## 🗃️ Fase B — Model de dades (PostgreSQL)
- [x] `admin_users`: id, email, password_hash, role (`owner|editor`), timestamps.
- [x] `titles`: id, slug, title, author, language, duration_sec, cover_path, status.
- [x] `products`: id, title_id FK, sku/ean, price_cents, notes.
- [x] `batches`: id, product_id FK, name, size, printed_at, notes.
- [x] `qr_codes`: id, product_id FK, qr (únic), owner_pin_hash, batch_id FK, state (`new|active|blocked`), created_at.
- [x] `device_bindings`: qr FK, device_id, created_at, last_seen_at, active.
- [x] `listening_progress`: qr FK, device_id, position_sec, chapter_id?, updated_at.
- [x] Índexos clau i migracions inicials.
**DoD:** migracions aplicades; `db` llesta per API.

## 🌐 Fase C — API pública (sense registre d’usuari final)
- [x] `GET /abook/{qr}/play-auth?device_id=...` → signed URL + `start_position`.
- [x] `POST /abook/{qr}/progress` → desa posició i actualitza `last_seen_at`.
- [x] `POST /abook/{qr}/recover` → amb `owner_pin`, allibera 1 slot o reset.
- [x] Job **neteja** dispositius inactius (> X dies).
**DoD:** proves amb curl/Postman; límit 2 dispositius; resume correcte.

## ☁️ Fase D — S3/MinIO + Proxy (HLS)
- [x] Bucket privat + policies; CORS habilitat.
- [x] Estructura: `hls/{book_id}/...`, `covers/{book_id}.jpg`, `manifests/{book_id}.json`.
- [x] Signatura d’URL per `master.m3u8` (TTL curt).
- [x] NGINX: `Accept-Ranges`, CORS, `Cache-Control` (curt per `.m3u8`, més llarg segments).
**DoD:** reproducció HLS funcional via proxy amb URL signada.

## 📱 Fase E — Frontend PWA (React)
- [x] PWA (`manifest.json`, Service Worker, instal·lable).
- [ ] Multillengua (CA/ES/EN).
- [x] Pantalles: Home, Escàner QR, Player, Errors/Estats, Recuperació PIN.
- [ ] Player HLS (`hls.js`) + `MediaSession` mòbil.
- [x] `device_id` web amb WebCrypto (clau privada no-extractable) + IndexedDB.
- [ ] Enviament `progress` periòdic (20–30 s i en pausa).
**DoD:** 2 dispositius OK, tercer bloquejat; resume precís; UX clara.

## 🛠️ Fase F — API d’Administració (backend)
- [ ] `/admin/login` (sessió o JWT).
- [ ] CRUD **admin_users** (només `owner` pot crear/editors).
- [ ] CRUD **titles** i **products**.
- [ ] **Batches/QR**: generar N QR + PIN (hash), export CSV (només en generació).
- [ ] **QR detall**: estat, dispositius vinculats, alliberar/reset.
**DoD:** admins poden crear catàleg, lots i gestionar QR/dispositius.

## 🖥️ Fase G — Panell d’Administració (frontend)
- [ ] Login admin.
- [ ] Vistes: Títols, Productes, Lots/QR, Detall QR, Usuaris admins.
- [ ] Pujar portada i vincular manifest `book_id`.
**DoD:** flux complet d’admin operatiu.

## 🔐 Fase H — Operacions i seguretat
- [ ] Rate limiting suau en `/abook/*`.
- [ ] Logs API i proxy; mètriques bàsiques.
- [ ] Backups de DB i versions de manifests.
- [ ] Pàgina legal (RGPD: no recollim dades personals d’usuaris finals).
**DoD:** proves d’estrès locals i simulació de reinici recuperable.

## 🚀 Fase I — Alpha interna
- [ ] Carregar 2–3 llibres (HLS, manifest, portada).
- [ ] Validar: targeta nova → 2 dispositius → resume → recuperació PIN.
- [ ] Informe QA i millores pendents.
**DoD:** fluxos reals validats en local.

---

### 📋 Regles de negoci
- **Fins a 2 dispositius actius per QR** (bindings).
- **Resume** per QR (última posició global entre dispositius actius).
- **Recuperació** amb **PIN** físic; caducitat automàtica d’slots per inactivitat.
- **Admins** amb rols (`owner|editor`) gestionen títols, productes, lots i QR.

---

### 🧪 PRs — què ha d’incloure cada PR
- Fase i sub-tasca del checklist.
- Canvis realitzats i fitxers afectats.
- Com provar-ho (URLs locals, passos).
- Resultat esperat (DoD) + checks (✅/🚧/❌).
- Riscos/regressions i pla de rollback.
