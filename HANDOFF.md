# HANDOFF NextHD — 14 Agustus 2026

---

## Konteks Proyek

| Item | Detail |
|---|---|
| **App** | NextHD (Frappe Framework v16, custom ITSM helpdesk) |
| **Site** | `desk.ciptamebel.co.id` |
| **Server** | VM `erpnext`, Tailscale IP `100.64.0.14`, SSH: `it@erpnext` |
| **Repo** | `silverefendy/nexthd` (GitHub) |
| **Bench path** | `/home/it/frappe` |
| **Akun operasional** | `support@ciptamebel.co.id` |
| **Workflow tim** | Claude (debug/SQL/dokumentasi) → Devin (implementasi via PR) → Efendy (verifikasi UI, eksekusi SSH) |

---

## ⚠️ ATURAN WAJIB — JANGAN DILANGGAR

### 🔴 Navigasi & Desktop — JANGAN DIUBAH TANPA PERSETUJUAN EFENDY

Konfigurasi navigasi berikut sudah dikunci dan **tidak boleh diubah** kecuali ada kebutuhan mendesak dan sudah mendapat persetujuan eksplisit dari Efendy:

| File/Setting | Nilai Saat Ini | Larangan |
|---|---|---|
| `nexthd/hooks.py` → `add_to_apps_screen.route` | `/desk/nexthd` | Jangan diubah ke `/desk` atau lainnya |
| `nexthd/fixtures/workspace_sidebar.json` → item pertama | `Dashboard → link_to: NextHD (Workspace)` | Jangan dihapus atau dipindah dari posisi pertama |
| System Settings → `default_app` | `nexthd` | Jangan diubah |
| User `support@ciptamebel.co.id` → `default_app` | `nexthd` | Jangan diubah |

**Alasan:** Kombinasi keempat setting ini yang memastikan user langsung masuk ke Workspace dashboard NextHD (bukan ke list Ticket) setiap kali login atau klik icon NextHD. Mengubah salah satu bisa merusak alur navigasi dan membutuhkan investigasi panjang untuk debug ulang.

> ✅ **Diverifikasi ulang 15 Agustus 2026** — semua 4 komponen masih persis sesuai kuncian ini,
> tidak ada drift. Lihat item #13 di bawah.

### Pola Kerja Teknis Wajib

1. **Jangan** paste multi-line Python langsung ke IPython console — selalu tulis ke file via heredoc, lalu pipe ke console
2. Baris kosong di tengah script yang di-pipe **akan memutus block** IPython — hindari blank line antar statement top-level
3. `doc.save()` selalu gagal di production (non-developer mode) — semua perubahan DocType/DocField wajib pakai **SQL langsung + `frappe.db.commit()`**
4. Setiap perubahan struktur **wajib** di-export ke fixture JSON dan commit ke repo, atau hilang saat `bench migrate`
5. Frappe v16 di instalasi ini — **banyak nama kolom tabel berbeda** dari dokumentasi umum. Selalu `DESCRIBE tabNamaTable` dulu sebelum query
6. **Tambah DocField baru via raw SQL wajib diikuti `ALTER TABLE ADD COLUMN`** — insert ke `tabDocField` saja tidak otomatis membuat kolom fisik di tabel data. Detail di `POLA_KERJA_DAN_BUG.md`
7. Setelah perubahan field/meta yang tidak muncul di UI meski data sudah benar di database, coba `bench clear-cache` + `bench restart` di server sebelum curiga ada bug data
8. **Kolom `action` di `tabWorkflow Transition` adalah Link ke `Workflow Action Master`** — tidak bisa diganti bebas via `doc.save()` tanpa master record-nya ada dulu. Kalau cuma perlu ubah `condition`, pakai raw SQL UPDATE
9. **Field baru jangan ditempatkan (idx) langsung setelah field bertipe Table** tanpa Column Break — kadang tidak ter-render di UI meski data valid
10. **`bench console` (IPython) yang dipipe via `<<EOF` sangat rawan memecah blok kode secara prematur**, khususnya `if/else`/`for` dengan baris kosong di tengah, atau saat script diketik manual dengan tab-completion aktif (menghasilkan baris duplikat/corrupt seperti listing direktori nyasar masuk ke heredoc). **Solusi paling aman:** bungkus seluruh logic dalam satu `exec("""...""")` — karena itu satu string literal panjang, IPython tidak memecahnya per baris kosong, dan generator expression/comprehension di dalamnya tetap harus dihindari (scope terpisah, lihat poin 11)
11. **Hindari generator expression/list comprehension yang mereferensikan variabel di scope `exec()` sekitarnya** — genexpr punya scope sendiri yang terisolasi dari `exec()`, menyebabkan `NameError` meski variabelnya "kelihatan" terdefinisi tepat di atasnya. Pakai `for` loop biasa sebagai gantinya kalau kode dijalankan lewat `exec()`
12. **Sebelum edit dokumen apa pun by `frappe.db.sql(... LIMIT 1)` atau `rows[0]`, SELALU filter eksplisit pakai `WHERE name = '...'` yang tepat** — jangan asumsikan hasil pertama query tanpa filter adalah record yang dimaksud. Lihat insiden sesi 24 Agustus (Sesi Sidebar Report) di bawah: `SELECT name FROM tabWorkspace Sidebar` tanpa filter mengembalikan `"Build"` (bawaan Frappe) di posisi pertama, bukan `"NextHD"`, dan item sempat nyasar ke sana sebelum ketahuan dan diperbaiki

---

## ✅ SELESAI & TERVERIFIKASI

### 1. Navigasi — Icon NextHD → Workspace Dashboard
**Status:** ✅ Selesai (14 Agustus 2026), diverifikasi ulang 15 Agustus 2026

