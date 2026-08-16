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

Ditemukan format tidak konsisten antar DocType:
- Ticket & Problem & Asset: format lama/statis (`TKT-.YYYY.-.####`, `PRB-2026-####`, `AST-2026-####`) — tersimpan di **Property Setter**, override DocField
- Change Request & Known Error: sudah `YY.MM` — tersimpan langsung di **DocField**, tanpa Property Setter

Diseragamkan semua ke format `YY.MM` (reset bulanan):

| DocType | Format Final | Contoh |
|---|---|---|
| NextHD Ticket | `TKT-.YY.MM.-.####.` | `TKT-2608-0001` |
| NextHD Problem | `PRB-.YY.MM.-.####.` | `PRB-2608-0001` |
| NextHD Asset | `AST-.YY.MM.-.####.` | `AST-2608-0001` |
| NextHD Change Request | `CHG-.YY.MM.-.####.` | *(tidak berubah)* |
| NextHD Known Error | `KE-.YY.MM.-.####.` | *(tidak berubah)* |

Diupdate via `frappe.db.set_value()` pada Property Setter (Ticket/Problem/Asset), commit + clear_cache. **Sudah ditest manual** — dokumen baru menghasilkan nomor sesuai format baru (verifikasi via private/incognito window karena isu cache browser di bawah).

**Dokumen lama tetap dibiarkan** apa adanya (konsisten dengan keputusan 14 Agustus).

### 3. Bug Ditemukan: Dropdown Naming Series Menampilkan Cache Lama
**Status:** ✅ Root cause ditemukan, bukan bug data

Setelah update Property Setter, dropdown "Naming Series" di form masih menampilkan opsi format lama meski data di database sudah benar (diverifikasi tidak ada duplikat Property Setter). **Solusi: hard refresh / buka di private-incognito window.** Ini murni cache boot info browser, bukan masalah server.

---

## ✅ SELESAI & TERVERIFIKASI (Sesi 15 Agustus, Bagian 2 — Relasi Asset)

### 4. Field `related_asset` di NextHD Problem + Auto-link dari Ticket
**Status:** ✅ Selesai (15 Agustus 2026)

Ditambahkan field baru `related_asset` (Link → NextHD Asset) di NextHD Problem, supaya Problem yang dibuat proaktif (tanpa lewat Ticket) tetap bisa dikaitkan ke aset spesifik.

Client Script `a258744559` ("Buat Problem dari Tiket") diupdate — saat Problem dibuat dari tombol ini, `related_asset` otomatis diisi dari `affected_asset` milik Ticket asal.

**Desain relasi Asset lengkap:**

| Relasi | Cara Terhubung |
|---|---|
| Ticket → Asset | Field langsung `affected_asset` (sudah ada sebelumnya) |
| Problem → Asset | Field langsung `related_asset` (baru) — auto-isi kalau dari Ticket, manual kalau Problem dibuat proaktif |
| Change Request → Asset | Field langsung `related_asset` (sudah ada sebelumnya) |
| Known Error → Asset | **Tidak langsung** — ditelusuri lewat `related_problem` → `related_asset` Problem. Keputusan sengaja: Known Error tanpa Problem dianggap kasus jarang (murni knowledge base), tidak diberi field asset sendiri untuk sekarang |

### 5. Tombol "Buat Change Request dari Asset"
**Status:** ✅ Selesai (15 Agustus 2026)

Client Script baru `cs_change_request_from_asset` di form NextHD Asset. Klik tombol → buat Change Request baru, auto-isi `title` dari `asset_name` dan `related_asset` dari nama Asset.

### 6. Search Fields NextHD Asset — Bisa Dicari dari Nama Pemakai
**Status:** ✅ Selesai (15 Agustus 2026)

Property Setter `search_fields` di NextHD Asset diset ke `asset_name,assigned_to,serial_number`. Efeknya: di semua dropdown Link yang mengarah ke NextHD Asset (`affected_asset` di Ticket, `related_asset` di Problem/Change Request), pencarian sekarang bisa pakai nama nomor aset, nama user pemakai (`assigned_to`), atau serial number — tidak cuma nama aset saja.

### 7. Bug: Field Baru via SQL Tidak Otomatis Jadi Kolom Fisik Tabel
**Status:** ✅ Ditemukan & diperbaiki (15 Agustus 2026)

Setelah insert `related_asset` ke `tabDocField`, error `Unknown column 'related_asset' in 'INSERT INTO'` / `'in SET'` muncul saat coba pakai field itu (baik insert Problem baru maupun update lewat `frappe.client.set_value`). **Root cause:** insert ke `tabDocField` cuma mendaftarkan metadata, tidak otomatis membuat kolom fisik di tabel data (`tabNextHD Problem`) — beda dengan `doc.save()`/migrate yang biasanya auto-sync ini.

