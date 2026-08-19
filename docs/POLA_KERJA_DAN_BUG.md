# NextHD — Pola Kerja & Riwayat Bug

> Frappe quirks, aturan wajib saat coding/debug, dan riwayat bug per sesi.
> File ini yang paling sering bertambah tiap sesi baru.
>
> **Last updated:** 2026-08-20 10:00 WIB

---

## 1. Frappe v16 — Desktop & Workspace (KRITIS)

Ada 3 sistem berbeda yang saling terhubung.

### A. `/desk/desktop` — Halaman Desktop (App Icons)

Dikontrol oleh **`tabDesktop Icon`** dan hook **`add_to_apps_screen`**.

**Kolom penting `tabDesktop Icon`:**
```
name, label, icon_type, link_type, link_to, link,
parent_icon, app, logo_url, icon, hidden, standard
```

**Untuk App icon (kepala):**
```python
icon_type = 'App'
link_type = 'Workspace Sidebar'   # ← BUKAN External, agar tidak buka tab baru
link_to   = 'NextHD'              # nama Workspace Sidebar
link      = NULL
app       = 'nexthd'
logo_url  = '/assets/nexthd/logo.svg'
standard  = 0                     # agar tidak terhapus saat migrate
```

**Hook `add_to_apps_screen` — WAJIB ADA di `hooks.py`:**
```python
add_to_apps_screen = [
    {
        "name": "nexthd",
        "logo": "/assets/nexthd/logo.svg",
        "title": "NextHD",
        "route": "/desk",
    }
]
```
Tanpa hook ini, nexthd tidak muncul di desktop meski ada di `tabDesktop Icon`.

**Logo WAJIB ADA** di `/home/it/frappe/apps/nexthd/nexthd/public/logo.svg`. Tanpa file logo, hook tidak terbaca.

> ✅ **FIXED (2026-08-11):** Sempat salah routing ke `/desk/nexthd-ticket`. Ternyata config DB
> sudah benar dari awal — murni masalah cache. Fix: `bench clear-cache` + `bench clear-website-cache`
> + `bench build --app nexthd` + `bench restart` + hard refresh browser.

### B. `/desk/nexthd` — Workspace Page

Dikontrol oleh **`tabWorkspace`** dan file `nexthd/next_helpdesk/workspace/nexthd/nexthd.json`.

> ⚠️ **JANGAN** generate `content` sebagai string literal dengan escape manual.
> **SELALU** build sebagai Python dict/list lalu `json.dumps()` sekali.
> Double-escape akan menyebabkan `SyntaxError` di browser.

**Number Cards di workspace:**
- Buat dulu di `tabNumber Card` (via SQL)
- Isi `number_card_name` di `tabWorkspace Number Card` (kolom kunci: `number_card_name`, bukan `card_name`)

> ✅ **FIXED (2026-08-11):** Root cause: block `content` JSON workspace pakai `"type": "card"`
> dengan key `"card_name"` — SALAH. Frappe v16 butuh `"type": "number_card"` dengan key
> `"number_card_name"`. Type yang tidak dikenal di-skip diam-diam tanpa error.

### C. Sidebar Kiri — `tabWorkspace Sidebar`

Dikontrol oleh **`tabWorkspace Sidebar`** dan **`tabWorkspace Sidebar Item`**.

> `standard=1` → sidebar tidak bisa diedit via UI. Fix: `UPDATE tabWorkspace Sidebar SET standard=0`

> ✅ **FIXED (2026-08-19):** Item **Holiday hilang dari sidebar, sidebar rusak saat diklik**.
> Root cause: `NextHD Holiday` (DocType terpisah dari `NextHD Business Hours`) tidak pernah
> terdaftar di fixture `nexthd/fixtures/workspace_sidebar.json`, sehingga insert manual
> sebelumnya selalu tertimpa/rusak tiap `bench migrate`. Fix: tambah entry Holiday langsung
> ke fixture file (bukan insert manual ke DB), lalu migrate.

### D. Aturan Fixtures — WAJIB

`bench migrate` akan hapus Desktop Icon dan Workspace Sidebar yang tidak ada di fixtures. Selalu export setelah perubahan:

```bash
bench --site desk.ciptamebel.co.id export-fixtures --app nexthd
```

---

## 2. Workspace Dashboard — Konfigurasi Saat Ini

