# SiapKerja

SiapKerja adalah aplikasi Android (Jetpack Compose) dengan backend FastAPI untuk simulasi persiapan kerja: review CV oleh AI, simulasi interview (pertanyaan dan feedback), serta career pathway. Dokumen ini merangkum struktur proyek, setup, alur aplikasi, dan referensi API.

## Arsitektur & Teknologi
- **Mobile**: Kotlin, Jetpack Compose, Retrofit + OkHttp logging, Room (riwayat lokal), DataStore (auth & preferensi), CameraX, Activity Result API.
- **Backend**: FastAPI, SQLAlchemy, Pydantic, JWT sederhana, dan integrasi LLM Gemini .
- **Komunikasi**: REST JSON di prefix `/api`.

## Struktur Repository
- `app/` — Aplikasi Android.
  - `data/network` — ApiClient, DbService (auth/user/history), AiService (AI endpoints), TokenProvider.
  - `data/local` — DataStore (auth & user prefs) dan Room DB (riwayat lokal CV/interview/roadmap).
  - `data/repository` — Abstraksi data (auth, profile, cv review, interview, career pathway).
  - `ui/` — Layar Compose: profile, interview, review CV, career, settings.
- `backend/` — FastAPI.
  - `routers/` — ai_router, auth_router, user_router, history_router.
  - `schemas.py` — Pydantic models (request/response).
  - `services/` — AI (Gemini), history.
  - `core/config.py` — konfigurasi.
- `.env` (root) — konfigurasi backend.
- `local.properties` — konfigurasi Android (mis. `GEMINI_API_KEY`).

## Setup Backend (dev)
Prereq: Python 3.11+, Postgres.

```bash
cd backend
python -m venv siapkerja311
source siapkerja311/Scripts/activate  # Windows PowerShell: .\siapkerja311\Scripts\Activate.ps1
pip install -r requirements.txt

# .env contoh (root repo):
# DATABASE_URL=postgresql://postgres:password@localhost:5432/siapkerja --> Default Postgres
# GEMINI_API_KEY=your-key
# GEMINI_MODEL=gemini_model_name --> Change as you wish
# REQUEST_TIMEOUT_SEC=60 --> Change as you wish

uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```
OpenAPI: `http://localhost:8000/docs` (emulator: `http://10.0.2.2:8000/docs`).

## Setup Android
- Buka `app/` di Android Studio, lakukan Gradle sync.
- `local.properties`: tambahkan `GEMINI_API_KEY=...` jika ingin fitur AI.
- Base URL otomatis:
  - Emulator: `http://10.0.2.2:8000/api/`
  - Device fisik: `BuildConfig.API_BASE_URL_PHYSICAL` (ubah di `app/build.gradle.kts` ke IP laptop di LAN, contoh `http://192.168.100.219:8000/api/`).
- Pastikan backend listen `0.0.0.0:8000` dan device/PC satu Wi-Fi (pastikan IP), izinkan port 8000 di firewall.

## Alur Utama Aplikasi
- **Guest mode**: Review CV dan Interview AI bisa jalan; riwayat disimpan lokal (Room). guest_mode di DataStore mengontrol pengalaman tanpa login.
- **Auth (register/login)**: menyimpan token di DataStore; preferensi user (bidang, level, tema) disimpan di UserPreferences; update profil tersinkron ke backend.
- **Review CV**: upload PDF (dibaca lalu dikirim ke AI), hasil disimpan lokal, dikirim ke cloud history jika login.
- **Interview AI**: ambil pertanyaan, kirim jawaban, terima feedback; dukung kamera/mikrofon (STT); riwayat lokal dan cloud (jika login).
- **Career Pathway**: generate roadmap berdasarkan bidang, role, skill; hasil disimpan lokal, dikirim ke cloud jika login.

## Referensi API (ringkas)
Base path: `/api`

### Auth
- `POST /api/db/auth/register`
  - Body: `{ "name", "email", "password", "job_field_preference"?, "experience_level"?, "device_id" }`
  - Resp: `{ user, access_token, refresh_token?, token_type, expires_in }`
- `POST /api/db/auth/login`
  - Body: `{ "email", "password", "device_id" }`
  - Resp sama seperti register.

### User (Bearer)
- `GET /api/db/user`
  - Resp: `{ "user": { id, name, email, job_field_preference?, experience_level?, created_at, updated_at } }`
- `PUT /api/db/user`
  - Body: `{ "name"?, "job_field_preference"?, "experience_level"? }`
  - Resp: `{ "user": { ...updated user... } }`
- `DELETE /api/db/user`
  - Resp: `{ "message": "..." }`

### History (Bearer)
- `GET /api/db/history` -> list `HistoryItem` `{ id, type, data, created_at }`
- `POST /api/db/history`
  - Body: `HistoryItem` (server men-generate id/created_at)
  - Resp: item tersimpan.

### AI
- `POST /api/ai/cv-review`
  - Body: `CvReviewRequest { job_field, target_role?, language="id", cv_file_url?, cv_file_base64? }`
  - Resp: `CvReviewResponse` (overall_score, rating_label, summary, strengths, weaknesses, recommendations, suggested_career_paths?).
- `POST /api/ai/interview-questions`
  - Body: `{ job_field, target_role?, difficulty, language="id", num_questions=5 }`
  - Resp: daftar pertanyaan.
- `POST /api/ai/interview-feedback`
  - Body: `{ job_field, target_role?, difficulty, language="id", question: {id?, text}, answer: {text} }`
  - Resp: skor + strengths + improvements + ideal answer + tips?.
- `POST /api/ai/career-roadmap`
  - Body: `{ job_field, target_role, current_level="ENTRY", known_skills[], language="id" }`
  - Resp: roadmap dengan stages & resources.
- `POST /api/ai/stt-interview` (multipart, file `audio`)
  - Resp: `{ "text": "..." }`

### Token & Keamanan
- JWT sederhana ditandatangani dengan `settings.database_url` (dev only).
- App Android menambahkan header `Authorization: Bearer <token>` jika token ada.
- Network security config mengizinkan cleartext untuk host lokal (10.0.2.2, localhost, 192.168.x.x).

## Penyimpanan Data di App
- **DataStore (AuthPreferences)**: access_token, refresh_token, userId, email, name.
- **DataStore (UserPreferences)**: job_field_preference, experience_level, language, theme_mode, guest_mode.
- **Room**: riwayat lokal CV review, interview session, career roadmap.

## Testing & QA
- Backend: pytest + FastAPI TestClient, mock panggilan Gemini; uji auth (valid/invalid token) dan AI endpoints (happy path + error).
- Android: unit test ViewModel/repository dengan `kotlinx-coroutines-test` + fake data sources; instrumented test alur guest dan auth; cek DataStore/Room integrasi.

## Tips Dev
- Jika IP laptop berubah, perbarui `API_BASE_URL_PHYSICAL` yang ada di `app/build.gradle.kts` lalu rebuild APK (emulator tetap 10.0.2.2).
- Jalankan backend dengan `--host 0.0.0.0` agar device fisik bisa terhubung; pastikan firewall tidak memblokir port 8000.
- OkHttp logging sudah aktif (Level.BODY) untuk debug jaringan.
