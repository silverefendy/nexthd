# NextHD — Pola Kerja (Aturan Wajib & Frappe Quirks)

> **File hasil pemecahan dari `POLA_KERJA_DAN_BUG.md` (30 Agustus 2026)** — berisi murni aturan
> wajib, pola kerja, dan Frappe quirks yang relatif stabil (jarang berubah drastis antar sesi).
> Riwayat bug per sesi (yang terus bertambah tiap sesi) dipisah ke file lain:
> - `docs/BUG_WORKSPACE_SIDEBAR.md` — riwayat bug Workspace/Desktop Icon/Sidebar (topik paling sering)
> - `docs/BUG_HISTORY.md` — riwayat bug lain (SLA, Telegram, naming series, dll)
> - `docs/WORKFLOW.md` — sudah punya riwayat bug workflow sendiri, tidak berubah
>
> **Status pemecahan:** Baru file INI yang sudah dibuat. `docs/POLA_KERJA_DAN_BUG.md` (versi lama,
> gabungan aturan + semua riwayat bug) **masih ada di repo untuk sementara** sebagai sumber
> kebenaran riwayat bug — belum dihapus/dipecah lebih lanjut. Sesi berikutnya perlu:
> 1. Ekstrak riwayat bug Workspace/Sidebar dari `POLA_KERJA_DAN_BUG.md` → `BUG_WORKSPACE_SIDEBAR.md`
> 2. Ekstrak riwayat bug lainnya → `BUG_HISTORY.md`
> 3. Setelah dipastikan semua konten sudah tersalin, hapus `POLA_KERJA_DAN_BUG.md`
> 4. Update `docs/SUMMARY.md` bagian "Struktur Dokumentasi" untuk menunjuk ke file-file baru
>
> **Last updated:** 2026-08-30 (tambah 2 aturan baru di §3 — pelajaran dari "Duplikasi Workflow Transition Round 4", lihat `docs/WORKFLOW.md §5`)

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

### B. `/desk/nexthd` — Workspace Page (Dashboard: Number Card & Shortcut Card)

Dikontrol oleh **`tabWorkspace`** (kolom `content`, JSON berisi urutan blok yang dirender) dan
file `nexthd/next_helpdesk/workspace/<nama_scrub>/<nama_scrub>.json`.

> ⚠️ **JANGAN** generate `content` sebagai string literal dengan escape manual.
> **SELALU** build sebagai Python dict/list lalu `json.dumps()` sekali.
> Double-escape akan menyebabkan `SyntaxError` di browser.

**Workspace baru WAJIB dibuat lewat UI (New Workspace), bukan insert langsung ke DB via `bench console`.**
Kalau terlanjur dibuat via script, fix-nya: pastikan `developer_mode=1`, lalu panggil `doc.save()`
sekali secara manual (bukan hanya insert) untuk memaksa Frappe menulis file fixture-nya. (Detail
kronologi kasus nyata: `BUG_WORKSPACE_SIDEBAR.md`, sesi 27 Agustus)

> ⚠️ **PENTING:** memanggil `doc.save()` pada `Workspace` (misalnya untuk memperbaiki baris
> `Workspace.links` yang rusak) bisa memicu efek samping tak terduga pada `Workspace Sidebar Item`
> — lihat catatan baru di §C poin 2 & 3 di bawah soal `Workspace Sidebar.standard` DAN `.app`
> (keduanya harus dicek terpisah, salah satu benar tidak berarti keduanya benar) sebelum memanggil
> `doc.save()` pada Workspace mana pun yang punya item sidebar manual.

**Number Cards di workspace:**
- Buat dulu di `tabNumber Card` (via SQL)
- Isi `number_card_name` di `tabWorkspace Number Card` (kolom kunci: `number_card_name`, bukan `card_name`)

> ✅ **FIXED (2026-08-11):** Root cause: block `content` JSON workspace pakai `"type": "card"`
> dengan key `"card_name"` — SALAH. Frappe v16 butuh `"type": "number_card"` dengan key
> `"number_card_name"`. Type yang tidak dikenal di-skip diam-diam tanpa error.