```
Sections:
  [Operasional]
    Shortcuts: New Ticket, All Tickets, NextHD Problem, NextHD Change Request

  [Statistik Tiket]
    Number Cards (6):
      Tiket Baru              → COUNT NextHD Ticket WHERE status = Baru
      Tiket Sedang Dikerjakan → COUNT WHERE status = Sedang Dikerjakan
      Menunggu User           → COUNT WHERE status = Menunggu User
      Tiket Selesai Bulan Ini → COUNT WHERE status = Selesai AND modified = this month
      Tiket Prioritas Kritis  → COUNT WHERE priority = Kritis AND status NOT IN Selesai,Ditutup
      Problem Terbuka         → COUNT NextHD Problem WHERE status NOT IN Selesai,Ditutup

  [Tiket Terbaru]
    Quick Lists (2):
      Open Tickets     → NextHD Ticket WHERE status NOT IN Selesai,Ditutup
      Critical Tickets → NextHD Ticket WHERE priority = Kritis AND status NOT IN Selesai,Ditutup

  [Konfigurasi]
    Shortcuts: NextHD Settings, NextHD SLA Policy, NextHD Team, NextHD Category
```

---

## 3. Aturan Wajib Saat Coding/Debug

### Pola Console — BENAR vs SALAH

**✅ BENAR — Selalu pakai file script + redirect:**
```bash
# Langkah 1: tulis ke file
cat > /home/it/nama_script.py << 'EOF'
import frappe

def run():
    results = []
    for item in list_data:
        results.append(str(item))
    print("\n".join(results))
    print("DONE")

run()
EOF

# Langkah 2: jalankan via redirect
bench --site desk.ciptamebel.co.id console < /home/it/nama_script.py
```

**❌ SALAH — Jangan paste langsung ke console interaktif:**
IPython akan error `IndentationError` atau loop tidak jalan sama sekali.

### Tabel Aturan Wajib Lainnya

