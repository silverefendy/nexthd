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

### Pola Kerja Teknis Wajib

1. **Jangan** paste multi-line Python langsung ke IPython console — selalu tulis ke file via heredoc, lalu pipe ke console
2. Baris kosong di tengah script yang di-pipe **akan memutus block** IPython — hindari blank line antar statement top-level
3. `doc.save()` selalu gagal di production (non-developer mode) — semua perubahan DocType/DocField wajib pakai **SQL langsung + `frappe.db.commit()`**
4. Setiap perubahan struktur **wajib** di-export ke fixture JSON dan commit ke repo, atau hilang saat `bench migrate`
5. Frappe v16 di instalasi ini — **banyak nama kolom tabel berbeda** dari dokumentasi umum. Selalu `DESCRIBE tabNamaTable` dulu sebelum query
6. **Tambah DocField baru via raw SQL wajib diikuti `ALTER TABLE ADD COLUMN`** — insert ke `tabDocField` saja tidak otomatis membuat kolom fisik di tabel data. Detail di `POLA_KERJA_DAN_BUG.md`
7. Setelah perubahan field/meta yang tidak muncul di UI meski data sudah benar di database, coba `bench clear-cache` + `bench restart` di server sebelum curiga ada bug data

---

## ✅ SELESAI & TERVERIFIKASI

### 1. Navigasi — Icon NextHD → Workspace Dashboard
**Status:** ✅ Selesai (14 Agustus 2026)

Root cause ditemukan setelah investigasi panjang. Solusi terdiri dari 4 komponen:

1. `hooks.py` → `add_to_apps_screen.route` diubah dari `/desk` ke `/desk/nexthd`
2. `workspace_sidebar.json` → item "Dashboard" (link ke Workspace NextHD) ditambahkan di posisi pertama
3. System Settings → `default_app` diset ke `nexthd`
4. User `support@ciptamebel.co.id` → `default_app` diset ke `nexthd`

Semua perubahan sudah di-commit ke repo (commit `59edfbe`).

### 2. Naming Series — Format YYMM
**Status:** ✅ Selesai (14 Agustus 2026)

Format baru (reset otomatis tiap bulan):

| DocType | Format Baru | Contoh |
|---|---|---|
| NextHD Problem | `PRB-.YY.MM.-.####.` | `PRB-2608-00001` |
| NextHD Change Request | `CHG-.YY.MM.-.####.` | `CHG-2608-00001` |
| NextHD Asset | `AST-.YY.MM.-.####.` | `AST-2608-00001` |
| NextHD Known Error | `KE-.YY.MM.-.####.` | `KE-2608-00001` |
| NextHD Ticket | Tidak diubah | `TKT-2026-xxxxx` |

Diupdate via SQL langsung ke `tabDocField`. Dokumen lama yang kena bug `####` (7 Problem, 1 Change Request, 1 Asset) **sengaja tidak di-rename** sesuai keputusan Efendy.

> ⚠️ **Belum ditest manual** — perlu buat 1 NextHD Problem baru dan verifikasi nama dokumennya `PRB-2608-xxxxx`.

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

## ❌ OPEN ITEMS — Belum Dikerjakan

### 1. Export Fixture — KRITIS
**Risiko: perubahan hilang saat `bench migrate` berikutnya**

Perubahan berikut **belum terdaftar di `hooks.py`** dan belum di-export ke fixture JSON:

| Perubahan | Fixture DocType yang Perlu Ditambahkan |
|---|---|
| Naming series (DocField) | `DocField` |
| Kolom list view (Property Setter) | `Property Setter` |
| Client Script "Buat Problem dari Tiket" | `Client Script` |

Yang sudah terdaftar (aman):
```python
fixtures = [
    {"dt": "Workflow", ...},
    {"dt": "Workflow Transition", ...},
    {"dt": "Desktop Icon", ...},
    {"dt": "Workspace Sidebar", ...}
]
```

**Langkah yang perlu dilakukan:**
1. Tambahkan `DocField`, `Property Setter`, `Client Script` ke `hooks.py` di bagian `fixtures`
2. Jalankan `bench --site desk.ciptamebel.co.id export-fixtures`
3. Commit hasil export ke repo

### 2. Test Manual Naming Series
Buat 1 NextHD Problem baru → verifikasi nama dokumen `PRB-2608-00001` (bukan format lama).

---

## Keputusan Final (Jangan Diulang Tanya)

| Keputusan | Detail |
|---|---|
| Dokumen lama kena bug `####` | **Tidak di-rename** — biarkan apa adanya |
| Format nomor baru | **YYMM** (reset bulanan), bukan YYYY |
| NextHD Ticket naming | **Tidak diubah** |
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

## ❌ OPEN ITEMS (Update)

### 1. ~~Export Fixture~~ — SELESAI, lihat di atas

### 2. Desktop Icon Routing — Verifikasi Route History Cleanup
**Masih menggantung dari sesi 13 Agustus**, belum diverifikasi ulang. Perlu cek apakah routing desktop icon tetap benar setelah cleanup Route History yang dilakukan sebelumnya.

---

## Keputusan Final (Update — Menggantikan Tabel 14 Agustus)

| Keputusan | Detail |
|---|---|
| NextHD Ticket naming | **DIUBAH** ke `YY.MM` (15 Agustus) — *keputusan 14 Agustus dibatalkan* |
| Format naming series semua DocType | Seragam `YY.MM` untuk Ticket, Problem, Asset, Change Request, Known Error |
| File backup lokal (`fixtures.bak_*`, `*.bak`) | Jangan ikut di-commit — tambahkan ke `.gitignore` |
| Known Error → Asset | **Tidak diberi field langsung** — ditelusuri lewat Problem. Bisa direvisi kalau ternyata sering butuh Known Error tanpa Problem yang terhubung ke Asset |
| Field baru via raw SQL ke `tabDocField` | **Wajib** diikuti `ALTER TABLE ADD COLUMN` manual — bukan otomatis |
