# NextHD — Frappe Helpdesk

Custom helpdesk module untuk Frappe Framework, dibangun untuk kebutuhan IT support internal pabrik.

## Fitur Utama

- Manajemen tiket insiden dan permintaan layanan
- Workflow approval untuk Change Request
- Manajemen Problem dan Known Error (ITIL-lite)
- Notifikasi real-time via Telegram Bot
- SLA monitoring otomatis (warning 30 menit sebelum breach)
- Multi-tim dengan assignment agent

## Prasyarat

- Frappe Framework v16
- Python 3.14
- Redis (untuk queue)
- MariaDB 10.11+

## Instalasi

```bash
bench get-app nexthd https://github.com/silverefendy/nexthd
bench --site your-site install-app nexthd
bench --site your-site migrate
```

## Setup Telegram Bot

1. Buat bot baru via [@BotFather](https://t.me/BotFather), catat token-nya
2. Di Frappe desk, buka **NextHD Settings**
3. Isi field **Telegram Bot Token** dengan token dari BotFather
4. Centang **Enable Telegram Notification**
5. Set webhook URL ke: `https://your-domain/api/method/nexthd.next_helpdesk.api.telegram_webhook.telegram_webhook`
6. Setiap user yang ingin menerima notifikasi harus mengirim `/start` ke bot, lalu ikuti instruksi verifikasi

## Setup SLA Policy

Setelah install, buat SLA Policy untuk setiap level prioritas:

1. Buka **NextHD SLA Policy** → New
2. Buat 4 record: Kritis, Tinggi, Sedang, Rendah
3. Isi `response_time_minutes` dan `resolution_time_minutes` sesuai SOP
4. Setiap SLA Policy harus terhubung ke **NextHD Business Hours**

## Dokumentasi

Semua dokumentasi teknis (arsitektur, doctype, permission, workflow, riwayat bugfix, schema tabel, instalasi) ada di folder [`docs/`](docs/). Mulai dari:

- [`docs/SUMMARY.md`](docs/SUMMARY.md) — Entry point / index dokumentasi
- [`docs/FAQ_DEVELOPER.md`](docs/FAQ_DEVELOPER.md) — Wajib dibaca sebelum kontribusi kode
- [`docs/ARSITEKTUR.md`](docs/ARSITEKTUR.md) — Struktur app, DocType, field, permission
- [`docs/WORKFLOW.md`](docs/WORKFLOW.md) — State machine & notifikasi Telegram
- [`docs/DAFTAR_FITUR.md`](docs/DAFTAR_FITUR.md) — Checklist lengkap semua fitur
- [`docs/POLA_KERJA_DAN_BUG.md`](docs/POLA_KERJA_DAN_BUG.md) — Frappe quirks, aturan kerja, riwayat bug
- [`docs/PANDUAN_INSTALASI.md`](docs/PANDUAN_INSTALASI.md) — Instalasi & setup
- [`docs/AUDIT_SISTEM.md`](docs/AUDIT_SISTEM.md) — Script audit kesehatan server
- [`docs/HANDOFF.md`](docs/HANDOFF.md) — Arsip riwayat sesi 14–24 Agustus 2026 (historis)

## Lisensi

MIT