| Aturan | Penjelasan |
|---|---|
| `continue`/`break` dalam loop di console | Error. Gunakan `if/else` sebagai gantinya |
| **Baris kosong di dalam blok manapun** (for/if/def) di script console | **Error/perilaku tidak terduga.** IPython nganggap baris kosong = akhir blok. Hindari baris kosong di DALAM blok — boleh ada ANTAR blok top-level saja |
| **Loop/logic kompleks di console** | **Selalu bungkus dalam 1 fungsi** (`def run(): ...` lalu panggil `run()` terpisah) — IPython baca seluruh body sebagai 1 unit |
| `doc.save()` | Selalu gagal di production. Pakai SQL INSERT/UPDATE + `frappe.db.commit()` — **kecuali** untuk `doc.insert()` pada custom DocType baru yang memang perlu validasi Frappe |
| **Field Link yang wajib diisi (`reqd=1`)** | Cek dulu via `frappe.get_meta(doctype)` — filter `f.reqd or f.fieldtype == "Link"`. Contoh: `NextHD Ticket` butuh `subject` dan `requested_by` — kalau test insert via console lupa isi ini, akan kena `MandatoryError` meski `calculate_sla()` sendiri sudah terpanggil dan sukses |
| **Field Link ke master doctype** | Master record harus **sudah ada duluan** sebelum insert dokumen yang mereferensikannya |
| Perubahan DB langsung | Export fixture → git commit → git push |
| `bench migrate` | Bisa hapus Desktop Icon dan Workspace Sidebar yang tidak di fixtures |
| Cek schema tabel | `DESCRIBE tabNama` dulu sebelum INSERT |
| **Fixtures export sebelum data ada** | `bench export-fixtures` membaca DARI database — kalau dijalankan saat tabel masih kosong, fixture JSON yang dihasilkan JUGA kosong (`[]`) dan akan menimpa file manual yang lengkap |
| MariaDB subquery | Versi lama tidak support `LIMIT` di subquery `IN` |
| JSON content workspace | Generate via `json.dumps()` Python, BUKAN string literal manual |
| Workspace number card block | Type HARUS `"number_card"` (bukan `"card"`), key HARUS `"number_card_name"` (bukan `"card_name"`) |
| `Workflow State` (fixtures) | Tidak punya kolom `workflow` — jangan filter berdasarkan itu. Master global, TIDAK masuk fixtures per-app |
| Role assignment ke user | Via UI (User → Roles), TIDAK perlu SQL |
| **Workflow State → `Update Field`** | Jangan isi sama dengan `workflow_state_field` kecuali `Update Value` juga diisi benar — kalau kosong, status akan tertimpa `None` setelah transisi. Lihat `WORKFLOW.md` |
| **`bench console` beda sesi = beda state Python** | Import/variable dari sesi sebelumnya TIDAK terbawa — harus import ulang |
| **Dua jalur ke satu state yang butuh side-effect** | Hapus transisi workflow polos yang bisa mencapai state itu tanpa lewat tombol/method custom |
| **Property Setter — filter fixture** | Tidak punya kolom `app`. Filter yang benar: `doc_type` (`=` atau `LIKE`), bukan `app =` |
| **DocField baru via raw SQL INSERT ke `tabDocField`** | **Wajib** diikuti `ALTER TABLE \`tabNamaDocType\` ADD COLUMN` manual. Insert ke `tabDocField` cuma daftar metadata, TIDAK otomatis membuat kolom fisik di tabel data — beda dari `doc.save()`/migrate yang auto-sync. Lupa langkah ini → error `Unknown column 'xxx' in 'INSERT INTO'` atau `'in SET'` saat field dipakai |
| **Field/meta baru tidak muncul di UI meski data DB sudah benar** | Coba `bench clear-cache` + `bench clear-website-cache` + `bench restart` dulu sebelum curiga bug struktur data. Sering kali murni cache boot info server, bukan masalah field/kolom |
| **`bench --site X mariadb -e "..."` tiap panggilan buka KONEKSI BARU** | `SET SQL_SAFE_UPDATES=0` di command `-e` terpisah TIDAK terbawa ke command `-e` berikutnya (safe update mode akan error lagi). WAJIB gabung dalam satu koneksi: `bench --site X mariadb << 'SQL' ... SQL` |
| **`bench migrate` — urutan wajib saat menambah kolom BARU lalu langsung mengisi datanya** | Migrate dulu (agar kolom fisik tercipta di DB) BARU UPDATE data. Kalau dibalik → `ERROR 1054 Unknown column` |
| **`__pycache__` basi setelah edit file `.py`** | Kadang perubahan logic Python tidak langsung kepakai meski file sudah diedit dan `bench restart` dijalankan. Kalau hasil eksekusi masih mengikuti kode versi lama, hapus `find <app_path> -type d -name "__pycache__" -exec rm -rf {} +` lalu restart lagi |
| **Selalu verifikasi isi file DI DISK dengan `grep`/`cat` sebelum asumsi kode sudah ter-replace** | Kasus nyata (2026-08-20): sesi sebelumnya "mengaku" sudah menulis ulang `calculate_sla()`, tapi `grep` di sesi berikutnya membuktikan file masih versi lama (`add_to_date`, bukan `add_working_time`). Root cause: perubahan tidak pernah benar-benar tersimpan ke disk sesi sebelumnya. **Jangan percaya catatan dokumentasi 100% — selalu cross-check langsung ke file sebelum lanjut debug** |

---

## 4. Riwayat Bug & Status Penyelesaian

### ✅ SELESAI — Bugfix dari Review Claude (2026-08-07)

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

### ✅ SELESAI — Bug Infrastructure & UI (2026-08-09 s/d 11)

| # | Masalah | Penyelesaian |
|---|---|---|
| 1 | Duplikasi folder `nexthd/doctype/` dan `nexthd/utils/` di root app | Hapus, pertahankan path di `next_helpdesk/` |
| 2 | "Next Helpdesk" workspace muncul di sidebar (tidak diinginkan) | Patch Python hapus via `frappe.db.delete()` |
| 3 | hooks.py syntax error setelah `sed` | Fix dengan script Python |
| 4 | nexthd.json terpotong saat `cat EOF` | Tulis ulang via `json.dumps()` Python |
| 5 | patches.txt dua patch tergabung satu baris | Python `str.replace()` tambah newline |
| 6 | `add_to_apps_screen` di-comment, desktop kosong | Un-comment, tambah logo.svg |
| 7 | Logo tidak ada → hook tidak terbaca | Buat `nexthd/public/logo.svg` |
| 8 | Desktop Icon dihapus tiap `bench migrate` | Tambah ke fixtures di hooks.py |
| 9 | Workspace Sidebar dihapus tiap `bench migrate` | Tambah ke fixtures di hooks.py |
| 10 | Workspace Sidebar `standard=1` tidak bisa diedit | `UPDATE tabWorkspace Sidebar SET standard=0` |
| 11 | Permission missing — 4 DocType tidak bisa dibuka | SQL INSERT ke `tabDocPerm` |
| 12 | Desktop icon NextHD buka tab baru | `link_type = Workspace Sidebar`, `link = NULL` |
| 13 | Number Card tidak muncul di workspace | UPDATE `tabWorkspace Number Card` SET `number_card_name` |
| 14 | Workspace content double escape → SyntaxError browser | Generate via `json.dumps()` |
| 15 | Fixtures Workflow State error kolom 'workflow' | Hapus Workflow State dari fixtures |
| 16 | NextHD Asset field statis saja | Tambah field dinamis per asset_type dengan `depends_on` |
| 17 | NextHD Ticket tidak ada link ke Asset | Tambah field `affected_asset` → Link: NextHD Asset |
| 18 | NextHD Problem field terlalu minimal | Tambah priority, category, workaround, known_error, change_request |