Root cause ditemukan setelah investigasi panjang. Solusi terdiri dari 4 komponen:

1. `hooks.py` → `add_to_apps_screen.route` diubah dari `/desk` ke `/desk/nexthd`
2. `workspace_sidebar.json` → item "Dashboard" (link ke Workspace NextHD) ditambahkan di posisi pertama
3. System Settings → `default_app` diset ke `nexthd`
4. User `support@ciptamebel.co.id` → `default_app` diset ke `nexthd`

Semua perubahan sudah di-commit ke repo (commit `59edfbe`).

### 2. Naming Series — Format YYMM
**Status:** ✅ Selesai (14 Agustus 2026, direvisi 15 Agustus — lihat Update di bawah)

### 3. Workflow Dedup
**Status:** ✅ Selesai (sesi sebelumnya)

Ticket, Problem, Change Request — semua sudah bersih, 1 transition per action. Sudah di-export ke fixture dan ada di repo.

### 4. Kolom List View
**Status:** ✅ Selesai (sesi sebelumnya)

Created By / Modified By / Created On / Modified On sudah ditambahkan ke 12 DocType via Property Setter.

> ⚠️ Field ini hanya muncul di **Report View**, bukan di Pick Columns list view biasa (karena Property Setter, bukan Custom Field).

### 5. Client Script "Buat Problem dari Tiket"
**Status:** ✅ Selesai (sesi sebelumnya)

Nama script: `a258744559`. Tombol standalone muncul di form NextHD Ticket ketika field `related_problem` masih kosong.

---

## Keputusan Final (Jangan Diulang Tanya)

| Keputusan | Detail |
|---|---|
| Dokumen lama kena bug `####` | **Tidak di-rename** — biarkan apa adanya |
| Format nomor baru | **YYMM** (reset bulanan) — **berlaku untuk SEMUA DocType termasuk Ticket**, lihat Update 15 Agustus |
| Tombol "Aksi" terpisah dari custom button | **Bukan bug** — perilaku normal Frappe, tidak diubah |
| Konfigurasi navigasi desktop/workspace | **Tidak boleh diubah** tanpa persetujuan Efendy |

---

## Info Teknis Frappe v16 (Instalasi Ini)

Nama kolom beberapa tabel berbeda dari dokumentasi umum — selalu `DESCRIBE` dulu:

| Tabel | Kolom yang TIDAK ADA (berbeda dari docs) |
|---|---|
| `tabWorkspace` | `route` (tidak ada) |
| `tabWorkspace Link` | `url` (tidak ada) |
| `tabWorkspace Shortcut` | `for_user` (tidak ada) |
| `tabModule Onboarding` | `reference_doctype` (tidak ada) |
| `tabDesktop Icon` | `module_name` (tidak ada) |
| `tabDocField` | `insert_after` (tidak ada — urutan field murni via `idx`) |

**Workspace NextHD:** didefinisikan dari file JSON di repo (`nexthd/next_helpdesk/workspace/nexthd/nexthd.json`), di-load ke DB saat `bench migrate`. Child records (Shortcut, Sidebar Item) tidak selalu ter-sync otomatis — selalu verifikasi via SQL setelah migrate.

> ⚠️ **PENTING (dikoreksi 24 Agustus 2026, lihat section terbawah "Arsitektur Sidebar"):**
> file `nexthd.json` ini mengontrol ISI HALAMAN Workspace (cards, shortcut, quick list) —
> **bukan** sidebar navigasi kiri. Sidebar kiri dikontrol doctype terpisah `Workspace Sidebar`.
> Jangan disamakan lagi — baca section "Arsitektur Sidebar NextHD" di bagian bawah dokumen ini
> sebelum menyentuh apa pun terkait sidebar.

**Lokasi file penting:**
```
/home/it/frappe/apps/nexthd/nexthd/hooks.py
/home/it/frappe/apps/nexthd/nexthd/fixtures/workspace_sidebar.json
/home/it/frappe/apps/nexthd/nexthd/fixtures/workflow.json
/home/it/frappe/apps/nexthd/nexthd/next_helpdesk/workspace/nexthd/nexthd.json
```
---

# UPDATE — 15 Agustus 2026

## ✅ SELESAI & TERVERIFIKASI (Sesi 15 Agustus, Bagian 1)

### 1. Export Fixture Lengkap — Item Kritis Kemarin, Sekarang Tuntas
**Status:** ✅ Selesai (15 Agustus 2026)

Fixture yang sebelumnya tercatat sebagai "belum di-export" di open items 14 Agustus sekarang sudah lengkap:
- `Client Script` (4 script: `a258744559`, `cs_known_error_from_problem`, `cs_change_request_from_problem`, `cs_change_request_from_known_error`)
- `Property Setter` (filter: `doc_type LIKE 'NextHD%'`)
- `DocField` (filter: parent Problem, Change Request, Asset, Known Error)

Ditambahkan ke `hooks.py` bagian `fixtures`, sudah di-export dan commit (`27efc80` → `a9a4e65`).

> ⚠️ Catatan filter: Property Setter **tidak punya kolom `app`** — filter yang benar pakai `doc_type LIKE`, bukan `app =`.

### 2. Naming Series — Keputusan Diperbarui, TERMASUK Ticket
**Status:** ✅ Selesai (15 Agustus 2026)
**⚠️ MENGGANTIKAN keputusan 14 Agustus** yang menyatakan "NextHD Ticket naming: Tidak diubah"

Diseragamkan semua ke format `YY.MM` (reset bulanan):

