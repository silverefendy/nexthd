# NextHD — Riwayat Bug Lain (SLA, Telegram, Naming Series, Asset, dll)

> **File hasil pemecahan dari `POLA_KERJA_DAN_BUG.md` (30 Agustus 2026)** — riwayat bug yang
> TIDAK terkait Workspace/Sidebar/Desktop Icon (lihat `docs/BUG_WORKSPACE_SIDEBAR.md` untuk itu).
> Untuk aturan/pola kerja umum, lihat `docs/POLA_KERJA.md`. Bug Workflow (state machine) punya
> riwayat sendiri di `docs/WORKFLOW.md §5`.
>
> **Last updated:** 2026-08-30

---

## ✅ Bugfix dari Review Claude (2026-08-07)

| # | Severity | File | Masalah | Penyelesaian |
|---|---|---|---|---|
| 1 | High | `api/__init__.py` | File tidak ada → Frappe tidak bisa import `telegram_webhook.py` | Buat file kosong |
| 2 | High | `utils/telegram.py` | `frappe.requests.post()` — `frappe.requests` tidak ada | Ganti ke `requests.post()` |
| 3 | High | `utils/telegram.py` | `frappe.enqueue()` tanpa full module path | Ganti ke full dotted path (6 fungsi) |
| 4 | High | `tasks.py` | `frappe.utils.now()` return string → `TypeError` saat + timedelta | Ganti ke `now_datetime()` |
| 5 | High | `tasks.py` | Duplicate key `sla_resolution_by` di dict filter | Ganti ke list of tuple |
| 6 | Medium | `telegram.py` | Parameter `link_telegram_account` bernama `verification_code` | Rename ke `chat_id` |
| 7 | Medium | `workflow/` | Belum ada fixture JSON workflow | Buat 3 file JSON workflow |
| 8 | Low | `api/README.md` | Masih berisi TODO lama | Update README |
| 9 | Low | `nexthd_ticket.json` | Naming series hardcoded `TKT-2026-####` | Ganti ke `TKT-.YYYY.-.####` |
| 10 | Low | `translations/id.csv` | Nama Doctype belum diterjemahkan | Tambah 12 entri terjemahan |

---

## ✅ TERVERIFIKASI — 2026-08-11 (via screenshot user)

| # | Item | Hasil |
|---|---|---|
| 1 | NextHD Ticket form — `affected_asset` & `service_catalog` | ✅ OK — `service_catalog` tersembunyi karena `depends_on`, sesuai desain |
| 2 | NextHD Problem form — `workaround`, `known_error`, `change_request` | ✅ OK — `known_error` tersembunyi karena `depends_on`, sesuai desain |

---

## ✅ Bug Session 2026-08-15 (Naming Series & Relasi Asset)

| # | Item | Masalah | Fix |
|---|---|---|---|
| 1 | Export fixture `Property Setter` gagal | `Unknown column 'app' in 'WHERE'` | Property Setter tidak punya kolom `app`. Filter benar: `doc_type LIKE 'NextHD%'` |
| 2 | Naming series tidak konsisten antar DocType | Ticket/Problem/Asset pakai format lama (`YYYY`/statis `2026`) via Property Setter, override DocField yang sudah `YY.MM` | Diseragamkan semua ke `YY.MM` via update Property Setter |
| 3 | Dropdown Naming Series di form tampil format lama meski data DB sudah benar | Cache boot info browser, bukan bug data | Hard refresh / buka private-incognito window |
| 4 | `Unknown column 'related_asset' in 'INSERT INTO'` / `'in SET'` saat pakai field baru di NextHD Problem | Field didaftarkan ke `tabDocField` via SQL, tapi kolom fisik di `tabNextHD Problem` tidak otomatis terbuat | `ALTER TABLE \`tabNextHD Problem\` ADD COLUMN \`related_asset\` VARCHAR(140)` manual |
| 5 | `Field related_problem not found` saat klik "Buat Known Error dari Problem" | Field sudah ada di DocField DAN kolom fisik (diverifikasi), murni cache metadata server | `bench clear-cache` + `bench clear-website-cache` + `bench restart` |

---

## ✅ Bug Session 2026-08-19 (Naming Series Semua DocType)

