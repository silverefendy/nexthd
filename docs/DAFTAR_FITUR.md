# NextHD — Daftar Fitur (Checklist Lengkap)

> **Satu tempat untuk cek semua fitur** — sudah selesai, sedang dikerjakan, atau masih
> rencana. (Sebelumnya `ROADMAP_FITUR.md`, sekarang termasuk juga desain yang sebelumnya
> nyasar di `ARSITEKTUR.md §8` dan `§9`).
>
> Status: ✅ Selesai & Live | 🔶 Sedang Dikerjakan/Menunggu Konfirmasi | ⬜ Belum Dikerjakan (Rencana)
>
> **Last updated:** 2026-09-09 (item PP — warna List View 5 DocType, fix `naming_rule` usang di 5 DocType, dan field `asset_type` DIHAPUS TOTAL dari metadata+kolom fisik database — sebelumnya di sesi 6 September cuma disembunyikan/deprecated, sekarang sudah tuntas dihapus permanen)

---

## Fitur Inti (Sudah Selesai & Live)

| Fitur | Status | Keterangan | Bukti/Referensi |
|---|---|---|---|
| SLA sadar jam kerja (all-or-nothing) | ✅ | `business_hours.py`, resolusi diulang penuh dari jam kerja berikutnya kalau tidak muat | `docs/BUG_HISTORY.md`, 20 Agustus |
| Tombol workflow "Mulai Kerjakan" | ✅ | Baru → Sedang Dikerjakan, catat `responded_on` | `nexthd_ticket_workflow.json` |
| Field impact/urgency/waiting_log di form Ticket | ✅ | Ada di `field_order` | `nexthd_ticket.json` |
| Priority matrix otomatis (Impact × Urgency) | ✅ | + override manual Agent Manager/IT Manager | [PR #7](https://github.com/silverefendy/nexthd/pull/7) |
| Pause/resume SLA saat "Menunggu User" | ✅ | + recalculate saat "Mulai Kerjakan" | [PR #8](https://github.com/silverefendy/nexthd/pull/8), bugfix `76ce3e9` |
| Permission NextHD SLA Policy & Business Hours | ✅ | Agent Manager/IT Manager override | Commit `31f35da` |
| Halaman NextHD SLA Policy 404 | ✅ | Root cause = permission, sudah fix | — |
| Web Form self-service `/tiket-saya` | ✅ | Requester bisa submit tiket sendiri | [PR #6](https://github.com/silverefendy/nexthd/pull/6), live 22 Agustus |
| Notifikasi Telegram (i18n) | ✅ | Bot terkonfirmasi balas pesan nyata | PR #6, verifikasi manual 22 Agustus |
| Permission `reply` di Waiting Log | ✅ | Requester bisa isi reply sendiri | Terverifikasi `bench console`, 22 Agustus |
| Sidebar Holiday di Workspace | ✅ | Terverifikasi via query | 22 Agustus |
| Regression test 3 workflow | ✅ | Ticket, Problem, Change Request semua lulus | 20 Agustus |
| Dedup transisi workflow duplikat + guard permanen anti-duplikasi | ✅ | 42 → 21 baris bersih (dedup pertama, 20 Agustus). Duplikasi sempat muncul lagi 3× (24, 25, 30-31 Agustus — Round 2-4). **Root cause final Round 4 (30-31 Agustus): 2 channel fixture saling menambah** — sudah diperbaiki permanen, guard `workflow_guard.py` (PR #10) berjalan ketat penuh tanpa celah skip migrate, diverifikasi stabil lintas 3× `bench migrate` berturut-turut | 20 Agustus, tuntas 31 Agustus |
| Number Card dashboard | ✅ | Fix `number_card_name` | 21 Agustus |
| Naming series seragam YY.MM | ✅ | Semua 6 DocType | 19 Agustus |
| `FAQ_DEVELOPER.md` | ✅ | Kurasi masalah berulang untuk Devin | 22 Agustus |
| `AUDIT_SISTEM.md` | ✅ | Script audit lengkap kesehatan server/repo | 23 Agustus |
| Fitur foto reusable (Ticket/Problem/Asset/Known Error) | ✅ | DocType `NextHD Photo` + `NextHD Photo Link`, galeri swipe, kompresi otomatis (Pillow), auto-copy saat convert Ticket→Problem/Problem→Known Error | PR #9, commit `03a3c5d`, merged 24 Agustus |
| NextHD Photo di sidebar Workspace + dashboard Number Card | ✅ | Link sidebar setelah Known Error, card "Total Foto Terupload" di dashboard, fixture Number Card lengkap (9 card, sebelumnya 0 ter-fixture). **Sempat tidak muncul di UI meski data sudah benar — root cause & fix di bawah** | Commit `a69df61`, 24 Agustus |
| Bug SLA Kritis `is_24x7` tidak sesuai SOP | ✅ | Diperbaiki langsung di DB via `bench console`, `is_24x7` Kritis: 0→1 | 24 Agustus |
| Business Hours Minggu (hari libur) | ✅ | Record ke-7 dibuat, `is_working_day=0` | 24 Agustus |
| NextHD Holiday 2026 — 17 hari libur nasional | ✅ | Diisi sesuai SKB 3 Menteri No. 1497/2025, 2/2025, 5/2025 (resmi Setneg) | 24 Agustus |
| `install.py` — nilai SLA default diperbaiki | ✅ | `create_default_sla_policies()` diupdate ke nilai SOP final 19 Agustus (Kritis 15/60 `is_24x7=1`, Tinggi 30/240, Sedang 60/2880, Rendah 120/10080) — instalasi baru sekarang otomatis dapat nilai benar | Commit `b3a24b2` → `2d795b9`, 24 Agustus |
| Sidebar "NextHD Photo" tidak muncul di UI meski data sudah live | ✅ | **Root cause:** `import_file_by_path(force=True)` berhasil sync field `number_cards`/`content` tapi TIDAK sync child table `links` (sidebar). **Fix:** append manual via `Workspace` doc ORM (`doc.append("links", ...)` + `doc.save()`), bukan reimport JSON | 24 Agustus |
| Duplikasi Workflow Transition (round 2) — Ticket/Problem/Change Request | ✅ | Ditemukan tiap transisi terduplikasi persis 4× (Ticket 28→7, Problem 24→6, CR 32→8). **Root cause dugaan awal:** `Workflow Action Master` "Convert to Known Error" tidak pernah dibuat. **Root cause sebenarnya (dikonfirmasi 25 Agustus):** fixture `workflow_transition.json` di repo menumpuk beberapa generasi export lama — lihat `docs/BUG_HISTORY.md` | 24–25 Agustus |
| Cuti Bersama 2026 — 8 hari | ✅ | Ditambahkan ke `NextHD Holiday` (total jadi 25 record: 17 nasional + 8 cuti bersama). **⚠️ Pemetaan tanggal↔nama event asumsi Claude berdasar pola umum, belum dicek silang ke teks SKB asli** | 24 Agustus |
| Script verifikasi ringan pasca-perbaikan | ✅ | Ditambahkan ke `AUDIT_SISTEM.md` — smoke test 9 titik spesifik (workflow, sidebar, number card, SLA, business hours, holiday, roles, photo doctype) | 24 Agustus |
| Naming Series `NextHD Photo` → `IMG-YYMM-####` | ✅ | `autoname: hash` → `naming_series:`, `naming_rule` → `By "Naming Series" field`, field `naming_series` (Select, hidden, opsi `IMG-.YY.MM.-.####`). Terverifikasi: dokumen baru `IMG-2608-0001` dst | 28 Agustus |
| Field baru `NextHD Photo` — Judul Foto, Lokasi, Kategori | ✅ | `photo_title` (Data, jadi `title_field`), `location` (Data), `category` (Link → `NextHD Category`, reuse DocType existing). **Keputusan desain:** referensi balik "dipakai di dokumen mana" sengaja TIDAK disimpan sebagai field tunggal (`reference_doctype`/`reference_name`) karena 1 foto bisa dipakai ulang di >1 dokumen — field tunggal akan tertimpa. Solusi dipindah ke Dashboard Connections (baris di bawah) | 28 Agustus |
| Dashboard Connections "Dipakai Di" pada `NextHD Photo` | ✅ | `get_dashboard_data()` di `nexthd_photo.py` — badge "Connections" real-time dihitung dari child table `NextHD Photo Link` di 4 parent (Ticket/Asset/Problem/Known Error), bukan field statis tersimpan. Trade-off: tidak bisa dipakai untuk filter/Report View (bukan field DB) — kalau nanti butuh laporan semacam itu perlu solusi tambahan terpisah. **Terpasang, perlu re-test dengan foto baru** (foto contoh lama sudah ikut terhapus tombol Reset Data Demo) | 28 Agustus |
| Tombol admin "Reset Data Demo" | ✅ | Custom Page `nexthd-reset-data` (shortcut section "Admin" di Workspace NextHD) memanggil `reset_demo_data()` di `nexthd/api.py`. Hapus 6 DocType transaksional (Ticket, Problem, Change Request, Known Error, Asset, Photo) + child table terkait, pertahankan data master (Category, Team, SLA Policy). Akses System Manager only (dicek di backend via `frappe.get_roles`), 2x konfirmasi (dialog + ketik `RESET` persis), backup otomatis (`frappe.utils.backups.new_backup()`), counter `tabSeries` ikut direset. **Test sungguhan berhasil:** 14 Ticket, 15 Problem, 3 Change Request, 2 Known Error, 6 Asset, 4 Photo terhapus, backup terbuat, data master utuh | 28 Agustus |
| Generalisasi NextHD Asset ke pola EAV | ✅ | `NextHD Asset Category` + `NextHD Asset Attribute` — lihat `docs/ARSITEKTUR.md §3` untuk detail lengkap. **6 September:** field lama `asset_type` (Select) di-deprecate (disembunyikan, non-destruktif) — 8 `depends_on` dialihkan penuh ke `asset_category`. **9 September (item PP):** `asset_type` **dihapus TOTAL** — dari metadata DocType DAN kolom fisik database (`DROP COLUMN`), setelah dikonfirmasi 0 dependensi tersisa & 100% data ter-cover `asset_category`. Report `Detail Aset Lengkap` disesuaikan di kedua tahap | 28–29 Agustus, deprecated 6 September, dihapus total 9 September |
| Bug `Link Type must be set first` pada Workspace NextHD | ✅ | Row "Reporting Data" bermasalah dihapus dari `tabWorkspace Link` — lihat `docs/BUG_WORKSPACE_SIDEBAR.md` item DD | 29 Agustus |
| **NextHD Ticket Worklog** — child table catatan progress teknisi | ✅ | 5 field (`waktu`, `teknisi`, `aktivitas`, `hasil`, `durasi_menit`) sesuai spec di bawah. Ditest fungsional 31 Agustus — tiket uji `TKT-2608-0007` tersimpan & terbaca benar | [PR #11](https://github.com/silverefendy/nexthd/pull/11), live + terverifikasi 31 Agustus |
| Field meta `Tanggal Dibuat`/`Tanggal Diedit` di 5 DocType | ✅ | Custom Field baru (Datetime, hidden+read_only) tersinkron dari `creation`/`modified` via `sync_meta_dates()` — Ticket, Problem, Known Error, Change Request, Asset. Backfill data lama 100% berhasil | 5-6 September |
| Report "Riwayat Progress Tiket" — gabungan Worklog lintas tiket | ✅ | Query Report standard, `JOIN` `NextHD Ticket Worklog`+`NextHD Ticket`, sortable by tanggal, 22 baris terverifikasi. Shortcut dashboard di Workspace "NextHD Report" | 5-6 September |
| Kolom Tag di report "Detail Tiket Lengkap" | ✅ | `LEFT JOIN tabTag Link` + `GROUP_CONCAT` — tag native Frappe (bukan field kustom), semua filter lama dipertahankan | 5-6 September |
| Riwayat Aktivitas/Progress (`NextHD Activity Log`) — Problem, Change Request, Known Error | ✅ | Child table shared (pola `NextHD Photo Link`): log otomatis saat status berubah + catatan manual Agent, opsional link dua arah ke dokumen lain (`related_doctype`+`related_document` Dynamic Link, klik langsung pindah dokumen) saat konversi Problem↔CR↔Known Error↔Asset. PR #12, commit `82344a0`, merged 7 September. Bug awal `self.reload()` hilang di `on_update()` (pola sama seperti Waiting Log PR #8) + schema drift `tanggal_dibuat`/`tanggal_diedit` (3 dari 5 DocType) terpicu migrate — keduanya diperbaiki manual tanpa Devin, commit `7af8deb`, 8 September | PR #12 + commit `7af8deb`, 8 September |
| Warna List View (indicator pill) — Priority/Ticket Type (Ticket), Kategori (Photo), Status/Asset Category (Asset) | ✅ | `formatters` di `nexthd_ticket_list.js`, file baru `nexthd_asset_list.js`/`nexthd_photo_list.js`, terdaftar di `hooks.py`. Kategori/Asset Category pakai hash-color dinamis (Link ke master yang bisa bertambah) | 9 September (item PP) |
| Fix `naming_rule="By Series"` usang — 5 DocType | ✅ | NextHD Asset, Problem, Change Request, Known Error, Service Catalog — diperbaiki ke `By "Naming Series" field`. Bug lama tidak pernah error sampai ada `doc.save()` penuh dijalankan | 9 September (item PP) |
| Hapus duplikat `Custom Field` "status" (Ticket/CR/Problem) | ✅ | Sisa eksperimen lama (`<DocType>-status`, Link ke Workflow State, hidden) — root cause ghost checkbox List View Settings & warna Status CR tidak muncul | 9 September (item PP) |

---

## 🔴 Bug Perlu Diperbaiki

| Bug | Status | Keterangan | PIC |
|---|---|---|---|
| Rename Module "Next Helpdesk" → "NextHD" belum dieksekusi | 🔴 | `tabModule Def` masih "Next Helpdesk" — sidebar module-based (Report page, Page kustom) masih menampilkan header lama. Dikonfirmasi 28 Agustus bukan Workspace nyasar. Perlu rename `Module Def` + update `modules.txt`, risiko menengah, sesi terpisah dengan backup — lihat `docs/SUMMARY.md` item EE | Claude + Efendy |

> **Catatan 30 Agustus:** dua bug lain yang sebelumnya tercatat di sini (Business Hours Sabtu, `Link Type must be set first`) **sudah selesai** — dipindah ke tabel "Fitur Inti" di atas / `docs/SUMMARY.md`. Cek `docs/SUMMARY.md §2` untuk daftar item pending terkini yang paling update (file ini diupdate lebih jarang dari `SUMMARY.md`).

---

## Tier 1 — Rencana Prioritas Berikutnya (Quick Win)

| Fitur | Status | Keterangan | Bergantung Pada |
|---|---|---|---|
| Knowledge Article (`NextHD Knowledge Article`) | ⬜ | DocType baru, field `visibility` (Publik/Internal) — solusi mandiri untuk requester, terpisah dari Known Error (yang teknis, untuk Agent). Lihat detail desain di bawah | — |
| Tag di Tiket | ✅ **sebagian sudah dipakai** | **Temuan 5-6 September:** Efendy sudah memakai fitur tag bawaan Frappe (`Tag Link` + `_user_tags`) secara manual untuk tiket (contoh: tag "pc", "psu") — tidak perlu development tambahan untuk filter dasar (List View sudah mendukung filter by Tag). Kolom "Tag" juga sudah ditambahkan ke report "Detail Tiket Lengkap" (lihat tabel Fitur Inti). Kalau ke depan butuh UI tag yang lebih terstruktur (dropdown kategori tag, dsb) baru perlu field custom | — |
| CSAT — survei kepuasan pasca-tiket | ⬜ | Field `csat_rating`, `csat_comment` di Ticket, trigger Telegram saat status "Selesai" | — |
| Merge tiket duplikat | ⬜ | Field `merged_into`, status "Digabung" | — |
| Auto-suggest Knowledge Article saat bikin tiket | ⬜ | Search artikel Publik yang cocok sebelum tiket disubmit | Knowledge Article |
| Dashboard trend chart | ⬜ | Tren volume tiket per minggu, breakdown kategori | — |
| Wipe Data Testing Tool — versi lengkap (UI checkbox per DocType) | ⬜ | Versi ringkas sudah live sebagai tombol "Reset Data Demo" (28 Agustus, lihat tabel Fitur Inti) — desain lengkap dengan granularitas per-DocType di bawah masih opsional kalau dibutuhkan | Reset Data Demo |

### Detail Desain: NextHD Ticket Worklog (✅ SELESAI — lihat tabel Fitur Inti)

**Status akhir:** diimplementasikan via PR #11, ditest fungsional & berhasil 31 Agustus 2026.
Spec desain asli (30 Agustus) dipertahankan di bawah untuk referensi historis.

**Latar belakang:** Efendy butuh cara mencatat progress penanganan tiket secara terstruktur.
Contoh kasus nyata: tiket "komputer mati" — teknisi perlu mencatat langkah troubleshooting
("cek & lepas HDD", "tes VGA", dst) berikut kapan dan siapa yang mengerjakan, supaya riwayat
penanganan tercatat rapi dan bisa direkap jadi laporan nanti (bukan cuma teks bebas di
Comment/Timeline bawaan Frappe yang sudah dipakai sementara).

**Keputusan desain kunci — BUKAN pola EAV seperti `NextHD Asset Attribute`.** EAV cocok untuk
Asset karena field-nya *berbeda-beda tergantung kategori* (laptop butuh CPU/RAM, kendaraan
butuh Plat Nomor/KM — tidak ada skema tetap yang berlaku semua kategori). Worklog progress
tiket **sebaliknya** — setiap entri progress berbentuk sama persis apa pun jenis masalahnya
(siapa, kapan, tindakan apa, hasil apa). Karena field-nya konsisten, **child table biasa
dengan field tetap** adalah pilihan yang tepat — sama seperti pola `NextHD Ticket Waiting Log`
yang sudah ada di project ini.

**DocType `NextHD Ticket Worklog`** (child table, `istable=1`, parent = `NextHD Ticket`,
`parentfield = "worklog"`) — **field final sesuai implementasi PR #11:**

| Fieldname | Fieldtype | Keterangan |
|---|---|---|
| `waktu` | Datetime | Kapan progress dicatat |
| `teknisi` | Link (User) | Siapa yang mengerjakan |
| `aktivitas` | Small Text | Deskripsi tindakan |
| `hasil` | Select: Berhasil / Belum Berhasil / Perlu Eskalasi / Menunggu Sparepart | Status hasil tindakan |
| `durasi_menit` | Int | Estimasi waktu — dipakai oleh report "Riwayat Progress Tiket" (5-6 September) |

**Laporan turunan yang sudah dibuat (5-6 September):** report "Riwayat Progress Tiket" —
gabungan semua worklog lintas tiket, sortable by tanggal, lihat tabel Fitur Inti.

**Kandidat pengembangan lanjutan (belum dikerjakan):**
- Report "Worklog per Teknisi" — rekap `durasi_menit` per user per periode, basis untuk
  laporan produktivitas (durasi_menit di data existing saat ini kebanyakan masih `0`,
  belum konsisten diisi teknisi)
- Notifikasi Telegram opsional saat entri worklog baru ditambahkan dengan `hasil = "Perlu
  Eskalasi"` — auto-notify Agent Manager
- Integrasi foto sebelum/sesudah per baris worklog (reuse `NextHD Photo`) — belum ada demand

### Detail Desain: Guard Duplikasi Workflow Transition (✅ SELESAI — lihat item LL di `docs/SUMMARY.md`)

**Status akhir:** root cause final Round 4 ditemukan & diperbaiki permanen 30-31 Agustus —
**2 channel fixture berbeda** (channel lama `hooks.py` + channel guard PR #10) saling
menambah. Setelah channel lama dihapus dan exception `in_migrate` di guard dihapus total,
diverifikasi stabil lintas 3× `bench migrate` berturut-turut. Detail lengkap kronologi di
`docs/SUMMARY.md` item LL dan `docs/WORKFLOW.md §5`. Spec desain asli (30 Agustus)
dipertahankan di bawah untuk referensi historis.

**Latar belakang:** Duplikasi `Workflow Transition` (kombinasi `state`+`action`+`next_state`
sama muncul berkali-kali dalam satu Workflow) sudah terjadi 4× — 20, 24, 25 Agustus (Round
1-3), dan 30 Agustus (Round 4). Root cause Round 1-3 (fixture JSON menumpuk generasi lama)
sudah dibersihkan tapi ternyata belum tuntas total — Round 4 mengungkap penyebab sesungguhnya
adalah dua channel fixture berbeda yang aktif bersamaan.

**Implementasi final:** `nexthd/next_helpdesk/utils/workflow_guard.py` — fungsi
`validate_no_duplicate_transitions(doc, method)` dipanggil via hook `doc_events["Workflow"]
["validate"]`, menolak `doc.save()` kalau ditemukan kombinasi `(state, action, next_state)`
duplikat di `NextHD Ticket`/`NextHD Problem`/`NextHD Change Request`. **Versi final (31
Agustus) tidak punya exception apa pun untuk konteks migrate/install/import** — divalidasi
ketat penuh di semua jalur, termasuk saat `bench migrate` reimport fixture.

### Detail Desain: Knowledge Article

**Keputusan (23 Agustus 2026):** DocType terpisah dari Known Error — Known Error ditulis
teknis untuk Agent (boleh detail infra), Knowledge Article ditulis untuk orang awam
(requester), campur keduanya berisiko bocorkan detail sensitif ke publik.

| Fieldname | Fieldtype | Keterangan |
|---|---|---|
| `title` | Data | Judul bahasa awam |
| `category` | Link (NextHD Category) | Reuse kategori existing |
| `content` | Text Editor | Langkah-langkah, boleh gambar |
| `visibility` | Select: Publik / Internal | Publik = baca tanpa login, Internal = role tertentu |
| `related_known_error` | Link (NextHD Known Error), opsional | Kalau lahir dari insiden nyata |
| `related_problem` | Link (NextHD Problem), opsional | Sama, opsional |
| `status` | Select: Draft / Published / Perlu Ditinjau Ulang | Approval sebelum tampil publik |
| `view_count` | Int, read-only | Tracking artikel paling sering dibaca |
| `author` | Link (User), read-only | Auto-fill |
| `last_reviewed_on` | Date | Penanda artikel perlu dicek relevansinya |

Artikel `visibility=Publik` perlu di-render lewat Frappe Web Page/Website Route (bukan Desk
form biasa) supaya bisa diakses tanpa login — pola mirip Web Form `/tiket-saya` tapi untuk
baca, bukan submit. Detail teknis dicek saat implementasi.

---

## Tier 2 — Struktural, Butuh Desain Lebih Matang

| Fitur | Status | Keterangan |
|---|---|---|
| Eskalasi otomatis | ⬜ | Bukan cuma warning H-30 menit — kalau SLA breach dan tiket belum direspon, auto-reassign/notify Agent Manager |
| Approval matrix Change Request (CAB sederhana) | ⬜ | 2 level: Agent Manager dulu, IT Manager kalau risiko tinggi |
| Bulk actions | ⬜ | Assign/tutup banyak tiket sekaligus |
| Integrasi PRTG → auto-create tiket | ⬜ | PRTG deteksi server down → otomatis bikin tiket |
| Arsip/retensi tiket lama | ⬜ | Tiket ditutup >1 tahun di-archive, bukan dihapus |
| **Generalisasi ke domain non-IT** | ✅ **sudah live, migrasi tuntas** | EAV Asset (`NextHD Asset Category`+`Attribute`) sudah live 28-29 Agustus, field lama `asset_type` sudah dihapus total 9 September — lihat tabel Fitur Inti. Rencana perluasan ke DocType lain di luar Asset masih rencana |
| **Wipe Data Testing Tool (versi lengkap)** | ⬜ | `NextHD Data Wipe Tool`, whitelist DocType per-checkbox, konfirmasi eksplisit, dry-run preview — desain lengkap di bawah. **Versi ringkas (tanpa checkbox, hapus semua sekaligus) sudah live sebagai tombol "Reset Data Demo", 28 Agustus** — lihat tabel Fitur Inti |

### Detail Desain: Wipe Data Testing Tool (Versi Lengkap)

**Status:** Desain final disepakati 20 Agustus 2026, belum diimplementasi sepenuhnya —
**versi ringkas** (tombol "Reset Data Demo", hapus semua DocType transaksional sekaligus,
tanpa checkbox per-DocType) **sudah live 28 Agustus** dan mencakup sebagian besar prinsip
di bawah (whitelist hardcoded, backup otomatis, konfirmasi eksplisit, reset `tabSeries`).
Bagian yang **belum** ada di versi live: UI checkbox pilih DocType satu-satu, dry-run/preview
jumlah record sebelum hapus, dan log audit terpisah (siapa/kapan reset dijalankan).

**Tujuan:** hapus data transaksional testing (Ticket, Problem, CR, Asset, Known Error)
tanpa menyentuh data konfigurasi/master (Business Hours, Holiday, SLA Policy, Team,
Category, Settings, Workflow, Permission, User, Workspace).

**Prinsip desain:**
- UI checkbox per DocType (bukan tombol "Wipe All")
- **Whitelist**, bukan blacklist — DocType baru yang lupa didaftarkan otomatis TIDAK
  terhapus (fail-safe)
- Prefix naming_series dibaca dinamis dari DocType meta
- Konfirmasi eksplisit: ketik `HAPUS DATA TESTING` persis
- Dry-run/preview jumlah record dulu sebelum hapus beneran
- Log hasil wipe (DocType, jumlah, waktu, siapa eksekusi)

**Whitelist (boleh dihapus):** NextHD Ticket (TKT), NextHD Problem (PRB), NextHD Change
Request (CHG), NextHD Asset (AST), NextHD Known Error (KE), NextHD Service Catalog (SVC).

**Selalu dikecualikan:** Business Hours, Holiday, SLA Policy, Team, Category, Settings,
User Profile, semua Workflow/Permission, User, Workspace.

**Rancangan:** Single DocType `NextHD Data Wipe Tool` — field `target_doctypes` (checklist),
`confirmation_text`, `preview_only` (Check, default 1), `last_wipe_log` (read-only). Tombol
"Preview Jumlah Data" dan "Hapus Sekarang" (aktif hanya kalau `preview_only` tidak dicentang
DAN teks konfirmasi cocok).

**Whitelist HARDCODED di kode Python** (`ALLOWED_DOCTYPES` list), bukan dibaca dinamis dari
input UI — supaya tidak bisa diakali lewat manipulasi request. Setelah wipe, `tabSeries`
untuk prefix terkait juga direset supaya penomoran mulai bersih (berkaca dari bug counter
tidak sinkron, 20 Agustus).

**Belum diputuskan sebelum implementasi (bagian yang belum ada di versi ringkas 28 Agustus):**
- Perlu checkbox per-DocType (bukan hapus semua sekaligus)?
- Perlu log aktivitas reset (siapa, kapan) ke DocType audit terpisah?
- Perlu kunci tambahan supaya reset tidak sengaja dipakai di luar konteks demo/testing?

---

## Tier 3 — Nice to Have, Belum Prioritas

| Fitur | Status | Kenapa Bisa Nunggu |
|---|---|---|
| Multi-channel (email-to-ticket, WhatsApp bot) | ⬜ | Telegram cukup untuk internal — relevan kalau ada requester eksternal |
| Custom SLA per Team | ⬜ | Baru dibutuhkan kalau tiap tim beda jauh standarnya |
| Gamification (leaderboard Agent) | ⬜ | Fun tapi bukan esensial untuk tim kecil |
| Dashboard "Aset Bermasalah" (Number Card) | ⬜ | Usulan lama, belum dikerjakan |
| SLA otomatis untuk Problem/Change Request | ⬜ | Saat ini SLA hanya untuk Ticket |
| Notifikasi Telegram untuk Problem/CR | ⬜ | Sengaja ditunda |
| Laporan bulanan otomatis (jumlah tiket, MTTR) | ⬜ | Usulan, belum dikerjakan |

---

## Item Housekeeping (Bukan Fitur, Tapi Perlu Ditindaklanjuti)

| Item | Status | Keterangan | PIC |
|---|---|---|---|
| Testing end-to-end workflow di UI browser | ⬜ | Backend sudah lulus 100% (20 Agustus), belum ditest klik manual | Efendy |
| Role assignment `support@ciptamebel.co.id` → IT Manager | ⬜ | Keputusan: sementara 1 akun shared dulu | Efendy |
| File `HANDOFF_SLA_NextHD_2026-08-19.md` belum ter-commit | ⬜ | Cek di server, `git add` kalau masih ada | Efendy |
| Guard permanen duplikasi workflow transition | ✅ | Selesai 31 Agustus — lihat tabel Fitur Inti & item LL di `docs/SUMMARY.md` | Claude + Efendy |
| NextHD Ticket Worklog | ✅ | Selesai 31 Agustus (PR #11) — lihat tabel Fitur Inti | Devin |
| Link Telegram untuk user test `test.requester` | ⬜ | Belum pernah kirim `/start`+`/link`, bukan bug | Efendy |
| Pemetaan tanggal Cuti Bersama 2026 belum dicek silang ke SKB asli | ⬜ | Data ditambahkan berdasar asumsi pola umum kalender cuti bersama Indonesia, bukan dibaca langsung dari teks SKB 3 Menteri | Efendy |
| Re-test Dashboard Connections "Dipakai Di" dengan foto baru | ⬜ | Foto contoh lama ikut terhapus tombol Reset Data Demo sebelum sempat ditest ulang — perlu buat foto baru → pakai di 1 Ticket → cek badge muncul di form Photo | Efendy |
| Rename Module "Next Helpdesk" → "NextHD" | 🔴 | Lihat tabel Bug Perlu Diperbaiki di atas | Claude + Efendy |
| `bench migrate` uji tahan (item KK/AA/MM) | ✅ | Root cause final regresi sidebar ditemukan & diperbaiki 2 September (item MM di `docs/SUMMARY.md`) — stabil lintas 2× migrate berturut-turut | Claude + Efendy |
| `git add`+commit+push semua file `.py`/`.json`/`.js` sesi 5-9 September (item NN, OO, PP) | 🔴 | Controller DocType, report, fixture, file JS warna List View — banyak yang belum di-commit ke git, menumpuk dari beberapa sesi. Lihat `docs/SUMMARY.md` untuk daftar lengkap | Efendy |
| Bersihkan `fixtures/property_setter.json` — label lama untuk `asset_type` yang sudah dihapus | ⬜ | Kosmetik, tidak error tapi kotor — sisa dari item PP (9 September) | Efendy |
| Cek apakah field `tanggal_dibuat`/`tanggal_diedit` & Workspace Shortcut baru perlu `export-fixtures` | 🔶 | Menyusul item NN, 5-6 September | Claude + Efendy |

---

## Urutan Eksekusi yang Disarankan (Tier 1)

1. **Knowledge Article + Tag** — fondasi dulu, karena Auto-Suggest bergantung ke Knowledge Article. Tag dasar sudah bisa dipakai native, fokus ke Knowledge Article dulu
2. **CSAT** — independen, bisa paralel dengan #1
3. **Dashboard Trend Chart** — independen, quick win terpisah
4. **Merge Tiket Duplikat** — bisa nunggu sampai ada kejadian nyata yang butuh ini
5. Tier 2 — nunggu sinyal nyata dibutuhkan, jangan dikerjakan preventif dulu

---

*Dokumen ini dikelola oleh Claude. Update status ✅/🔶/⬜ begitu ada progres — pindahkan
baris ke bagian "Sudah Selesai" begitu terverifikasi live, jangan dihapus dari sini
supaya riwayat lengkap tetap tercatat.*