| DocType | Format Final | Contoh |
|---|---|---|
| NextHD Ticket | `TKT-.YY.MM.-.####.` | `TKT-2608-0001` |
| NextHD Problem | `PRB-.YY.MM.-.####.` | `PRB-2608-0001` |
| NextHD Asset | `AST-.YY.MM.-.####.` | `AST-2608-0001` |
| NextHD Change Request | `CHG-.YY.MM.-.####.` | *(tidak berubah)* |
| NextHD Known Error | `KE-.YY.MM.-.####.` | *(tidak berubah)* |

### 3–13. Relasi Asset, Guard Workflow, Verifikasi Navigasi
*(Detail lengkap ada di riwayat commit dan `POLA_KERJA_DAN_BUG.md §4`)*

---

# UPDATE — 16 Agustus 2026

## ✅ SELESAI & TERVERIFIKASI (Sesi 16 Agustus — Data Master & Permission)

### 14. Data Master Diisi: Team, Category, Business Hours, SLA Policy
**Status:** ✅ Selesai (16 Agustus 2026)

- **NextHD Team:** 2 record (Infrastructure, Application Support)
- **NextHD Category:** 5 record (Hardware, Network, Software, Akun & Akses, Printer)
- **NextHD Business Hours:** Senin s/d Sabtu (1 record per hari, field `day` nama Indonesia)
- **NextHD SLA Policy:** 4 record (Kritis 15/240 menit, Tinggi 30/480, Sedang 60/1440, Rendah 120/2880)

### 15–16. Bug Desain SLA Policy & Permission
*(Lihat catatan di `POLA_KERJA_DAN_BUG.md §4`)*

---

# UPDATE — 19 Agustus 2026 (SLA Sadar Jam Kerja & Prioritas Otomatis)

## ✅ Keputusan Desain Final (Disepakati 19 Agustus — Jangan Ditanya Ulang)

| Keputusan | Detail |
|---|---|
| Aturan SLA luar jam kerja | **All-or-nothing** — durasi penuh diulang dari jam kerja berikutnya kalau tidak muat hari ini |
| Field `business_hours` di SLA Policy | **Dihapus**, diganti `is_24x7` (Check). Kritis=1, lainnya=0 |
| Prioritas tiket | **Otomatis** dari matriks Impact×Urgency. Impact/Urgency bebas diisi user (fase edukatif). Agent Manager/IT Manager berhak override |
| Titik mulai `sla_resolution_by` | **Saat tombol "Mulai Kerjakan" diklik**, bukan saat tiket dibuat |
| Status "Menunggu User" | **Pause SLA Resolution**, riwayat di child table `NextHD Ticket Waiting Log` |
| Hari libur | Cukup `NextHD Holiday`, tanpa cuti bersama |

## ✅ Sudah Dikerjakan di Server (19 Agustus)

1. DocType `NextHD Holiday` dan `NextHD Ticket Waiting Log` dibuat dan migrate
2. Field `impact`, `urgency`, `responded_on`, `waiting_log` ditambahkan ke NextHD Ticket
3. `NextHD SLA Policy`: `business_hours` dihapus, `is_24x7` ditambahkan
4. Bug `naming_rule` usang di Ticket dan SLA Policy dikoreksi

---

# UPDATE — 20–21 Agustus 2026 (Telegram, Web Form Requester, Dedup Workflow)

## ✅ SELESAI (20 Agustus)

### 17. Bug Telegram — Root Cause & Fix di-commit (`fb9369c`)
`get_bot_token()` dan `is_telegram_enabled()` di `telegram.py` pakai `get_single_value()` yang salah untuk DocType non-Single. Diperbaiki ke `frappe.db.get_value()`. Bug `frappe.logger.info()` (kurang kurung) di `tasks.py` juga difix bersamaan.

**⚠️ Belum ada konfirmasi retest end-to-end di produksi (bot balas `/start`).**

### 18. Web Form "Tiket Saya" untuk Role Requester (PR #6)
Merged ke `main` (20 Agustus 2026). Semua string Telegram juga sudah i18n (`frappe._()`). **⚠️ Belum di-deploy ke server produksi.**

### 19–21. Dedup Workflow, Fix Dashboard, Fix Shortcut
Dedup 21 transisi (idx=0), regression test semua lulus. Number Card workspace fix (`number_card_name`). Shortcut `doc_view` dikosongkan.

## ❌ OPEN ITEMS (Update 21 Agustus)

