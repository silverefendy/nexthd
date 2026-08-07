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

- Frappe Framework v14 atau v15
- Python 3.10+
- Redis (untuk queue)
- MariaDB 10.6+

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
5. Set webhook URL ke: `https://your-domain/api/method/nexthd.next_helpdesk.api.telegram_webhook.handle_webhook` 
6. Setiap user yang ingin menerima notifikasi harus mengirim `/start` ke bot, lalu ikuti instruksi verifikasi

## Setup SLA Policy

Setelah install, buat SLA Policy untuk setiap level prioritas:

1. Buka **NextHD SLA Policy** → New
2. Buat 4 record: Kritis, Tinggi, Sedang, Rendah
3. Isi `response_time_minutes` dan `resolution_time_minutes` sesuai SOP
4. Setiap SLA Policy harus terhubung ke **NextHD Business Hours**

## Dokumentasi

Lihat folder `docs/` untuk detail teknis:
- `docs/NEXTHD_SPEC.md` — Spesifikasi lengkap fitur
- `docs/BUGFIX_SUMMARY.md` — Riwayat bugfix

## Lisensi

MIT
