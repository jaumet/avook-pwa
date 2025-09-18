# CHECKLIST.md — Audiovook (Access Manager + Player)

> Versió: 1.0 (MVP Parts 1 i 2)  
> Abast: Gestor d’accés (URL/QR) i Player PWA amb progrés d’escolta.  
> Repo recomanat: `avook.pwa` (mono‑repo) — **des de zero**.

---

## 0) Prerequisits

- [ ] **Domini**: `play.audiovook.com` in local will work as ""/play""
- [ ] **Entorn local**: Docker + Docker Compose, Make, Node 20+, Python 3.12+
- [ ] **Secrets**: definir `.env` a partir de `.env.example`
- [ ] **Decisions** (confirmades):
  - [x] Subdomini: `play.audiovook.com/t/{token}`
  - [x] Login lleuger: Google/Apple + OTP (guest opcional)
  - [x] Sampler 5–10 min sense login
  - [x] Emmagatzematge LocalFS → preparat per S3
  - [x] WooCommerce → webhook a `/api/shop/purchase`
  - [x] Frontend **SvelteKit** + `svelte-i18n`
  - [x] Backend **FastAPI** + PostgreSQL + Redis

---

## 1) Estructura del repo

```
avook.pwa/
  apps/
    api/            # FastAPI
      app/
        api/        # access.py, play.py, preview.py, auth.py, shop.py
        core/       # config, security, rate_limit
        models/     # qr, account, device, binding, progress, session
        services/   # storage/{base,local,s3}, media_signer, oauth, otp, sampler
      tests/
    web/            # SvelteKit (PWA Player)
      src/
        routes/
          access/
          player/
          error/
        lib/i18n/   # ca.json, es.json, en.json
        lib/api.ts
  infra/
    docker-compose.yml
    nginx/default.conf
  .github/workflows/ci.yml
  .env.example
  Makefile
  README.md
```

- [x] Crear arbre anterior i fer **commit inicial** (branch `main`).

---

## 2) Infra i arrencada

- [x] **Docker Compose** amb serveis: `db` (Postgres), `cache` (Redis), `api`, `web`, `nginx` (i `minio` opcional)
- [x] **Makefile** amb objectius:
  - [x] `make dev` — aixeca serveis
  - [x] `make test` — executa tests
  - [x] `make format` — lint/format (ruff, black, prettier)
  - [x] `make seed` — dades de prova

**Comandes d’exemple**
```bash
docker compose -f infra/docker-compose.yml up --build
make dev
make test
```

**.env.example (claus principals)**
```
POSTGRES_USER=avook
POSTGRES_PASSWORD=avook
POSTGRES_DB=avook
REDIS_URL=redis://cache:6379/0

JWT_SECRET=change-me
HMAC_MEDIA_SECRET=change-me-too

OAUTH_GOOGLE_CLIENT_ID=
OAUTH_GOOGLE_CLIENT_SECRET=
OAUTH_APPLE_TEAM_ID=
OAUTH_APPLE_KEY_ID=
OAUTH_APPLE_PRIVATE_KEY=

S3_ENDPOINT=
S3_ACCESS_KEY=
S3_SECRET_KEY=
S3_BUCKET=
```

- **Criteris d’acceptació**:
  - [x] `GET /health` de l’API retorna `200`
  - [x] `web` serveix `/` i assets

---

## 3) Model de dades (PostgreSQL)

- [ ] Crear models i migració #1:
  - [ ] `qr_code(id uuid pk, token text unique, status enum('new','active','blocked'), product_id int, batch_id int, created_at, registered_at, max_reactivations int default 999, cooldown_until timestamptz null)`
  - [ ] `account(id uuid pk, email text unique null, provider enum('google','apple','otp','guest'), created_at)`
  - [ ] `device(id uuid pk, account_id uuid null, ua_hash text, created_at)`
  - [ ] `qr_binding(qr_id uuid fk, device_id uuid fk, account_id uuid null, active bool, created_at, revoked_at null)`
  - [ ] `play_session(id uuid pk, qr_id, device_id, started_at, ended_at null, ip_hash text)`
  - [ ] `listening_progress(qr_id, account_id null, device_id, track_id text, position_ms int, updated_at, primary key(qr_id, device_id, track_id))`
  - [ ] Índexos: `idx_qr_token`, `idx_progress_updated_at`, `idx_binding_qr_active`
- [ ] **Seed**: crear `qr_code` de prova amb `token` dummy

- **Criteris d’acceptació**:
  - [ ] Migracions aplicables a entorn net i existent
  - [ ] Seed crea com a mínim 3 QR vàlids

---

## 4) Access Manager (API)

### Endpoints
- [ ] `POST /api/access/validate`
  - **Req**: `{ "token": "abc", "device_id": "uuid" }`
  - **Res**: `{ "status": "new|registered|invalid|blocked", "can_reregister": true, "cooldown_until": "ISO", "preview_available": true, "product": {"id":1,"title":"…"} }`
- [ ] `POST /api/access/register` (primer vincle)
  - **Req**: `{ "token": "abc", "device_id": "uuid", "account_id": "uuid|null" }`
- [ ] `POST /api/access/reregister` (moure binding a nou device)
  - **Req**: `{ "token": "abc", "new_device_id": "uuid" }`
- [ ] **Rate limits** Redis: `/api/access/*` → 30 req/min per IP
- [ ] **Polítiques**:
  - [ ] **Sessió concurrent única** per `qr_id` (expulsa antigues al `play-auth`)
  - [ ] **Quota dispositius** per `qr` (p. ex. 3)
  - [ ] **Cooldown** 48 h si >3 re-registres en 24 h