**Shortcut Cards (DocType/Report) di dashboard — `tabWorkspace Shortcut`:**
- Tabel terpisah dari `tabWorkspace Link` (sidebar kiri, lihat §C di bawah) — dua-duanya
  `child table` dari `Workspace`, tapi `parentfield` beda (`shortcuts` vs `links`) dan
  fungsinya beda: `Workspace Shortcut` = kartu di badan dashboard, `Workspace Link` = daftar
  di sidebar kiri.
- Block content untuk memunculkan kartu shortcut: `{"type": "shortcut", "data": {"shortcut_name": "<label>", "col": N}}` — `shortcut_name` harus **persis sama** dengan kolom `label` di `tabWorkspace Shortcut`, kalau tidak match, kartu di-skip diam-diam (sama seperti number card).
- **Untuk `type = "Report"`, kolom `report_ref_doctype` WAJIB diisi** (DocType yang jadi rujukan report). Kalau kosong/`NULL`, Frappe kemungkinan besar gagal resolve report saat resolve config kartu, sehingga kartu **tidak ikut dirender** di dashboard — tidak ada error yang terlihat di UI atau log biasa.
- **Update `content` via SQL langsung TIDAK otomatis invalidate cache** — Frappe nge-cache konten Workspace di Redis per-app. Setelah `UPDATE tabWorkspace SET content=...` via SQL, WAJIB `bench clear-cache` + `bench clear-website-cache` (bukan cuma hard refresh browser) baru kartu baru muncul.
- **Kartu shortcut TIDAK otomatis muncul hanya karena row-nya ada di `tabWorkspace Shortcut`** — sama seperti Number Card, harus ada blok referensinya di `Workspace.content`.

### C. Sidebar Kiri — 4 Doctype Berlapis + Module Sidebar (Sistem ke-5, Terpisah Total)

1. **`Workspace.links` (child table `tabWorkspace Link`)** — daftar link "mentah" yang tersimpan
   sebagai bagian dari dokumen Workspace itu sendiri. Bertahan lewat `bench migrate` selama
   tersimpan di file fixture Workspace (lihat §B). **Ini BUKAN sumber langsung yang dirender ke
   sidebar** — mengedit `Workspace.links` saja TIDAK otomatis membuat item baru muncul di sidebar kiri.
   Baris di tabel ini juga divalidasi ketat oleh `doc.save()` Workspace (`link_type` wajib salah
   satu dari DocType/Page/Report, dan `link_to` divalidasi sesuai `link_type`-nya) — baris yang
   `link_type`-nya kosong/tidak valid akan membuat `doc.save()` Workspace **gagal total** dengan
   `ValidationError: Link Type must be set first`.
2. **`Workspace Sidebar` (dokumen terpisah, 1 per workspace/app, contoh: dokumen bernama "NextHD")**
   — **inilah yang benar-benar dibaca untuk merender sidebar kiri.** Field pentingnya:
   - `app` — harus terisi nama app (`nexthd`), kalau kosong file fixture TIDAK akan ter-export.
     **Catatan penting:** field ini bisa kosong (`None`) untuk Workspace Sidebar yang dibuat
     lebih baru meski `standard` sudah benar — **kedua field (`app` DAN `standard`) harus dicek
     terpisah**, jangan asumsikan salah satu benar berarti keduanya benar.
   - `standard` — harus `1` agar `export_sidebar()` mau menulis file **dan** agar item sidebar
     manual (yang ditambah lewat UI, bukan auto-generate dari `Workspace.links`) tidak rawan
     tersapu saat ada proses lain (mis. `doc.save()` pada Workspace) yang memicu regenerasi.
   - Item-itemnya disimpan di child table **`Workspace Sidebar Item`** (lihat poin 3).