**Fix:** `ALTER TABLE \`tabNextHD Problem\` ADD COLUMN \`related_asset\` VARCHAR(140)` manual. Ditambahkan aturan wajib baru di `POLA_KERJA_DAN_BUG.md` — detail lengkap di sana.

Dilakukan pengecekan menyeluruh untuk 5 DocType inti (Ticket, Problem, Change Request, Known Error, Asset) — semua field DocField vs kolom fisik sudah sinkron 100% setelah fix ini.

### 8. Bug: "Field related_problem not found" — Murni Cache
**Status:** ✅ Root cause ditemukan, bukan bug data

Setelah semua field terverifikasi ada (baik DocField maupun kolom fisik), tombol "Buat Known Error dari Problem" sempat gagal dengan pesan "Field related_problem not found" — padahal field itu sudah ada sejak lama. **Fix:** `bench clear-cache` + `bench clear-website-cache` + `bench restart`, lalu hard refresh browser. Ini kasus kedua di sesi ini di mana gejala terlihat seperti bug data padahal murni cache server/browser — lihat juga item #3 di atas.

---

## ✅ SELESAI & TERVERIFIKASI (Sesi 15 Agustus, Bagian 3 — Guard Workflow & Perbaikan Lanjutan)

### 9. Guard Transisi "Convert to Known Error" — Celah Ditutup
**Status:** ✅ Selesai (15 Agustus 2026)

Ditemukan transisi workflow polos `Investigasi → Known Error` yang sudah dihapus tanggal 11
Agustus **muncul lagi tanpa disengaja** (kemungkinan re-import/edit manual tidak tercatat).
Ini membuka celah lama: status Problem bisa pindah ke "Known Error" tanpa field `known_error`
terisi, karena transisi polos cuma ubah status tanpa membuat record.

**Fix:** transisi diberi `condition: doc.known_error` via raw SQL (percobaan pertama pakai
`doc.save()` untuk rename action gagal — `action` adalah Link ke Workflow Action Master, lihat
`WORKFLOW.md §4 Jebakan 3`). Sekarang tombol transisi ini hanya muncul di Actions kalau
`known_error` sudah terisi (baik lewat tombol otomatis atau dipilih manual). Detail lengkap
riwayat bug dan fix di `WORKFLOW.md §5`.

**Sudah di-export ke fixture dan commit.**

### 10. Bug: Field `related_asset` di Problem Tidak Muncul di UI
**Status:** ✅ Ditemukan & diperbaiki (15 Agustus 2026)