1. Semua Open Items SLA dari 19 Agustus (#1–7) — masih terbuka
2. Deploy PR #6 ke server produksi
3. Verifikasi end-to-end Telegram
4. File `HANDOFF_SLA_NextHD_2026-08-19.md` tidak ter-commit ke repo
5. Guard permanen duplikasi workflow transition

---

# UPDATE — 22 Agustus 2026 (Verifikasi Kode Langsung dari Repo)

## Konteks

Sesi ini melakukan **verifikasi kode langsung** ke repo (bukan hanya membaca dokumentasi) untuk meluruskan status open items yang tidak konsisten antar catatan sesi sebelumnya. File yang dicek: `business_hours.py`, `nexthd_ticket.py`, `nexthd_ticket.json`, `nexthd_ticket_workflow.json`, `hooks.py`.

## ✅ Item yang Ternyata SUDAH SELESAI (belum tercatat sebelumnya)

| Item | Status Open Items Lama | Status Aktual di Kode |
|---|---|---|
| `business_hours.py` — logic all-or-nothing | ❌ "Belum, masih partial carry-over" | ✅ **Sudah benar** — `add_working_time()` sudah loop per-hari, lompat ke hari kerja berikutnya kalau durasi tidak muat, identik dengan keputusan A (19 Agustus) |
| Tombol workflow "Mulai Kerjakan" | ❌ "Belum dibuat" | ✅ **Sudah ada** — transisi `Baru → Sedang Dikerjakan` dengan action "Mulai Kerjakan" ada di `nexthd_ticket_workflow.json` |
| Field `impact`, `urgency`, `waiting_log` di form Ticket | ❌ "Tidak muncul di UI" | ✅ **Sudah ada di `field_order`** — ketiga field terdaftar di `nexthd_ticket.json`. Kalau masih tidak muncul di UI, coba `bench clear-cache` + `bench restart` |

> **Catatan:** Perbedaan antara catatan lama dan kondisi aktual kemungkinan disebabkan oleh sesi tambahan yang tidak sempat didokumentasikan di HANDOFF. Ini menegaskan aturan wajib: **selalu verifikasi kode langsung, jangan percaya 100% pada catatan**.

## 🆕 Item BARU Ditemukan (belum pernah tercatat sebagai open item sebelumnya)

Saat cross-check `calculate_sla()` di `nexthd_ticket.py` terhadap keputusan desain tabel di atas (19 Agustus: *"Titik mulai `sla_resolution_by`: Saat tombol Mulai Kerjakan diklik, bukan saat tiket dibuat"*), ditemukan kode **belum mengimplementasikan keputusan ini**:

- `calculate_sla()` hanya dipanggil di `validate()`, dan hanya kalau `self.is_new()` — artinya SLA (response DAN resolution) dihitung **sekali saja, dari `now_datetime()` saat ticket di-insert**.
- `hooks.py` → `doc_events["NextHD Ticket"]` hanya punya `on_insert` (notify Telegram) dan `on_update` (notify Telegram) — **tidak ada logic yang memanggil ulang `calculate_sla()` atau menggeser `sla_resolution_by` saat status berubah ke "Sedang Dikerjakan"**.
- Dampak: tiket yang "nganggur" lama di status Baru sebelum dikerjakan agent akan salah hitung waktu resolusi (mundur dari saat insert, padahal seharusnya dari saat mulai dikerjakan) — makin lama nganggur, makin besar risiko SLA breach palsu/dini.
- Ditambahkan sebagai **item T** (prioritas tinggi) di `docs/SUMMARY.md §2`. Terkait erat dengan item B (pause/resume SLA saat Menunggu User) — sebaiknya dikerjakan dalam satu batch karena sama-sama menyentuh ulang logic `sla_resolution_by` di titik transisi status.

## ❌ OPEN ITEMS per 22 Agustus 2026 (Final, Terverifikasi dari Kode)

Untuk daftar lengkap dengan kategorisasi prioritas, lihat `docs/SUMMARY.md §2`.

### 🔴 Belum Ada di Kode — Prioritas Tinggi

| # | Item |
|---|---|
| A | Logic priority otomatis dari matriks Impact × Urgency di `nexthd_ticket.py` — field `impact`/`urgency` sudah ada tapi tidak dipakai |
| B | Pause/resume SLA saat "Menunggu User" — tidak ada hook di `nexthd_ticket.py` yang menghitung durasi pause dari `waiting_log` dan menambahkannya ke `sla_resolution_by` |
| C | Override permission `priority` untuk Agent Manager / IT Manager — saat ini `read_only=1` global tanpa pengecualian per role |
| T | `sla_resolution_by` tidak recalculate saat "Mulai Kerjakan" diklik — SLA masih dihitung dari waktu insert, bukan dari waktu mulai dikerjakan sesuai keputusan 19 Agustus |

### 🟡 Kode Sudah Ada, Perlu Deploy/Verifikasi di Produksi

| # | Item |
|---|---|
| D | Deploy PR #6 (Web Form + Telegram i18n) ke `desk.ciptamebel.co.id` |
| E | Retest Telegram end-to-end — kirim `/start` ke bot setelah `bench restart` |
| F | Test permission `reply` di Waiting Log (permlevel 1 belum pernah ditest) |
| G | Cek 404 halaman NextHD SLA Policy (dugaan: perlu `bench build` penuh) |
| H | Konfirmasi `NextHD Holiday` sudah muncul di sidebar UI produksi |

### 🟢 Belum Mendesak

- File `HANDOFF_SLA_NextHD_2026-08-19.md` — cek di server, commit kalau masih ada
- Guard permanen duplikasi workflow transition
- Fitur Attach Image + kompresi
- Test data skenario D/E/F
- Dashboard "Aset Bermasalah", SLA untuk Problem/CR, notifikasi Telegram Problem/CR, laporan bulanan, dll

---

---

# UPDATE — 22 Agustus 2026, Sesi Lanjutan (Fix Item B + Verifikasi Live A/B/C/T/U/G di Server)

## Konteks

Sesi ini melanjutkan dari update 22 Agustus sebelumnya (verifikasi kode dari repo). PR #7 dan PR #8 sudah di-cek dan ternyata **sudah merged**, kode item A, B, C, T, U sudah ada di `main`. Sesi ini melakukan **verifikasi live di server** (bukan cuma baca kode) dengan test manual lewat `bench console`, dan menemukan bug baru di item B yang tidak terdeteksi sebelumnya.

## 🐛 Bug Baru Ditemukan & Difix: Item B (Waiting Log Hilang)

**Root cause:** `_create_waiting_log_entry()` di `nexthd_ticket.py` (hasil PR #8 dari Devin) memakai `frappe.new_doc("NextHD Ticket Waiting Log").insert()` untuk membuat child row. Baris ini berhasil masuk ke DB, tapi **tidak ikut tersinkron ke in-memory `self.waiting_log`** milik dokumen parent. Akibatnya, saat `save()` dipanggil lagi pada transisi status berikutnya, mekanisme sinkronisasi child table bawaan Frappe menganggap `self.waiting_log` (kosong) sebagai sumber kebenaran dan **menghapus baris yang baru dibuat** sebelum sempat di-update `replied_on`-nya oleh `_close_waiting_log_and_extend_sla()`. Efeknya: SLA `extend` tidak pernah jalan sama sekali.

**Fix (commit `76ce3e9`, di-push oleh Efendy):**
1. `_create_waiting_log_entry()` diubah untuk insert row lewat `frappe.db.sql()` langsung (pola yang sama dengan `_close_waiting_log_and_extend_sla()` yang sudah benar), bukan lewat ORM `insert()`
2. Ditambahkan `self.load_from_db()` di akhir method tersebut untuk resync in-memory child table, supaya `save()` berikutnya pada instance dokumen yang sama tidak menghapus row yang baru diinsert

**Test setelah fix (bench console, live di server):**
- Tiket dibuat dengan Impact=Tinggi, Urgency=Tinggi → `priority` otomatis jadi `Kritis` ✅
- Status Baru → Sedang Dikerjakan → `responded_on` terisi, `sla_resolution_by` recalculate ✅
- Status Sedang Dikerjakan → Menunggu User → 1 baris `waiting_log` dibuat (`replied_on: None`) ✅
- Status Menunggu User → Sedang Dikerjakan → baris `waiting_log` **tetap ada** (tidak hilang lagi), `replied_on` terisi ✅
- `sla_resolution_by` **ter-extend** sesuai durasi pause (dari `2026-08-22 14:07` jadi `2026-08-24 08:07`) ✅

## ✅ Verifikasi Live Item G (404 SLA Policy)

Dicek lewat `frappe.has_permission()` sebagai user dengan role Agent Manager (`ahmad.fauzi@ciptamebel.co.id`), bukan Administrator:
- `has_permission("NextHD SLA Policy", "read")` → `True`
- `has_permission("NextHD SLA Policy", "write")` → `True`
- Meta permission tidak kosong lagi (3 baris DocPerm, sebelumnya `[]`)

Root cause 404 (item U) terkonfirmasi sudah fix untuk role non-Administrator.

## Status Setelah Sesi Ini

Item A, C, T, U — sudah diverifikasi bekerja di server ini sebelumnya (kode dari PR #7/#8 + commit `31f35da`), **tidak ada perubahan kode baru** untuk item-item ini di sesi ini.

Item B — **kode PR #8 punya bug tambahan yang baru ditemukan di sesi ini**, sudah difix dan diverifikasi ulang, commit `76ce3e9` sudah di-push ke `main`.

**Catatan penting:** Server `it@erpnext` (`desk.ciptamebel.co.id`) yang dipakai sesi ini sudah di-`bench restart` beberapa kali selama proses debug — artinya kode terbaru (termasuk fix item B) **sudah live** di server ini. Kalau server ini sama dengan server produksi yang dimaksud di dokumentasi sebelumnya, maka item A, B, C, T, U bisa dianggap **sudah efektif di produksi**, bukan lagi "menunggu deploy".

## ❌ Item yang Masih Perlu Dikerjakan (tidak berubah dari sebelumnya)

| # | Item |
|---|---|
| D | Deploy PR #6 (Web Form + Telegram i18n) — belum di-`bench migrate` |
| E | Retest Telegram end-to-end — kirim `/start` ke bot nyata |
| F | Test permission `reply` di Waiting Log di UI produksi |
| H | Konfirmasi `NextHD Holiday` tampil di sidebar UI produksi |

## Catatan untuk Sesi Berikutnya

- Heredoc multi-line lewat SSH/PowerShell di server ini **sangat rawan corrupt** (baris kosong dan triple-quote `'''` sering diinterpretasi ulang oleh shell/tab-completion). Untuk edit file `.py`, lebih aman pakai `sed` dengan line number atau python script base64-encoded daripada heredoc langsung dengan blok `try/except`/`if`/triple-quote string panjang.
- `bench console` juga tidak menerima blok Python dengan indentasi (`def`, `try`, `if`) yang dikirim lewat stdin redirect — selalu tulis kode **flat tanpa nested block** kalau perlu dieksekusi lewat `bench console < file.py`.

---

# UPDATE — 24 Agustus 2026 (Sidebar Photo Fix, Dedup Workflow Round 2, Cuti Bersama, install.py)

## Konteks

Sesi ini melanjutkan verifikasi item W (fitur foto, PR #9 sudah merged sebelumnya) dan
membereskan sejumlah temuan audit dari sesi 24 Agustus sebelumnya: sidebar "NextHD Photo"
tidak muncul di UI meski data sudah live, duplikasi Workflow Transition yang muncul lagi,
Cuti Bersama 2026 yang belum diinput, dan bug `install.py` SLA usang.

## 🐛 Bug Baru Ditemukan & Difix: Sidebar "NextHD Photo" Tidak Sync

**Root cause:** `import_file_by_path(force=True, ignore_version=True)` (dipakai untuk
force-reimport `nexthd.json` ke Workspace) berhasil menimpa field top-level seperti
`number_cards` dan `content`, tapi **tidak menyentuh child table `links`** (yang me-render
sidebar). Akibatnya, Number Card "Total Foto Terupload" langsung muncul setelah reimport,
tapi item sidebar "NextHD Photo" tetap tidak ada di DB meski sudah ada di file JSON.

**Fix:** append manual lewat ORM — `frappe.get_doc("Workspace", "NextHD")`, `ws.append("links", {...})`, `ws.save(ignore_permissions=True)`. Ini mem-bypass keterbatasan `import_file_by_path`
di atas.

**⚠️ KOREKSI 24 Agustus, sesi lanjutan (lihat section terbawah):** analisis ini TERNYATA SALAH
ALAMAT. `Workspace.links` (field yang di-append di sini) **bukan** yang merender sidebar kiri
navigasi — field ini mengontrol bagian lain (kemungkinan referensi internal/cards di halaman
Workspace). Sidebar kiri navigasi yang sebenarnya dikontrol oleh doctype terpisah bernama
**`Workspace Sidebar`**. Fix di atas kemungkinan besar tidak benar-benar menyelesaikan masalah
"Photo hilang dari sidebar" — hanya kebetulan terlihat solved sesaat karena reload cache.

**Ditemukan juga (bukan bug, tapi drift):** sidebar production punya item "NextHD Business
Hours" yang **tidak ada** di `nexthd.json` repo — kemungkinan ditambahkan manual via UI di
suatu waktu. **Belum diputuskan** apakah perlu disinkronkan ke repo atau dibiarkan.

## 🐛 Bug Baru Ditemukan & Difix: Duplikasi Workflow Transition (Round 2)

**Temuan:** setiap transisi di ketiga workflow terduplikasi persis 4× (Ticket 28→7 unik,
Problem 24→6, Change Request 32→8) — bukan cuma masalah `idx`, tapi baris child table
benar-benar berulang identik.

**Root cause:** `Workflow Action Master` untuk action "Convert to Known Error" tidak pernah
dibuat sebagai record — ini membuat validasi Link gagal setiap kali proses dedup/reimport
sebelumnya mencoba `wf.save()` di tengah jalan, meninggalkan data dalam kondisi tidak
konsisten (sebagian ter-dedup, sebagian tidak, atau reimport berulang tanpa pembersihan).

**Fix:**
1. `Workflow Action Master` "Convert to Known Error" dibuat
2. Dedup ulang by-value (bandingkan seluruh field transisi, bukan cuma `idx`) untuk Problem
   dan Change Request (Ticket sudah berhasil di percobaan pertama)
3. Backup transisi lama tersimpan di `/home/it/workflow_transitions_backup.json` di server
   sebelum dedup dijalankan, untuk jaga-jaga

**Belum ada mekanisme pencegahan otomatis** supaya duplikasi tidak muncul lagi di masa
depan — dicatat sebagai item M (guard permanen) di `docs/SUMMARY.md`.

## ✅ Selesai: Cuti Bersama 2026

8 record ditambahkan ke `NextHD Holiday` (total 25: 17 nasional + 8 cuti bersama). Schema
`NextHD Holiday` cuma punya `holiday_date` + `description` (tidak ada field pembeda tipe
libur), jadi dibedakan lewat teks description saja.

**⚠️ Pemetaan tanggal↔nama event cuti bersama adalah asumsi Claude** berdasar pola umum
kalender cuti bersama Indonesia — belum dicek silang langsung ke teks SKB 3 Menteri
No. 1497/2025, 2/2025, 5/2025 yang jadi rujukan resmi.

## ✅ Selesai: `install.py` — SLA Default Diperbaiki

`create_default_sla_policies()` diupdate ke nilai SOP final 19 Agustus (Kritis 15/60
`is_24x7=1`, Tinggi 30/240, Sedang 60/2880, Rendah 120/10080). Commit `b3a24b2`, sempat
`rejected` saat push karena `main` sudah maju (merge PR #9 + update dokumentasi lain) —
di-`pull`/merge otomatis tanpa konflik, lalu berhasil push ke `2d795b9`.

## 🔴 Anomali Baru Ditemukan, BELUM Ditindaklanjuti: Business Hours "Sabtu"

Audit verifikasi akhir sesi menemukan **Business Hours Sabtu tercatat `is_working_day=1`**
(hari kerja) di production — padahal `install.py` yang baru diperbaiki di atas men-set
default Sabtu **`0`** (bukan hari kerja). Tidak jelas mana yang benar: apakah production
sengaja dibuat Sabtu jadi hari kerja (lalu `install.py` perlu disesuaikan lagi), atau ini
data lama yang salah dan perlu dikoreksi ke `0`. **Tidak ada perubahan dilakukan terhadap
ini — murni dilaporkan, menunggu keputusan Efendy.**

## Dokumentasi Terkini

Semua perubahan sesi ini sudah disinkronkan ke `main`:
- `docs/AUDIT_SISTEM.md` — ditambahkan script verifikasi ringan pasca-perbaikan (commit `7dc4c23`)
- `docs/DAFTAR_FITUR.md` — semua item selesai sesi ini dipindah ke tabel "Sudah Selesai & Live", ditambahkan bug Business Hours Sabtu (commit `a1d46f6`)
- `docs/SUMMARY.md` — item W & X dipindah ke "Live & Terverifikasi", item Y (Business Hours Sabtu) ditambahkan sebagai open item baru (commit `6988046`)
- `HANDOFF.md` — section ini

Instance Claude berikutnya tinggal baca `docs/SUMMARY.md` → `docs/DAFTAR_FITUR.md` →
bagian ini untuk konteks penuh sesi 24 Agustus.

## Catatan Teknis Tambahan untuk Sesi Berikutnya

- **`bench console` via `exec("""...""")` masih bisa gagal** kalau isinya pakai generator
  expression/comprehension yang mereferensikan variabel di scope `exec()` luar — scope
  genexpr terisolasi, hasilnya `NameError` meski variabel "kelihatan" terdefinisi. Selalu
  pakai `for` loop biasa di dalam blok `exec()`, lihat aturan wajib #11 di atas.
- **`doc.save()` bisa gagal dengan `LinkValidationError`** kalau child table (mis. Workflow
  Transition) mereferensikan master record (mis. Workflow Action Master) yang ternyata
  belum ada — meski data lama "tampak normal" di database (kemungkinan besar masuk lewat
  jalur yang bypass validasi ORM, seperti fixture/raw SQL). Kalau ketemu error ini saat
  hendak `save()` ulang data lama, cek dulu semua Link field-nya benar-benar py punya master
  record, jangan asumsikan data lama otomatis valid.

---

# UPDATE — 24 Agustus 2026, Sesi Lanjutan (Server Ketinggalan Commit, Report Formatter)

## Konteks

Sesi ini menindaklanjuti laporan Efendy bahwa 4 kolom di beberapa report (`Tiket per Bulan`,
`Tiket per Agent`, `Tiket per Prioritas`, `SLA Compliance Bulanan`) seharusnya bisa diklik
(link ke `NextHD Ticket` dengan filter terkait) tapi tidak berfungsi, dan report `Aset
Bermasalah` sama sekali tidak muncul. Awalnya dicurigai masalah teknis paste heredoc di
terminal SSH Windows Efendy (baris `cd` sempat "hilang" saat paste blok panjang).

## 🐛 Root Cause Sebenarnya: Server Produksi Ketinggalan Commit dari `origin/main`

Setelah investigasi, ternyata **bukan** masalah paste terminal. Root cause: repo lokal di
server (`~/frappe/apps/nexthd`) ketinggalan 1 commit dari `origin/main` (`fa37aa7` →
`f873a24`, commit "Update report") — commit ini berisi **6 report lengkap** (termasuk 3
folder yang sebelumnya sama sekali tidak ada di server: `tiket_per_agent`,
`sla_compliance_bulanan`, `aset_bermasalah`).

`git pull` awalnya gagal karena 2 file `.js` (`tiket_per_bulan.js`,
`tiket_per_prioritas.js`) berstatus **untracked** di server — sisa dari percobaan `cat >`
manual sebelumnya, isinya kebetulan identik dengan versi commit terbaru. Setelah file
untracked itu dihapus, `git pull origin main` berhasil fast-forward, disusul
`bench --site all migrate` + `clear-cache` + `restart`.

**Hasil akhir:** semua 6 folder report (`aset_bermasalah`, `sla_compliance_bulanan`,
`tiket_per_agent`, `tiket_per_bulan`, `tiket_per_kategori`, `tiket_per_prioritas`) sudah
terverifikasi ada di server dan migrate sukses tanpa error fatal.

## Catatan untuk Sesi Berikutnya

- **Kalau file report/DocType "hilang" di server padahal ada di GitHub, cek `git log
  HEAD..origin/main` dulu sebelum menduga masalah paste/heredoc** — pola yang lebih sering
  terjadi adalah server memang belum `git pull`, bukan file corrupt saat paste.
- **File untracked di working tree bisa memblokir `git pull`** (`error: ... would be
  overwritten by merge`). Kalau isinya sudah dipastikan identik dengan versi remote (bisa
  dicek dulu dengan `diff` atau `cat` manual), aman dihapus sebelum pull. Kalau isinya beda
  dan penting, `git stash` dulu, bukan langsung `rm`.
- **Batasan kerja disepakati dengan Efendy (24 Agustus):** Claude **tidak push file kode**
  (`.py`, `.json`, `.js`, atau tipe lain) ke repo `silverefendy/nexthd` — hanya file `.md`
  (dokumentasi) yang boleh di-push langsung oleh Claude via GitHub API. Perubahan kode tetap
  lewat jalur PR (Devin) atau dieksekusi langsung oleh Efendy di server.

---

# UPDATE — 24 Agustus 2026, Sesi Lanjutan #2 (Arsitektur Sidebar NextHD — DITEMUKAN & DILURUSKAN)

## Konteks

Efendy melaporkan 2 hal: (1) tidak ada menu Report gabungan di sidebar kiri untuk mengakses
6 report NextHD sekaligus, dan (2) item "NextHD Photo" hilang lagi dari sidebar kiri
(padahal sempat "diperbaiki" di sesi 24 Agustus sebelumnya). Sesi ini akhirnya menemukan
**akar masalah sesungguhnya**: pemahaman sebelumnya tentang komponen mana yang mengontrol
sidebar kiri navigasi **salah**, sudah 2 sesi berturut-turut mengedit tempat yang keliru.

## 🎯 Arsitektur Sidebar NextHD — SUMBER KEBENARAN YANG BENAR (baca ini dulu sebelum sentuh sidebar apa pun)

Ada **3 komponen berbeda** yang sekilas terlihat mirip tapi punya fungsi terpisah total. Jangan
tertukar lagi:

| Komponen | Fungsi Sebenarnya | Lokasi Sumber |
|---|---|---|
| **`Workspace Sidebar`** (doctype) + child **`Workspace Sidebar Item`** | **INI yang benar-benar merender sidebar kiri navigasi** yang terlihat user (Dashboard, NextHD Ticket, NextHD Problem, dst). Satu record per app/module — nama record app ini adalah **`"NextHD"`** (BUKAN nama lain) | Live di database, DIAKSES via `frappe.get_doc("Workspace Sidebar", "NextHD")` |
| `Workspace.links` (child table `links` di doctype `Workspace`) | **BUKAN sidebar kiri.** Fungsi sebenarnya belum sepenuhnya dikonfirmasi, kemungkinan referensi internal/related links di halaman workspace itu sendiri — **JANGAN edit ini untuk masalah sidebar** | Live di database, `frappe.get_doc("Workspace", "NextHD")` |
| `nexthd/next_helpdesk/workspace/nexthd/nexthd.json` (`workspace_json` hook) | Mengontrol **ISI HALAMAN** Workspace saat diklik — cards, number card, shortcut button, quick list. **Bukan sidebar kiri** | File repo, di-load via `bench migrate` |
| `nexthd/fixtures/workspace_sidebar.json` | Skema-nya **benar** (cocok dengan `Workspace Sidebar Item`), TAPI **sengaja dinonaktifkan** dari fixtures di `hooks.py` (alasan: mencegah bug "orphan workspace" saat migrate). Mengedit file ini **TIDAK BERPENGARUH** ke server — murni arsip/dokumentasi | File repo, TIDAK di-load otomatis |

## 🐛 Kronologi Kesalahan Sesi Ini (supaya tidak terulang)

1. **Percobaan 1:** edit `Workspace.links` (nambah "NextHD Report") → gagal dengan
   `MandatoryError: [Workspace, NextHD]: type` — field `type` di record `NextHD` ternyata
   `NULL` di database (anomali data lama, entah kenapa bisa lolos selama ini karena hanya
   fixture reimport yang bypass validasi `save()` biasa yang pernah menyentuhnya)
2. **Percobaan 2:** field `type` diisi ulang `"Workspace"`, `Workspace.links` berhasil di-save
   dengan item baru — **tapi sidebar kiri tetap tidak berubah**. Ini seharusnya jadi sinyal
   bahwa `Workspace.links` memang bukan sumber yang benar
3. **Percobaan 3:** ditemukan doctype `Workspace Sidebar` (terkonfirmasi juga di
   `ARSITEKTUR.md §6` sebagai `tabWorkspace Sidebar` + `tabWorkspace Sidebar Item` — sudah
   lama terdokumentasi skemanya, tapi belum ada yang menyadari inilah yang aktif dipakai)
4. **Kesalahan fatal:** query `SELECT name FROM tabWorkspace Sidebar` **tanpa filter**,
   lalu ambil `rows[0].name` — mengira hasil pertama otomatis adalah `"NextHD"`. Ternyata
   hasil pertama adalah **`"Build"`** (workspace bawaan Frappe developer tools). Item
   "NextHD Photo" dan "NextHD Report" sempat ke-append ke `Workspace Sidebar` record
   **"Build"**, bukan **"NextHD"**
5. **Fix final:** hapus 2 item yang nyasar dari `Build`, tambahkan ke record `NextHD` yang
   benar. **Dikonfirmasi Efendy: sudah muncul di sidebar.**

## ✅ Status Setelah Sesi Ini

- Item **"NextHD Photo"** dan **"NextHD Report"** sudah live di `Workspace Sidebar` record
  `"NextHD"` di database production, **terkonfirmasi tampil di browser**
- "NextHD Report" saat ini link ke `Report` DocType filtered by `module = "Next Helpdesk"`
  (menampilkan semua 6 report NextHD dalam satu list saat diklik)

## ❌ Belum Beres — PENTING untuk Sesi Berikutnya

**Perubahan di atas HANYA ADA DI DATABASE, belum di-export/commit ke repo dalam bentuk apa
pun.** Karena `Workspace Sidebar` **sengaja dikeluarkan dari mekanisme fixtures** (lihat
komentar di `hooks.py`), TIDAK ADA jalur otomatis untuk membuatnya permanen lewat cara yang
sudah dipakai sejauh ini. Risiko: kalau ada proses lain yang someday mereset/reimport
`Workspace Sidebar` (misal reinstall app, restore dari backup lama), 2 item baru ini bisa
hilang lagi tanpa jejak di repo.

**Belum diputuskan** cara permanen terbaiknya — opsi yang perlu dipertimbangkan Efendy/Devin:
- (a) Re-enable `Workspace Sidebar` di `fixtures` list `hooks.py` — TAPI ini yang justru
  sengaja dimatikan karena pernah menyebabkan bug "orphan workspace hilang" saat migrate,
  jadi perlu investigasi ulang kenapa itu terjadi sebelum diaktifkan lagi
- (b) Simpan snapshot manual (export JSON) ke `nexthd/fixtures/workspace_sidebar.json`
  sebagai **dokumentasi/arsip saja** (bukan otomatis ter-load), lalu punya SOP manual re-apply
  item ini tiap kali ada indikasi sidebar reset
- (c) Bikin patch/migration script Python kustom yang dijalankan sekali di `after_migrate`
  hook untuk memastikan item sidebar penting selalu ada — pendekatan lebih robust tapi
  perlu effort development

## Catatan Wajib untuk Sesi Berikutnya

- **JANGAN PERNAH** ambil hasil pertama dari query tanpa `WHERE name = '...'` yang eksplisit
  saat mengedit dokumen apa pun via `bench console` — selalu filter nama spesifik dulu, dan
  `print()` hasil query sebelum melakukan `.save()` apa pun, supaya kesalahan ketahuan
  sebelum tersimpan, bukan sesudah
- **Untuk masalah SIDEBAR KIRI navigasi** (bukan isi halaman Workspace): satu-satunya
  sumber kebenaran adalah `frappe.get_doc("Workspace Sidebar", "NextHD")`, child table
  `items`. JANGAN sentuh `Workspace.links` atau `nexthd.json` untuk masalah ini
- Field-field valid di child `Workspace Sidebar Item` (dari `frappe.get_meta`):
  `type` (Select: Link/Card Break), `label`, `icon`, `description`, `hidden`, `link_type`
  (Select: DocType/Page/Report), `link_to` (Dynamic Link), `report_ref_doctype`,
  `dependencies`, `only_for`, `onboard`, `is_query_report`, `link_count`
- Sesi 24 Agustus sebelumnya (section di atas, "Sidebar Photo Fix") **analisisnya keliru** —
  root cause yang diklaim sudah fix di situ (`Workspace.links` + `import_file_by_path`)
  ternyata bukan penyebab sebenarnya. Jangan jadikan referensi solusi untuk masalah sidebar
  serupa di masa depan