3. **`Workspace Sidebar Item`** (child table dari `Workspace Sidebar`) — daftar item aktual yang
   dirender di sidebar. Ini yang di-generate otomatis dari `Workspace.links` **untuk link
   bertipe DocType/Workspace**, TAPI **link bertipe "Report" TIDAK ikut ter-auto-generate**
   ke sini (Frappe v16 by design — jumlah item di sini normalnya lebih sedikit dari
   `Workspace.links`, selisihnya persis jumlah link Report — bukan bug).
   - **Cara resmi menambah SATU item baru ke sidebar:** lewat UI, klik ikon **panah ke bawah di
     KIRI ATAS** halaman Workspace (⚠️ BUKAN titik tiga "⋯" di kanan atas — dua menu berbeda)
     **→ Edit Sidebar**.
   - **Cara aman menambah BANYAK item sekaligus (via script, bukan klik satu-satu di UI):**
     `doc = frappe.get_doc("Workspace Sidebar", "<nama>")`, lalu `doc.append("items", {...})`
     untuk tiap item, lalu `doc.save(ignore_permissions=True)`. Pola ini setara dengan tombol UI
     "Edit Sidebar" (bukan raw SQL langsung ke `tabWorkspace Sidebar Item`), sehingga idx/validasi
     otomatis benar dan fixture ter-export. **Penting:** ini `doc.save()` pada dokumen
     **`Workspace Sidebar`**, BUKAN pada `Workspace` — risiko regresi jauh lebih rendah karena
     beda doctype dari yang pernah menyebabkan insiden penghapusan item manual.
4. **`tabWorkspace Shortcut`** — **bukan bagian sidebar sama sekali**, ini kartu dashboard
   (lihat §B). Jangan disamakan hanya karena sama-sama "shortcut"-nya Workspace.
5. **"Module Sidebar" — SISTEM TERPISAH TOTAL, bukan bagian dari 4 lapisan di atas.** Ini yang
   muncul otomatis (sidebar pendek/berbeda) saat membuka halaman **Report atau DocType**
   (`/desk/query-report/...`, list DocType, dll) — BUKAN halaman Workspace. Karakteristik penting:
   - **Auto-generate secara REAL-TIME**, bukan dari file/dokumen tersimpan — dihitung ulang setiap
     kali halaman dibuka, dari kombinasi semua `Workspace`+`DocType`+`Report` yang punya
     `module` sama dengan DocType/Report yang sedang dibuka.
   - **TIDAK ADA file fixture untuk ini, TIDAK BISA diedit/ditambahkan** kecuali override kode
     inti Frappe (berisiko tinggi terhadap update Frappe di masa depan).
   - **Ini adalah known limitation Frappe v16** (dikonfirmasi via GitHub Issue #36317 dan forum
     resmi) — sidebar Workspace lengkap memang didesain HANYA tampil di halaman Workspace itu
     sendiri, otomatis berganti ke Module Sidebar begitu masuk halaman DocType/Report.
   - **Sempat salah diduga sebagai "Route History"** (riwayat navigasi user) — sudah dicek via
     query `tabRoute History` dan terbukti TIDAK cocok. Bukan riwayat navigasi.
   - **Keputusan project (30 Agustus 2026):** dibiarkan apa adanya, tidak dikejar untuk diperbaiki
     — konsisten dengan limitasi platform yang sudah dikonfirmasi. Kompensasi yang sudah ada:
     breadcrumb 2-level ("NextHD / <Nama Report>") di tiap file `.js` report, supaya minimal
     1 klik bisa balik ke dashboard NextHD dari halaman report manapun.

**⚠️ JEBAKAN LOKASI FILE FIXTURE `Workspace Sidebar` (SANGAT PENTING):**

File fixture untuk `Workspace Sidebar` **TIDAK** disimpan di dalam folder module seperti
Workspace biasa (`next_helpdesk/workspace_sidebar/...`). Fungsi `create_directory_on_app_path("workspace_sidebar", app)`
di controller Frappe menulis **langsung di root app**, tanpa folder module:

