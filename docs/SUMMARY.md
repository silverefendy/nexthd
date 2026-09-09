# NextHD — Index Dokumentasi

> **Entry point.** Baca ini dulu — berisi overview dan pointer ke file detail.
>
> **Last updated:** 2026-09-09 (Item PP — warna List View untuk Ticket/Problem/Change Request/Asset/Photo; ditemukan & diperbaiki bug `naming_rule` usang (`"By Series"`, nilai tidak valid Frappe v16) di 5 DocType sekaligus; field `asset_type` (deprecated sejak item NN) akhirnya dihapus TOTAL — dari metadata DocType, kolom fisik database, dan report `Detail Aset Lengkap`. Detail lengkap di update paling bawah file ini)

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
| `docs/BUG_HISTORY.md` | Riwayat bug lain di luar Workspace/Sidebar — SLA/Business Hours, Telegram, naming series, Asset EAV, navigasi relasi antar dokumen, dll |
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
| **Notifikasi** | Telegram Bot (utama, **terkonfirmasi live** 22 Agustus) + In-app notification bawaan Frappe — TIDAK pakai email |
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
- Notifikasi real-time via Telegram Bot — **✅ terkonfirmasi live**, bot sudah balas dan token/enable sudah terkonfirmasi di NextHD Settings
- SLA monitoring otomatis berbasis jam kerja (warning 30 menit sebelum breach), termasuk **titik-mulai resolution saat "Mulai Kerjakan" + pause/resume saat "Menunggu User"** (PR #8, bugfix `76ce3e9`) — **✅ live + terverifikasi**
- Priority otomatis dari matriks Impact × Urgency, dengan override manual untuk Agent Manager/IT Manager (PR #7) — **✅ live + terverifikasi**
- Multi-tim dengan assignment agent
- Custom reports: Tiket per Bulan, Tiket per Agent, Tiket per Kategori, Tiket per Prioritas (breach SLA), SLA Compliance Bulanan, Aset Bermasalah, Detail Aset Lengkap, **Riwayat Progress Tiket** (baru — gabungan `NextHD Ticket Worklog` lintas semua tiket, sortable by tanggal, item NN, 5-6 September) — **kartu shortcut dashboard "Laporan" sudah ditambah (26 Agustus, fix `report_ref_doctype`+cache, menunggu konfirmasi visual)**, sidebar kiri "NextHD" (17 item, termasuk Asset Category) dan sidebar Workspace "NextHD Report" (8 item, +1 shortcut "Riwayat Progress Tiket" sejak item NN) **✅ dikonfirmasi PERMANEN & stabil lintas migrate 2 September (item MM)**, sidebar "NextHD Reporting" (11 shortcut Detail Report Lengkap) sudah live sejak 27 Agustus. Report "Detail Tiket Lengkap" kini juga menampilkan kolom **Tag** (native Frappe `Tag Link`, item NN). Report "Detail Aset Lengkap" **9 September:** kolom & filter `asset_type` dihapus total, filter diganti `asset_category` (item PP)
- Field meta `Tanggal Dibuat`/`Tanggal Diedit` (tersinkron otomatis dari `creation`/`modified` via `sync_meta_dates()`) ditambahkan ke 5 DocType (Ticket, Problem, Known Error, Change Request, Asset) supaya bisa ditampilkan di List View biasa — **✅ live, item NN, 5-6 September**
- Riwayat Aktivitas/Progress (`NextHD Activity Log`) untuk Problem, Change Request, Known Error — log otomatis saat status berubah + catatan manual Agent + link dua arah opsional ke dokumen lain saat konversi — **✅ live, item OO, 7-8 September** (lihat detail di §2)
- **Warna List View (indicator pill)** ditambahkan ke Priority & Ticket Type (Ticket), Kategori (Photo, hash-color dinamis), Status & Asset Category (Asset, hash-color dinamis) — **✅ live, item PP, 9 September**
- Foto/gambar reusable & bisa di-link antar Ticket/Problem/Asset/Known Error (PR #9) — **✅ live + terverifikasi 24 Agustus**, termasuk sidebar & dashboard Number Card. **Shortcut dashboard "NextHD Photo" (kartu terpisah di section Konfigurasi) ditambah 26 Agustus**, sempat tidak muncul karena cache — sudah difix, menunggu konfirmasi visual. **28 Agustus:** naming series diubah ke `IMG-YYMM-####`, field Judul Foto/Lokasi/Kategori ditambah, dan badge "Dipakai Di" (Dashboard Connections, real-time dari child table, tidak disimpan sebagai field) terpasang di form Photo — **✅ terpasang, perlu re-test dengan foto baru**
- Tombol admin "Reset Data Demo" (hapus semua data transaksi untuk testing, System Manager only, 2x konfirmasi + backup otomatis) — **✅ live + terverifikasi end-to-end 28 Agustus**
- Generalisasi NextHD Asset ke pola EAV (`NextHD Asset Category` + `NextHD Asset Attribute`) — **✅ live 28 Agustus malam, terverifikasi aman 29 Agustus** (item II). **29 Agustus (lanjutan):** field terstruktur lama (brand/model/cpu/ram/storage/os/dst di section PC/Network/Printer) yang sudah duplikat dengan EAV **dihapus dari form**, `search_fields` & report `Detail Aset Lengkap` disesuaikan (item JJ). **30 Agustus:** "NextHD Asset Category" ditambahkan ke sidebar Workspace "NextHD" (item KK). **6 September (item NN):** field `asset_type` (Select lama, paralel dengan `asset_category` sejak migrasi EAV tapi belum pernah di-deprecate) **disembunyikan** (non-destruktif) — 8 `depends_on` field dinamis dialihkan penuh ke `asset_category`, report `Detail Aset Lengkap` disesuaikan (kolom "Tipe" → "Kategori"). **9 September (item PP):** `asset_type` **dihapus total** (metadata + kolom fisik DB), setelah dikonfirmasi 0 field lain bergantung & 100% data ter-cover `asset_category`
- **Rencana ke depan:** Knowledge Base publik (self-service), tag di tiket, CSAT — lihat `docs/DAFTAR_FITUR.md`

---

## 2. Status Item Belum Dikerjakan

> Bagian ini yang **paling sering diupdate tiap sesi**. Item selesai dipindah ke `docs/BUG_WORKSPACE_SIDEBAR.md` atau `docs/BUG_HISTORY.md` (sebelumnya `POLA_KERJA_DAN_BUG.md`, sudah dihapus 30 Agustus).
> Untuk rencana fitur besar yang belum jadi task konkret, lihat `docs/DAFTAR_FITUR.md`.

### ✅ Item PP — SELESAI (9 September): Warna List View, Fix `naming_rule` Usang 5 DocType, Hapus Total `asset_type`

| # | Item | Keterangan | PIC |
|---|---|---|---|
| PP-1 | Warna (indicator pill) belum ada di kolom Priority/Ticket Type (Ticket), Kategori (Photo), Status/Asset Category (Asset) — hanya Status Ticket/Problem/CR yang sudah berwarna dari sesi sebelumnya | `formatters` ditambahkan di `nexthd_ticket_list.js` (Priority: Kritis=red/Tinggi=orange/Sedang=yellow/Rendah=grey; Ticket Type: Insiden=red/Permintaan Layanan=blue), file baru `nexthd_asset_list.js` (Status: Aktif=green/Rusak=red/Diperbaiki=orange/Dihapus=grey; Asset Category: hash-color dinamis) dan `nexthd_photo_list.js` (Kategori: hash-color dinamis, karena Link ke master yang bisa nambah kapan saja). Didaftarkan di `hooks.py` `doctype_list_js`. Semua warna ditentukan Claude atas permintaan eksplisit Efendy | Claude (desain warna+kode) + Efendy (eksekusi) |
| PP-2 | Ghost checkbox "Status" ×2-3 di List View Settings (Ticket/CR/Problem) tidak bisa dihapus meski sudah tidak dicentang; warna Status Change Request tidak pernah muncul meski `Workflow State.style` sudah benar di DB | **Root cause:** `Custom Field` bernama `<DocType>-status` (fieldtype Link ke Workflow State, `hidden=1`) tersisa di ketiga DocType — sisa eksperimen lama yang tidak pernah dibersihkan, terpisah dari field `status` asli (`Select`, dipakai Workflow). Duplikasi fieldname di metadata inilah yang membuat dropdown List View Settings menampilkan 2 entri "Status" dan membuat resolusi warna indicator ambigu. **Fix:** ketiga `Custom Field` dihapus via `frappe.delete_doc()`. Field `status` asli (Select, dipakai Workflow) tidak tersentuh | Claude (diagnosa) + Efendy (eksekusi) |
| PP-3 | Field `asset_type` (sudah di-hide non-destruktif sejak item NN, 6 September) diminta dihapus total oleh Efendy | **Verifikasi sebelum eksekusi:** audit membuktikan 0 field lain masih `depends_on` ke `asset_type` (semua 8 sudah dialihkan ke `asset_category` di item NN), dan 100% data Asset (8/8) sudah punya `asset_category` terisi — aman dihapus total. **Insiden saat eksekusi:** `doc.save()` pertama gagal `ValidationError: Naming Rule cannot be "By Series"` — bukan disebabkan field `asset_type`, melainkan bug lama tidak terkait yang baru ketahuan karena ini kali pertama `doc.save()` penuh dijalankan ke DocType ini (biasanya cuma disentuh SQL/`ALTER TABLE` yang skip validasi ini). Diperbaiki jadi `naming_rule = 'By "Naming Series" field'` (sesuai `autoname: naming_series:`). **Audit lanjutan menemukan 4 DocType lain punya bug `naming_rule` sama** — lihat PP-4. Setelah `naming_rule` benar, field `asset_type` berhasil dihapus dari `nexthd_asset.json` via `doc.save()` (regenerate otomatis, developer_mode=1). **Ditemukan juga** file JSON di repo (`nexthd_asset.json`) sudah sangat basi — masih berisi 20 field terstruktur lama (brand/cpu/ram/dst) yang sebenarnya sudah tidak ada di DB sejak item JJ (29 Agustus) tapi tidak pernah tersinkron ke file. Pendekatan **regenerate via `doc.save()`** (bukan edit JSON manual) dipilih justru karena insiden ini — memastikan file akhirnya benar-benar mencerminkan kondisi DB, bukan tambal-sulam di atas file basi. Report `detail_aset_lengkap.py` (query `SELECT a.asset_type`, tidak dipakai di kolom output, aman dihapus) dan `detail_aset_lengkap.json` (filter dropdown `asset_type`, diganti `asset_category`) turut diperbaiki. `bench migrate` dijalankan bersih, lalu `ALTER TABLE DROP COLUMN asset_type` dieksekusi. Report diverifikasi jalan normal pasca perubahan (8 baris data, tanpa error) | Claude (diagnosa+script) + Efendy (eksekusi) |
| PP-4 | Audit proaktif: DocType lain kemungkinan punya bug `naming_rule` usang yang sama | **Terkonfirmasi benar** — `NextHD Problem`, `NextHD Change Request`, `NextHD Known Error`, `NextHD Service Catalog` semua punya `naming_rule="By Series"` (nilai tidak valid Frappe v16, cuma belum ketahuan karena belum pernah ada `doc.save()` penuh ke DocType-DocType itu). Diperbaiki sekaligus (script per-DocType dengan `try/except` terpisah supaya kegagalan satu tidak menghentikan yang lain) — 4/4 berhasil, tidak ada yang gagal. Total 7 DocType (termasuk Ticket, Photo, Asset yang sudah benar sebelumnya) terverifikasi `naming_rule = 'By "Naming Series" field'` | Claude (script) + Efendy (eksekusi) |

> **Pelajaran baru:** (a) `naming_rule="By Series"` adalah nilai usang peninggalan versi Frappe lama yang sudah tidak valid di v16 — kalau ada DocType lain ditambahkan di masa depan dengan cara copy-paste dari DocType existing yang sudah lama tidak pernah di-`doc.save()` penuh, bug ini bisa ikut tercopy tanpa ketahuan sampai ada operasi yang memicu validasi penuh; (b) IPython/`bench console` memutus eksekusi fungsi kalau ada baris kosong DI DALAM `def` — kesalahan ini sempat terjadi di sesi ini sendiri (`NameError: name 'doc' is not defined`) meski sudah berkali-kali didokumentasikan sebagai aturan wajib di `docs/POLA_KERJA.md`, membuktikan aturan ini perlu tetap di-double check setiap menulis script baru, bukan dianggap otomatis diingat; (c) sebelum menghapus field lama secara "aman", jangan hanya `grep` nama field itu sendiri — cek juga apakah ada field/report/test lain yang punya makna sama tapi nama beda (kasus PP-3: hampir menimpa kolom "Kategori" yang sudah ada duluan sebelum sadar itu bukan bagian dari `asset_type` — meski kali ini akhirnya tidak terjadi karena diagnosa dilakukan lebih hati-hati dari kasus serupa di item NN-3).

### ✅ Item OO — SELESAI (7-8 September): NextHD Activity Log (Riwayat Progress Problem/CR/Known Error) + 2 Bug Diperbaiki Manual

| # | Item | Keterangan | PIC |
|---|---|---|---|
| OO | Fitur baru "Riwayat Aktivitas" untuk Problem, Change Request, Known Error | Child table `NextHD Activity Log` (shared, pola `NextHD Photo Link`) — log otomatis saat status berubah, catatan manual Agent, link dua arah opsional (`related_doctype`+`related_document` Dynamic Link) ke dokumen lain saat konversi Problem↔CR↔Known Error↔Asset. Diimplementasi Devin, PR #12 (commit `82344a0`, merged 7 September 22:56 WIB). **Review kode Claude sebelum deploy** menemukan 1 bug: `on_update()` di Problem/CR tidak memanggil `self.reload()` setelah insert SQL — pola sama seperti bug Waiting Log lama (PR #8, commit `76ce3e9`), berisiko baris log hilang kalau dokumen di-save lagi tanpa reload. **Ditemukan juga bug kedua** (bukan dari PR #12, tapi terpicu olehnya): field `tanggal_dibuat`/`tanggal_diedit` (item NN) hilang dari metadata 3 dari 5 DocType (Problem/CR/Known Error) — root cause: field itu cuma pernah di-insert manual ke `tabDocField`, tidak pernah ditulis ke JSON DocType atau didaftarkan fixtures, jadi ikut terhapus saat migrate PR #12 memicu resync penuh JSON yang berubah. **Kedua bug diperbaiki manual oleh Efendy (tanpa Devin)** via script heredoc: field tanggal ditulis permanen ke 3 file JSON, `self.reload()` ditambahkan ke 2 controller, keduanya diverifikasi via `bench console` sebelum-sesudah. Commit `7af8deb`, 8 September. **Belum ditest:** skenario cross-document link dua arah via UI browser | Claude (spec+review) + Efendy (eksekusi fix) |

> **Pelajaran baru:** setiap kali migrate dipicu untuk alasan APAPUN pada DocType yang punya field custom yang cuma dilindungi SQL manual (bukan JSON/fixtures), field itu berisiko ikut ter-resync/hilang — persis pola drift `related_asset` 28 Agustus, sekarang terulang untuk `tanggal_dibuat`/`tanggal_diedit`. Sebelum menyentuh JSON DocType manapun untuk kebutuhan baru, jalankan dulu audit schema drift (`docs/AUDIT_SISTEM.md §1`) untuk DocType yang akan disentuh.

### ✅ Item NN — SELESAI (5–6 September): Field Tanggal Meta di 5 DocType, Report "Riwayat Progress Tiket", Migrasi Penuh Asset Category, Kolom Tag di Report

| # | Item | Keterangan | PIC |
|---|---|---|---|
| NN-1 | List View tidak bisa menampilkan tanggal absolut "Dibuat"/"Diedit" (cuma relative time "1d"/"2h" dari kolom `modified` bawaan) | **Root cause:** field meta `creation`/`modified` tidak terdaftar sebagai DocField, jadi tidak muncul di dialog "+ Add/Remove Fields". **Fix:** 2 Custom Field baru per DocType (`tanggal_dibuat`, `tanggal_diedit`, Datetime, hidden+read_only) disinkron otomatis dari `creation`/`modified` via method baru `sync_meta_dates()` yang dipanggil dari `on_update()`. **Diterapkan ke 5 DocType:** NextHD Ticket, Problem, Known Error, Change Request, Asset — backfill data lama untuk semua record existing berhasil (0 gagal). Pola teknis: patch `.py` pakai regex dengan **auto-detect indentasi** (bukan hardcode tab/spasi), backup timestamp otomatis, wajib lolos `ast.parse()` sebelum file ditulis. **Temuan sampingan:** field `resolved_on`/`closed_on` di NextHD Ticket ternyata **sudah otomatis terisi benar sejak lama** (logic di `update_timestamps()`) — cuma belum dicentang di List View, tidak perlu fix kode. **⚠️ Update 8 September (item OO):** field ini sempat hilang lagi dari metadata untuk 3 dari 5 DocType, lihat item OO di atas | Claude + Efendy |
| NN-2 | Butuh laporan gabungan riwayat progress (Worklog) lintas banyak tiket sekaligus, sortable by tanggal | Report baru **"Riwayat Progress Tiket"** dibuat sebagai Standard Query Report (`is_standard=Yes`, file fisik ter-generate ke `nexthd/next_helpdesk/report/riwayat_progress_tiket/`) — `JOIN` `NextHD Ticket Worklog` (PR #11) dengan `NextHD Ticket` induk, kolom: No Tiket, Subjek, Status, Waktu, Teknisi, Aktivitas, Hasil, Durasi Menit, default `ORDER BY waktu DESC`. Terverifikasi 22 baris data langsung tampil. Ditambahkan juga sebagai shortcut dashboard di Workspace "NextHD Report" (struktur di-copy dari template shortcut existing "Detail Tiket Lengkap" untuk hindari bug `report_ref_doctype` kosong yang pernah terjadi 26 Agustus) — **terkonfirmasi tampil di UI**. Problem/Known Error/Change Request tidak punya child table progress serupa, jadi laporan ini murni dari Ticket | Claude + Efendy |
| NN-3 | **Temuan tak terduga:** `NextHD Asset Category` + `NextHD Asset Attribute` (EAV, item II/JJ, commit `281072a`/`81889c0`) ternyata sudah live sejak 28-29 Agustus, TAPI field `asset_type` (Select lama) masih berjalan **paralel** dengan `asset_category` (Link baru) tanpa sinkronisasi otomatis — berisiko divergen | **Keputusan Efendy:** deprecate `asset_type` lama, full migrasi ke `asset_category`. **Dikerjakan:** (1) backfill `asset_category` dari `asset_type` untuk data lama (hasil: 0 mismatch, sudah konsisten semua); (2) **8 `depends_on`** field dinamis (section PC/Laptop/Server, Network Device, Printer, Lainnya) dialihkan dari `doc.asset_type` → `doc.asset_category`; (3) field `asset_type` **disembunyikan** (`hidden=1, read_only=1`) — **non-destruktif**, data lama tetap ada di kolom database, tidak merusak `test_nexthd_asset.py` yang masih mereferensikannya (item W2); (4) report "Detail Aset Lengkap" dipatch, kolom "Tipe" (asset_type) → "Kategori" (asset_category). **Insiden kecil (sudah diperbaiki):** patch report sempat menghasilkan 2 kolom "Kategori" duplikat karena diagnostic awal cuma `grep asset_type`, tidak sadar file report **sudah punya kolom "Kategori" terpisah sejak awal** (bagian dari kerja EAV Devin yang sama, juga tidak terdokumentasi) — diperbaiki via script dedup dengan safety check jumlah kolom sebelum/sesudah, terverifikasi 1 kolom Kategori, field dinamis form tetap berfungsi normal. **⚠️ Update 9 September (item PP):** `asset_type` yang tadinya cuma di-hide di sini, sekarang sudah dihapus TOTAL (metadata + kolom fisik) | Claude + Efendy |
| NN-4 | Butuh laporan filter berdasarkan tag (contoh: tag "pc"/"psu" di tiket) | **Temuan:** tag yang dipakai Efendy adalah **tag native Frappe** (`Tag Link` + `_user_tags`), bukan field kustom — beda dari item "Tag di Tiket" di `DAFTAR_FITUR.md` yang masih ⬜ rencana. Sudah bisa dipakai tanpa development tambahan lewat filter List View bawaan. **Dikerjakan tambahan:** report "Detail Tiket Lengkap" ditulis ulang — ditambahkan kolom "Tag" via `LEFT JOIN tabTag Link` + `GROUP_CONCAT`, filter `tag` baru tersedia, semua filter lama (`from_date`, `to_date`, `status`, `priority`, `team`) dipertahankan persis. Terverifikasi tag tampil benar di kolom baru | Claude + Efendy |

> **Pelajaran baru:** (a) diagnostic `grep` harus mencakup istilah terkait, bukan cuma kata kunci utama — kasus nyata NN-3, `grep asset_type` tidak menangkap kolom "Kategori" yang sudah ada duluan di report yang sama, menyebabkan duplikat kolom sesaat; (b) dokumentasi bisa jauh ketinggalan dari kode aktual kalau Devin bekerja tanpa sesi Claude mendampingi — commit "Update devin eav" sama sekali tidak tercermin di `DAFTAR_FITUR.md` sebelum sesi ini; (c) migrasi field non-destruktif (hide, bukan hapus) terbukti aman untuk field yang masih direferensikan test suite lama — **dan menjadi jembatan aman sebelum penghapusan total (lihat item PP)**.

### ✅ Item MM — SELESAI (2 September): Root Cause Final Regresi Sidebar "NextHD" 17→15 Setiap `bench migrate`

| # | Item | Keterangan | PIC |
|---|---|---|---|
| MM | Sidebar Workspace "NextHD" selalu turun dari 17 item kembali ke 15 item setiap `bench migrate` dijalankan — regresi ini sudah terjadi berulang kali sejak akhir Agustus (sempat dikira selesai di item DD/KK, ternyata belum) | **Root cause final terkonfirmasi lewat investigasi sistematis** (eliminasi satu-per-satu semua fungsi di pipeline `migrate.py`, plus trigger MySQL `BEFORE DELETE` untuk audit langsung karena `general_log` MariaDB tidak bisa diaktifkan/butuh privilege SUPER): file **`nexthd/fixtures/workspace_sidebar.json` masih ada secara FISIK di disk**, meski sudah lama dihapus dari **daftar array** `fixtures = [...]` di `hooks.py`. Ternyata `sync_fixtures()` → `import_fixtures()` (`frappe/utils/fixtures.py`) men-scan **SELURUH isi folder `fixtures/` via `os.listdir()`**, tidak peduli sama sekali apakah file terdaftar di `hooks.py` — jadi menghapus entri dari `hooks.py` **tidak cukup**, file fisiknya juga wajib dihapus dari disk. **Fix:** `rm nexthd/fixtures/workspace_sidebar.json`, tambahkan lagi 2 item yang hilang via `doc.append()`+`doc.save()`. **Diverifikasi stabil lintas 2× `bench migrate` berturut-turut setelah fix** — total tetap 17 item, tidak ada regresi. Detail kronologi lengkap ada di `docs/BUG_WORKSPACE_SIDEBAR.md` bug session 2 September | Claude + Efendy |

### 🔴 PRIORITAS SESI BERIKUTNYA

| # | Item | Keterangan |
|---|---|---|
| 1 | Rename Module "Next Helpdesk" → "NextHD" (item EE) | Masih pending — lihat detail di bawah. Sekarang jadi prioritas utama karena item sidebar (KK/AA/LL/MM) sudah tuntas total 2 September |
| 2 | Konfirmasi visual dashboard shortcut "NextHD Photo" + 6 Report (item BB) | Sudah difix dari sisi data & cache sejak 26 Agustus, tinggal menunggu Efendy hard refresh & konfirmasi visual sebelum di-export ke fixture |
| 3 | Test manual UI: cross-document link dua arah Activity Log (item OO) | Klik tombol "Buat CR dari Problem" dkk, cek baris Activity Log muncul di kedua dokumen dan bisa diklik saling silang |
| 4 | Verifikasi visual browser — warna List View 5 DocType (item PP) | Cek Ticket/Problem/Change Request/Asset/Photo di browser, pastikan ghost checkbox "Status" sudah beneran hilang (bukan cuma tidak dicentang) di List View Settings Ticket/CR/Problem |
| 5 | Bersihkan `fixtures/property_setter.json` (label lama `asset_type`) | Kosmetik, sisa basi dari sebelum item PP, tidak error tapi kotor — bisa dibersihkan kapan saja |
| 6 | `git add`+commit+push semua file `.py`/`.json` yang berubah sesi 5-9 September | Bagian Efendy sesuai aturan project (Claude cuma boleh push `.md`) — banyak perubahan menumpuk dari item NN, OO, PP belum ter-commit ke git |
| 7 | Audit berkala folder `nexthd/fixtures/` vs `hooks.py` + schema drift field custom | Menyusul temuan item MM, OO, PP — cek apakah ada file fixture fisik usang lain, field custom yang cuma dilindungi SQL manual, atau DocType lain dengan `naming_rule` usang yang belum ketahuan |

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
| W2 | `test_nexthd_asset.py` — test lama assert field yang sudah dihapus | Perlu revisi menyeluruh (assert field lama, `MandatoryError asset_category`, `DuplicateEntryError`). **Update 9 September:** sekarang juga akan assert `asset.asset_type` yang sudah dihapus TOTAL (bukan cuma hidden) — makin mendesak untuk direvisi, meski masih prioritas rendah karena tidak mempengaruhi produksi live | Devin |

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

Ringkasan lengkap seluruh item historis (Agustus s/d awal September) tidak diulang di sini — lihat versi sebelumnya di riwayat git file ini. Tambahan sesi 9 September:

| Item | Selesai |
|---|---|
| **Warna List View (Priority/Ticket Type Ticket, Kategori Photo, Status/Asset Category Asset) (item PP)** | ✅ **9 September.** `formatters` di `nexthd_ticket_list.js`, file baru `nexthd_asset_list.js` & `nexthd_photo_list.js`, terdaftar di `hooks.py`. Build+restart sukses, verifikasi visual browser masih pending (lihat Prioritas Sesi Berikutnya) |
| **Hapus duplikat `Custom Field` "status" di Ticket/CR/Problem (item PP)** | ✅ **9 September.** 3 Custom Field (`<DocType>-status`, sisa eksperimen lama) dihapus via `frappe.delete_doc()`. Root cause ghost checkbox List View Settings + warna Status CR yang tidak muncul |
| **Fix `naming_rule="By Series"` usang di 5 DocType (item PP)** | ✅ **9 September.** NextHD Asset, Problem, Change Request, Known Error, Service Catalog — semua diperbaiki ke `By "Naming Series" field`. Bug ini tidak pernah ketahuan sebelumnya karena belum pernah ada `doc.save()` penuh ke DocType-DocType tsb |
| **Hapus total field `asset_type` — metadata + kolom fisik DB (item PP)** | ✅ **9 September.** Sebelumnya cuma di-hide (item NN, 6 September). Sekarang dihapus permanen dari `nexthd_asset.json` (via regenerate `doc.save()`, bukan edit manual — file lama ternyata sudah sangat basi), kolom fisik `DROP COLUMN`, report `detail_aset_lengkap.py`/`.json` disesuaikan (query & filter). `bench migrate` bersih, report diverifikasi jalan normal pasca perubahan |

---

*Dokumen ini dikelola oleh Claude. Update terakhir: 2026-09-09.*

---

## Update 2026-09-09 — Item PP: Warna List View, Fix `naming_rule` Usang 5 DocType, Hapus Total `asset_type`

**Konteks:** Sesi dimulai dari permintaan Efendy menambahkan warna (indicator pill) ke beberapa kolom List View yang masih polos: Priority & Ticket Type (Ticket), Kategori (Photo), Status & "Asset Category" (Asset) — sekaligus menindaklanjuti keluhan lama bahwa 2 baris "Status" di List View Settings Ticket tidak bisa dihapus meski sudah tidak dicentang, dan warna Status Change Request tidak pernah muncul.

**Bagian 1 — Root cause ghost "Status":** audit `tabDocField` menunjukkan hanya 1 baris `status` per DocType (normal), tapi `get_meta()` menghitung 2 — ternyata ada `Custom Field` (`<DocType>-status`, Link ke Workflow State, `hidden=1`) sisa eksperimen lama yang tidak pernah dibersihkan, identik di Ticket/CR/Problem. Dihapus, root cause sekaligus menjelaskan kenapa warna Status Change Request tidak pernah muncul (metadata ambigu field mana yang jadi acuan render).

**Bagian 2 — Permintaan Efendy soal "asset category" ternyata mengarah ke temuan besar:** dari investigasi, ternyata `NextHD Asset Category` (DocType EAV, item II/JJ) memang sudah dipakai dan `asset_type` sudah di-hide sejak item NN (6 September) — tapi field lama itu **masih terpasang di metadata dan kolom fisik DB**, cuma disembunyikan dari form. Efendy meminta dihapus total.

**Bagian 3 — Insiden `naming_rule` yang tidak terduga:** percobaan pertama hapus `asset_type` via `doc.save()` gagal dengan `ValidationError: Naming Rule cannot be "By Series"` — bug lama yang sudah ada sejak dulu tapi baru ketahuan karena `doc.save()` penuh belum pernah dijalankan ke `NextHD Asset`. Setelah `naming_rule` diperbaiki (`By "Naming Series" field`, sesuai `autoname: naming_series:`), audit proaktif ke 5 DocType lain menemukan **4 di antaranya (Problem, Change Request, Known Error, Service Catalog) punya bug identik** — semua diperbaiki dalam satu batch dengan `try/except` per-DocType.

**Bagian 4 — Kesalahan teknis kecil (langsung diperbaiki):** script fix `naming_rule`+hapus `asset_type` pertama gagal total dengan `NameError: name 'doc' is not defined` — root cause: baris kosong di dalam `def main_check():`, melanggar aturan wajib project sendiri (`docs/POLA_KERJA.md`) yang sudah berkali-kali didokumentasikan. Diperbaiki di percobaan kedua, sukses tanpa insiden lanjutan.

**Bagian 5 — Verifikasi sebelum penghapusan final:** dipastikan dulu 0 field lain masih `depends_on` ke `asset_type` (semua 8 sudah ke `asset_category` sejak item NN) dan 100% data (8/8 Asset) sudah punya `asset_category` terisi — baru field dihapus permanen dari JSON (via regenerate `doc.save()`, karena file JSON di repo ternyata sudah sangat basi dan tidak sinkron dengan DB) dan kolom fisik. Report `detail_aset_lengkap` diperbaiki di 2 tempat (query `.py` yang tidak dipakai di kolom output, dan filter dropdown `.json`) — diverifikasi jalan normal (8 baris data) sebelum dan sesudah `bench migrate` + `DROP COLUMN`.

**Pola teknis yang terbukti penting di sesi ini:** (a) selalu verifikasi struktur data (`cat`/`grep`) sebelum menulis script edit — 1 percobaan edit `detail_aset_lengkap.json` sempat gagal `KeyError: 'fields'` karena asumsi struktur JSON salah (report ini pakai key `"filters"`, bukan `"fields"`/`"columns"`); (b) regenerate metadata via `doc.save()` (dengan `developer_mode=1` sementara) lebih aman daripada edit JSON manual untuk DocType yang filenya dicurigai sudah tidak sinkron dengan DB — pola ini sudah dipakai sebelumnya untuk kasus Workspace (item MM) dan sekarang terbukti juga berlaku untuk DocType biasa.

**Status akhir:** semua perubahan database & file `.py`/`.json` sudah live di server, **belum di-`git commit`/push** (bagian Efendy). Verifikasi visual warna List View di browser masih pending — masuk prioritas sesi berikutnya.