| # | Item | Masalah | Fix |
|---|---|---|---|
| 1 | Bug penomoran `####` di SEMUA DocType (bukan cuma Ticket) | Opsi `naming_series` di JSON DocType pakai literal salah tanpa titik pemisah: `PRB-2026-####`, `CHG-2026-####`, `AST-2026-####`, `KE-2026-####`, `SVC-2026-####` | Diseragamkan ke format `.YY.MM.-.####` (reset otomatis per bulan) di 6 DocType (Ticket, Problem, Change Request, Asset, Known Error, Service Catalog) + update data existing + bersihkan row lama `tabSeries` + migrate developer_mode. Terverifikasi record baru format `XXX-2608-0001` |

> Item dedup Workflow Transition & sidebar Holiday di sesi ini — lihat `WORKFLOW.md §5` dan
> `BUG_WORKSPACE_SIDEBAR.md`.

---

## ✅ Bug Session 2026-08-20 (SLA Enforcement Business Hours) — DITUTUP TOTAL

**Root cause awal:** `calculate_sla()` lama pakai `add_to_date()` mentah, sama sekali tidak
menghitung jam kerja/hari libur.

**Yang dikerjakan:**
- `business_hours.py` — bug lama: `WEEKDAY_MAP` pakai nama Inggris (Monday dst) padahal
  `tabNextHD Business Hours` isinya nama Indonesia (Senin dst), jadi `get_business_hours()`
  selalu `None`. Diperbaiki ke nama Indonesia.
- `add_working_time()` ditulis ulang jadi versi loop all-or-nothing (kalau durasi tidak muat
  sebelum jam pulang, seluruh durasi diulang dari jam kerja berikutnya) — menangani durasi
  multi-hari (Sedang 2 hari, Rendah 1 minggu).
- `NextHD SLA Policy` — field diubah jadi `response_value`+`response_unit` dan
  `resolution_value`+`resolution_unit` (Menit/Jam/Hari), auto-terhitung ke
  `response_time_minutes`/`resolution_time_minutes` via controller `validate()`.
- Data SOP final: Kritis response 15 menit/resolusi 1 jam, Tinggi 30 menit/4 jam, Sedang 60
  menit/2 hari kerja, Rendah 120 menit/7 hari kerja. `is_24x7 = 0` untuk semua priority.

**Verifikasi test (2026-08-20 05:32 WIB):**

| Field | Hasil |
|---|---|
| Waktu insert | 2026-08-20 05:32 (di luar jam kerja) |
| `sla_response_by` | 2026-08-20 09:00 (jam buka 08:00 + 60 menit, prioritas Sedang) ✅ |
| `sla_resolution_by` | 2026-08-26 12:30 (+2 hari kerja dari jam buka) ✅ |

Ticket test: `TKT-2608-0004`. Commit `8d3f26d`, push ke `origin/main`.

> ✅ Gap titik-mulai resolution (item T) difix via PR #8 (lihat sesi 22 Agustus di bawah).

---

## ✅ Bug Session 2026-08-20 (Bot Telegram Tidak Balas)

**Root cause #1 (kritis, commit `fb9369c`):** `get_bot_token()` dan `is_telegram_enabled()` di
`telegram.py` pakai `frappe.db.get_single_value("NextHD Settings", ...)`. Tapi `NextHD Settings`
`issingle=0` (BUKAN Single DocType) — `get_single_value()` selalu return `None`. Fix: ganti ke
`frappe.db.get_value("NextHD Settings", {}, field)`.

**Root cause #2 (flooding error log):** `frappe.logger.info(...)` (kurang kurung) di
`check_sla_response_breach()` → `tasks.py`. Fix ke `frappe.logger().info(...)`.

**Bug ke-3 (prioritas rendah, belum difix):** Pesan "Peringatan SLA Response" di `tasks.py`
masih pakai f-string mentah (bukan `frappe._()`). Luput dari scope PR #6 karena ada di
`tasks.py`, bukan `telegram.py`.

**Status:** Fix sudah di-commit. Verifikasi end-to-end (bot balas `/start`) sudah dikonfirmasi
22 Agustus (lihat item E di `SUMMARY.md`).

---

## ✅ Bug Session 2026-08-22 (Permission & SLA Recalc — PR #7 & #8)