```
✅ BENAR (lokasi aktif yang benar-benar dibaca & terus di-update):
nexthd/nexthd/workspace_sidebar/<judul_scrub>.json

❌ SALAH (kalau ada file di sini, itu FILE USANG — hapus, jangan diedit):
nexthd/nexthd/next_helpdesk/workspace_sidebar/<judul_scrub>.json
```

**Selalu verifikasi kedua lokasi** kalau menemukan situasi "sudah export tapi file tidak berubah".

### D. Aturan Fixtures — WAJIB

`bench migrate` akan hapus Desktop Icon dan Workspace Sidebar yang tidak ada di fixtures. Selalu export setelah perubahan:

```bash
bench --site desk.ciptamebel.co.id export-fixtures --app nexthd
```

**Catatan:** `export-fixtures --app nexthd` **TIDAK menyentuh** doctype `Workspace`
maupun `Workspace Sidebar` sama sekali (hanya meng-export Workflow, Desktop Icon, Client Script,
Property Setter, DocField, Web Form, Number Card). Untuk kedua doctype ini, export file
fixture-nya HANYA terjadi lewat `doc.save()` resmi (trigger `on_update()`/`before_save()`
masing-masing controller) — bukan lewat `export-fixtures`.

> ⚠️ **Dua fixture yang menyentuh child table yang sama TIDAK BOLEH aktif bersamaan** — lihat
> aturan baru di §3 (tabel Aturan Wajib Lainnya) untuk detail dan contoh kasus nyata.

### E. Web Worker vs Terminal — `PATH` Environment Terbatas

Kode Python yang dieksekusi dari klik tombol UI (proses web Frappe/gunicorn) **TIDAK** punya
`PATH` environment selengkap sesi terminal SSH biasa. Memanggil binary shell seperti `bench`
lewat `subprocess.run(["bench", ...])` di dalam kode yang jalan dari request web akan gagal
dengan `FileNotFoundError: [Errno 2] No such file or directory: 'bench'`, meski perintah yang
sama persis berjalan normal kalau dicoba manual di terminal. **Untuk kebutuhan seperti backup,
selalu panggil fungsi internal Python-nya langsung** (mis. `frappe.utils.backups.new_backup()`),
bukan shell out ke `bench`.

---

## 2. Workspace Dashboard — Konfigurasi Saat Ini (Status 30 Agustus 2026)

```
Workspace "NextHD" — Body Dashboard:
  [Operasional]
    Shortcuts: New Ticket, All Tickets, NextHD Problem, NextHD Change Request

  [Statistik Tiket]
    Number Cards (6): Tiket Baru, Tiket Sedang Dikerjakan, Menunggu User,
    Tiket Selesai Bulan Ini, Tiket Prioritas Kritis, Problem Terbuka

  [Tiket Terbaru]
    Quick Lists (2): Open Tickets, Critical Tickets

  [Konfigurasi]
    Shortcuts: NextHD Settings, NextHD SLA Policy, NextHD Team, NextHD Category, NextHD Photo

  [Laporan]
    Shortcuts (Report): Tiket per Bulan, Tiket per Agent, Tiket per Prioritas,
    Tiket per Kategori, SLA Compliance Bulanan, Aset Bermasalah

  [Admin]
    Shortcuts: Reset Data Demo

Sidebar kiri Workspace "NextHD" (17 item):
  Dashboard, NextHD Ticket, NextHD Problem, NextHD Change Request, NextHD Known Error,
  NextHD Photo, NextHD Asset, NextHD Asset Category, NextHD Team, NextHD Category,
  NextHD SLA Policy, NextHD Business Hours, NextHD Holiday, NextHD Service Catalog,
  NextHD User Profile, NextHD Settings, NextHD Reporting (→ link ke Workspace "NextHD Report")

Sidebar kiri Workspace "NextHD Report" (8 item, diperkaya 30 Agustus):
  Dashboard (→ NextHD), NextHD Report (→ dirinya sendiri), NextHD Ticket, NextHD Problem,
  NextHD Change Request, NextHD Known Error, NextHD Asset, NextHD Asset Category
  (Laporan/Report sengaja TIDAK ditambahkan ke sidebar ini — 11 shortcut report sudah
  otomatis tampil di body/dashboard Workspace "NextHD Report" begitu dibuka)

Module Sidebar (muncul di halaman Report/DocType, BUKAN Workspace):
  Auto-generate dari field module='Next Helpdesk' — TIDAK bisa diedit, dibiarkan apa adanya
  (lihat §1.C poin 5)
```

