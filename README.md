# SiapKerja

Aplikasi mobile (Android, Jetpack Compose) + backend (FastAPI) untuk simulasi persiapan kerja: review CV, interview AI, career pathway. Ini adalah dokumen ringkas untuk developer.

## Struktur
- `app/` – Android app (Compose, CameraX, Retrofit, Room, DataStore).
- `backend/` – FastAPI + Postgres/SQLite + Gemini AI wrapper.
- `.env` (root) – konfigurasi backend (lihat di bawah).
- `local.properties` – konfigurasi Android (mis. `GEMINI_API_KEY` untuk app).

## Menjalankan Backend (dev)
Prereq: Python 3.11+, Postgres (opsional, bisa SQLite).

```bash
cd backend
python -m venv siapkerja311
source siapkerja311/Scripts/activate  # Windows Git Bash / PowerShell: .\siapkerja311\Scripts\Activate.ps1
pip install -r requirements.txt

# .env di root repo, contoh:
# DATABASE_URL=postgresql://postgres:password@localhost:5432/siapkerja
# GEMINI_API_KEY=your-key (opsional)
# GEMINI_MODEL=gemini-2.0-flash

uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```
OpenAPI docs tersedia di `http://localhost:8000/docs` (atau `http://10.0.2.2:8000/docs` dari emulator).

## Menjalankan Android App
- Buka di Android Studio, lakukan Gradle sync.
- Pastikan `local.properties` berisi `GEMINI_API_KEY=...` jika ingin analisis CV via Gemini.
- Base URL otomatis:
  - Emulator: `http://10.0.2.2:8000/api/`
  - Device fisik: `BuildConfig.API_BASE_URL_PHYSICAL` (ubah di `app/build.gradle.kts` ke IP laptop di LAN, mis. `http://192.168.x.x:8000/api/`).
- Jalankan app di emulator/device.

## Endpoint Backend (ringkas)
- `/api/ai/*`: cv-review, interview-questions, interview-feedback, career-roadmap.
- `/api/db/auth/*`: register, login (JWT sederhana).
- `/api/db/user`: get/put/delete profil.
- `/api/db/history`: get/post riwayat (cloud).
- `/api/db/sync`: (stub, perlu implementasi lanjut untuk sinkronisasi batch).

## Testing
- Android: siapkan unit test ViewModel/repo dengan `kotlinx-coroutines-test` dan fake data sources; instrumented test untuk alur guest (Review CV, Interview) dan login+history cloud.
- Backend: gunakan pytest + FastAPI TestClient untuk auth/history/ai (mock LLM). Uji kasus sukses, input invalid, token expired.

## Observability
- Tambah logging terstruktur di backend (request id, user id) dan catat latency/error untuk panggilan LLM.
- Pantau log di app (OkHttp logging sudah aktif untuk debug).

## Demo & Skenario
1) Guest: buka app, Review CV (upload), lihat hasil AI, cek Riwayat Lokal.
2) Guest: Interview AI, kirim jawaban, lihat feedback, cek Riwayat Lokal.
3) Login/Register: masuk, lalu lakukan Review/Interview; hasil otomatis dikirim ke history cloud.
4) Sensor: di layar Interview, izinkan kamera/mikrofon, lihat preview kamera + status proximity, uji STT untuk jawaban.
