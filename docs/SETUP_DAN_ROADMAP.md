# NextHD — Setup, Roadmap & Referensi

> Instalasi, setup Telegram/SLA, alur deploy, pembagian kerja, dan referensi.
> Dipakai sekali di awal atau saat butuh reinstall.
>
> **Last updated:** 2026-08-22 19:10 WIB

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

> ⚠️ **Pastikan `bench restart` dijalankan setelah update kode** — Frappe worker mungkin masih load kode lama dari memory kalau tidak di-restart.

### Setup SLA Policy & Business Hours

> ✅ **Untuk instalasi di `desk.ciptamebel.co.id` — data sudah terisi semua per 2026-08-20.**
> Bagian ini adalah panduan untuk instalasi BARU di server lain.

1. Buka **NextHD Business Hours** → New → isi **1 record per hari** (Senin s/d Sabtu):
   - `day`: nama hari dalam Bahasa Indonesia (Senin, Selasa, dst) — **wajib pakai nama Indonesia**, karena `business_hours.py` memetakan weekday Python ke nama ini
   - `start_time`, `end_time`, `is_working_day`
   - Contoh CML: Senin–Jumat 08:00–17:00, Sabtu 08:00–14:00, Minggu = `is_working_day: 0`

2. Buka **NextHD Holiday** → New → isi tanggal hari libur nasional satu per satu

3. Buka **NextHD SLA Policy** → New → buat 4 record:

   | Priority | Response | Resolusi | `is_24x7` |
   |---|---|---|---|
   | Kritis | 15 menit | 1 jam | 0 |
   | Tinggi | 30 menit | 4 jam | 0 |
   | Sedang | 60 menit | 2 hari kerja (2880 menit) | 0 |
   | Rendah | 120 menit | 7 hari kerja (10080 menit) | 0 |

   > ⚠️ Field `business_hours` **sudah dihapus** dari NextHD SLA Policy (sejak 2026-08-19) — jangan cari field itu. SLA sekarang selalu merujuk ke tabel `NextHD Business Hours` secara global (semua policy pakai jam kerja yang sama). Field `is_24x7` (Check) menggantikannya — kalau dicentang, SLA dihitung 24 jam tanpa melihat jam kerja.

### Alur Deploy setelah Devin selesai kerja

```bash
# Di server produksi, setelah PR Devin di-merge ke main:
cd /home/it/frappe/apps/nexthd
git pull origin main
cd /home/it/frappe
bench --site desk.ciptamebel.co.id migrate
bench restart   # wajib kalau ada perubahan hooks.py, logic Python, atau utils
```

---

## 2. Urutan Baca untuk Devin (Handover)

> ⚠️ **`docs/FAQ.md` WAJIB dibaca PALING PERTAMA**, sebelum menyentuh file apapun —
> berisi kurasi masalah yang sudah berulang kali terjadi (Workspace rusak pasca-migrate,
> Desktop Icon hilang, dll) dan aturan navigasi yang terkunci (tidak boleh diubah tanpa
> izin eksplisit dari Efendy). Kalau task menyentuh `hooks.py`, fixture JSON, Workspace,
> atau Desktop Icon, ini bacaan yang paling menentukan apakah task berhasil atau malah
> merusak hal lain yang tidak terkait.

1. **`docs/FAQ.md`** ← **BACA DULU** — kurasi masalah berulang + hal yang tidak boleh diubah
2. `docs/SUMMARY.md` ← entry point, termasuk daftar open items terkini
3. `docs/ARSITEKTUR.md` ← DocType, field, permission, schema DB
4. `docs/WORKFLOW.md` ← state machine + notifikasi Telegram
5. `docs/POLA_KERJA_DAN_BUG.md` ← aturan wajib + riwayat bug (versi lengkap, FAQ.md cuma kurasi)
6. `nexthd/next_helpdesk/doctype/*/README.md` (spek per-doctype)
7. `nexthd/next_helpdesk/utils/email_helper.py` & `telegram.py`
8. `nexthd/next_helpdesk/api/telegram_webhook.py`
9. `nexthd/next_helpdesk/tasks.py`
10. `nexthd/next_helpdesk/workflow/`

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

*Dokumen ini dikelola oleh Claude. Update terakhir: 2026-08-22 19:10 WIB.*