---

## 3. Aturan Wajib Saat Coding/Debug

### Pola Console — BENAR vs SALAH

**✅ BENAR — Selalu pakai file script + redirect, indentasi 4-spasi lalu convert ke tab:**
```bash
# Langkah 1: tulis ke file dengan indentasi 4-spasi (aman lewat paste/clipboard)
cat > /home/it/nama_script.py << 'EOF'
def main_check():
    results = []
    for item in list_data:
        results.append(str(item))
    print("\n".join(results))
    print("DONE")

main_check()
EOF

# Langkah 2: convert indentasi 4-spasi jadi tab di sisi server
sed -i 's/^    /\t/' /home/it/nama_script.py

# Langkah 3: jalankan via redirect
bench --site desk.ciptamebel.co.id console < /home/it/nama_script.py
```

**❌ SALAH — Jangan paste langsung ke console interaktif:**
IPython akan error `IndentationError` atau loop tidak jalan sama sekali.

**❌ SALAH — Jangan pakai tab langsung di heredoc script:**
Karakter tab kerap **hilang saat proses copy-paste** dari chat ke terminal, menyebabkan
`IndentationError: expected an indented block`. Tulis dengan 4-spasi dulu, baru convert ke
tab via `sed` di server.

**❌ SALAH — Jangan pakai nama fungsi `run`:**
IPython punya automagic `%run` yang bisa "menangkap" pemanggilan `run()` sebagai magic command.
Selalu pakai nama fungsi lain, misal `main_check()`, `main_test()`, dst.

**❌ SALAH — Jangan tulis skrip Python bercabang (`if`/`for`) langsung ke `bench console` interaktif:**
Untuk skrip yang perlu dijalankan sekali di server, lebih andal pakai `bench execute <module.fungsi>`
dibanding paste multi-baris ke `bench console`.

### Tabel Aturan Wajib Lainnya

