# NextHD — Index Dokumentasi

> **Entry point.** Baca ini dulu — berisi overview dan pointer ke file detail.
>
> **Last updated:** 2026-08-30 15:20 WIB (`docs/HANDOFF.md` selesai dirombak — banner "arsip beku" dihapus, isi dipangkas dari ~39KB jadi log ringkas ~6KB, commit `89b76f0`. Restrukturisasi dokumentasi dinyatakan **TUNTAS**; review file besar lain — `ARSITEKTUR.md`/`DAFTAR_FITUR.md`/`AUDIT_SISTEM.md` — diputuskan **tidak perlu dipangkas** karena isinya berupa script siap-pakai & referensi teknis yang masih aktif dipakai, bukan kronologi usang seperti `HANDOFF.md`/`POLA_KERJA_DAN_BUG.md` dulu; risiko kehilangan script saat rangkuman lebih besar dari manfaat pemendekan)

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
| `docs/BUG_WORKSPACE_SIDEBAR.md` | Riwayat bug khusus Workspace/Desktop Icon/Sidebar/Dashboard Shortcut (paling sering terjadi & paling tebal) — 12 sesi bug, 24–29 Agustus |
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
- Workflow approval untuk Change Request (state machine terverifikasi via regression test, 2026-08-20; dedup ulang 24 & 25 Agustus)
- Manajemen Problem dan Known Error (ITIL-lite)
- Notifikasi real-time via Telegram Bot — **✅ terkonfirmasi live**, bot sudah balas dan token/enable sudah terkonfirmasi di NextHD Settings
- SLA monitoring otomatis berbasis jam kerja (warning 30 menit sebelum breach), termasuk **titik-mulai resolution saat "Mulai Kerjakan" + pause/resume saat "Menunggu User"** (PR #8, bugfix `76ce3e9`) — **✅ live + terverifikasi**
- Priority otomatis dari matriks Impact × Urgency, dengan override manual untuk Agent Manager/IT Manager (PR #7) — **✅ live + terverifikasi**
- Multi-tim dengan assignment agent
- Custom reports: Tiket per Bulan, Tiket per Agent, Tiket per Kategori, Tiket per Prioritas (breach SLA), SLA Compliance Bulanan, Aset Bermasalah, Detail Aset Lengkap — **kartu shortcut dashboard "Laporan" sudah ditambah (26 Agustus, fix `report_ref_doctype`+cache, menunggu konfirmasi visual)**, sidebar kiri submenu 6 link Report masih di item AA, sidebar "NextHD Reporting" (11 shortcut Detail Report Lengkap) sudah live sejak 27 Agustus, dikonfirmasi permanen 29 Agustus (item DD), dan Workspace tujuannya ("NextHD Report") sidebar-nya sendiri diperkaya jadi 8 item 30 Agustus (item KK)
- Foto/gambar reusable & bisa di-link antar Ticket/Problem/Asset/Known Error (PR #9) — **✅ live + terverifikasi 24 Agustus**, termasuk sidebar & dashboard Number Card. **Shortcut dashboard "NextHD Photo" (kartu terpisah di section Konfigurasi) ditambah 26 Agustus**, sempat tidak muncul karena cache — sudah difix, menunggu konfirmasi visual. **28 Agustus:** naming series diubah ke `IMG-YYMM-####`, field Judul Foto/Lokasi/Kategori ditambah, dan badge "Dipakai Di" (Dashboard Connections, real-time dari child table, tidak disimpan sebagai field) terpasang di form Photo — **✅ terpasang, perlu re-test dengan foto baru**
- Tombol admin "Reset Data Demo" (hapus semua data transaksi untuk testing, System Manager only, 2x konfirmasi + backup otomatis) — **✅ live + terverifikasi end-to-end 28 Agustus**
- Generalisasi NextHD Asset ke pola EAV (`NextHD Asset Category` + `NextHD Asset Attribute`) — **✅ live 28 Agustus malam, terverifikasi aman 29 Agustus** (item II). **29 Agustus (lanjutan):** field terstruktur lama (brand/model/cpu/ram/storage/os/dst di section PC/Network/Printer) yang sudah duplikat dengan EAV **dihapus dari form**, `search_fields` & report `Detail Aset Lengkap` disesuaikan (item JJ). **30 Agustus:** "NextHD Asset Category" ditambahkan ke sidebar Workspace "NextHD" (item KK)
- **Rencana ke depan:** Knowledge Base publik (self-service), tag di tiket, CSAT — lihat `docs/DAFTAR_FITUR.md`

---

## 2. Status Item Belum Dikerjakan

> Bagian ini yang **paling sering diupdate tiap sesi**. Item selesai dipindah ke `docs/BUG_WORKSPACE_SIDEBAR.md` atau `docs/BUG_HISTORY.md` (sebelumnya `POLA_KERJA_DAN_BUG.md`, sudah dihapus 30 Agustus).
> Untuk rencana fitur besar yang belum jadi task konkret, lihat `docs/DAFTAR_FITUR.md`.

### ✅ Restrukturisasi Dokumentasi — TUNTAS (30 Agustus)

| # | Item | Keterangan | PIC |
|---|---|---|---|
| — | Pecah `POLA_KERJA_DAN_BUG.md` (82KB) jadi 3 file | `POLA_KERJA.md` + `BUG_WORKSPACE_SIDEBAR.md` + `BUG_HISTORY.md`, file lama dihapus (commit `7e4c0d1`) | Claude |
| — | Rombak `docs/HANDOFF.md` | Banner "arsip beku" dihapus, isi dipangkas dari kronologi naratif ~39KB jadi tabel log ringkas ~6KB per-tanggal yang menunjuk ke file tematik. Commit `89b76f0` | Claude |
| — | Review `ARSITEKTUR.md`/`DAFTAR_FITUR.md`/`AUDIT_SISTEM.md`/`PANDUAN_INSTALASI.md` | **Diputuskan tidak perlu dirangkum.** Berbeda dari `HANDOFF.md`/`POLA_KERJA_DAN_BUG.md` (kronologi sesi yang menumpuk & banyak terduplikasi), keempat file ini isinya referensi teknis aktif (schema DB, script `bench console` siap pakai, panduan instalasi) yang masih relevan penuh — memangkasnya berisiko menghilangkan detail/script yang justru paling sering dipakai ulang. `PANDUAN_INSTALASI.md` (4.6KB) memang sudah ringkas | Claude |

**Struktur dokumentasi final (10 file di `docs/`):** `SUMMARY.md` (index), `FAQ_DEVELOPER.md`, `DAFTAR_FITUR.md`, `ARSITEKTUR.md`, `WORKFLOW.md`, `POLA_KERJA.md`, `BUG_WORKSPACE_SIDEBAR.md`, `BUG_HISTORY.md`, `PANDUAN_INSTALASI.md`, `AUDIT_SISTEM.md`, `HANDOFF.md`.

### ✅ Item KK — SELESAI (30 Agustus): Sidebar "NextHD" +Asset Category, Sidebar "NextHD Report" Diperkaya

| # | Item | Keterangan | PIC |
|---|---|---|---|
| KK | Sidebar Workspace "NextHD" belum ada "NextHD Asset Category"; sidebar Workspace "NextHD Report" cuma 2 item | **Bagian 1:** "NextHD Asset Category" (DocType baru dari migrasi EAV 28-29 Agustus) ditambahkan ke sidebar "NextHD" via UI Edit Sidebar — idx=8, icon `copy-check`, total sidebar jadi **17 item**. **Bagian 2:** sidebar Workspace "NextHD Report" (sebelumnya cuma "Dashboard" + "NextHD Report" sejak dibuat 27 Agustus) diperkaya jadi **8 item** — ditambahkan 6 DocType utama (Ticket, Problem, Change Request, Known Error, Asset, Asset Category), dengan icon konsisten mengikuti sidebar "NextHD". Keputusan Efendy: laporan TIDAK perlu ditambahkan ke sidebar ini, karena begitu masuk Workspace "NextHD Report", 11 shortcut report sudah otomatis tampil di body/dashboard. **Temuan sebelum eksekusi:** field `Workspace Sidebar.app` untuk "NextHD Report" ternyata `None` (beda dari "NextHD" yang sudah `nexthd`) — diperbaiki dulu via `frappe.db.set_value()` sebelum insert item, supaya fixture bisa ter-export permanen. **Eksekusi:** karena item yang ditambahkan banyak (6 sekaligus), dipakai script `doc.append("items", {...})` + `doc.save(ignore_permissions=True)` pada dokumen `Workspace Sidebar` "NextHD Report" — pola ini setara dengan tombol UI "Edit Sidebar", risiko regresi jauh lebih rendah dibanding `doc.save()` pada `Workspace` (beda doctype) yang pernah menyebabkan regresi di item DD. **Verifikasi:** sidebar "NextHD" (17 item) dikonfirmasi TIDAK terpengaruh oleh perubahan sidebar "NextHD Report". Fixture `nexthd/workspace_sidebar/nexthd_report.json` — **ternyata belum pernah ter-commit ke git sejak dibuat 27 Agustus** (`untracked` di `git status`) — sekarang sudah masuk repo untuk pertama kalinya. Commit `beec05c`, sudah di-push ke `main`. **Belum diverifikasi:** `bench migrate` sungguhan belum dijalankan sejak semua fix sidebar (item DD 29 Agustus + item KK 30 Agustus) — lihat catatan pending di bawah | Efendy |

> **Temuan sampingan penting (30 Agustus):** sidebar pendek yang muncul di halaman Report/DocType (mis. `/desk/query-report/...`) sempat diduga "Route History" (riwayat navigasi), tapi **terbukti salah** setelah dicek `tabRoute History` — isinya tidak cocok dengan yang tampil di UI. Kesimpulan final: itu adalah **"Module Sidebar"** bawaan Frappe — di-generate otomatis secara real-time dari kombinasi semua `Workspace`+`DocType`+`Report` yang punya `module='Next Helpdesk'`. **Bukan file, bukan dokumen tersimpan, tidak bisa diedit/ditambahkan** tanpa override kode inti Frappe (berisiko tinggi, konsisten dengan limitasi Frappe v16 yang sudah dikonfirmasi sebelumnya — GitHub Issue #36317). **Keputusan final Efendy: dibiarkan apa adanya, tidak perlu dikejar lagi.**

### 🔴 PRIORITAS SESI BERIKUTNYA — `bench migrate` Uji Tahan (Belum Pernah Dijalankan)

`bench migrate` belum pernah dijalankan sejak fix item DD (29 Agustus) maupun item KK (30 Agustus). Kedua faktor risiko regresi yang diketahui (`Workspace Sidebar.standard` dan `.app` untuk record "NextHD" & "NextHD Report") sudah diperbaiki ke nilai benar, tapi belum ada bukti empiris (belum diuji migrate sungguhan) bahwa keduanya bertahan. **Rekomendasi:** jalankan `bench migrate` sebagai uji tahan (aman, bukan operasi destruktif), lalu verifikasi ulang jumlah item sidebar "NextHD" (harus 17) dan "NextHD Report" (harus 8) + pastikan `doc.save()` pada Workspace "NextHD" masih berhasil tanpa error. Bisa digabung sekalian dengan uji migrate final untuk item AA (sidebar 6 link Report di `Workspace.links`) yang juga masih pending dari 25 Agustus.

### ✅ Item DD — SELESAI (29 Agustus, ~17:45 WIB): Bug `Link Type must be set first` pada Workspace NextHD

| # | Item | Keterangan | PIC |
|---|---|---|---|
| DD | `frappe.get_doc("Workspace", "NextHD").save()` gagal validasi | **Root cause:** row `tabWorkspace Link` (`name=u6nb1c41c1`, label "Reporting Data", `link_to=/app/nexthd-report`, `type=URL`, `link_type` kosong) — sisa percobaan lama yang tidak pernah valid (Page `nexthd-report` yang dimaksud tidak pernah ada di `tabPage`). **Percobaan gagal:** set `link_type="Workspace"` → ditolak (field cuma terima DocType/Page/Report); set `link_type="Page"` → `LinkValidationError` karena Page `nexthd-report` tidak eksis. **Fix final:** baris "Reporting Data" **dihapus total** dari `tabWorkspace Link` — fungsinya memang sudah digantikan sidebar "NextHD Reporting" (dibuat 27 Agustus lewat UI, mengarah ke Workspace "NextHD Report" berisi 11 shortcut report). Setelah dihapus, `doc.save()` berhasil dan menulis ulang fixture `nexthd/next_helpdesk/workspace/nexthd/nexthd.json`. **Regresi ditemukan & diperbaiki dalam sesi yang sama:** proses `doc.save()` di atas sempat menghapus item sidebar manual "NextHD Reporting" dari `Workspace Sidebar Item` (root cause: `Workspace Sidebar.standard` ternyata `0`, bukan `1` — `standard` harus `1` agar `export_sidebar()` menulis file & perubahan permanen, lihat `docs/POLA_KERJA.md`). Fix: `standard` diset ke `1` via `frappe.db.set_value()`, lalu "NextHD Reporting" ditambahkan kembali lewat UI **"panah ke bawah (kiri atas) → Edit Sidebar"** (BUKAN via titik tiga kanan atas — lokasi menu berbeda dari dugaan awal). **Verifikasi akhir (semua ✅):** `doc.save()` Workspace NextHD jalan tanpa error berulang kali, sidebar "NextHD" tetap 16 item lengkap (termasuk "NextHD Reporting"), fixture `nexthd/nexthd/workspace_sidebar/nexthd.json` berisi label "NextHD Reporting". **Catatan tambahan:** saat diklik, "NextHD Reporting" berpindah ke Workspace "NextHD Report" yang sidebar-nya sendiri cuma 2 item (Dashboard + NextHD Report) — ini **bukan bug**, memang workspace itu didesain sebagai halaman kumpulan shortcut report, bukan hub navigasi. **Update 30 Agustus:** sidebar Workspace "NextHD Report" ini sekarang sudah diperkaya jadi 8 item — lihat item KK. Detail kronologi lengkap di `docs/BUG_WORKSPACE_SIDEBAR.md` | Claude + Efendy |

### 🔴 Item EE — Task Pending: Rename Module "Next Helpdesk" → "NextHD"

| # | Item | Keterangan | PIC |
|---|---|---|---|
| EE | `tabModule Def` masih bernama "Next Helpdesk" | Menyebabkan sidebar module-based (Report page, Page kustom seperti `nexthd-reset-data`) masih menampilkan header "Next Helpdesk", bukan "NextHD". Dikonfirmasi ulang 28 Agustus bukan Workspace nyasar, murni dari nama Module Def. **Catatan 30 Agustus:** ini juga sumber label "Next Helpdesk" pada Module Sidebar (sidebar pendek di halaman Report/DocType) — TAPI Efendy sudah memutuskan Module Sidebar dibiarkan apa adanya (lihat item KK), jadi rename ini sekarang relevan untuk alasan lain saja (breadcrumb, header report page), bukan lagi soal sidebar. Solusi: rename `Module Def` + update `modules.txt`, risiko menengah (mempengaruhi banyak referensi internal) — perlu sesi terpisah dengan backup wajib | Claude + Efendy |

### 🔶 Item BB — Dashboard Shortcut "NextHD Photo" & 6 Report (Menunggu Konfirmasi Visual, 26 Agustus)

| # | Item | Keterangan | PIC |
|---|---|---|---|
| BB | Kartu shortcut dashboard `/desk/nexthd`: 1 DocType (NextHD Photo) + 6 Report (section baru "Laporan") | Insert ke `tabWorkspace Shortcut` + update `Workspace.content` sudah dijalankan (7 shortcut baru, total 32 blok). Sempat tidak muncul di dashboard — root cause: `report_ref_doctype` kosong untuk 6 shortcut Report (fixed), dan cache Redis untuk shortcut Photo (fixed via `bench clear-cache`+`clear-website-cache`). **Menunggu Efendy hard refresh & konfirmasi visual** sebelum di-export ke fixture. Detail lengkap di `docs/BUG_WORKSPACE_SIDEBAR.md` bug session 26 Agustus | Claude + Efendy |

> **Catatan penting:** item BB (kartu dashboard, tabel `Workspace Shortcut`) **terpisah total** dari item AA di bawah (sidebar kiri, tabel `Workspace.links`) — dua sistem berbeda meski sama-sama menyangkut Report & Photo. Jangan disatukan saat verifikasi.

### 🔶 Item AA — Sidebar 6 Link Report (Sedang Berjalan, 25 Agustus) — Bisa Digabung dengan Uji Migrate Item KK

| # | Item | Keterangan | PIC |
|---|---|---|---|
| AA | Ganti menu sidebar "NextHD Report" generic dengan 6 link report langsung | **Root cause ditemukan:** sidebar sebenarnya punya dua tabel — `Workspace Sidebar Item` (turunan/auto-generate, ditimpa ulang tiap migrate) dan `Workspace.links` (sumber asli, bertahan lewat migrate). Percobaan pertama (edit `Workspace Sidebar Item` langsung) **gagal saat migrate diuji** — data sempat hilang, sudah di-restore dari backup. Pendekatan baru (edit `Workspace.links` langsung) **sudah dijalankan dan diverifikasi** via `bench console`: 19 item total (13 lama + 6 report baru). **`bench migrate` untuk konfirmasi final BELUM dijalankan.** **Catatan 30 Agustus:** ini bisa digabung sekalian dengan uji migrate yang juga pending untuk item KK — satu kali `bench migrate`, verifikasi keduanya sekaligus. Detail lengkap + script di `docs/AUDIT_SISTEM.md` | Claude + Efendy |

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
| KK | Sidebar "NextHD" +Asset Category (17 item); sidebar "NextHD Report" diperkaya 2→8 item (DocType utama) | Fixture `nexthd/workspace_sidebar/nexthd.json` (modified) & `nexthd_report.json` (baru pertama kali ter-commit) — commit `beec05c`, 30 Agustus. `bench migrate` uji tahan **belum dijalankan**, lihat catatan pending di atas | Efendy |

> **Catatan Item E:** user test `test.requester@ciptamebel.co.id` sendiri belum pernah kirim `/start`+`/link` ke bot (field `telegram_chat_id` masih kosong untuk akun ini) — tapi ini bukan bug, cuma user dummy tsb memang belum di-link manual. Bot-nya sendiri sudah terbukti bekerja pakai akun Telegram lain.

### 🟢 Prioritas Rendah — Belum Mendesak / Masih Wacana

| # | Fitur | Keterangan | PIC |
|---|---|---|---|
| I | Wipe data testing (versi lama/checklist) | Sudah **diimplementasikan versi ringkas** sebagai tombol "Reset Data Demo" (item HH, 28 Agustus) — desain lengkap dengan UI checkbox per DocType di `DAFTAR_FITUR.md` masih jadi opsi pengembangan lanjutan kalau dibutuhkan granularitas lebih | Claude (desain), Efendy (waktu eksekusi) |
| J | Workflow — testing end-to-end di UI browser | Regression test backend sudah lulus 100% (2026-08-20). Belum ditest klik manual di browser untuk verifikasi tombol Actions & permission per role tampil benar | Efendy |
| K | Role assignment ke user spesifik | `support@ciptamebel.co.id` → role IT Manager. Keputusan: sementara 1 akun shared dulu | Efendy |
| L | File `HANDOFF_SLA_NextHD_2026-08-19.md` | Disebut di riwayat lama, tidak ada di repo. Kalau masih ada di server, perlu `git add` + commit sebelum hilang | Efendy |
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

> Detail lengkap ada di `docs/BUG_WORKSPACE_SIDEBAR.md` + `docs/BUG_HISTORY.md` dan log ringkas `docs/HANDOFF.md`.

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
| Dashboard shortcut "NextHD Photo" + 6 Report ditambah ke `Workspace Shortcut` (item BB) | ✅ Diinsert 26 Agustus (7 shortcut baru, `content` 32 blok). Sempat tidak render — root cause `report_ref_doctype` kosong (6 Report) + cache Redis (Photo), keduanya sudah difix. Menunggu konfirmasi visual Efendy — lihat `docs/AUDIT_SISTEM.md` & `docs/BUG_WORKSPACE_SIDEBAR.md` |
| Naming Series `NextHD Photo` → `IMG-YYMM-####` (item FF) | ✅ 28 Agustus, terverifikasi dokumen baru `IMG-2608-0001` |
| Field baru `NextHD Photo` — Judul Foto, Lokasi, Kategori (item GG) | ✅ 28 Agustus. Reference balik "dipakai di mana" sengaja **tidak** disimpan sebagai field statis (risiko tertimpa kalau 1 foto dipakai di >1 dokumen) — dipindah ke Dashboard Connections |
| Dashboard Connections "Dipakai Di" pada `NextHD Photo` | ✅ Terpasang 28 Agustus via `get_dashboard_data()`, real-time dari child table `NextHD Photo Link` di semua parent (Ticket/Asset/Problem/Known Error), tidak ada risiko data tertimpa. **Perlu re-test dengan foto baru** — foto contoh lama sudah ikut terhapus tombol Reset Data Demo sebelum sempat ditest ulang |
| Tombol "Reset Data Demo" (item HH) | ✅ Selesai & terverifikasi end-to-end 28 Agustus — System Manager only (cek backend), 2x konfirmasi (dialog + ketik `RESET`), backup otomatis via `frappe.utils.backups.new_backup()`, counter `tabSeries` ikut direset. Bug awal `subprocess.run(["bench",...])` gagal di web worker (`FileNotFoundError`) — diganti panggilan langsung ke fungsi Python `new_backup()`, tidak bergantung shell `PATH` |
| Shortcut Workspace "Admin" (tombol Reset Data Demo) tidak muncul di UI | ✅ 28 Agustus. Root cause: Workspace v16 dikontrol field `content` (JSON blocks), bukan otomatis baca semua row `tabWorkspace Shortcut`. Fix: update `content` via `frappe.db.set_value()` langsung (skip validasi dokumen penuh karena bug lain — lihat item DD), dijalankan via `bench execute` (bukan `bench console`, supaya cabang `if/else` tidak salah parse indentasi) |
| Housekeeping struktur dokumentasi — `HANDOFF.md` dipindah dari root repo ke `docs/HANDOFF.md` | ✅ 28 Agustus. `README.md` diperbarui (link dokumentasi mengikuti struktur `docs/` multi-file terbaru). Sekarang semua file `.md` project konsisten berada di `docs/` (README.md tetap di root sesuai konvensi GitHub) |
| Generalisasi EAV `NextHD Asset` (item II/S) — `NextHD Asset Category` + `NextHD Asset Attribute` | ✅ Dikerjakan 28 Agustus malam (commit `281072a`+`81889c0`, oleh Efendy/Devin), diverifikasi aman 29 Agustus pagi: DocType & kolom fisik ter-migrate, 6/6 record Asset existing sudah terisi kategorinya, 7 record master, 19 baris attribute terpakai |
| Cleanup field terstruktur Asset lama + rewrite `Detail Aset Lengkap` berbasis EAV (item JJ) | ✅ 29 Agustus, commit `d964531` → `b148223`. 20 field + 4 column break dihapus dari `nexthd_asset.json`; Property Setter `search_fields` diupdate (`asset_name,assigned_to,serial_number` → `asset_name,assigned_to`); `detail_aset_lengkap.py` ditulis ulang pakai `LEFT JOIN` + `GROUP_CONCAT` ke `NextHD Asset Attribute`. Terverifikasi via screenshot Efendy: form bersih, report EAV jalan, report "Aset Bermasalah" tetap normal, search Link ke Asset jalan |
| Bug `Link Type must be set first` pada Workspace NextHD (item DD) + regresi sidebar "NextHD Reporting" | ✅ 29 Agustus ~17:45 WIB. Row "Reporting Data" (`link_type` kosong, sisa percobaan lama yang tak pernah valid) dihapus dari `tabWorkspace Link`. `doc.save()` berhasil. Regresi: `doc.save()` sempat menghapus "NextHD Reporting" dari sidebar karena `Workspace Sidebar.standard=0` — diperbaiki ke `1`, item ditambahkan kembali via UI "Edit Sidebar" (menu di panah kiri atas, bukan titik tiga kanan atas), diverifikasi permanen via `bench console` berulang kali (`doc.save()` tetap sukses, 16 item sidebar tetap utuh, fixture ter-update) | Efendy |
| Sidebar "NextHD" +Asset Category, sidebar "NextHD Report" diperkaya 2→8 item, klarifikasi Module Sidebar bukan editable (item KK) | ✅ 30 Agustus. `Workspace Sidebar.app` untuk "NextHD Report" diperbaiki dari `None`→`nexthd` sebelum insert 6 item DocType via script `doc.append()`+`doc.save()` pada `Workspace Sidebar` (bukan `Workspace`, lebih aman). Fixture `nexthd_report.json` ter-commit pertama kali. Sidebar pendek di halaman Report/DocType dikonfirmasi sebagai Module Sidebar bawaan Frappe (auto-generate dari field `module`), bukan bug, diputuskan dibiarkan. Commit `beec05c` | Efendy |
| Restrukturisasi `docs/POLA_KERJA_DAN_BUG.md` (82KB) jadi 3 file terpisah | ✅ 30 Agustus. Dipecah jadi `docs/POLA_KERJA.md` (aturan wajib, commit `8338fa2`), `docs/BUG_WORKSPACE_SIDEBAR.md` (riwayat bug Workspace/Sidebar, commit `fb04898`), `docs/BUG_HISTORY.md` (riwayat bug lain, commit `08a801c`). File lama dihapus dari repo (commit `7e4c0d1`) setelah semua konten dipastikan tersalin. Tabel "Struktur Dokumentasi" di file ini diupdate mengikuti struktur baru | Claude |
| Rombak `docs/HANDOFF.md` — banner "arsip beku" dihapus, dipangkas jadi log ringkas | ✅ 30 Agustus, commit `89b76f0`. Dari ~39KB kronologi naratif penuh jadi ~6KB tabel log per-tanggal yang menunjuk ke file tematik. Restrukturisasi dokumentasi dinyatakan **TUNTAS** — 4 file besar lain (`ARSITEKTUR.md`, `DAFTAR_FITUR.md`, `AUDIT_SISTEM.md`, `PANDUAN_INSTALASI.md`) diputuskan **tidak perlu dipangkas**, karena isinya referensi teknis & script aktif yang masih dipakai, bukan kronologi usang | Claude |

---

*Dokumen ini dikelola oleh Claude. Update terakhir: 2026-08-30 15:20 WIB.*

---

## Update 2026-08-28 (Lanjutan #2) — Navigasi Relasi Antar Dokumen & Schema Drift Ditemukan

**Konteks:** Menindaklanjuti investigasi "Connections Asset-Problem tidak muncul" dari sesi sebelumnya hari yang sama.

**Temuan kritis:** Field `related_asset` di NextHD Problem sempat **hilang dari metadata Frappe** (schema drift) meski data & kolom fisik aman — root cause: fixture `DocField` di `hooks.py` sudah tidak terdaftar. Sudah direstore permanen ke `nexthd_problem.json`. **Ini memperkuat pentingnya menjalankan `docs/AUDIT_SISTEM.md §1` secara berkala** — drift semacam ini tidak menimbulkan error apa pun sampai field-nya dibutuhkan.

**Ditutup:** Rencana pakai `internal_links`/`get_dashboard_data()` untuk memunculkan relasi forward-link di widget Connections — **dikonfirmasi tidak applicable** (hanya berlaku untuk child table). Diganti solusi tombol Client Script manual, sudah diimplementasi & live untuk semua pasangan relasi (Problem↔Asset, Problem↔Change Request, Problem↔Known Error, Problem↔Ticket, Change Request↔Asset, Change Request↔Problem, Known Error↔Problem). Detail lengkap di `docs/BUG_HISTORY.md`.

**Bug tambahan difix:** `related_asset` tidak ter-copy otomatis saat "Buat Change Request dari Problem" (sekarang sudah), dan race condition di `frappe.client.set_value` yang menyebabkan field balik `Problem.change_request` gagal ter-set diam-diam (sudah difix + data lama di-backfill).

**Item baru untuk sesi berikutnya:** Known Error tidak punya field balik ke Change Request yang dibuat darinya — belum ada tombol "Lihat Change Request Terkait" di Known Error. Prioritas rendah, bukan bug kritis.

---

## Update 2026-08-30 15:20 WIB — Restrukturisasi Dokumentasi TUNTAS

**Konteks:** Menindaklanjuti pending item dari update 13:05 WIB (rombak `HANDOFF.md` + review file besar lain).

**Yang dikerjakan:**
1. `docs/HANDOFF.md` dirombak total — banner "Status: ARSIP" (kebijakan yang sudah dicabut Efendy) dihapus, isi dipangkas dari kronologi naratif penuh 14–30 Agustus (~39KB) jadi tabel log ringkas per-tanggal (~6KB) yang menunjuk ke file tematik untuk detail lengkap. Commit `89b76f0`.
2. Review 4 file besar lain (`ARSITEKTUR.md` 22KB, `DAFTAR_FITUR.md` 20KB, `AUDIT_SISTEM.md` 46KB, `PANDUAN_INSTALASI.md` 4.6KB) — **diputuskan tidak perlu dipangkas**. Berbeda dari `HANDOFF.md`/`POLA_KERJA_DAN_BUG.md` (lama) yang isinya kronologi sesi menumpuk dan banyak terduplikasi ke file lain, keempat file ini isinya referensi teknis aktif yang tidak terduplikasi: schema DB & field DocType (`ARSITEKTUR.md`), checklist fitur (`DAFTAR_FITUR.md`), script `bench console` siap pakai untuk audit server (`AUDIT_SISTEM.md`), dan panduan setup (`PANDUAN_INSTALASI.md`, sudah ringkas). Memangkas isinya berisiko menghilangkan script/detail yang justru paling sering dipakai ulang — manfaat pemendekan tidak sebanding risikonya.

**Status akhir restrukturisasi dokumentasi (dimulai sejak pemecahan `POLA_KERJA_DAN_BUG.md` 82KB):** **TUNTAS**. Struktur final 11 file `.md` di `docs/` — lihat tabel "Struktur Dokumentasi" di bagian atas file ini.

**Untuk sesi berikutnya:** tidak ada lagi task restrukturisasi dokumentasi pending. Item teknis prioritas berikutnya: `bench migrate` uji tahan (belum pernah dijalankan sejak fix item DD & KK) — lihat §2 di atas.
