# NextHD — Index Dokumentasi

> **Entry point.** Baca ini dulu — berisi overview dan pointer ke file detail.
>
> **Last updated:** 2026-08-29 17:45 WIB (Item DD ditutup — bug `Link Type must be set first` pada Workspace NextHD sudah diperbaiki, termasuk regresi sidebar "NextHD Reporting" yang sempat hilang akibat proses fix, sudah dikembalikan dan diverifikasi permanen)

---

## Struktur Dokumentasi

| File | Isi |
|---|---|
| `docs/FAQ_DEVELOPER.md` | **Wajib dibaca Devin pertama kali** — kurasi masalah berulang (Workspace/Desktop Icon pasca-migrate) + pembagian kerja Claude/Devin/Efendy + hal yang tidak boleh diubah tanpa izin |
| `docs/SUMMARY.md` | **File ini** — index + project overview + status item belum dikerjakan (operasional harian) |
| `docs/DAFTAR_FITUR.md` | Checklist lengkap semua fitur (selesai/dikerjakan/rencana) dalam satu tabel, termasuk desain Generalisasi Non-IT & Wipe Data Tool (sebelumnya di `ARSITEKTUR.md §8/§9`) |
| `docs/ARSITEKTUR.md` | Infrastruktur, struktur app, DocType/field lengkap, permissions, schema tabel, label ID |
| `docs/WORKFLOW.md` | Notifikasi Telegram + semua state machine + riwayat bug workflow |
| `docs/POLA_KERJA_DAN_BUG.md` | Frappe quirks (Desktop/Workspace/Dashboard Shortcut), aturan wajib saat coding/debug, riwayat bug lengkap |
| `docs/PANDUAN_INSTALASI.md` | Instalasi, setup Telegram/SLA, alur deploy, referensi |
| `docs/AUDIT_SISTEM.md` | Script audit lengkap (schema drift, Workspace, Workflow master data, SLA, fixtures) + script verifikasi ringan pasca-perbaikan + script gabungan cek semua isu Workspace/Sidebar/Dashboard. Dipakai on-demand untuk cek kesehatan server atau sebelum install ke server baru |
| `docs/HANDOFF.md` | **Arsip historis** riwayat sesi 14–24 Agustus 2026 (dipindah dari root repo, 28 Agustus). Sebagian besar isinya sudah dimigrasikan ke file-file di atas — hanya dipakai untuk konteks sejarah, bukan rujukan status terkini |

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
- Workflow approval untuk Change Request (state machine terverifikasi via regression test, 2026-08-20; dedup ulang 24 & 25 Agustus)
- Manajemen Problem dan Known Error (ITIL-lite)
- Notifikasi real-time via Telegram Bot — **✅ terkonfirmasi live**, bot sudah balas dan token/enable sudah terkonfirmasi di NextHD Settings
- SLA monitoring otomatis berbasis jam kerja (warning 30 menit sebelum breach), termasuk **titik-mulai resolution saat "Mulai Kerjakan" + pause/resume saat "Menunggu User"** (PR #8, bugfix `76ce3e9`) — **✅ live + terverifikasi**
- Priority otomatis dari matriks Impact × Urgency, dengan override manual untuk Agent Manager/IT Manager (PR #7) — **✅ live + terverifikasi**
- Multi-tim dengan assignment agent
- Custom reports: Tiket per Bulan, Tiket per Agent, Tiket per Kategori, Tiket per Prioritas (breach SLA), SLA Compliance Bulanan, Aset Bermasalah, Detail Aset Lengkap — **kartu shortcut dashboard "Laporan" sudah ditambah (26 Agustus, fix `report_ref_doctype`+cache, menunggu konfirmasi visual)**, sidebar kiri submenu 6 link Report masih di item AA, sidebar "NextHD Reporting" (11 shortcut Detail Report Lengkap) sudah live sejak 27 Agustus dan dikonfirmasi permanen 29 Agustus (lihat item DD)
- Foto/gambar reusable & bisa di-link antar Ticket/Problem/Asset/Known Error (PR #9) — **✅ live + terverifikasi 24 Agustus**, termasuk sidebar & dashboard Number Card. **Shortcut dashboard "NextHD Photo" (kartu terpisah di section Konfigurasi) ditambah 26 Agustus**, sempat tidak muncul karena cache — sudah difix, menunggu konfirmasi visual. **28 Agustus:** naming series diubah ke `IMG-YYMM-####`, field Judul Foto/Lokasi/Kategori ditambah, dan badge "Dipakai Di" (Dashboard Connections, real-time dari child table, tidak disimpan sebagai field) terpasang di form Photo — **✅ terpasang, perlu re-test dengan foto baru**
- Tombol admin "Reset Data Demo" (hapus semua data transaksi untuk testing, System Manager only, 2x konfirmasi + backup otomatis) — **✅ live + terverifikasi end-to-end 28 Agustus**
- Generalisasi NextHD Asset ke pola EAV (`NextHD Asset Category` + `NextHD Asset Attribute`) — **✅ live 28 Agustus malam, terverifikasi aman 29 Agustus** (item II). **29 Agustus (lanjutan):** field terstruktur lama (brand/model/cpu/ram/storage/os/dst di section PC/Network/Printer) yang sudah duplikat dengan EAV **dihapus dari form**, `search_fields` & report `Detail Aset Lengkap` disesuaikan (item JJ)
- **Rencana ke depan:** Knowledge Base publik (self-service), tag di tiket, CSAT — lihat `docs/DAFTAR_FITUR.md`

---

## 2. Status Item Belum Dikerjakan

> Bagian ini yang **paling sering diupdate tiap sesi**. Item selesai dipindah ke `POLA_KERJA_DAN_BUG.md`.
> Untuk rencana fitur besar yang belum jadi task konkret, lihat `docs/DAFTAR_FITUR.md`.

### ✅ Item DD — SELESAI (29 Agustus, ~17:45 WIB): Bug `Link Type must be set first` pada Workspace NextHD

| # | Item | Keterangan | PIC |
|---|---|---|---|
| DD | `frappe.get_doc("Workspace", "NextHD").save()` gagal validasi | **Root cause:** row `tabWorkspace Link` (`name=u6nb1c41c1`, label "Reporting Data", `link_to=/app/nexthd-report`, `type=URL`, `link_type` kosong) — sisa percobaan lama yang tidak pernah valid (Page `nexthd-report` yang dimaksud tidak pernah ada di `tabPage`). **Percobaan gagal:** set `link_type="Workspace"` → ditolak (field cuma terima DocType/Page/Report); set `link_type="Page"` → `LinkValidationError` karena Page `nexthd-report` tidak eksis. **Fix final:** baris "Reporting Data" **dihapus total** dari `tabWorkspace Link` — fungsinya memang sudah digantikan sidebar "NextHD Reporting" (dibuat 27 Agustus lewat UI, mengarah ke Workspace "NextHD Report" berisi 11 shortcut report). Setelah dihapus, `doc.save()` berhasil dan menulis ulang fixture `nexthd/next_helpdesk/workspace/nexthd/nexthd.json`. **Regresi ditemukan & diperbaiki dalam sesi yang sama:** proses `doc.save()` di atas sempat menghapus item sidebar manual "NextHD Reporting" dari `Workspace Sidebar Item` (root cause: `Workspace Sidebar.standard` ternyata `0`, bukan `1` — menurut `POLA_KERJA_DAN_BUG.md §1.C`, `standard` harus `1` agar `export_sidebar()` menulis file & perubahan permanen). Fix: `standard` diset ke `1` via `frappe.db.set_value()`, lalu "NextHD Reporting" ditambahkan kembali lewat UI **"panah ke bawah (kiri atas) → Edit Sidebar"** (BUKAN via titik tiga kanan atas — lokasi menu berbeda dari dugaan awal). **Verifikasi akhir (semua ✅):** `doc.save()` Workspace NextHD jalan tanpa error berulang kali, sidebar "NextHD" tetap 16 item lengkap (termasuk "NextHD Reporting"), fixture `nexthd/nexthd/workspace_sidebar/nexthd.json` berisi label "NextHD Reporting". **Catatan tambahan:** saat diklik, "NextHD Reporting" berpindah ke Workspace "NextHD Report" yang sidebar-nya sendiri cuma 2 item (Dashboard + NextHD Report) — ini **bukan bug**, memang workspace itu didesain sebagai halaman kumpulan shortcut report, bukan hub navigasi. Detail kronologi lengkap di `docs/POLA_KERJA_DAN_BUG.md` bug session 29 Agustus | Claude + Efendy |

### 🔴 Item EE — Task Pending: Rename Module "Next Helpdesk" → "NextHD"

| # | Item | Keterangan | PIC |
|---|---|---|---|
| EE | `tabModule Def` masih bernama "Next Helpdesk" | Menyebabkan sidebar module-based (Report page, Page kustom seperti `nexthd-reset-data`) masih menampilkan header "Next Helpdesk", bukan "NextHD". Dikonfirmasi ulang 28 Agustus bukan Workspace nyasar, murni dari nama Module Def. Solusi: rename `Module Def` + update `modules.txt`, risiko menengah (mempengaruhi banyak referensi internal) — perlu sesi terpisah dengan backup wajib | Claude + Efendy |

### 🔶 Item BB — Dashboard Shortcut "NextHD Photo" & 6 Report (Menunggu Konfirmasi Visual, 26 Agustus)

| # | Item | Keterangan | PIC |
|---|---|---|---|
| BB | Kartu shortcut dashboard `/desk/nexthd`: 1 DocType (NextHD Photo) + 6 Report (section baru "Laporan") | Insert ke `tabWorkspace Shortcut` + update `Workspace.content` sudah dijalankan (7 shortcut baru, total 32 blok). Sempat tidak muncul di dashboard — root cause: `report_ref_doctype` kosong untuk 6 shortcut Report (fixed), dan cache Redis untuk shortcut Photo (fixed via `bench clear-cache`+`clear-website-cache`). **Menunggu Efendy hard refresh & konfirmasi visual** sebelum di-export ke fixture. Detail lengkap di `docs/POLA_KERJA_DAN_BUG.md` bug session 26 Agustus | Claude + Efendy |

> **Catatan penting:** item BB (kartu dashboard, tabel `Workspace Shortcut`) **terpisah total** dari item AA di bawah (sidebar kiri, tabel `Workspace.links`) — dua sistem berbeda meski sama-sama menyangkut Report & Photo. Jangan disatukan saat verifikasi.

### 🔶 Item AA — Sidebar 6 Link Report (Sedang Berjalan, 25 Agustus)

| # | Item | Keterangan | PIC |
|---|---|---|---|
| AA | Ganti menu sidebar "NextHD Report" generic dengan 6 link report langsung | **Root cause ditemukan:** sidebar sebenarnya punya dua tabel — `Workspace Sidebar Item` (turunan/auto-generate, ditimpa ulang tiap migrate) dan `Workspace.links` (sumber asli, bertahan lewat migrate). Percobaan pertama (edit `Workspace Sidebar Item` langsung) **gagal saat migrate diuji** — data sempat hilang, sudah di-restore dari backup. Pendekatan baru (edit `Workspace.links` langsung) **sudah dijalankan dan diverifikasi** via `bench console`: 19 item total (13 lama + 6 report baru). **`bench migrate` untuk konfirmasi final BELUM dijalankan.** Detail lengkap + script di `docs/AUDIT_SISTEM.md` | Claude + Efendy |

### ✅ Item Y & Z — Selesai (24 Agustus)

| # | Item | Keterangan | PIC |
|---|---|---|---|
| Y | Business Hours "Sabtu" | **Keputusan Efendy:** Sabtu hari kerja, 08:00–15:00. Data production diupdate via `bench console`, `install.py` diselaraskan (Sabtu beda jam dari Senin-Jumat, `is_working_day=1`) | Efendy |
| Z | `install.py` kehilangan indentasi (bug baru, dari commit `b3a24b2`) | File jadi `IndentationError` jika dijalankan — root cause: tab kemungkinan hilang saat heredoc/paste ke terminal sesi sebelumnya. Ditulis ulang dengan indentasi tab, diverifikasi via `python3 -c "import ast; ast.parse(...)"` sebelum commit | Efendy |

### ✅ Semua Item Utama SUDAH Live & Terverifikasi

| # | Fitur | Bukti Verifikasi | PIC |
|---|---|---|---|
| A+C | Priority matrix otomatis + override permission | [PR #7](https://github.com/silverefendy/nexthd/pull/7). `bench console`: Impact=Tinggi+Urgency=Tinggi → `priority=Kritis` otomatis. `permlevel=1` + Agent Manager/IT Manager override terkonfirmasi | Efendy |
| B+T | Pause/resume SLA + recalculate saat "Mulai Kerjakan" | [PR #8](https://github.com/silverefendy/nexthd/pull/8) + bugfix `76ce3e9` (waiting_log sempat ke-wipe saat save berikutnya, sudah difix). `sla_resolution_by` ter-extend sesuai durasi pause, terverifikasi | Efendy |
| U | Permission `NextHD SLA Policy` & `Business Hours` | Commit `31f35da`. `has_permission()` role Agent Manager return `True` untuk read & write | Efendy |
| G | Halaman NextHD SLA Policy 404 | Root cause (item U) fix, halaman sudah bisa diakses non-Administrator | Efendy |
| D | Deploy PR #6 (Web Form + Telegram i18n) | `bench console`: Web Form `Tiket Saya` ditemukan, `route: tiket-saya`, `published: 1` | Efendy |
| E | Verifikasi end-to-end Telegram | Bot `@cmlhelpdesk_bot` terkonfirmasi balas pesan nyata (test manual 22 Agustus). `NextHD Settings`: token terisi, `enable_telegram_notification: 1` | Efendy |
| F | Permission `reply` di Waiting Log | `bench console`: field `reply` `permlevel=1`, role Requester `permlevel=1, write=1` — konfigurasi terkonfirmasi benar | Efendy |
| H | `NextHD Holiday` di sidebar Workspace | `bench console`: query `tabWorkspace Sidebar Item` → Holiday ditemukan (`True`) | Efendy |
| W | Fitur foto reusable (Ticket/Problem/Asset/Known Error) | [PR #9](https://github.com/silverefendy/nexthd/pull/9), commit `03a3c5d`, merged 24 Agustus. DocType `NextHD Photo`/`NextHD Photo Link` aktif, sidebar + Number Card "Total Foto Terupload" terverifikasi live via `bench console` 24 Agustus | Efendy |
| X | `install.py` — nilai SLA default usang | Diperbaiki ke nilai SOP final 19 Agustus, di-commit `b3a24b2` → `2d795b9`, 24 Agustus. **Lihat juga item Z** — commit ini sempat merusak indentasi file, sudah diperbaiki ulang | Efendy |
| FF | Naming Series `NextHD Photo` → `IMG-YYMM-####` | Diverifikasi: dokumen baru bernama `IMG-2608-0001` dst | Efendy |
| GG | Field baru `NextHD Photo`: Judul Foto (`title_field`), Lokasi, Kategori (Link → `NextHD Category`) | Terpasang 28 Agustus | Efendy |
| HH | Tombol "Reset Data Demo" — hapus semua data transaksi (System Manager only) | Test sungguhan berhasil: 14 Ticket, 15 Problem, 3 Change Request, 2 Known Error, 6 Asset, 4 Photo terhapus; backup otomatis, data master tidak ikut terhapus, penomoran `tabSeries` ikut direset | Efendy |
| II | Generalisasi EAV `NextHD Asset` (`NextHD Asset Category` + `NextHD Asset Attribute`) | `bench console`: DocType ada di DB, kolom fisik ter-migrate, 6/6 record Asset existing sudah terisi `asset_category`. Commit `281072a`+`81889c0`, 28 Agustus 23:07 WIB | Efendy |
| JJ | Cleanup field terstruktur Asset lama (duplikat EAV) + rewrite `Detail Aset Lengkap` | Field brand/model/cpu/ram/storage/os/dst (20 field + 4 column break) dihapus dari `nexthd_asset.json`; `search_fields` & report disesuaikan; commit `d964531` → `b148223`, 29 Agustus. Terverifikasi via screenshot: form bersih, report EAV jalan, search Asset jalan | Efendy |
| DD | Bug `Link Type must be set first` pada Workspace NextHD | Row "Reporting Data" bermasalah dihapus, `doc.save()` berhasil. Regresi sidebar "NextHD Reporting" (sempat hilang, root cause `Workspace Sidebar.standard=0`) diperbaiki dalam sesi sama, dikonfirmasi permanen 29 Agustus ~17:45 WIB | Efendy |

> **Catatan Item E:** user test `test.requester@ciptamebel.co.id` sendiri belum pernah kirim `/start`+`/link` ke bot (field `telegram_chat_id` masih kosong untuk akun ini) — tapi ini bukan bug, cuma user dummy tsb memang belum di-link manual. Bot-nya sendiri sudah terbukti bekerja pakai akun Telegram lain.

### 🟢 Prioritas Rendah — Belum Mendesak / Masih Wacana

| # | Fitur | Keterangan | PIC |
|---|---|---|---|
| I | Wipe data testing (versi lama/checklist) | Sudah **diimplementasikan versi ringkas** sebagai tombol "Reset Data Demo" (item HH, 28 Agustus) — desain lengkap dengan UI checkbox per DocType di `DAFTAR_FITUR.md` masih jadi opsi pengembangan lanjutan kalau dibutuhkan granularitas lebih | Claude (desain), Efendy (waktu eksekusi) |
| J | Workflow — testing end-to-end di UI browser | Regression test backend sudah lulus 100% (2026-08-20). Belum ditest klik manual di browser untuk verifikasi tombol Actions & permission per role tampil benar | Efendy |
| K | Role assignment ke user spesifik | `support@ciptamebel.co.id` → role IT Manager. Keputusan: sementara 1 akun shared dulu | Efendy |
| L | File `HANDOFF_SLA_NextHD_2026-08-19.md` | Disebut di `docs/HANDOFF.md` tapi tidak ada di repo. Kalau masih ada di server, perlu `git add` + commit sebelum hilang | Efendy |
| M | Guard permanen duplikasi workflow transition | Root cause **sekarang terkonfirmasi** (25 Agustus): `Workflow Transition` adalah fixture aktif di `hooks.py`, dan file fixture-nya menumpuk beberapa generasi export lama — dedup di database saja tidak permanen kalau fixture di repo tidak ikut dibersihkan. Sudah dibersihkan total 2× (commit `9cf994f`, lalu `322827f` untuk perbaiki `name` mismatch). Belum ada mekanisme pencegahan otomatis | Claude |
| N | Pemetaan tanggal Cuti Bersama 2026 belum dicek silang ke SKB asli | Data ditambahkan berdasar asumsi pola umum kalender cuti bersama Indonesia, bukan dibaca langsung dari teks SKB 3 Menteri | Efendy |
| O | Dashboard "Aset Bermasalah" (Number Card) | Usulan, belum dikerjakan | - |
| P | SLA otomatis untuk Problem/Change Request | Saat ini SLA hanya untuk Ticket | - |
| Q | Notifikasi Telegram untuk Problem/CR | Sengaja ditunda, fokus ke fitur lain dulu | - |
| R | Laporan bulanan otomatis (jumlah tiket, MTTR) | Usulan, belum dikerjakan | - |
| V | Link Telegram untuk user test `test.requester` | Belum pernah kirim `/start`+`/link` — kalau mau dites tuntas, tinggal eksekusi manual + rerun script verifikasi | Efendy |
| W2 | `test_nexthd_asset.py` — test lama assert field yang sudah dihapus, lebih luas dari dugaan awal | Beberapa test method (sekitar baris 272, 349, 408) meng-assert `asset.brand`, `.model`, `.serial_number`, dst yang sudah tidak ada di form NextHD Asset (dihapus di item JJ, 29 Agustus). **Update 29 Agustus (uji coba sesi lanjutan):** dari 16 test, 8 gagal — TAPI mayoritas kegagalan (6 test) ternyata bukan dari field yang dihapus, melainkan `MandatoryError: asset_category` (field wajib sejak migrasi EAV 28 Agustus, test lama tidak mengisi ini), 1 `DuplicateEntryError` (sisa data test tidak ke-cleanup), 2 `AssertionError` ekspektasi salah (`None` vs `""`). Cakupan masalah test suite ini lebih luas dari dugaan awal — perlu revisi menyeluruh, bukan cuma soal field lama. Testing sempat diaktifkan sementara (`allow_tests=true`) untuk diagnosa, sudah dimatikan lagi. Cocok untuk task Devin terpisah, prioritas rendah, tidak mendesak | Devin |

> **Item S (Generalisasi non-IT/EAV) sudah dipindah ke tabel "SUDAH Live & Terverifikasi" di atas** (lihat item II & JJ) — dikerjakan 28-29 Agustus, terverifikasi aman. Tidak lagi berstatus wacana.
>
> **Catatan lain:** rencana fitur besar (Knowledge Base publik, tag, CSAT, merge tiket, eskalasi
> otomatis, dst) dipindahkan ke `docs/DAFTAR_FITUR.md` supaya tidak bercampur dengan open
> items operasional di atas.

### GitHub Issues & PR — Riwayat Devin

| # | Judul | Status |
|---|---|---|
| [Issue #4](https://github.com/silverefendy/nexthd/issues/4) | User Portal Requester via Frappe Web Form | Selesai via PR #6 |
| [Issue #5](https://github.com/silverefendy/nexthd/issues/5) | Telegram Notification — i18n (`frappe._()`) | Selesai via PR #6 |
| [PR #6](https://github.com/silverefendy/nexthd/pull/6) | feat: Add Web Form for Requester role and Telegram i18n | Merged 2026-08-20 — **✅ dideploy & terverifikasi live 22 Agustus** |
| [PR #7](https://github.com/silverefendy/nexthd/pull/7) | Task 1: Priority matrix otomatis + override permission | Merged 2026-08-22 10:13 WIB — **✅ live + terverifikasi** |
| [PR #8](https://github.com/silverefendy/nexthd/pull/8) | Task 2: SLA resolution timing — mulai "Mulai Kerjakan", pause "Menunggu User" | Merged 2026-08-22 10:31 WIB, bugfix `76ce3e9` — **✅ live + terverifikasi** |
| [PR #9](https://github.com/silverefendy/nexthd/pull/9) | Fitur foto reusable — `NextHD Photo` + `NextHD Photo Link`, galeri swipe, kompresi otomatis | Merged 24 Agustus, commit `03a3c5d` — **✅ live + terverifikasi (termasuk sidebar) 24 Agustus** |

---

## 3. Hal-hal yang SUDAH Selesai (Ringkasan)

> Detail lengkap ada di `POLA_KERJA_DAN_BUG.md §4` dan riwayat update `docs/HANDOFF.md` (arsip).

| Item | Selesai |
|---|---|
| `business_hours.py` — logic all-or-nothing | ✅ 2026-08-20 |
| Tombol workflow "Mulai Kerjakan" (Baru → Sedang Dikerjakan) | ✅ Ada di `nexthd_ticket_workflow.json`, 7 transisi terverifikasi |
| Field `impact`, `urgency`, `waiting_log` di form Ticket | ✅ Ada di `field_order` `nexthd_ticket.json` |
| Priority matrix otomatis + override manual (item A+C) | ✅ PR #7, **live + terverifikasi 22 Agustus** |
| Pause/resume SLA saat "Menunggu User" (item B+T) | ✅ PR #8 + bugfix `76ce3e9`, **live + terverifikasi 22 Agustus** |
| Permission `NextHD SLA Policy` & `NextHD Business Hours` (item U) | ✅ Commit `31f35da`, **live + terverifikasi 22 Agustus** |
| Halaman NextHD SLA Policy 404 (item G) | ✅ Root cause (item U) fix, **live + terverifikasi 22 Agustus** |
| Deploy PR #6 ke produksi (item D) | ✅ **Live + terverifikasi 22 Agustus** — Web Form `tiket-saya` published |
| Verifikasi Telegram end-to-end (item E) | ✅ **Live + terverifikasi 22 Agustus** — bot balas, settings terkonfirmasi |
| Permission `reply` Waiting Log (item F) | ✅ **Terverifikasi 22 Agustus** — permlevel & role permission benar |
| `NextHD Holiday` di sidebar (item H) | ✅ **Terverifikasi 22 Agustus** — ditemukan di query sidebar |
| Regression test workflow (Ticket, Problem, Change Request) | ✅ 2026-08-20, semua lulus |
| Dedup 21 transisi workflow duplikat | ✅ 2026-08-20 |
| Bug Telegram `get_single_value` | ✅ Fix commit, dan sudah diverifikasi live (item E) |
| Number Card dashboard (kolom `number_card_name`) | ✅ 2026-08-21 |
| Shortcut `doc_view` NextHD Settings | ✅ 2026-08-21 |
| Naming series seragam YY.MM semua DocType | ✅ 2026-08-19 |
| `docs/FAQ_DEVELOPER.md` dibuat — kurasi masalah berulang untuk Devin + pembagian kerja | ✅ 2026-08-22, digabung 2026-08-23 |
| `docs/AUDIT_SISTEM.md` dibuat — script audit lengkap kesehatan server/repo | ✅ 2026-08-23 |
| `docs/DAFTAR_FITUR.md` dibuat — checklist lengkap semua fitur dalam satu tabel | ✅ 2026-08-23 |
| Restrukturisasi dokumentasi — rename `PANDUAN_INSTALASI.md`, hapus file lama, potong §8/§9 dari `ARSITEKTUR.md` | ✅ 2026-08-23 |
| Fitur foto reusable (item W) — DocType, galeri, kompresi, sidebar, dashboard | ✅ PR #9, commit `03a3c5d` + `a69df61`, **live + terverifikasi penuh 24 Agustus** |
| `install.py` — nilai SLA default usang (item X) | ✅ Commit `b3a24b2` → `2d795b9`, 24 Agustus |
| Sidebar "NextHD Photo" tidak sync dari reimport JSON | ✅ Root cause: `import_file_by_path` tidak sync child table `links`. Fix manual via ORM `doc.save()`, 24 Agustus |
| Duplikasi Workflow Transition round 2 (Ticket/Problem/Change Request) | ✅ Root cause: `Workflow Action Master` hilang. Dedup ulang + master dibuat, 24 Agustus |
| Cuti Bersama 2026 — 8 hari ditambahkan ke `NextHD Holiday` | ✅ 24 Agustus (total 25 record) |
| Script verifikasi ringan pasca-perbaikan ditambahkan ke `AUDIT_SISTEM.md` | ✅ 24 Agustus |
| Business Hours Sabtu — dikonfirmasi hari kerja 08:00–15:00 (item Y) | ✅ Keputusan Efendy, 24 Agustus. Data production + `install.py` diselaraskan |
| `install.py` kehilangan indentasi akibat commit sebelumnya (item Z) | ✅ Ditulis ulang + diverifikasi syntax-nya sebelum commit, 24 Agustus |
| Duplikasi Workflow Transition round 3 — root cause fixture di repo (bukan Workflow Action Master) ditemukan & diperbaiki | ✅ 25 Agustus, fixture ditulis ulang (commit `9cf994f`), lalu `name` disamakan dengan DB (commit `322827f`). Belum diuji lewat migrate baru |
| Root cause sidebar dikoreksi total — `Workspace.links` (bukan `Workspace Sidebar Item`) adalah sumber asli | ✅ 25 Agustus. Percobaan pertama sempat menghapus data sidebar via migrate, di-restore dari backup. 6 link report berhasil dipindahkan ke `Workspace.links` (19 item total), migrate belum diuji — lihat item AA & `docs/AUDIT_SISTEM.md` |
| Dashboard shortcut "NextHD Photo" + 6 Report ditambah ke `Workspace Shortcut` (item BB) | ✅ Diinsert 26 Agustus (7 shortcut baru, `content` 32 blok). Sempat tidak render — root cause `report_ref_doctype` kosong (6 Report) + cache Redis (Photo), keduanya sudah difix. Menunggu konfirmasi visual Efendy — lihat `docs/AUDIT_SISTEM.md` & `POLA_KERJA_DAN_BUG.md` |
| Naming Series `NextHD Photo` → `IMG-YYMM-####` (item FF) | ✅ 28 Agustus, terverifikasi dokumen baru `IMG-2608-0001` |
| Field baru `NextHD Photo` — Judul Foto, Lokasi, Kategori (item GG) | ✅ 28 Agustus. Reference balik "dipakai di mana" sengaja **tidak** disimpan sebagai field statis (risiko tertimpa kalau 1 foto dipakai di >1 dokumen) — dipindah ke Dashboard Connections |
| Dashboard Connections "Dipakai Di" pada `NextHD Photo` | ✅ Terpasang 28 Agustus via `get_dashboard_data()`, real-time dari child table `NextHD Photo Link` di semua parent (Ticket/Asset/Problem/Known Error), tidak ada risiko data tertimpa. **Perlu re-test dengan foto baru** — foto contoh lama sudah ikut terhapus tombol Reset Data Demo sebelum sempat ditest ulang |
| Tombol "Reset Data Demo" (item HH) | ✅ Selesai & terverifikasi end-to-end 28 Agustus — System Manager only (cek backend), 2x konfirmasi (dialog + ketik `RESET`), backup otomatis via `frappe.utils.backups.new_backup()`, counter `tabSeries` ikut direset. Bug awal `subprocess.run(["bench",...])` gagal di web worker (`FileNotFoundError`) — diganti panggilan langsung ke fungsi Python `new_backup()`, tidak bergantung shell `PATH` |
| Shortcut Workspace "Admin" (tombol Reset Data Demo) tidak muncul di UI | ✅ 28 Agustus. Root cause: Workspace v16 dikontrol field `content` (JSON blocks), bukan otomatis baca semua row `tabWorkspace Shortcut`. Fix: update `content` via `frappe.db.set_value()` langsung (skip validasi dokumen penuh karena bug lain — lihat item DD), dijalankan via `bench execute` (bukan `bench console`, supaya cabang `if/else` tidak salah parse indentasi) |
| Housekeeping struktur dokumentasi — `HANDOFF.md` dipindah dari root repo ke `docs/HANDOFF.md` | ✅ 28 Agustus. `README.md` diperbarui (link dokumentasi mengikuti struktur `docs/` multi-file terbaru). Sekarang semua file `.md` project konsisten berada di `docs/` (README.md tetap di root sesuai konvensi GitHub) |
| Generalisasi EAV `NextHD Asset` (item II/S) — `NextHD Asset Category` + `NextHD Asset Attribute` | ✅ Dikerjakan 28 Agustus malam (commit `281072a`+`81889c0`, oleh Efendy/Devin), diverifikasi aman 29 Agustus pagi: DocType & kolom fisik ter-migrate, 6/6 record Asset existing sudah terisi kategorinya, 7 record master, 19 baris attribute terpakai |
| Cleanup field terstruktur Asset lama + rewrite `Detail Aset Lengkap` berbasis EAV (item JJ) | ✅ 29 Agustus, commit `d964531` → `b148223`. 20 field + 4 column break dihapus dari `nexthd_asset.json`; Property Setter `search_fields` diupdate (`asset_name,assigned_to,serial_number` → `asset_name,assigned_to`); `detail_aset_lengkap.py` ditulis ulang pakai `LEFT JOIN` + `GROUP_CONCAT` ke `NextHD Asset Attribute`. Terverifikasi via screenshot Efendy: form bersih, report EAV jalan, report "Aset Bermasalah" tetap normal, search Link ke Asset jalan |
| Bug `Link Type must be set first` pada Workspace NextHD (item DD) + regresi sidebar "NextHD Reporting" | ✅ 29 Agustus ~17:45 WIB. Row "Reporting Data" (`link_type` kosong, sisa percobaan lama yang tak pernah valid) dihapus dari `tabWorkspace Link`. `doc.save()` berhasil. Regresi: `doc.save()` sempat menghapus "NextHD Reporting" dari sidebar karena `Workspace Sidebar.standard=0` — diperbaiki ke `1`, item ditambahkan kembali via UI "Edit Sidebar" (menu di panah kiri atas, bukan titik tiga kanan atas), diverifikasi permanen via `bench console` berulang kali (`doc.save()` tetap sukses, 16 item sidebar tetap utuh, fixture ter-update) | Efendy |

---

*Dokumen ini dikelola oleh Claude. Update terakhir: 2026-08-29 17:45 WIB.*

---

## Update 2026-08-28 (Lanjutan #2) — Navigasi Relasi Antar Dokumen & Schema Drift Ditemukan

**Konteks:** Menindaklanjuti investigasi "Connections Asset-Problem tidak muncul" dari sesi sebelumnya hari yang sama.

**Temuan kritis:** Field `related_asset` di NextHD Problem sempat **hilang dari metadata Frappe** (schema drift) meski data & kolom fisik aman — root cause: fixture `DocField` di `hooks.py` sudah tidak terdaftar. Sudah direstore permanen ke `nexthd_problem.json`. **Ini memperkuat pentingnya menjalankan `docs/AUDIT_SISTEM.md §1` secara berkala** — drift semacam ini tidak menimbulkan error apa pun sampai field-nya dibutuhkan.

**Ditutup:** Rencana pakai `internal_links`/`get_dashboard_data()` untuk memunculkan relasi forward-link di widget Connections — **dikonfirmasi tidak applicable** (hanya berlaku untuk child table). Diganti solusi tombol Client Script manual, sudah diimplementasi & live untuk semua pasangan relasi (Problem↔Asset, Problem↔Change Request, Problem↔Known Error, Problem↔Ticket, Change Request↔Asset, Change Request↔Problem, Known Error↔Problem). Detail lengkap di `POLA_KERJA_DAN_BUG.md §5`.

**Bug tambahan difix:** `related_asset` tidak ter-copy otomatis saat "Buat Change Request dari Problem" (sekarang sudah), dan race condition di `frappe.client.set_value` yang menyebabkan field balik `Problem.change_request` gagal ter-set diam-diam (sudah difix + data lama di-backfill).

**Item baru untuk sesi berikutnya:** Known Error tidak punya field balik ke Change Request yang dibuat darinya — belum ada tombol "Lihat Change Request Terkait" di Known Error. Prioritas rendah, bukan bug kritis.

---

## Update 2026-08-29 08:15 WIB — Item II Ditutup: Struktur EAV NextHD Asset Terkonfirmasi Aman

**Konteks:** Menindaklanjuti Item II (temuan sesi pagi ini) — struktur EAV `NextHD Asset` yang sempat dicurigai sebagai perubahan tak terdokumentasi/berisiko.

**Hasil investigasi (script `bench console` dijalankan Efendy):**
- `NextHD Asset Category` & `NextHD Asset Attribute`: ada di database ✅
- Kolom fisik `asset_category` di `tabNextHD Asset`: sudah ter-migrate ✅
- **6/6 record NextHD Asset existing (AST-2608-0001 s/d 0006) semua sudah terisi `asset_category`** — 0 record kosong ✅
- 7 record master `NextHD Asset Category`, 19 baris `NextHD Asset Attribute` sudah dipakai ✅
- `asset_category` memang `reqd=1` di meta server, tapi aman karena semua data existing sudah lengkap

**Sumber perubahan (dari `git log`):** commit `281072a` ("Update devin eav") dan `81889c0` ("Update devin attribute eav"), author **silverefendy**, Jumat 28 Agustus 2026 pukul 23:07:42 WIB dan setelahnya. **Kesimpulan: ini pekerjaan sah Efendy sendiri (via Devin), bukan insiden atau perubahan tak terotorisasi** — sekadar belum sempat dilaporkan/didokumentasikan ke sesi chat Claude sebelumnya karena dikerjakan di luar percakapan tersebut.

**Tidak ada tindakan perbaikan yang diperlukan.** Peringatan "jangan create/edit NextHD Asset" dari update sebelumnya (jam 09:00 pagi ini) **sudah dicabut** — form Asset aman dipakai normal.

**Pelajaran untuk sesi berikutnya:** kalau menemukan perubahan kode/struktur yang tidak tercatat di riwayat chat, cek dulu `git log --oneline -- <path>` dan `git log -1 --format="%an %ad %s" -- <path>` sebelum menyimpulkan itu insiden — bisa jadi memang pekerjaan sah yang dilakukan di luar sesi chat tersebut (lewat Devin langsung, atau sesi lain).

---

## Update 2026-08-29 09:45 WIB — Item JJ Selesai: Cleanup Field Terstruktur Asset (Duplikat EAV)

**Konteks:** Menindaklanjuti item II (EAV dikonfirmasi aman) — field terstruktur lama di `NextHD Asset` (per `asset_type`: PC/Laptop/Server, Network Device, Printer) sekarang sudah punya 2 tempat penyimpanan yang tumpang tindih dengan `asset_attributes` (EAV). Efendy minta field lama dihapus, field catatan bebas dipertahankan.

**Langkah verifikasi sebelum eksekusi (wajib, sesuai pola project ini — jangan hapus field tanpa cek referensi & backfill dulu):**
1. Script `bench console` bandingkan tiap field lama (non-kosong) di 6 Asset existing vs baris `NextHD Asset Attribute` — **semua cocok, 0 data hilang**.
2. Cek referensi field yang akan dihapus di Property Setter, Client Script, Report, Print Format:
   - Property Setter `search_fields` (`NextHD Asset-main-search_fields`) memakai `serial_number` — **wajib diupdate**.
   - Report `detail_aset_lengkap.py` — raw SQL langsung baca 6 kolom yang akan dihapus — **wajib ditulis ulang**.
   - Client Script (`a258744559`, `cs_known_error_from_problem`) dan report "Tiket per Bulan" sempat ke-flag tapi setelah dicek isi baris persisnya, ternyata **false positive** (substring match kata "os" di "phot**os**"/"cl**os**ed_on", bukan field `os` asli) — tidak perlu disentuh.
   - `test_nexthd_asset.py` punya beberapa test method yang meng-assert field lama — akan gagal, **sengaja tidak digarap** di sesi ini (dicatat sebagai item W2, pending untuk Devin).

**Eksekusi:**
- `nexthd_asset.json`: 20 field (`brand`, `model`, `serial_number`, `cpu`, `ram`, `storage`, `os`, `net_brand`, `net_model`, `net_serial_number`, `ip_address`, `mac_address`, `device_role`, `printer_brand`, `printer_model`, `printer_serial_number`, `printer_type`) + 4 column break dihapus dari `field_order` dan `fields`. Field catatan bebas (`peripheral_notes`, `net_notes`, `printer_notes`, `other_description`) dan section "Lainnya" **tidak diubah**.
- Property Setter `search_fields`: `asset_name,assigned_to,serial_number` → `asset_name,assigned_to` (child table EAV tidak bisa dipakai di `search_fields` Link).
- `detail_aset_lengkap.py` ditulis ulang: `LEFT JOIN` ke `NextHD Asset Attribute`, kolom baru "Spesifikasi (EAV)" (agregat `attribute_name: attribute_value` via `GROUP_CONCAT`), plus kolom `brand`/`serial_number`/`sumber`/`catatan` yang ternyata sudah ada langsung sebagai kolom di child table EAV (bukan cuma `attribute_name`/`attribute_value`/`unit` generik seperti desain awal di `DAFTAR_FITUR.md`).

**Hasil `bench migrate` + verifikasi Efendy (screenshot):**
- Form NextHD Asset: section PC/Network/Printer cuma tampil field catatan, EAV tetap terisi ✅
- Report "Detail Aset Lengkap": kolom Spesifikasi/Brand/dst terisi benar dari EAV ✅
- Report "Aset Bermasalah": tetap tampil normal ✅
- Search Link ke Asset (di form Ticket, field `affected_asset`) masih berfungsi ✅

**Temuan sampingan (tidak berbahaya, dicatat untuk kejelasan):** commit yang sama (`d964531`) ikut membawa `git add .` perubahan tak terkait di `aset_bermasalah.json`/`.py` (filter diganti dari `asset_type` Select ke `asset_category` Link) — dikonfirmasi via `git show` bahwa ini **bukan** dari script Claude, melainkan perubahan yang sudah ada di working directory server sebelum sesi ini (kemungkinan sisa kerja Devin terkait migrasi EAV 28 Agustus malam yang belum sempat di-commit). Sudah diverifikasi jalan normal, tidak ada regresi — cuma "menumpang" commit karena `git add .`.

**Pelajaran:** kalau memakai `git add .` di server yang mungkin punya perubahan lain menumpuk, selalu `git status`/`git diff` dulu sebelum commit untuk memastikan tidak ada perubahan tak terduga ikut ter-commit tanpa direview — di kasus ini aman, tapi bisa jadi masalah kalau perubahan menumpuk itu ternyata belum siap/salah.

**Pending untuk sesi berikutnya (item W2):** `test_nexthd_asset.py` perlu direvisi (hapus/update test yang assert field lama) — cocok untuk task Devin terpisah, tidak mendesak.

---

## Update 2026-08-29 17:45 WIB — Item DD Selesai: Bug Workspace Link + Regresi Sidebar "NextHD Reporting"

**Konteks:** Menindaklanjuti item DD (pending sejak 28 Agustus) — bug `Link Type must be set first` yang menghalangi `doc.save()` normal pada Workspace NextHD.

**Kronologi fix:**
1. Row bermasalah `tabWorkspace Link` (`name=u6nb1c41c1`, label "Reporting Data", `link_type` kosong, `link_to=/app/nexthd-report`) dicek ulang — Page `nexthd-report` yang dituju **tidak pernah ada** di `tabPage` (yang eksis cuma `nexthd-reset-data`), jadi baris ini memang sejak awal tidak pernah valid/berfungsi.
2. Dua percobaan set `link_type` (`Workspace`, lalu `Page`) sama-sama gagal validasi. Diputuskan **hapus total** baris tersebut — fungsinya sudah digantikan sidebar "NextHD Reporting" (dibuat 27 Agustus via UI, mengarah ke Workspace "NextHD Report" berisi 11 shortcut report).
3. Setelah dihapus, `frappe.get_doc("Workspace", "NextHD").save()` **berhasil** — fixture `nexthd/next_helpdesk/workspace/nexthd/nexthd.json` ter-tulis ulang otomatis.

**Regresi ditemukan dalam sesi yang sama:** setelah `doc.save()` di atas, item sidebar manual "NextHD Reporting" **hilang** dari `Workspace Sidebar Item` (15 item tersisa, semuanya auto-generate dari `Workspace.links`). Root cause: `Workspace Sidebar.standard` untuk record "NextHD" ternyata `0` (bukan `1`) — sesuai `POLA_KERJA_DAN_BUG.md §1.C`, `standard` harus `1` agar perubahan sidebar permanen dan `export_sidebar()` mau menulis file; kalau `0`, sidebar rawan tersapu ulang oleh proses lain (dalam kasus ini, kemungkinan besar oleh proses `doc.save()` Workspace itu sendiri yang memicu regenerasi).

**Fix regresi:**
1. `Workspace Sidebar.standard` diset dari `0` → `1` via `frappe.db.set_value()`.
2. "NextHD Reporting" (`link_type: Workspace`, `link_to: NextHD Report`) ditambahkan kembali lewat UI — **catatan penting:** menu yang benar adalah ikon **panah ke bawah di kiri atas** halaman Workspace, bukan titik tiga (⋯) di kanan atas seperti dugaan sebelumnya di `POLA_KERJA_DAN_BUG.md §1.C`. Perlu koreksi kecil di dokumen tersebut untuk sesi berikutnya.
3. Verifikasi berulang: `doc.save()` Workspace NextHD dipanggil lagi (2×) setelah fix — sidebar "NextHD" tetap 16 item lengkap (termasuk "NextHD Reporting") di kedua percobaan, tidak tersapu lagi.
4. Fixture `nexthd/nexthd/workspace_sidebar/nexthd.json` dikonfirmasi berisi label "NextHD Reporting" (lokasi yang benar, sesuai `POLA_KERJA_DAN_BUG.md §1.C`).

**Catatan tambahan (bukan bug):** saat "NextHD Reporting" diklik, tampilan berpindah ke Workspace "NextHD Report" yang sidebar-nya sendiri cuma 2 item (Dashboard + NextHD Report) — ini perilaku normal Frappe v16 (sidebar per-Workspace, bukan gabungan), bukan regresi lanjutan. Workspace "NextHD Report" dikonfirmasi masih utuh (`public=1`, `is_hidden=0`, 11 shortcut report).

**Status akhir:** Item DD ditutup tuntas — bug asli dan regresi sampingannya sudah diverifikasi selesai, tidak ada data yang hilang permanen.

**Pending untuk sesi berikutnya:** commit + push kode yang berubah oleh Efendy (`nexthd.json` Workspace fixture yang baru ter-generate, fixture Workspace Sidebar kalau ada perubahan file lain). Koreksi kecil di `POLA_KERJA_DAN_BUG.md §1.C` soal lokasi menu "Edit Sidebar" (panah kiri atas, bukan titik tiga kanan atas).
