# NextHD — Index Dokumentasi

> **Entry point.** Baca ini dulu — berisi overview dan pointer ke file detail.
>
> **Last updated:** 2026-09-12 (item QQ — root cause notifikasi Telegram tidak konsisten
> ditemukan dan diperbaiki: `hooks.py` pakai `"on_insert"` yang bukan event valid Frappe,
> seharusnya `"after_insert"`; fitur baru multi-assignee/requester/team terdampak disepakati
> dan mulai dikerjakan — Tahap 1-2 dari 4 tahap sudah selesai, Tahap 3-4 pending sesi
> berikutnya. Detail lengkap di update paling bawah file ini dan di `docs/BUG_HISTORY.md`)

---

## Struktur Dokumentasi

| File | Isi |
|---|---|
| `docs/FAQ_DEVELOPER.md` | **Wajib dibaca Devin pertama kali** — kurasi masalah berulang (Workspace/Desktop Icon pasca-migrate) + pembagian kerja Claude/Devin/Efendy + hal yang tidak boleh diubah tanpa izin |
| `docs/SUMMARY.md` | **File ini** — index + project overview + status item belum dikerjakan (operasional harian) |
| `docs/DAFTAR_FITUR.md` | Checklist lengkap semua fitur (selesai/dikerjakan/rencana) dalam satu tabel, termasuk desain Generalisasi Non-IT & Wipe Data Tool (sebelumnya di `ARSITEKTUR.md §8/§9`) |
| `docs/ARSITEKTUR.md` | Infrastruktur, struktur app, DocType/field lengkap, permissions, schema tabel, label ID |
| `docs/WORKFLOW.md` | Notifikasi Telegram + semua state machine + riwayat bug workflow |
| `docs/POLA_KERJA.md` | Aturan wajib saat coding/debug di server (pola console, fixtures, Frappe quirks Workspace/Desktop Icon/Dashboard Shortcut) — **tanpa** riwayat bug (lihat 2 file bug di bawah). Pecahan dari `POLA_KERJA_DAN_BUG.md` lama (dihapus 30 Agustus) |
| `docs/BUG_WORKSPACE_SIDEBAR.md` | Riwayat bug khusus Workspace/Desktop Icon/Sidebar/Dashboard Shortcut (paling sering terjadi & paling tebal) — 13 sesi bug, 24 Agustus s/d 2 September, termasuk **root cause final regresi sidebar (item MM, 2 September)** |
| `docs/BUG_HISTORY.md` | Riwayat bug lain di luar Workspace/Sidebar — SLA/Business Hours, Telegram, naming series, Asset EAV, navigasi relasi antar dokumen, dll. **Terbaru: root cause `on_insert` vs `after_insert` (item QQ, 10-12 September)** |
| `docs/PANDUAN_INSTALASI.md` | Instalasi, setup Telegram/SLA, alur deploy, referensi |
| `docs/AUDIT_SISTEM.md` | Script audit lengkap (schema drift, Workspace, Workflow master data, SLA, fixtures) + script verifikasi ringan pasca-perbaikan + script gabungan cek semua isu Workspace/Sidebar/Dashboard. Dipakai on-demand untuk cek kesehatan server atau sebelum install ke server baru |
| `docs/HANDOFF.md` | **Log riwayat sesi ringkas** (dirombak total 30 Agustus — bukan lagi kronologi naratif penuh, sekarang tabel log per-tanggal yang menunjuk ke file tematik untuk detail) |

---

## 1. Project Overview

| Item | Detail |
|---|---|
| **Nama App** | NextHD |
| **Tujuan** | Sistem ITSM internal (Incident, Problem, Change, Asset, Known Error, Service Catalog) untuk tim IT CML |
| **Basis** | Frappe Framework v16 murni (BUKAN ERPNext) |
| **User** | Karyawan internal saja |
| **Autentikasi** | Username-based login, TANPA email asli (email dummy `@noemail.internal`) |
| **Notifikasi** | Telegram Bot (utama, **terkonfirmasi live** 22 Agustus, **root cause bug assignment/team saat insert diperbaiki 10-12 September — lihat item QQ**) + In-app notification bawaan Frappe — TIDAK pakai email |
| **Bahasa UI** | Bahasa Indonesia (default) |
| **Cakupan ITIL** | Incident, Problem, Change, Known Error, Asset/CMDB, Service Catalog |
| **Repo Git** | `silverefendy/nexthd`, branch `main` |
| **Alur Development** | Claude (kerangka & spesifikasi) → Devin (implementasi) → Claude (finishing, bugfix, review) |
| **Jam Kerja** | Senin–Jumat 08:00–17:00, **Sabtu 08:00–15:00** (hari kerja), Minggu libur |
| **Instalasi ke server baru** | TIDAK pakai Alembic — Frappe pakai skema deklaratif dari file DocType JSON, `bench migrate` otomatis sync struktur DB. Yang perlu manual: data master (Team/Category/Holiday), Workflow State & Action Master (global), NextHD Settings (token Telegram). Lihat `docs/AUDIT_SISTEM.md` untuk verifikasi kesiapan sebelum install |