### ✅ TERVERIFIKASI — 2026-08-11 (via screenshot user)

| # | Item | Hasil |
|---|---|---|
| 1 | NextHD Ticket form — `affected_asset` & `service_catalog` | ✅ OK — `service_catalog` tersembunyi karena `depends_on`, sesuai desain |
| 2 | NextHD Problem form — `workaround`, `known_error`, `change_request` | ✅ OK — `known_error` tersembunyi karena `depends_on`, sesuai desain |

### ✅ SELESAI — Bug Session 2026-08-11 (lanjutan)

| # | Item | Masalah | Fix |
|---|---|---|---|
| 1 | Number cards "Statistik Tiket" | Tidak render di `/desk/nexthd` | Block `content` JSON pakai `type: "card"` salah, seharusnya `"number_card"` + key `number_card_name`. Detail di `POLA_KERJA_DAN_BUG.md §1.B` |
| 2 | Desktop icon routing | Klik icon → sempat ke `/desk/nexthd-ticket` | Ternyata cuma cache — `clear-cache` + `build` + restart + hard refresh |
| 3 | Workflow kosong di database | 0 Workflow padahal fixture JSON ada di repo | 7 lapis bug (lihat `WORKFLOW.md §5`) |
| 4 | Dokumentasi field NextHD Known Error salah | §4 sempat tulis field `root_cause`, `problem`, `status` — semua tidak ada | Dikoreksi ke field asli: `symptom`, `related_problem`, tanpa `status` |
| 5 | `WorkflowPermissionError: ... from Investigasi to Terbuka` saat klik tombol NextHD Problem | Semua state punya `Update Field = status` + `Update Value = None` | Kosongkan `update_field`/`update_value` di semua state (detail di `WORKFLOW.md §5`) |
| 6 | Bug `update_field` yang sama di NextHD Ticket & Change Request | Kelima state Ticket dan kedelapan state Change Request kena hal yang sama | Fix sama diterapkan ke kedua workflow sekaligus |
| 7 | Transisi `Investigasi → Known Error` redundan & berisiko | Ada tombol custom yang sudah lebih lengkap | Hapus transisi tersebut dari `Workflow.transitions` (detail di `WORKFLOW.md §5`) |

### ✅ SELESAI — Bug Session 2026-08-15 (Naming Series & Relasi Asset)

| # | Item | Masalah | Fix |
|---|---|---|---|
| 1 | Export fixture `Property Setter` gagal | `Unknown column 'app' in 'WHERE'` | Property Setter tidak punya kolom `app`. Filter benar: `doc_type LIKE 'NextHD%'` |
| 2 | Naming series tidak konsisten antar DocType | Ticket/Problem/Asset pakai format lama (`YYYY`/statis `2026`) via Property Setter, override DocField yang sudah `YY.MM` | Diseragamkan semua ke `YY.MM` via update Property Setter |
| 3 | Dropdown Naming Series di form tampil format lama meski data DB sudah benar | Cache boot info browser, bukan bug data (diverifikasi tidak ada duplikat Property Setter) | Hard refresh / buka private-incognito window |
| 4 | `Unknown column 'related_asset' in 'INSERT INTO'` / `'in SET'` saat pakai field baru di NextHD Problem | Field didaftarkan ke `tabDocField` via SQL, tapi kolom fisik di `tabNextHD Problem` tidak otomatis terbuat | `ALTER TABLE \`tabNextHD Problem\` ADD COLUMN \`related_asset\` VARCHAR(140)` manual. Aturan baru ditambahkan di §3 |
| 5 | `Field related_problem not found` saat klik "Buat Known Error dari Problem" | Field sudah ada di DocField DAN kolom fisik (diverifikasi), murni cache metadata server | `bench clear-cache` + `bench clear-website-cache` + `bench restart` |