Setelah field `related_asset` berhasil dibuat (item #4 di atas), field-nya **tidak tampil**
di form meski `hidden=0` dan data valid. **Root cause:** field ditempatkan (idx) tepat setelah
field bertipe **Table** (`related_tickets`) tanpa Column Break di antaranya — Frappe kadang
tidak konsisten me-render field biasa yang menempel langsung setelah field Table.

**Fix:** field dipindah (ubah `idx`) ke posisi sejajar dengan Priority/Category, di bagian atas
form, bukan menumpuk di section "Tiket Terkait". Sudah diverifikasi tampil normal di browser.
Sudah di-export ke fixture dan commit.

### 11. Klarifikasi Alur: Known Error vs Change Request, Urutan Mana Dulu
**Status:** ✅ Diklarifikasi (15 Agustus 2026), didokumentasikan di `WORKFLOW.md §2`

Tidak ada urutan wajib — tergantung situasi: kalau perbaikan permanen butuh waktu/approval,
Known Error dibuat dulu sebagai referensi sementara sebelum Change Request. Kalau solusi bisa
langsung dieksekusi, Change Request bisa langsung dibuat tanpa Known Error. Kalau solusi sudah
pernah didokumentasikan di Known Error lama, tinggal dipilih manual, tidak perlu duplikasi.

Juga diklarifikasi: **Ticket tidak wajib berhubungan dengan Problem** — mayoritas tiket rutin
selesai dan ditutup langsung tanpa pernah masuk alur Problem.

### 12. Catatan Referensi: Generalisasi ke Domain Non-IT
**Status:** ✅ Rencana teknis lengkap disusun (15 Agustus 2026), belum ada jadwal eksekusi

Dibahas kemungkinan NextHD dipakai untuk domain lain (bengkel/otomotif, maintenance pabrik,
fasilitas gedung) — pola Ticket→Problem→CR→KE bersifat generik ITSM, bisa dipakai lintas
domain. **Belum ada rencana eksekusi konkret** (masih wacana), tapi rencana teknis lengkap
sudah disusun sebagai draft siap-pakai: DocType baru `NextHD Asset Category` (master kategori
extensible: Komputer & IT, Kendaraan, Mesin Produksi, Infrastruktur & Fasilitas, dll) dan
`NextHD Asset Attribute` (child table key-value/EAV untuk field spesifik per kategori tanpa
perlu ubah struktur tiap tambah kategori baru), plus rencana migrasi 5 langkah untuk data
existing. Detail lengkap di `ARSITEKTUR.md §8`.

---

## ✅ SELESAI & TERVERIFIKASI (Sesi 15 Agustus, Bagian 4 — Penutupan Item Lama)

### 13. Desktop Icon Routing — Verifikasi Route History Cleanup
**Status:** ✅ Terverifikasi (15 Agustus 2026) — item ini menggantung sejak 13 Agustus

Dicek ulang semua 5 komponen konfigurasi navigasi terkunci (lihat bagian "ATURAN WAJIB" di
atas): `add_to_apps_screen.route`, Desktop Icon `link_type`, item pertama Workspace Sidebar,
`default_app` System Settings, `default_app` user `support@ciptamebel.co.id`. **Semua cocok
persis** dengan konfigurasi yang dikunci sejak 14 Agustus — tidak ada drift. Diverifikasi juga
manual di browser (private window): klik icon NextHD langsung masuk ke Dashboard, bukan ke
list Ticket.

---

## ❌ OPEN ITEMS (Update Terbaru)

### 1. Fitur Kandidat (Belum Dikerjakan, Sekadar Usulan)
Dibahas 15 Agustus, belum ada keputusan eksekusi:
- Dashboard "Aset Bermasalah" (Number Card hitung Ticket per Asset)
- SLA otomatis untuk Problem/Change Request (saat ini SLA cuma untuk Ticket)
- Notifikasi Telegram untuk Problem/Change Request (saat ini trigger baru ada untuk Ticket + approval CR)
- Laporan bulanan otomatis (jumlah tiket, MTTR, aset bermasalah)
- Field "Root Cause Category" di Problem untuk analisis tren

### 2. Skenario Test Data — Disiapkan, Perlu Dieksekusi Manual
Tiga skenario end-to-end sudah disusun untuk mengisi data test sekaligus verifikasi semua alur
(termasuk relasi Asset dan guard workflow baru): (A) Ticket→Problem→CR full flow dengan Asset,
(B) Ticket→Problem→Known Error dengan root cause, (C) Ticket mandiri tanpa Problem + Problem
proaktif tanpa Ticket. Belum dikonfirmasi sudah dieksekusi atau belum.

### 3. Generalisasi Domain Non-IT — Menunggu Kebutuhan Nyata
Rencana teknis sudah lengkap di `ARSITEKTUR.md §8`, tidak butuh tindakan sampai ada kebutuhan
konkret (misal benar-benar mau pakai NextHD untuk bengkel/maintenance/dll).

---

## Keputusan Final (Update — Menggantikan Tabel 14 Agustus)

| Keputusan | Detail |
|---|---|
| NextHD Ticket naming | **DIUBAH** ke `YY.MM` (15 Agustus) — *keputusan 14 Agustus dibatalkan* |
| Format naming series semua DocType | Seragam `YY.MM` untuk Ticket, Problem, Asset, Change Request, Known Error |
| File backup lokal (`fixtures.bak_*`, `*.bak`) | Jangan ikut di-commit — tambahkan ke `.gitignore` |
| Known Error → Asset | **Tidak diberi field langsung** — ditelusuri lewat Problem. Bisa direvisi kalau ternyata sering butuh Known Error tanpa Problem yang terhubung ke Asset |
| Field baru via raw SQL ke `tabDocField` | **Wajib** diikuti `ALTER TABLE ADD COLUMN` manual — bukan otomatis |
| Transisi workflow "Convert to Known Error" | **Tidak dihapus lagi** — diberi `condition: doc.known_error` supaya lebih tahan terhadap re-import tidak sengaja |
| Generalisasi ke domain non-IT | **Masih wacana**, tapi rencana teknis lengkap sudah disusun di `ARSITEKTUR.md §8`, siap dieksekusi kapan pun dibutuhkan |
| Desktop Icon Routing (item 13 Agustus) | **Ditutup** — diverifikasi ulang 15 Agustus, semua konfigurasi cocok, tidak ada drift |
