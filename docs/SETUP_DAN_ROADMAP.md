# NextHD — Setup, Roadmap & Referensi

> Instalasi, setup Telegram/SLA, alur deploy, pembagian kerja, dan referensi.
> Dipakai sekali di awal atau saat butuh reinstall.
>
> **Last updated:** 2026-08-12 10:00 WIB

---

## 1. Instalasi & Setup Awal

### Install App

```bash
bench get-app nexthd https://github.com/silverefendy/nexthd
bench --site desk.ciptamebel.co.id install-app nexthd
bench --site desk.ciptamebel.co.id migrate
```

### Setup Telegram Bot

1. Buat bot baru via [@BotFather](https://t.me/BotFather), catat token-nya
2. Di Frappe desk, buka **NextHD Settings**
3. Isi field **Telegram Bot Token**
4. Centang **Enable Telegram Notification**
5. Set webhook:
   ```
   POST https://api.telegram.org/bot<TOKEN>/setWebhook
   Body: {"url": "https://desk.ciptamebel.co.id/api/method/nexthd.next_helpdesk.api.telegram_webhook.telegram_webhook"}
   ```
6. Setiap user harus kirim `/start` ke bot, lalu ikuti instruksi verifikasi

### Setup SLA Policy

1. Buka **NextHD Business Hours** → New → isi jam kerja Senin–Sabtu
2. Buka **NextHD SLA Policy** → New → buat 4 record: Kritis, Tinggi, Sedang, Rendah
3. Isi `response_time_minutes` dan `resolution_time_minutes` sesuai SOP (**belum ditentukan** — lihat item #7 di `SUMMARY.md §2`)
4. Hubungkan setiap SLA Policy ke Business Hours yang sudah dibuat

### Alur Deploy setelah Devin selesai kerja

```bash
# Di server produksi, setelah PR Devin di-merge ke main:
cd /home/it/frappe/apps/nexthd
git pull origin main
cd /home/it/frappe
bench --site desk.ciptamebel.co.id migrate
bench restart   # kalau ada perubahan hooks.py / backend logic
```

---

## 2. Urutan Baca untuk Devin (Handover)

1. `docs/SUMMARY.md` ← entry point
2. `docs/ARSITEKTUR.md` ← DocType, field, permission, schema DB
3. `docs/WORKFLOW.md` ← state machine + notifikasi Telegram
4. `docs/POLA_KERJA_DAN_BUG.md` ← aturan wajib + riwayat bug
5. `nexthd/next_helpdesk/doctype/*/README.md` (spek per-doctype)
6. `nexthd/next_helpdesk/utils/email_helper.py` & `telegram.py`
7. `nexthd/next_helpdesk/api/telegram_webhook.py`
8. `nexthd/next_helpdesk/tasks.py`
9. `nexthd/next_helpdesk/workflow/`

---

## 3. Pembagian Kerja: Claude vs Devin vs Efendy

| Siapa | Kapan dipakai |
|---|---|
| **Efendy** | Verifikasi manual UI, keputusan SOP/bisnis (SLA, portal requester), akses infra langsung (SSH, DNS, decommission VM), role assignment individual |
| **Claude** | Kerja di server produksi (SQL, console script, fixtures export), debugging bug produksi, verifikasi teknis (workflow, SLA scheduler), tulis spec/prompt untuk Devin, push `.md` file ke repo |
| **Devin** | Implementasi fitur baru di repo (kode Python/JS baru) via PR — tidak punya akses server produksi, hasil kerjanya wajib di-pull manual + `bench migrate` setelah merge |

### Batasan Push ke Repo

| Siapa | Boleh push langsung | Harus lewat script lokal |
|---|---|---|
| Claude | File `.md` saja | `.py`, `.js`, `.json` |
| Devin | Semua file via PR | — |

---

## 4. Referensi

- Frappe v16 migration guide: https://github.com/frappe/frappe/wiki/Migrating-to-version-16
- Apps page hook docs: https://docs.frappe.io/framework/user/en/apps-page
- Frappe Discuss: https://discuss.frappe.io
- GitHub repo nexthd: https://github.com/silverefendy/nexthd
- GitHub repo visitor_management (referensi pola): https://github.com/silverefendy/visitor_management

---

*Dokumen ini dikelola oleh Claude. Update terakhir: 2026-08-12 10:00 WIB.*