### ✅ SELESAI — Bug Session 2026-08-19 (Sidebar Holiday, Dedup Workflow, Naming Series Semua DocType)

| # | Item | Masalah | Fix |
|---|---|---|---|
| 1 | Sidebar Holiday hilang, rusak saat diklik | `NextHD Holiday` tidak ada di fixture `workspace_sidebar.json` | Tambah entry Holiday ke fixture, migrate. Lihat §1.C |
| 2 | Dedup transisi workflow NextHD Ticket & Change Request | Baris duplikat semua punya `idx=0` (prefix nama `ai9*`), baris asli idx berurutan (prefix `l86*`/`l87*`) | `DELETE FROM tabWorkflow Transition WHERE name LIKE 'ai9%'` per parent. Hasil akhir: Ticket 7 transisi, Change Request 8 transisi |
| 3 | Bug penomoran `####` di SEMUA DocType (bukan cuma Ticket) | Opsi `naming_series` di JSON DocType pakai literal salah tanpa titik pemisah: `PRB-2026-####`, `CHG-2026-####`, `AST-2026-####`, `KE-2026-####`, `SVC-2026-####` | Diseragamkan ke format `.YY.MM.-.####` (reset otomatis per bulan) di 6 DocType (Ticket, Problem, Change Request, Asset, Known Error, Service Catalog) + update data existing + bersihkan row lama `tabSeries` + migrate developer_mode. Terverifikasi record baru format `XXX-2608-0001` |

### ✅ SELESAI — Bug Session 2026-08-20 (SLA Enforcement Business Hours)

Root cause awal: `calculate_sla()` lama pakai `add_to_date()` mentah, sama sekali tidak menghitung jam kerja/hari libur.

**Yang dikerjakan:**
- `business_hours.py` (utils) — bug lama: `WEEKDAY_MAP` pakai nama Inggris (Monday dst) padahal `tabNextHD Business Hours` isinya nama Indonesia (Senin dst), jadi `get_business_hours()` selalu `None`. Diperbaiki ke nama Indonesia.
- `add_working_time()` ditulis ulang jadi versi loop (mengurangi sisa menit per hari kerja, lompat ke hari kerja berikutnya) — menangani durasi multi-hari (Sedang 2 hari, Rendah 1 minggu).
- `NextHD SLA Policy` — field diubah jadi `response_value`+`response_unit` dan `resolution_value`+`resolution_unit` (Menit/Jam/Hari), auto-terhitung ke `response_time_minutes`/`resolution_time_minutes` via controller `validate()`.
- Data SOP final (semua business hours): Kritis response 15 menit/resolusi 1 jam, Tinggi response 30 menit/resolusi 4 jam, Sedang response 60 menit/resolusi 2 hari kerja, Rendah response 120 menit/resolusi 7 hari kerja. `is_24x7 = 0` untuk semua priority.
- **Root cause kenapa fix sebelumnya "belum jalan":** `calculate_sla()` di `nexthd_ticket.py` ternyata **belum pernah benar-benar diarahkan** memanggil `add_working_time()` — masih memanggil `add_to_date()` mentah. Klaim sesi sebelumnya bahwa fungsi "sudah ditulis ulang" tidak akurat; diverifikasi langsung via `grep` di file disk.
- Fix final: tambah import `from nexthd.next_helpdesk.utils.business_hours import add_working_time`, replace body `calculate_sla()` agar memanggil `add_working_time(now, minutes, is_24x7=...)` untuk `sla_response_by` dan `sla_resolution_by`.

**Verifikasi test (2026-08-20 05:32 WIB insert):**

| Field | Hasil | Status |
|---|---|---|
| Waktu insert | 2026-08-20 05:32 (di luar jam kerja) | — |
| `sla_response_by` | 2026-08-20 09:00 (jam buka 08:00 + 60 menit, prioritas Sedang) | ✅ Benar |
| `sla_resolution_by` | 2026-08-26 12:30 (+2 hari kerja dari jam buka) | ✅ Benar |

Ticket test: `TKT-2608-0004`. Sudah di-commit (`8d3f26d`) dan push ke `origin/main`.

**Tersisa (masuk ke `SUMMARY.md` §2 sebagai item baru):**
- Verifikasi custom reports (item #2 lama) sekarang bisa jalan penuh di produksi karena `sla_resolution_by` sudah konsisten terisi.

---

*Dokumen ini dikelola oleh Claude. Update terakhir: 2026-08-20 10:00 WIB.*