### Modul Aplikasi

- Manajemen tiket insiden dan permintaan layanan
- Web Form self-service untuk Requester di `/tiket-saya` (PR #6) — **✅ terkonfirmasi live** di produksi 22 Agustus (`published: 1`, route `tiket-saya` aktif)
- Workflow approval untuk Change Request (state machine terverifikasi via regression test, 2026-08-20; dedup ulang 24 & 25 Agustus; **guard permanen anti-duplikasi live sejak 30-31 Agustus, lihat item LL**)
- Manajemen Problem dan Known Error (ITIL-lite)
- Catatan progress teknisi per tiket (`NextHD Ticket Worklog`, PR #11) — **✅ live + terverifikasi fungsional 31 Agustus**, lihat item LL
- Notifikasi real-time via Telegram Bot — **✅ terkonfirmasi live**, bot sudah balas dan token/enable sudah terkonfirmasi di NextHD Settings. **10-12 September (item QQ):** root cause notifikasi assignment/team tidak konsisten saat insert ditemukan & diperbaiki (`hooks.py` salah pakai `"on_insert"`, seharusnya `"after_insert"`) — sekarang notif langsung masuk baik dari Quick Entry, Full Form, maupun edit belakangan
- SLA monitoring otomatis berbasis jam kerja (warning 30 menit sebelum breach), termasuk **titik-mulai resolution saat "Mulai Kerjakan" + pause/resume saat "Menunggu User"** (PR #8, bugfix `76ce3e9`) — **✅ live + terverifikasi**
- Priority otomatis dari matriks Impact × Urgency, dengan override manual untuk Agent Manager/IT Manager (PR #7) — **✅ live + terverifikasi**
- Multi-tim dengan assignment agent. **Sedang dikembangkan (item QQ, Tahap 1-2/4 selesai):** dukungan multi-assignee, multi-requester, dan tim/bagian terdampak tambahan (lihat detail di §2)
- Custom reports: Tiket per Bulan, Tiket per Agent, Tiket per Kategori, Tiket per Prioritas (breach SLA), SLA Compliance Bulanan, Aset Bermasalah, Detail Aset Lengkap, Riwayat Progress Tiket — **kartu shortcut dashboard "Laporan" sudah ditambah (26 Agustus, fix `report_ref_doctype`+cache, menunggu konfirmasi visual)**, sidebar kiri "NextHD" (17 item, termasuk Asset Category) dan sidebar Workspace "NextHD Report" (8 item) **✅ dikonfirmasi PERMANEN & stabil lintas migrate 2 September (item MM)**, sidebar "NextHD Reporting" (11 shortcut Detail Report Lengkap) sudah live sejak 27 Agustus. Report "Detail Aset Lengkap" **9 September:** kolom & filter `asset_type` dihapus total, filter diganti `asset_category` (item PP)
- Field meta `Tanggal Dibuat`/`Tanggal Diedit` (tersinkron otomatis dari `creation`/`modified` via `sync_meta_dates()`) ditambahkan ke 5 DocType (Ticket, Problem, Known Error, Change Request, Asset) supaya bisa ditampilkan di List View biasa — **✅ live, item NN, 5-6 September**
- Riwayat Aktivitas/Progress (`NextHD Activity Log`) untuk Problem, Change Request, Known Error — log otomatis saat status berubah + catatan manual Agent + link dua arah opsional ke dokumen lain saat konversi — **✅ live, item OO, 7-8 September** (lihat detail di §2)
- **Warna List View (indicator pill)** ditambahkan ke Priority & Ticket Type (Ticket), Kategori (Photo, hash-color dinamis), Status & Asset Category (Asset, hash-color dinamis) — **✅ live, item PP, 9 September**
- Foto/gambar reusable & bisa di-link antar Ticket/Problem/Asset/Known Error (PR #9) — **✅ live + terverifikasi 24 Agustus**, termasuk sidebar & dashboard Number Card. **Shortcut dashboard "NextHD Photo" (kartu terpisah di section Konfigurasi) ditambah 26 Agustus**, sempat tidak muncul karena cache — sudah difix, menunggu konfirmasi visual. **28 Agustus:** naming series diubah ke `IMG-YYMM-####`, field Judul Foto/Lokasi/Kategori ditambah, dan badge "Dipakai Di" (Dashboard Connections, real-time dari child table, tidak disimpan sebagai field) terpasang di form Photo — **✅ terpasang, perlu re-test dengan foto baru**
- Tombol admin "Reset Data Demo" (hapus semua data transaksi untuk testing, System Manager only, 2x konfirmasi + backup otomatis) — **✅ live + terverifikasi end-to-end 28 Agustus**
- Generalisasi NextHD Asset ke pola EAV (`NextHD Asset Category` + `NextHD Asset Attribute`) — **✅ live 28 Agustus malam, terverifikasi aman 29 Agustus** (item II). **29 Agustus (lanjutan):** field terstruktur lama yang sudah duplikat dengan EAV **dihapus dari form**, `search_fields` & report `Detail Aset Lengkap` disesuaikan (item JJ). **30 Agustus:** "NextHD Asset Category" ditambahkan ke sidebar Workspace "NextHD" (item KK). **6 September (item NN):** field `asset_type` **disembunyikan** (non-destruktif). **9 September (item PP):** `asset_type` **dihapus total** (metadata + kolom fisik DB)
- **Rencana ke depan:** Knowledge Base publik (self-service), tag di tiket, CSAT — lihat `docs/DAFTAR_FITUR.md`

---

## 2. Status Item Belum Dikerjakan

> Bagian ini yang **paling sering diupdate tiap sesi**. Item selesai dipindah ke `docs/BUG_WORKSPACE_SIDEBAR.md` atau `docs/BUG_HISTORY.md` (sebelumnya `POLA_KERJA_DAN_BUG.md`, sudah dihapus 30 Agustus).
> Untuk rencana fitur besar yang belum jadi task konkret, lihat `docs/DAFTAR_FITUR.md`.

### 🔶 Item QQ — SEDANG DIKERJAKAN (10-12 September): Fix Notifikasi Telegram + Fitur Multi-Assignee/Requester/Team Terdampak

**Bagian A — Fix Notifikasi Telegram (✅ SELESAI, terverifikasi via UI):**

| # | Item | Keterangan | PIC |
|---|---|---|---|
| QQ-A | Notifikasi assignment/Team tidak konsisten — kadang muncul (edit tiket existing), kadang tidak (insert langsung via Quick Entry/Full Form) | **Root cause:** `hooks.py` pakai `"on_insert"` untuk `NextHD Ticket` — **bukan nama event valid** yang benar-benar dipanggil Frappe (`run_post_save_methods()`) saat insert. Terdaftar tanpa error, muncul benar di `frappe.get_hooks()`, tapi tidak pernah terpanggil. **Fix:** ganti ke `"after_insert"`. Tambahan: `notify_ticket_created()` sekarang cek `assigned_to` juga (bukan cuma Team), `notify_ticket_updated()` ditambah `notify_team_assigned()` untuk Team yang ditambahkan belakangan lewat edit. **Ketiga skenario ditest via UI browser — semua ✅.** Detail lengkap di `docs/BUG_HISTORY.md` | Claude (diagnosa+fix) + Efendy (eksekusi+test) |

**Bagian B — Fitur Multi-Assignee/Requester/Team Terdampak (🔶 Tahap 1-2/4 selesai):**

Field lama (`assigned_to`, `requested_by`, `team`) dipertahankan 1 nilai (tetap jadi patokan
SLA/permission/report), ditambah field baru (Table MultiSelect) untuk banyak nilai:

| Field Lama (tetap) | Field Baru | Kegunaan |
|---|---|---|
| `assigned_to` | `additional_assignees` | Agent tambahan, ikut notif |
| `requested_by` | `additional_requesters` | Pelapor tambahan (CC), ikut notif |
| `team` (tim IT internal) | `additional_teams` | Bagian/departemen **terdampak** (mis. Accounting) — reuse `NextHD Team` + field baru `team_type` |

| Tahap | Isi | Status |
|---|---|---|
| 1 | Field `team_type` (Select: "Tim Internal IT"/"Bagian/Departemen") di `NextHD Team` | ✅ Selesai (sempat kena bug `naming_rule` usang lagi, sama pola item PP, sudah difix) |
| 2 | 3 DocType child baru: `NextHD Ticket Assignee`, `NextHD Ticket Requester`, `NextHD Ticket Team Link` | ✅ Selesai (via `developer_mode=1`, file JSON+PY auto-generate) |
| 3 | Field `additional_assignees`/`additional_requesters`/`additional_teams` di `NextHD Ticket` + filter dropdown field `team` lama | ❌ **BELUM — lanjutan sesi berikutnya** |
| 4 | Update `telegram.py` — notif ke field tambahan (perlu bandingkan list child table lama vs baru, `has_value_changed()` tidak berlaku untuk Table MultiSelect) | ❌ **BELUM — lanjutan sesi berikutnya** |

> **Detail teknis lengkap, script yang dipakai, dan pelajaran baru** (bug `on_insert`, base64
> heredoc, audit `naming_rule`, `developer_mode` DocType creation, `Table MultiSelect` +
> `link_filters`) ada di `docs/BUG_HISTORY.md` bug session 2026-09-10 s/d 12.

### ✅ Item PP — SELESAI (9 September): Warna List View, Fix `naming_rule` Usang 5 DocType, Hapus Total `asset_type`

| # | Item | Keterangan | PIC |
|---|---|---|---|
| PP-1 | Warna (indicator pill) belum ada di kolom Priority/Ticket Type (Ticket), Kategori (Photo), Status/Asset Category (Asset) — hanya Status Ticket/Problem/CR yang sudah berwarna dari sesi sebelumnya | `formatters` ditambahkan di `nexthd_ticket_list.js` (Priority: Kritis=red/Tinggi=orange/Sedang=yellow/Rendah=grey; Ticket Type: Insiden=red/Permintaan Layanan=blue), file baru `nexthd_asset_list.js` (Status: Aktif=green/Rusak=red/Diperbaiki=orange/Dihapus=grey; Asset Category: hash-color dinamis) dan `nexthd_photo_list.js` (Kategori: hash-color dinamis, karena Link ke master yang bisa nambah kapan saja). Didaftarkan di `hooks.py` `doctype_list_js`. Semua warna ditentukan Claude atas permintaan eksplisit Efendy | Claude (desain warna+kode) + Efendy (eksekusi) |
| PP-2 | Ghost checkbox "Status" ×2-3 di List View Settings (Ticket/CR/Problem) tidak bisa dihapus meski sudah tidak dicentang; warna Status Change Request tidak pernah muncul meski `Workflow State.style` sudah benar di DB | **Root cause:** `Custom Field` bernama `<DocType>-status` (fieldtype Link ke Workflow State, `hidden=1`) tersisa di ketiga DocType — sisa eksperimen lama yang tidak pernah dibersihkan, terpisah dari field `status` asli (`Select`, dipakai Workflow). Duplikasi fieldname di metadata inilah yang membuat dropdown List View Settings menampilkan 2 entri "Status" dan membuat resolusi warna indicator ambigu. **Fix:** ketiga `Custom Field` dihapus via `frappe.delete_doc()`. Field `status` asli (Select, dipakai Workflow) tidak tersentuh | Claude (diagnosa) + Efendy (eksekusi) |
| PP-3 | Field `asset_type` (sudah di-hide non-destruktif sejak item NN, 6 September) diminta dihapus total oleh Efendy | **Verifikasi sebelum eksekusi:** audit membuktikan 0 field lain masih `depends_on` ke `asset_type` (semua 8 sudah dialihkan ke `asset_category` di item NN), dan 100% data Asset (8/8) sudah punya `asset_category` terisi — aman dihapus total. **Insiden saat eksekusi:** `doc.save()` pertama gagal `ValidationError: Naming Rule cannot be "By Series"` — bukan disebabkan field `asset_type`, melainkan bug lama tidak terkait yang baru ketahuan karena ini kali pertama `doc.save()` penuh dijalankan ke DocType ini. Diperbaiki jadi `naming_rule = 'By "Naming Series" field'`. **Audit lanjutan menemukan 4 DocType lain punya bug `naming_rule` sama** — lihat PP-4. Field `asset_type` berhasil dihapus dari `nexthd_asset.json` via `doc.save()` (regenerate otomatis, developer_mode=1). Report `detail_aset_lengkap.py`/`.json` turut diperbaiki | Claude (diagnosa+script) + Efendy (eksekusi) |
| PP-4 | Audit proaktif: DocType lain kemungkinan punya bug `naming_rule` usang yang sama | **Terkonfirmasi benar** — `NextHD Problem`, `NextHD Change Request`, `NextHD Known Error`, `NextHD Service Catalog` semua punya `naming_rule="By Series"`. Diperbaiki sekaligus. Total 7 DocType terverifikasi `naming_rule` benar. **⚠️ Update 10-12 September (item QQ): ditemukan 1 lagi di `NextHD Team` (`"By Field Name"`, bukan `"By fieldname"`) — konfirmasi pola ini bisa muncul di DocType manapun yang belum pernah kena `doc.save()` penuh, kemungkinan besar ada lagi yang belum ketahuan** | Claude (script) + Efendy (eksekusi) |

> **Pelajaran baru:** (a) `naming_rule="By Series"` adalah nilai usang peninggalan versi Frappe lama yang sudah tidak valid di v16 — kalau ada DocType lain ditambahkan di masa depan dengan cara copy-paste dari DocType existing yang sudah lama tidak pernah di-`doc.save()` penuh, bug ini bisa ikut tercopy tanpa ketahuan sampai ada operasi yang memicu validasi penuh; (b) IPython/`bench console` memutus eksekusi fungsi kalau ada baris kosong DI DALAM `def` — kesalahan ini sempat terjadi di sesi ini sendiri (`NameError: name 'doc' is not defined`) meski sudah berkali-kali didokumentasikan sebagai aturan wajib di `docs/POLA_KERJA.md`, membuktikan aturan ini perlu tetap di-double check setiap menulis script baru, bukan dianggap otomatis diingat; (c) sebelum menghapus field lama secara "aman", jangan hanya `grep` nama field itu sendiri — cek juga apakah ada field/report/test lain yang punya makna sama tapi nama beda.

### ✅ Item OO — SELESAI (7-8 September): NextHD Activity Log (Riwayat Progress Problem/CR/Known Error) + 2 Bug Diperbaiki Manual

| # | Item | Keterangan | PIC |
|---|---|---|---|
| OO | Fitur baru "Riwayat Aktivitas" untuk Problem, Change Request, Known Error | Child table `NextHD Activity Log` (shared, pola `NextHD Photo Link`) — log otomatis saat status berubah, catatan manual Agent, link dua arah opsional (`related_doctype`+`related_document` Dynamic Link) ke dokumen lain saat konversi Problem↔CR↔Known Error↔Asset. Diimplementasi Devin, PR #12 (commit `82344a0`, merged 7 September 22:56 WIB). **Review kode Claude sebelum deploy** menemukan 1 bug: `on_update()` di Problem/CR tidak memanggil `self.reload()` setelah insert SQL — pola sama seperti bug Waiting Log lama (PR #8, commit `76ce3e9`). **Ditemukan juga bug kedua:** field `tanggal_dibuat`/`tanggal_diedit` (item NN) hilang dari metadata 3 dari 5 DocType — root cause: field itu cuma pernah di-insert manual ke `tabDocField`, tidak pernah ditulis ke JSON DocType, jadi ikut terhapus saat migrate PR #12 memicu resync penuh. **Kedua bug diperbaiki manual oleh Efendy** — commit `7af8deb`, 8 September. **Belum ditest:** skenario cross-document link dua arah via UI browser | Claude (spec+review) + Efendy (eksekusi fix) |

> **Pelajaran baru:** setiap kali migrate dipicu untuk alasan APAPUN pada DocType yang punya field custom yang cuma dilindungi SQL manual (bukan JSON/fixtures), field itu berisiko ikut ter-resync/hilang — persis pola drift `related_asset` 28 Agustus, sekarang terulang untuk `tanggal_dibuat`/`tanggal_diedit`. Sebelum menyentuh JSON DocType manapun untuk kebutuhan baru, jalankan dulu audit schema drift (`docs/AUDIT_SISTEM.md §1`) untuk DocType yang akan disentuh.

### ✅ Item NN — SELESAI (5–6 September): Field Tanggal Meta di 5 DocType, Report "Riwayat Progress Tiket", Migrasi Penuh Asset Category, Kolom Tag di Report

| # | Item | Keterangan | PIC |
|---|---|---|---|
| NN-1 | List View tidak bisa menampilkan tanggal absolut "Dibuat"/"Diedit" (cuma relative time "1d"/"2h" dari kolom `modified` bawaan) | 2 Custom Field baru per DocType (`tanggal_dibuat`, `tanggal_diedit`, Datetime, hidden+read_only) disinkron otomatis via `sync_meta_dates()` dipanggil dari `on_update()`. Diterapkan ke 5 DocType. **⚠️ Update 8 September (item OO):** field ini sempat hilang lagi dari metadata untuk 3 dari 5 DocType, lihat item OO di atas | Claude + Efendy |
| NN-2 | Butuh laporan gabungan riwayat progress (Worklog) lintas banyak tiket sekaligus, sortable by tanggal | Report baru **"Riwayat Progress Tiket"** — `JOIN` `NextHD Ticket Worklog` dengan `NextHD Ticket` induk. Terverifikasi 22 baris data langsung tampil | Claude + Efendy |
| NN-3 | Field `asset_type` (Select lama) masih berjalan paralel dengan `asset_category` (Link baru EAV) tanpa sinkronisasi otomatis | Backfill `asset_category` dari `asset_type` (0 mismatch), 8 `depends_on` dialihkan ke `asset_category`, field `asset_type` disembunyikan non-destruktif. **⚠️ Update 9 September (item PP):** dihapus TOTAL | Claude + Efendy |
| NN-4 | Butuh laporan filter berdasarkan tag | Tag native Frappe (`Tag Link` + `_user_tags`) — report "Detail Tiket Lengkap" ditambah kolom "Tag" via `LEFT JOIN tabTag Link` + `GROUP_CONCAT` | Claude + Efendy |

### ✅ Item MM — SELESAI (2 September): Root Cause Final Regresi Sidebar "NextHD" 17→15 Setiap `bench migrate`

| # | Item | Keterangan | PIC |
|---|---|---|---|
| MM | Sidebar Workspace "NextHD" selalu turun dari 17 item kembali ke 15 item setiap `bench migrate` | **Root cause final:** file `nexthd/fixtures/workspace_sidebar.json` masih ada secara FISIK di disk, meski sudah lama dihapus dari daftar array `fixtures = [...]` di `hooks.py`. `sync_fixtures()` men-scan SELURUH isi folder `fixtures/` via `os.listdir()`, tidak peduli apakah file terdaftar di `hooks.py`. **Fix:** `rm nexthd/fixtures/workspace_sidebar.json` + tambah lagi 2 item hilang. **Diverifikasi stabil lintas 2× `bench migrate`** | Claude + Efendy |

### 🔴 PRIORITAS SESI BERIKUTNYA

| # | Item | Keterangan |
|---|---|---|
| 1 | **Lanjutkan Tahap 3 & 4 item QQ (multi-assignee/requester/team)** | Tahap 3: tambah field `additional_assignees`/`additional_requesters`/`additional_teams` (Table MultiSelect) ke `NextHD Ticket` + filter dropdown field `team` lama (`link_filters` supaya cuma tampilkan `team_type = "Tim Internal IT"`) — **cek dulu `naming_rule` NextHD Ticket sebelum `doc.save()`, kemungkinan sudah benar dari fix 9 September tapi tetap verifikasi**. Tahap 4: update `telegram.py` supaya notif juga jalan ke field tambahan (bandingkan list child table lama vs baru sebelum-sesudah save, `has_value_changed()` tidak berlaku untuk Table MultiSelect) |
| 2 | `git add`/commit/push semua file yang berubah sesi 10-12 September | `hooks.py`, `telegram.py`, `nexthd_team.json`, 3 DocType child baru (`nexthd_ticket_assignee`, `nexthd_ticket_requester`, `nexthd_ticket_team_link`). **Sudah dilakukan Efendy (commit `d44fdb5`)** — tapi ikut ter-commit banyak file backup `*.bak_*` yang seharusnya dibersihkan dulu, lihat item 3 |
| 3 | Bersihkan file backup `*.bak_*` yang ikut ter-commit | Hasil `git add .` tanpa filter sebelumnya ikut membawa `hooks.py.bak_*` dan beberapa `telegram.py.bak_*` ke repo — bukan bug fungsional, tapi kotor. Hapus dari repo di sesi berikutnya |
| 4 | Rename Module "Next Helpdesk" → "NextHD" (item EE) | Masih pending dari beberapa sesi lalu |
| 5 | Konfirmasi visual dashboard shortcut "NextHD Photo" + 6 Report (item BB) | Sudah difix dari sisi data & cache sejak 26 Agustus, tinggal menunggu Efendy hard refresh & konfirmasi visual |
| 6 | Test manual UI: cross-document link dua arah Activity Log (item OO) | Klik tombol "Buat CR dari Problem" dkk, cek baris Activity Log muncul di kedua dokumen |
| 7 | Verifikasi visual browser — warna List View 5 DocType (item PP) | Cek Ticket/Problem/Change Request/Asset/Photo di browser |
| 8 | Audit berkala `naming_rule` DocType lain yang belum pernah `doc.save()` penuh | Sudah ditemukan di 7 DocType (item PP: Asset/Problem/CR/Known Error/Service Catalog, item QQ: Team) — kemungkinan ada yang belum ketahuan (mis. DocType child, NextHD Category, NextHD Business Hours, dll — belum pernah diaudit) |

### ✅ Semua Item Utama SUDAH Live & Terverifikasi

| # | Fitur | Bukti Verifikasi | PIC |
|---|---|---|---|
| A+C | Priority matrix otomatis + override permission | [PR #7](https://github.com/silverefendy/nexthd/pull/7). `bench console`: Impact=Tinggi+Urgency=Tinggi → `priority=Kritis` otomatis. `permlevel=1` + Agent Manager/IT Manager override terkonfirmasi | Efendy |
| B+T | Pause/resume SLA + recalculate saat "Mulai Kerjakan" | [PR #8](https://github.com/silverefendy/nexthd/pull/8) + bugfix `76ce3e9` | Efendy |
| U | Permission `NextHD SLA Policy` & `Business Hours` | Commit `31f35da` | Efendy |
| G | Halaman NextHD SLA Policy 404 | Root cause (item U) fix | Efendy |
| D | Deploy PR #6 (Web Form + Telegram i18n) | Web Form `Tiket Saya`, `published: 1` | Efendy |
| E | Verifikasi end-to-end Telegram | Bot terkonfirmasi balas pesan nyata | Efendy |
| F | Permission `reply` di Waiting Log | permlevel & role permission benar | Efendy |
| H | `NextHD Holiday` di sidebar Workspace | Ditemukan di query sidebar | Efendy |
| W | Fitur foto reusable | PR #9, commit `03a3c5d`, merged 24 Agustus | Efendy |
| X | `install.py` — nilai SLA default usang | Commit `b3a24b2` → `2d795b9` | Efendy |
| FF | Naming Series `NextHD Photo` → `IMG-YYMM-####` | Dokumen baru `IMG-2608-0001` dst | Efendy |
| GG | Field baru `NextHD Photo`: Judul Foto, Lokasi, Kategori | Terpasang 28 Agustus | Efendy |
| HH | Tombol "Reset Data Demo" | Test sungguhan berhasil | Efendy |
| II | Generalisasi EAV `NextHD Asset` | Commit `281072a`+`81889c0`, 28 Agustus | Efendy |
| JJ | Cleanup field terstruktur Asset lama (duplikat EAV) | Commit `d964531` → `b148223`, 29 Agustus | Efendy |
| DD | Bug `Link Type must be set first` pada Workspace NextHD | Row bermasalah dihapus | Efendy |
| KK | Sidebar "NextHD" +Asset Category (17 item); sidebar "NextHD Report" 2→8 item | Commit `beec05c`, dikonfirmasi permanen 2 September (item MM) | Efendy |
| LL | Duplikasi Workflow Transition Round 4 + guard ketat penuh + PR #11 | Commit `53c63b3`/`fac453b`/`b3bc670`/`bbeda78` | Claude + Efendy |
| MM | Root cause final regresi sidebar "NextHD" 17→15 setiap migrate | File fixture usang dihapus, stabil 2× migrate, 2 September | Claude + Efendy |
| NN | Field tanggal meta 5 DocType + Report Worklog + migrasi asset_category + kolom Tag | Diverifikasi Efendy di browser, 5-6 September | Claude + Efendy |
| OO | `NextHD Activity Log` + fix `self.reload()` + fix schema drift tanggal meta | PR #12 (`82344a0`) + fix manual `7af8deb`, 8 September | Claude + Efendy |
| PP | Warna List View 5 DocType + fix `naming_rule` usang 5 DocType + hapus total `asset_type` | Diverifikasi via `bench console` tiap tahap; report `detail_aset_lengkap` jalan normal pasca perubahan; 9 September | Claude + Efendy |
| QQ-A | Root cause notifikasi Telegram `on_insert`→`after_insert` | Diverifikasi via marker debug + UI browser (Quick Entry, Full Form, edit Team belakangan), 10-12 September | Claude + Efendy |

### 🟢 Prioritas Rendah — Belum Mendesak / Masih Wacana

| # | Fitur | Keterangan | PIC |
|---|---|---|---|
| I | Wipe data testing (versi lama/checklist) | Sudah diimplementasikan versi ringkas (item HH) | Claude (desain), Efendy (eksekusi) |
| J | Workflow — testing end-to-end di UI browser | Backend lulus 100%, belum ditest klik manual | Efendy |
| K | Role assignment ke user spesifik | Sementara 1 akun shared dulu | Efendy |
| L | File `HANDOFF_SLA_NextHD_2026-08-19.md` | Tidak ada di repo, cek server | Efendy |
| M | Guard permanen duplikasi workflow transition | ✅ Selesai — lihat item LL | Claude |
| N | Pemetaan tanggal Cuti Bersama 2026 belum dicek silang ke SKB asli | Asumsi pola umum | Efendy |
| O | Dashboard "Aset Bermasalah" (Number Card) | Usulan | - |
| P | SLA otomatis untuk Problem/Change Request | Saat ini hanya Ticket | - |
| Q | Notifikasi Telegram untuk Problem/CR | Sengaja ditunda | - |
| R | Laporan bulanan otomatis (jumlah tiket, MTTR) | Usulan | - |
| V | Link Telegram untuk user test `test.requester` | Belum kirim `/start`+`/link` | Efendy |
| W2 | `test_nexthd_asset.py` — test lama assert field yang sudah dihapus | Perlu revisi menyeluruh. Makin mendesak sejak `asset_type` dihapus total (9 September) | Devin |

> **Catatan lain:** rencana fitur besar (Knowledge Base publik, tag, CSAT, merge tiket, eskalasi otomatis, dst) dipindahkan ke `docs/DAFTAR_FITUR.md` supaya tidak bercampur dengan open items operasional di atas.

### GitHub Issues & PR — Riwayat Devin

| # | Judul | Status |
|---|---|---|
| [Issue #4](https://github.com/silverefendy/nexthd/issues/4) | User Portal Requester via Frappe Web Form | Selesai via PR #6 |
| [Issue #5](https://github.com/silverefendy/nexthd/issues/5) | Telegram Notification — i18n (`frappe._()`) | Selesai via PR #6 |
| [PR #6](https://github.com/silverefendy/nexthd/pull/6) | feat: Add Web Form for Requester role and Telegram i18n | Merged 2026-08-20 — **✅ live 22 Agustus** |
| [PR #7](https://github.com/silverefendy/nexthd/pull/7) | Priority matrix otomatis + override permission | Merged 22 Agustus — **✅ live** |
| [PR #8](https://github.com/silverefendy/nexthd/pull/8) | SLA resolution timing | Merged 22 Agustus, bugfix `76ce3e9` — **✅ live** |
| [PR #9](https://github.com/silverefendy/nexthd/pull/9) | Fitur foto reusable | Merged 24 Agustus — **✅ live** |
| PR #10 | `workflow_guard.py` — guard anti-duplikasi | **✅ live + stabil lintas 3× migrate, 31 Agustus** |
| PR #11 | `NextHD Ticket Worklog` | **✅ ditest fungsional & berhasil, 31 Agustus** |
| PR #12 | `NextHD Activity Log` | Merged 7 September (commit `82344a0`), 2 bug diperbaiki manual (commit `7af8deb`, 8 September) |

---

## 3. Hal-hal yang SUDAH Selesai (Ringkasan)

> Detail lengkap ada di `docs/BUG_WORKSPACE_SIDEBAR.md` + `docs/BUG_HISTORY.md` dan log ringkas `docs/HANDOFF.md`.

Ringkasan lengkap seluruh item historis (Agustus s/d awal September) tidak diulang di sini — lihat versi sebelumnya di riwayat git file ini.

| Item | Selesai |
|---|---|
| **Warna List View (Priority/Ticket Type Ticket, Kategori Photo, Status/Asset Category Asset) (item PP)** | ✅ **9 September.** `formatters` di `nexthd_ticket_list.js`, file baru `nexthd_asset_list.js` & `nexthd_photo_list.js`, terdaftar di `hooks.py`. Build+restart sukses, verifikasi visual browser masih pending |
| **Hapus duplikat `Custom Field` "status" di Ticket/CR/Problem (item PP)** | ✅ **9 September.** 3 Custom Field (`<DocType>-status`, sisa eksperimen lama) dihapus via `frappe.delete_doc()` |
| **Fix `naming_rule="By Series"` usang di 5 DocType (item PP)** | ✅ **9 September.** NextHD Asset, Problem, Change Request, Known Error, Service Catalog — semua diperbaiki ke `By "Naming Series" field` |
| **Hapus total field `asset_type` — metadata + kolom fisik DB (item PP)** | ✅ **9 September.** Kolom fisik `DROP COLUMN`, report `detail_aset_lengkap.py`/`.json` disesuaikan, `bench migrate` bersih |
| **Root cause & fix notifikasi Telegram `on_insert` vs `after_insert` (item QQ)** | ✅ **10-12 September.** `hooks.py` diganti ke `after_insert`, `telegram.py` ditambah notif assignment saat insert + notif Team saat diedit belakangan. Ditest via UI browser (3 skenario, semua ✅) |
| **Tahap 1-2 fitur multi-assignee/requester/team terdampak (item QQ)** | ✅ **10-12 September.** Field `team_type` di `NextHD Team` + 3 DocType child baru (`NextHD Ticket Assignee`/`Requester`/`Team Link`) untuk Table MultiSelect. Tahap 3-4 (field di Ticket + update notif) masih pending |

---

*Dokumen ini dikelola oleh Claude. Update terakhir: 2026-09-12.*