**Temuan 1 — `permissions: []` kosong total di 2 DocType master:** `NextHD SLA Policy` dan
`NextHD Business Hours` sama-sama punya array `permissions` kosong. Fix: commit `31f35da`,
langsung push ke `main`. Root cause kandidat kuat item G (404 halaman SLA Policy).

**Temuan 2:** Permission `reply` Waiting Log dikonfirmasi BENAR di JSON — tidak perlu fix kode.

**Temuan 3 — Fix item A+C: [PR #7](https://github.com/silverefendy/nexthd/pull/7), merged
2026-08-22 10:13 WIB:**
- `nexthd_ticket.json`: field `priority` diubah dari `"read_only": 1` ke `"permlevel": 1`,
  ditambah permission `{"role": "Agent Manager", "permlevel": 1, "read": 1, "write": 1}` dan
  sama untuk `IT Manager`.
- Field baru `priority_manually_set` (Check, hidden) — dipakai `set_priority_from_matrix()`
  mendeteksi kalau `priority` sudah diubah manual, supaya matrix tidak menimpa override lagi.
- Logic matrix: Tinggi+Tinggi→Kritis, Tinggi+Rendah→Tinggi, Rendah+Tinggi→Sedang,
  Rendah+Rendah→Rendah. Hanya jalan kalau `impact` dan `urgency` terisi.
- 8 test case baru di `test_nexthd_ticket.py`.

**Fix item B+T (SLA pause/resume): [PR #8](https://github.com/silverefendy/nexthd/pull/8),
merged 2026-08-22 10:31 WIB:**
- `on_update()` memanggil `handle_workflow_sla_transitions()` — cek `has_value_changed("status")`
  + `get_doc_before_save()` untuk transisi lama→baru.
- 4 skenario: Baru→Sedang Dikerjakan (`_recalculate_sla_resolution_on_start()`),
  Sedang Dikerjakan→Menunggu User (`_create_waiting_log_entry()`), Menunggu User→Sedang
  Dikerjakan (`_close_waiting_log_and_extend_sla()`), Menunggu User→Selesai
  (`_close_waiting_log_on_resolve()`).
- Semua update pakai `self.db_set()`/`frappe.db.set_value()` langsung, BUKAN `self.save()` di
  dalam `on_update()` — mencegah infinite recursion. Test khusus
  `test_workflow_sla_no_infinite_recursion` konfirmasi ini.

**Bugfix tambahan (sesi lanjutan, 22 Agustus) — Item B: Waiting Log Hilang:**

**Root cause:** `_create_waiting_log_entry()` pakai `frappe.new_doc(...).insert()` untuk child
row — berhasil masuk DB tapi **tidak ikut tersinkron ke in-memory `self.waiting_log`**. Saat
`save()` dipanggil lagi di transisi berikutnya, sinkronisasi child table bawaan menganggap
`self.waiting_log` (kosong) sebagai sumber kebenaran dan **menghapus baris yang baru dibuat**
sebelum sempat diupdate `replied_on`-nya. Efeknya: SLA `extend` tidak pernah jalan.

**Fix (commit `76ce3e9`):**
1. `_create_waiting_log_entry()` diubah insert row lewat `frappe.db.sql()` langsung (bukan ORM
   `insert()`).
2. Ditambahkan `self.load_from_db()` di akhir method untuk resync in-memory child table.

**Test setelah fix (live di server):** Priority matrix, recalculate `sla_resolution_by`,
waiting_log tetap ada + `replied_on` terisi, `sla_resolution_by` ter-extend sesuai durasi pause
— semua ✅.

**Verifikasi Item G (404 SLA Policy):** `has_permission()` sebagai Agent Manager
(`ahmad.fauzi@ciptamebel.co.id`) → `read`/`write` = `True`. Root cause item U terkonfirmasi fix.

---

## ✅ Bug Session 2026-08-24, Sesi Lanjutan — Server Ketinggalan Commit dari `origin/main`

**Konteks:** Laporan Efendy — 4 kolom di report (`Tiket per Bulan`, `Tiket per Agent`, `Tiket
per Prioritas`, `SLA Compliance Bulanan`) seharusnya bisa diklik tapi tidak berfungsi, report
`Aset Bermasalah` sama sekali tidak muncul.

**Root cause sebenarnya:** repo lokal server ketinggalan 1 commit dari `origin/main` (`fa37aa7`
→ `f873a24`) — berisi 6 report lengkap (3 folder sebelumnya sama sekali tidak ada di server).
`git pull` awalnya gagal karena 2 file `.js` berstatus **untracked** (sisa percobaan manual
`cat >` sebelumnya, isinya identik dengan versi terbaru). Setelah dihapus, `git pull` sukses
fast-forward, disusul `bench --site all migrate` + `clear-cache` + `restart`.

**Pelajaran:** kalau file report/DocType "hilang" di server padahal ada di GitHub, cek `git log
HEAD..origin/main` dulu sebelum menduga masalah paste/heredoc. File untracked di working tree
bisa memblokir `git pull` — kalau isinya sudah dipastikan identik dengan remote, aman dihapus
sebelum pull; kalau beda dan penting, `git stash` dulu.

**Batasan kerja disepakati (24 Agustus):** Claude tidak push file kode (`.py`/`.json`/`.js`) ke
repo — hanya `.md` yang boleh di-push langsung via GitHub API. Perubahan kode lewat PR (Devin)
atau dieksekusi langsung Efendy di server.

---

## ✅ Bug Session 2026-08-28 — Naming Series & Field NextHD Photo, Dashboard Connections, Reset Data Demo

**1 — Naming Series `NextHD Photo` → `IMG-YYMM-####`:** `autoname` diubah `hash` →
`naming_series:`, field baru `naming_series` (Select, hidden, opsi `IMG-.YY.MM.-.####`).
Terverifikasi dokumen baru `IMG-2608-0001` dst.

**2 — Field baru + keputusan desain:** Ditambah `photo_title` (jadi `title_field`), `location`,
`category` (Link → `NextHD Category`). Rencana awal field tunggal `reference_doctype`+
`reference_name` **dibatalkan** setelah disadari 1 foto bisa dipakai ulang di >1 dokumen —
field tunggal akan tertimpa.

**3 — Dashboard Connections "Dipakai Di":** `get_dashboard_data()` di `nexthd_photo.py` — badge
"Connections" real-time dari child table `NextHD Photo Link` di 4 parent. Trade-off: akurat &
tanpa risiko tertimpa, tapi tidak bisa dipakai untuk filter/Report View.

**4 — Tombol admin "Reset Data Demo":** Custom Page `nexthd-reset-data` memanggil
`reset_demo_data()` di `nexthd/api.py`. Hapus 6 DocType transaksional + child table terkait,
pertahankan data master. System Manager only (backend check via `frappe.get_roles`), 2x
konfirmasi (dialog + ketik `RESET`), backup otomatis, counter `tabSeries` ikut direset.

**Bug #1 — `subprocess.run(["bench", ...])` gagal di web worker:**

**Gejala:** `FileNotFoundError: 'bench'` saat tombol diklik dengan konfirmasi benar.

**Root cause:** Proses web Frappe berjalan dengan `PATH` environment terbatas — tidak mengenali
`bench` sebagai command shell.

**Dampak:** Tidak ada — kode pakai `check=True` sehingga berhenti sebelum sempat menghapus data.

**Fix:** Ganti `subprocess.run(["bench", "--site", site, "backup"])` dengan pemanggilan
langsung fungsi internal `frappe.utils.backups.new_backup(ignore_files=True)`.

*(Bug #2 & #3 di sesi ini terkait Workspace Shortcut & `Link Type must be set first` — lihat
`BUG_WORKSPACE_SIDEBAR.md`.)*

---

## ✅ SELESAI (data), 🔵 Bug Session 2026-08-28 Lanjutan (Problem.related_asset Kosong Saat Convert dari Ticket)

**Konteks:** `TKT-2608-0001` dengan `affected_asset = AST-2608-0005`, klik "Buat Problem dari
Tiket" → `PRB-2608-0001` terbentuk tapi `related_asset` kosong.

**Fix data:** `PRB-2608-0001.related_asset` di-backfill manual via `frappe.db.set_value()`.
Terverifikasi: `related_asset = AST-2608-0005`.

**Temuan penting — kode client script SUDAH BENAR:** Dump `a258744559` dicek langsung dari
database, baris `related_asset: frm.doc.affected_asset` **sudah ada**. Root cause kemungkinan
besar **cache browser** (versi script lama tanpa baris ini sempat ter-load), bukan bug aktif.

**Status:** Data diperbaiki. Kode belum diubah — menunggu hasil test ulang.

---

## ✅ Bug Session 2026-08-29 — Cleanup Field Terstruktur NextHD Asset (Duplikat EAV, Item JJ)

**Konteks:** Menindaklanjuti Item II (struktur EAV `asset_category` + `asset_attributes`
dikonfirmasi live sah via Devin, 28 Agustus malam — commit `281072a`+`81889c0`, author
`silverefendy`, 28 Agustus 23:07 WIB — **pekerjaan sah, bukan insiden tak terotorisasi**).
Efendy minta field terstruktur lama per `asset_type` (PC/Laptop/Server, Network Device,
Printer) dihapus dari form karena sudah duplikat isinya dengan EAV. Field catatan bebas
dipertahankan.

**Langkah verifikasi (wajib sebelum eksekusi):**

1. **Verifikasi backfill** — script bandingkan 17 field lama (non-kosong) di 6 record Asset
   existing vs baris `NextHD Asset Attribute`. **Hasil: semua cocok, 0 data hilang**.
2. **Cek referensi field:**
   - Property Setter `search_fields` (`NextHD Asset-main-search_fields`): isinya
     `asset_name,assigned_to,serial_number` — **field `serial_number` dipakai, wajib diupdate**.
   - Client Script & report "Tiket per Bulan": 2 hit awal — ternyata **false positive**
     (substring "os" nyangkut di "phot**os**"/"cl**os**ed_on", bukan field `os` asli).
   - `grep` manual ke file `.py`/`.js`: ditemukan **`detail_aset_lengkap.py` melakukan raw SQL
     langsung baca 6 kolom yang akan dihapus** — **wajib ditulis ulang**. Juga ditemukan
     `test_nexthd_asset.py` meng-assert field lama — **sengaja tidak digarap** (item W2).

**Eksekusi:**
- `nexthd_asset.json`: 20 field (`brand`, `model`, `serial_number`, `cpu`, `ram`, `storage`,
  `os`, `net_brand`, `net_model`, `net_serial_number`, `ip_address`, `mac_address`,
  `device_role`, `printer_brand`, `printer_model`, `printer_serial_number`, `printer_type`) +
  4 column break dihapus. Field catatan bebas (`peripheral_notes`, `net_notes`,
  `printer_notes`, `other_description`) TIDAK diubah.
- Property Setter `search_fields`: `asset_name,assigned_to,serial_number` →
  `asset_name,assigned_to` (child table EAV tidak bisa dipakai di `search_fields` Link).
- `detail_aset_lengkap.py` ditulis ulang: `LEFT JOIN` ke `tabNextHD Asset Attribute`, kolom
  baru "Spesifikasi (EAV)" (agregat via `GROUP_CONCAT`), plus kolom `brand`/`serial_number`/
  `sumber`/`catatan` yang ternyata sudah jadi kolom langsung di child table EAV.

**Hasil `bench migrate` + verifikasi Efendy (screenshot):**
- Form Asset: section PC/Network/Printer cuma tampil field catatan, EAV tetap terisi ✅
- Report "Detail Aset Lengkap": kolom Spesifikasi/Brand/dst terisi benar ✅
- Report "Aset Bermasalah": tetap normal ✅
- Search Link ke Asset masih berfungsi ✅

**Temuan sampingan (bukan bug):** Commit yang sama (`d964531`, hasil `git add .`) ikut membawa
perubahan tak terkait di `aset_bermasalah.json`/`.py` (filter `asset_type`→`asset_category`) —
dikonfirmasi via `git show` **bukan** dari script Claude, sudah ada di working directory
sebelum sesi ini (sisa kerja Devin migrasi EAV). Diverifikasi jalan normal, tidak ada regresi.

**Commit:** `d964531` → `b148223` (setelah merge dengan `e16e097` sesi lain).

**Pending:** `test_nexthd_asset.py` (item W2) — 8/16 test gagal, mayoritas `MandatoryError:
asset_category` (bukan cuma field lama) — cocok task Devin terpisah.

---

## ✅ Sesi 2026-08-28 (Lanjutan #2) — Schema Drift `related_asset`, Race Condition `set_value`, Navigasi Timbal-Balik

### Schema Drift Field `related_asset` di NextHD Problem

**Gejala:** Field "Aset Terkait" tidak muncul di form NextHD Problem, meski data
`PRB-2608-0001.related_asset` tersimpan benar.

**Root cause:** `frappe.get_meta("NextHD Problem").get_field("related_asset")` return `None` —
baris `DocField` hilang dari `tabDocField`, padahal kolom fisik masih ada. Field ini awalnya
ditambah manual via SQL (15 Agustus), dilindungi fixture `DocField` terpisah — fixture ini
**sudah tidak terdaftar** di `hooks.py`, sehingga `bench migrate` berikutnya menghapus baris
`DocField` (kolom fisik & data dibiarkan — "kolom siluman").

**Fix permanen:** Field `related_asset` ditambahkan langsung ke `nexthd_problem.json` (bukan
bergantung fixture `DocField` terpisah) — pola paling robust, satu sumber kebenaran per DocType.

**Verifikasi tambahan:** sebelum hapus fixture `docfield.json` lama (usang, menumpuk 3-4
generasi duplikat), dijalankan pembanding otomatis: semua field di meta/DB untuk 5 DocType
sudah tercakup di file JSON masing-masing. **Semua AMAN**, `docfield.json` lama dihapus tanpa
risiko.

### Race Condition `frappe.client.set_value` di Client Script

**Gejala:** Setelah klik "Buat Change Request dari Problem", CR terbentuk & ter-link ke Problem,
TAPI field balik `Problem.change_request` tetap `None`.

**Root cause:** `frappe.call({method: 'frappe.client.set_value', ..., callback() {
frm.reload_doc(); frappe.set_route(...); }})` — `set_route()` dipanggil di dalam `callback()`
yang sama, tapi `new_doc.save().then()` di luarnya tidak menunggu hasil `frappe.call()` dengan
benar, menyebabkan race condition.

**Fix:** Rantai promise diperbaiki — `.then(() => { frappe.set_route(...); })` memastikan
urutan: simpan CR → set field balik → baru pindah halaman. Data lama di-backfill.

**Pelajaran:** `frm.reload_doc()` bersamaan dengan `frappe.set_route()` ke halaman lain berisiko
race condition — taruh `set_route()` sebagai langkah PALING TERAKHIR di ujung rantai `.then()`.

### Ditutup: Investigasi "Connections Widget Tidak Muncul untuk Forward-Link"

**Keputusan final:** dokumentasi resmi Frappe (`internal_links` di `get_dashboard_data()`)
**hanya berlaku untuk link di dalam child table** — TIDAK applicable untuk Link field biasa
langsung di parent doctype (`Problem.related_asset`).

**Solusi yang diterapkan (bekerja):** tombol Client Script manual per pasangan relasi:
```javascript
if (frm.doc.<fieldname>) {
    frm.add_custom_button(__('Lihat <Target> Terkait'), function() {
        frappe.set_route('Form', '<Target DocType>', frm.doc.<fieldname>);
    });
}
```
Untuk one-to-many (Problem → banyak Ticket): buka List View dengan filter, bukan lompat ke
1 dokumen.

**Client Script navigasi timbal-balik aktif:**

| Client Script | DocType | Tombol |
|---|---|---|
| `cs_change_request_from_problem` | NextHD Problem | Buat CR, Lihat CR Terkait, Lihat Aset Terkait |
| `cs_known_error_from_problem` | NextHD Problem | Buat Known Error, Lihat Known Error, Lihat Tiket Terkait (list) |
| `cs_lihat_aset_dari_change_request` | NextHD Change Request | Lihat Aset Terkait |
| `cs_lihat_problem_dari_change_request` | NextHD Change Request | Lihat Problem Terkait |
| `cs_lihat_problem_dari_known_error` | NextHD Known Error | Lihat Problem Terkait |
| `cs_change_request_from_known_error` | NextHD Known Error | Buat CR (belum ada "Lihat CR" — Known Error tidak punya field `change_request`, potensi item tindak lanjut) |
| `cs_change_request_from_asset` | NextHD Asset | Buat CR dari Asset |

**Client Script mati:** `cs_lihat_aset_dari_problem` (`enabled=0`) — digabung ke
`cs_change_request_from_problem`.

---

*Dokumen ini dikelola oleh Claude. Update terakhir: 2026-08-30.*