| Aturan | Penjelasan |
|---|---|
| `continue`/`break` dalam loop di console | Error. Gunakan `if/else` sebagai gantinya |
| **Baris kosong di dalam blok manapun** (for/if/def) di script console | **Error/perilaku tidak terduga.** IPython nganggap baris kosong = akhir blok. Hindari baris kosong di DALAM blok — boleh ada ANTAR blok top-level saja |
| **Loop/logic kompleks di console** | **Selalu bungkus dalam 1 fungsi** (`def main_check(): ...` lalu panggil terpisah) — IPython baca seluruh body sebagai 1 unit |
| **Karakter tab hilang saat paste ke terminal** | Tulis heredoc dengan indentasi 4-spasi, lalu jalankan `sed -i 's/^    /\t/' nama_file.py` di server sebelum eksekusi |
| **Nama fungsi `run`** | Bentrok dengan IPython magic `%run` — pakai nama lain seperti `main_check()` |
| **Import via `from module import nama_fungsi`** | Kadang tidak ter-bind dengan benar di scope IPython saat dipiped dari file. **Fix aman:** taruh import DI DALAM fungsi, bukan di level top file |
| `doc.save()` | Selalu gagal di production **kecuali `developer_mode=1` sedang aktif** atau untuk `doc.insert()` pada custom DocType baru. Untuk update data biasa, tetap pakai SQL UPDATE + `frappe.db.commit()`. `doc.save()` pada `Workspace` juga menjalankan validasi penuh child table `links` — pastikan semua baris `Workspace.links` valid sebelum memanggil ini |
| **Field Link yang wajib diisi (`reqd=1`)** | Cek dulu via `frappe.get_meta(doctype)` — filter `f.reqd or f.fieldtype == "Link"` |
| **Field Link ke master doctype** | Master record harus **sudah ada duluan** sebelum insert dokumen yang mereferensikannya |
| Perubahan DB langsung | Export fixture → git commit → git push |
| `bench migrate` | Bisa hapus Desktop Icon dan Workspace Sidebar yang tidak di fixtures |
| Cek schema tabel | `DESCRIBE tabNama` dulu sebelum INSERT |
| **Fixtures export sebelum data ada** | `bench export-fixtures` membaca DARI database — kalau dijalankan saat tabel masih kosong, fixture JSON yang dihasilkan JUGA kosong (`[]`) dan akan menimpa file manual yang lengkap. Command ini juga sama sekali tidak menyentuh `Workspace`/`Workspace Sidebar` |
| MariaDB subquery | Versi lama tidak support `LIMIT` di subquery `IN` |
| JSON content workspace | Generate via `json.dumps()` Python, BUKAN string literal manual |
| Workspace number card block | Type HARUS `"number_card"` (bukan `"card"`), key HARUS `"number_card_name"` (bukan `"card_name"`) |
| **Workspace shortcut block bertipe Report** | Kolom `report_ref_doctype` di `tabWorkspace Shortcut` WAJIB diisi, kalau tidak kartu di-skip diam-diam dari dashboard |
| **Update `Workspace.content` via SQL langsung** | Tidak auto-invalidate cache Redis — WAJIB `bench clear-cache` + `bench clear-website-cache` setelahnya, baru hard refresh browser |
| **Workspace baru dibuat via insert manual/script (bukan UI)** | File fixture JSON-nya TIDAK otomatis ter-generate. Selalu buat Workspace baru lewat UI, atau kalau terlanjur via script, paksa `doc.save()` manual dengan `developer_mode=1` aktif |
| **Menambah SATU item baru ke sidebar kiri** | HARUS lewat UI (ikon **panah ke bawah di kiri atas** halaman Workspace → **Edit Sidebar** — BUKAN titik tiga "⋯" kanan atas), BUKAN hanya mengedit `Workspace.links` |
| **Menambah BANYAK item sekaligus ke sidebar kiri** | Pakai script: `doc = frappe.get_doc("Workspace Sidebar", "<nama>")` + `doc.append("items", {...})` per item + `doc.save(ignore_permissions=True)` — setara jalur resmi UI, lebih aman daripada raw SQL, dan risiko regresi jauh lebih rendah dibanding `doc.save()` pada `Workspace` |
| **`Workspace Sidebar.app`/`.standard` kosong atau salah** | `export_sidebar()` hanya menulis file kalau `app` terisi nama app DAN `standard=1` DAN `developer_mode=1`. **Kedua field harus dicek terpisah** — `app` bisa kosong (`None`) meski `standard` sudah benar, terutama untuk Workspace Sidebar yang dibuat belakangan. `standard=0` juga membuat item sidebar manual rawan **hilang** (bukan cuma "tidak ter-export") kalau ada proses lain (mis. `doc.save()` pada Workspace induk) yang memicu regenerasi |
| **Menyembunyikan Workspace (`is_hidden=1`) yang diakses lewat sidebar link biasa** | JANGAN. Akan membuat link tersebut hilang total dari sidebar |
| `Workflow State` (fixtures) | Tidak punya kolom `workflow` — jangan filter berdasarkan itu. Master global, TIDAK masuk fixtures per-app |
| Role assignment ke user | Via UI (User → Roles), TIDAK perlu SQL |
| **Workflow State → `Update Field`** | Jangan isi sama dengan `workflow_state_field` kecuali `Update Value` juga diisi benar — kalau kosong, status akan tertimpa `None` setelah transisi. Lihat `WORKFLOW.md` |
| **`bench console` beda sesi = beda state Python** | Import/variable dari sesi sebelumnya TIDAK terbawa — harus import ulang |
| **Dua jalur ke satu state yang butuh side-effect** | Hapus transisi workflow polos yang bisa mencapai state itu tanpa lewat tombol/method custom |
| **Property Setter — filter fixture** | Tidak punya kolom `app`. Filter yang benar: `doc_type` (`=` atau `LIKE`), bukan `app =` |
| **DocField baru via raw SQL INSERT ke `tabDocField`** | **Wajib** diikuti `ALTER TABLE \`tabNamaDocType\` ADD COLUMN` manual. Insert ke `tabDocField` cuma daftar metadata, TIDAK otomatis membuat kolom fisik di tabel data |
| **Field/meta baru tidak muncul di UI meski data DB sudah benar** | Coba `bench clear-cache` + `bench clear-website-cache` + `bench restart` dulu sebelum curiga bug struktur data |
| **`bench --site X mariadb -e "..."` tiap panggilan buka KONEKSI BARU** | `SET SQL_SAFE_UPDATES=0` di command `-e` terpisah TIDAK terbawa ke command `-e` berikutnya. WAJIB gabung dalam satu koneksi: `bench --site X mariadb << 'SQL' ... SQL` |
| **`bench migrate` — urutan wajib saat menambah kolom BARU lalu langsung mengisi datanya** | Migrate dulu (agar kolom fisik tercipta di DB) BARU UPDATE data. Kalau dibalik → `ERROR 1054 Unknown column` |
| **`__pycache__` basi setelah edit file `.py`** | Kadang perubahan logic Python tidak langsung kepakai meski file sudah diedit dan `bench restart` dijalankan. Hapus `find <app_path> -type d -name "__pycache__" -exec rm -rf {} +` lalu restart lagi |
| **Selalu verifikasi isi file DI DISK dengan `grep`/`cat` sebelum asumsi kode sudah ter-replace** | Jangan percaya catatan dokumentasi 100% — selalu cross-check langsung ke file (dan pastikan path-nya benar) sebelum lanjut debug |
| **Counter `tabSeries` bisa TIDAK SINKRON dari data fisik** | Kalau ketemu `DuplicateEntryError` saat insert padahal nomor "terlihat aman", cek `SELECT MAX(...) FROM tabDocType` vs `SELECT current FROM tabSeries WHERE name = 'PREFIX-'` — kalau beda, sinkronkan |
| **`frappe.db.get_single_value(doctype, field)` HANYA jalan untuk Single DocType** | Cek dulu `frappe.db.get_value("DocType", "<nama>", "issingle")` — kalau `0`, pakai `frappe.db.get_value(doctype, {}, field)` sebagai gantinya |
| **`frappe.logger` vs `frappe.logger()`** | `frappe.logger` adalah fungsi, BUKAN objek logger — harus dipanggil dulu `frappe.logger()` baru bisa `.info(...)`/`.error(...)` |
| **DocType dengan `"permissions": []` kosong total di JSON** | DocType HANYA bisa diakses Administrator — semua role lain kena `PermissionError`/404. Selalu tambahkan minimal 1 baris permission untuk setiap DocType baru |
| **Pola aman untuk logic side-effect di `on_update()`** | Gunakan `self.db_set(...)` / `frappe.db.set_value(...)` langsung, BUKAN `self.save()`, supaya tidak memicu infinite recursion |
| **Report shortcut URL selalu `/desk/query-report/<Nama Report>`** | Ini route standar Frappe, tidak bisa diubah jadi `/desk/nexthd/...` tanpa menulis ulang report sebagai custom Page |
| **Memanggil fungsi backend asli untuk diagnosa "kenapa X tidak muncul di UI"** | Cari fungsi resmi yang benar-benar dipanggil UI, panggil manual via console, baru simpulkan di lapisan mana masalahnya |
| **Kode yang jalan dari klik tombol UI (web worker) TIDAK punya `PATH` selengkap terminal SSH** | Untuk kebutuhan yang biasanya lewat CLI (backup, dll.) dari kode yang jalan di request web, selalu panggil fungsi Python internal-nya langsung |
| **Field reference balik many-to-many disimpan sebagai field tunggal** | JANGAN simpan referensi balik sebagai field `reference_doctype`+`reference_name` tunggal kalau 1 record bisa dipakai ulang di >1 dokumen. Pakai `get_dashboard_data()` (badge Connections, real-time dari child table) sebagai gantinya |
| **Sebelum menghapus field DocType yang dicurigai duplikat/usang, WAJIB 2 langkah verifikasi dulu** | (1) verifikasi backfill — cek SEMUA record existing sudah punya data sama di struktur baru; (2) cek referensi — grep di Property Setter, Client Script, Report, Print Format |
| **Child table (Table fieldtype) TIDAK BISA dipakai di `search_fields` Property Setter** | `search_fields` cuma bisa baca kolom di tabel utama DocType, bukan child table |
| **`git add .` bisa membundel perubahan tak terkait ke commit yang sama** | Selalu `git status`/`git diff` dulu sebelum `git add .` + commit kalau server punya kemungkinan perubahan menumpuk dari sesi/pekerjaan lain |
| **Baris `Workspace.links` dengan `link_type` kosong/tidak valid memblokir `doc.save()` Workspace total** | `link_type` hanya boleh salah satu dari `DocType`/`Page`/`Report`. Kalau baris semacam ini ditemukan dan tidak ada tujuan valid, opsi teraman adalah **menghapus baris tersebut** |
| **`doc.save()` pada Workspace bisa memicu regenerasi sidebar yang menyapu item manual, kalau `Workspace Sidebar.standard=0`** | WAJIB cek & set `standard=1` dulu sebelum memanggil `doc.save()` pada Workspace yang sidebar-nya sudah berisi item manual, dan verifikasi ulang isi sidebar setelah setiap `doc.save()` |
| **Module Sidebar (sidebar pendek di halaman Report/DocType) BUKAN file/dokumen, tidak bisa diedit** | Auto-generate real-time dari field `module`. Bukan Route History. Known limitation Frappe v16 (GitHub Issue #36317) — dibiarkan apa adanya, jangan coba diperbaiki lagi tanpa permintaan eksplisit |
| **Dua fixture yang menyentuh child table yang sama TIDAK BOLEH aktif bersamaan** | Kalau salah satu sumber (mis. fixture parent dengan child rows ter-embed) **tidak punya field `name` eksplisit** di child rows-nya, Frappe akan hapus-sisip ulang baris itu (nama baru) tiap `bench migrate`. Sementara itu, fixture LAIN yang menyentuh child table yang sama tapi berbasis `name` eksplisit akan **menambah** baris di atasnya, bukan menimpanya — hasilnya duplikasi berlipat tiap migrate. Sebelum mendaftarkan fixture baru untuk sebuah child table, cek dulu apakah child table itu sudah ter-embed di fixture parent lain. Kasus nyata: fixture `Workflow` (transitions ter-embed) + fixture `Workflow Transition` terpisah — lihat `docs/WORKFLOW.md §5` "Duplikasi Round 4" |
| **Guard/validasi yang menolak `bench migrate` BELUM TENTU false-positive** | Sebelum menambah pengecualian "skip validasi saat `frappe.flags.in_migrate`/`in_install`/`in_import`" pada sebuah hook, pastikan dulu secara langsung (cek data di DB) apakah kondisi yang ditolak guard itu memang seharusnya tidak terjadi. Menambah exception tanpa verifikasi ini bisa menutupi bug nyata alih-alih menyelesaikannya — guard akhirnya "diam" sementara masalah tetap terjadi tanpa terdeteksi. Kasus nyata: `docs/WORKFLOW.md §5` "Duplikasi Round 4" |

---

*Dokumen ini dikelola oleh Claude. Update terakhir: 2026-08-30. Riwayat bug per sesi ada di
`docs/BUG_WORKSPACE_SIDEBAR.md` dan `docs/BUG_HISTORY.md` (belum dibuat, pending sesi berikutnya
— sementara masih di `docs/POLA_KERJA_DAN_BUG.md` versi lama).*