- [ ] **Logs estructurats**: `request_id`, `token_hash`, `device_id`, `ip_hash`, `event_type`

- **Criteris d’acceptació**:
  - [ ] Tests unit/integ: nous, registrats, invalids, cooldown i rate-limit
  - [ ] Logs JSON amb camps requerits

---

## 5) Player Auth & Progress (API)

- [ ] `POST /api/play-auth`
  - **Req**: `{ "token": "abc", "device_id": "uuid" }`
  - **Res**: `{ "media": { "type":"hls", "url":"https://…/playlist.m3u8?sig=…" }, "start_position_ms": 73422, "tracks":[{ "id":"t1", "title":"Capítol 1", "duration_ms":600000 }] }`
  - [ ] **Signed URL** efímera (60–180 s), device‑bound
  - [ ] En forçar sessió única, marca sessions antigues com a tancades
- [ ] `POST /api/progress`
  - **Req**: `{ "token":"abc", "device_id":"uuid", "track_id":"t1", "position_ms":81234 }`
  - **Res**: `204` — upsert `listening_progress`

- **Criteris d’acceptació**:
  - [ ] Reprendre reproducció a la posició guardada
  - [ ] Expiració de URL signada → el client la renova sense perdre estat

---

## 6) Preview / Sampler (API)

- [ ] `GET /api/preview/manifest.m3u8?token=…`
  - [ ] Generar playlist amb només els primers 5–10 min
  - [ ] Signatura curta i expiració curta (60–120 s)
  - [ ] Throttling: 10 req/min per IP

- **Criteris d’acceptació**:
  - [ ] Sense login es pot escoltar el sampler
  - [ ] La URL del sampler no és reutilitzable fora de finestra

---

## 7) Web (SvelteKit PWA)

- [ ] Rutes: `/access?token=…`, `/player`, `/error`
- [ ] `svelte-i18n` (CA/ES/EN) i **DejaVu Sans**
- [ ] **DeviceID**: UUID v4 guardat a `localStorage`
- [ ] **Access flow**:
  - [ ] Cridar `validate` i mostrar CTA segons estat (nou/registrat/re‑registrar/preview)
- [ ] **Player**:
  - [ ] `play-auth`, inicialitzar a `start_position_ms`
  - [ ] Autosave cada 15–30 s i en `pause`/`visibilitychange`
  - [ ] Renovació silenciosa de signed URL
- [ ] **A11y**:
  - [ ] Controls ≥44px, contrast AA, focus visible
  - [ ] Tecles: Space (play/pause), ←/→ (±10s), ↑/↓ (volum), `h` (ajuda)
- [ ] **PWA** (Workbox): offline només UI (sense àudio)

- **Criteris d’acceptació**:
  - [ ] Flux complet: QR → access → player → resume
  - [ ] Playwright E2E passa en CI

---

## 8) Auth lleuger

- [ ] OAuth Google/Apple (PKCE)
- [ ] OTP magic link (email) i mode guest
- [ ] Cookies httpOnly + **JWT curt (15–30 min)** + **refresh (1–7 dies)**
- [ ] Enllaç `account_id` ↔ `device_id` en login

- **Criteris d’acceptació**:
  - [ ] Login/out estable
  - [ ] Guest pot promoure’s a compte amb OTP/OAuth sense perdre progrés

---

## 9) Streaming

- [ ] MVP: HTTP Range (via Nginx; opcional `X-Accel-Redirect`) + firma HMAC
- [ ] HLS preparat (packager i playlists); **Storage provider** (`local|s3`)

- **Criteris d’acceptació**:
  - [ ] Reproducció estable local
  - [ ] Canvi a S3 via ENV sense canvis de codi d’app

---

## 10) Hardening, CI i docs

- [ ] CORS i CSP bàsica
- [ ] Rotació de claus HMAC/JWT (`kid`)
- [ ] 429 per rate limits i pàgina d’error amable
- [ ] GitHub Actions: lint + tests + build imatges
- [ ] README: setup local, `.env`, rutes de prova, troubleshooting

- **Criteris d’acceptació**:
  - [ ] CI verd en PRs principals
  - [ ] Documentació suficient per al nou dev

---

## 11) Definició global de “Done” (MVP Parts 1 i 2)

- [ ] **Access Manager**: validar/register/re‑register amb polítiques de sessions, quota i cooldown
- [ ] **Player**: play‑auth, resume, autosave, renovació de signed URL
- [ ] **Preview**: sampler 5–10 min sense login, segur i limitat
- [ ] **Web PWA**: flux complet i E2E passant
- [ ] **Infra**: docker up, `.env`, tests i CI funcionals
- [ ] **Logs**: JSON amb `request_id`, `token_hash`, `device_id`, `ip_hash`

---

## 12) Issues recomanades (crear al repo)

- [ ] Fase A — Bootstrap i infra (docker, make, health)
- [ ] Models i migració #1 (DB)
- [ ] Endpoints Access: validate/register/reregister + rate limits
- [ ] Player: play-auth i progress
- [ ] Preview/sampler
- [ ] Web: access i player (UI + i18n + A11y)
- [ ] Auth lleuger (OAuth/OTP, sessions)
- [ ] Streaming MVP (Range + sign)
- [ ] Provider S3
- [ ] Hardening + CI + README
