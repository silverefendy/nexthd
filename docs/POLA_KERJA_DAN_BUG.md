# NextHD — Pola Kerja & Riwayat Bug

> Frappe quirks, aturan wajib saat coding/debug, dan riwayat bug per sesi.
> File ini yang paling sering bertambah tiap sesi baru.
>
> **Last updated:** 2026-08-27

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
Kasus nyata 27 Agustus (lihat §4): Workspace "NextHD Report" dibuat via script insert manual ke `tabWorkspace`
— datanya valid 100% tapi file fixture JSON-nya **tidak pernah ter-generate otomatis**, karena hook
`.save()`/`on_update()` yang biasanya memicu export hanya jalan lewat jalur simpan resmi Frappe. Kalau
terlanjur dibuat via script, fix-nya: pastikan `developer_mode=1`, lalu panggil `doc.save()` sekali secara
manual (bukan hanya insert) untuk memaksa Frappe menulis file fixture-nya.

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
- **Untuk `type = "Report"`, kolom `report_ref_doctype` WAJIB diisi** (DocType yang jadi rujukan report). Kalau kosong/`NULL`, Frappe kemungkinan besar gagal resolve report saat resolve config kartu, sehingga kartu **tidak ikut dirender** di dashboard — tidak ada error yang terlihat di UI atau log biasa. Lihat bug session 2026-08-26.
- **Update `content` via SQL langsung TIDAK otomatis invalidate cache** — Frappe nge-cache konten Workspace di Redis per-app. Setelah `UPDATE tabWorkspace SET content=...` via SQL, WAJIB `bench clear-cache` + `bench clear-website-cache` (bukan cuma hard refresh browser) baru kartu baru muncul.

### C. Sidebar Kiri — 4 Doctype Berlapis (KOREKSI 27 Agustus — baca sebelum edit sidebar apapun)

> ⚠️ **Koreksi dari catatan versi sebelumnya:** paragraf lama menyebut "3 tabel", tapi hasil
> investigasi 27 Agustus menemukan lapisan ke-4 (`Workspace Sidebar` / `Workspace Sidebar Item`)
> yang justru merupakan **sumber sebenarnya** yang dirender ke sidebar kiri — bukan `Workspace.links`
> secara langsung seperti anggapan sebelumnya. Detail lengkap kronologi ada di §4, sesi 27 Agustus.

1. **`Workspace.links` (child table `tabWorkspace Link`)** — daftar link "mentah" yang tersimpan
   sebagai bagian dari dokumen Workspace itu sendiri. Bertahan lewat `bench migrate` selama
   tersimpan di file fixture Workspace (lihat §B). **Ini BUKAN sumber langsung yang dirender ke
   sidebar** — mengedit `Workspace.links` saja TIDAK otomatis membuat item baru muncul di sidebar kiri.
2. **`Workspace Sidebar` (dokumen terpisah, 1 per workspace/app, contoh: dokumen bernama "NextHD")**
   — **inilah yang benar-benar dibaca untuk merender sidebar kiri.** Field pentingnya:
   - `app` — harus terisi nama app (`nexthd`), kalau kosong file fixture TIDAK akan ter-export.
   - `standard` — harus `1` agar `export_sidebar()` mau menulis file. Kalau `0`, perubahan hanya
     tersimpan di database dan akan hilang praktiknya (tidak permanen lintas deploy).
   - Item-itemnya disimpan di child table **`Workspace Sidebar Item`** (lihat poin 3).
3. **`Workspace Sidebar Item`** (child table dari `Workspace Sidebar`) — daftar item aktual yang
   dirender di sidebar. Ini yang di-generate otomatis dari `Workspace.links` **untuk link
   bertipe DocType/Workspace**, TAPI **link bertipe "Report" TIDAK ikut ter-auto-generate**
   ke sini (Frappe v16 by design, dikonfirmasi 27 Agustus — jumlah item di sini normalnya lebih
   sedikit dari `Workspace.links`, selisihnya persis jumlah link Report — bukan bug, jangan
   "diperbaiki" lagi tanpa bukti baru).
   - **Cara resmi menambah item baru ke sidebar:** lewat UI, klik **"⋯" (titik tiga di header
     workspace) → Edit Sidebar**, lalu tambah item baru di sana. Ini akan menyimpan langsung ke
     `Workspace Sidebar Item` — TIDAK perlu (dan tidak akan otomatis tersinkron) hanya dengan
     mengedit `Workspace.links`.
4. **`tabWorkspace Shortcut`** — **bukan bagian sidebar sama sekali**, ini kartu dashboard
   (lihat §B). Jangan disamakan hanya karena sama-sama "shortcut"-nya Workspace.

**⚠️ JEBAKAN LOKASI FILE FIXTURE `Workspace Sidebar` (ditemukan 27 Agustus, sangat penting):**

File fixture untuk `Workspace Sidebar` **TIDAK** disimpan di dalam folder module seperti
Workspace biasa (`next_helpdesk/workspace_sidebar/...`). Fungsi `create_directory_on_app_path("workspace_sidebar", app)`
di controller Frappe menulis **langsung di root app**, tanpa folder module:

```
✅ BENAR (lokasi aktif yang benar-benar dibaca & terus di-update):
nexthd/nexthd/workspace_sidebar/<judul_scrub>.json

❌ SALAH (kalau ada file di sini, itu FILE USANG — hapus, jangan diedit):
nexthd/nexthd/next_helpdesk/workspace_sidebar/<judul_scrub>.json
```

Kasus nyata: file di lokasi salah (`next_helpdesk/workspace_sidebar/nexthd.json`) sempat ada di
repo sejak sesi-sesi awal proyek dan tidak pernah diperbarui lagi — sementara file yang benar-benar
aktif (`nexthd/nexthd/workspace_sidebar/nexthd.json`) terus berubah setiap `export_sidebar()`
dipanggil. Ini menyebabkan debugging berputar-putar cukup lama karena semua orang (termasuk Claude)
mengira file yang di dalam `next_helpdesk/` itu sumber kebenarannya. **Selalu verifikasi kedua lokasi**
kalau menemukan situasi "sudah export tapi file tidak berubah".

> ⚠️ **Jangan tertukar keempatnya.** Kasus nyata 26 Agustus: perubahan sesi ini dilakukan di
> `tabWorkspace Shortcut` (kartu dashboard) untuk fitur Foto (DocType) dan 6 Report — ini
> **terpisah total** dari pekerjaan item AA (25 Agustus, sidebar kiri via `Workspace.links`)
> yang migrate-nya belum dijalankan. Keduanya boleh berjalan paralel tanpa saling mengganggu,
> tapi harus jelas dokumentasi/perubahan mana untuk sistem yang mana.

### D. Aturan Fixtures — WAJIB

`bench migrate` akan hapus Desktop Icon dan Workspace Sidebar yang tidak ada di fixtures. Selalu export setelah perubahan:

```bash
bench --site desk.ciptamebel.co.id export-fixtures --app nexthd
```

**Catatan 27 Agustus:** `export-fixtures --app nexthd` **TIDAK menyentuh** doctype `Workspace`
maupun `Workspace Sidebar` sama sekali (dikonfirmasi dari output command — hanya meng-export
Workflow, Desktop Icon, Client Script, Property Setter, DocField, Web Form, Number Card). Untuk
kedua doctype ini, export file fixture-nya HANYA terjadi lewat `doc.save()` resmi (trigger
`on_update()`/`before_save()` masing-masing controller) — bukan lewat `export-fixtures`. Jangan
mengandalkan `export-fixtures` untuk mengamankan perubahan Workspace/Workspace Sidebar.

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
    Shortcuts: NextHD Settings, NextHD SLA Policy, NextHD Team, NextHD Category, NextHD Photo (ditambah 26 Agustus)

  [Laporan] (ditambah 26 Agustus)
    Shortcuts (Report, report_ref_doctype terisi): Tiket per Bulan, Tiket per Agent,
    Tiket per Prioritas, Tiket per Kategori, SLA Compliance Bulanan (ref NextHD Ticket),
    Aset Bermasalah (ref NextHD Asset)

Sidebar kiri (Workspace Sidebar Item, ditambah 27 Agustus):
  "NextHD Reporting" → link ke Workspace "NextHD Report" (berisi 11 shortcut Detail Report Lengkap:
  Tiket, Aset, Known Error, Problem, Change Request)
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
Karakter tab kerap **hilang saat proses copy-paste** dari chat ke terminal (tergantung terminal/emulator), menyebabkan `IndentationError: expected an indented block`. Lihat entri `sed` di §3 tabel bawah untuk solusinya — tulis dengan 4-spasi dulu, baru convert ke tab via `sed` di server.

**❌ SALAH — Jangan pakai nama fungsi `run`:**
IPython punya automagic `%run` yang bisa "menangkap" pemanggilan `run()` sebagai magic command, bukan pemanggilan fungsi Python biasa — menghasilkan error aneh `Exception: File '()' not found`. Selalu pakai nama fungsi lain, misal `main_check()`, `main_test()`, dst.

### Tabel Aturan Wajib Lainnya

| Aturan | Penjelasan |
|---|---|
| `continue`/`break` dalam loop di console | Error. Gunakan `if/else` sebagai gantinya |
| **Baris kosong di dalam blok manapun** (for/if/def) di script console | **Error/perilaku tidak terduga.** IPython nganggap baris kosong = akhir blok. Hindari baris kosong di DALAM blok — boleh ada ANTAR blok top-level saja |
| **Loop/logic kompleks di console** | **Selalu bungkus dalam 1 fungsi** (`def main_check(): ...` lalu panggil terpisah) — IPython baca seluruh body sebagai 1 unit. Berlaku juga untuk banyak fungsi helper terpisah — kalau saling panggil, gabung semua jadi SATU fungsi tunggal, jangan pecah jadi beberapa `def` di level top |
| **Karakter tab hilang saat paste ke terminal** | Tulis heredoc dengan indentasi 4-spasi (aman lewat clipboard), lalu jalankan `sed -i 's/^    /\t/' nama_file.py` di server sebelum eksekusi, supaya hasil akhirnya tetap tab murni seperti yang dibutuhkan IPython |
| **Nama fungsi `run`** | Bentrok dengan IPython magic `%run` (automagic) — pakai nama lain seperti `main_check()` |
| **Import via `from module import nama_fungsi`** | Kadang tidak ter-bind dengan benar di scope IPython saat dipiped dari file (nama fungsi jadi `NameError` walau tanpa error saat import). **Fix aman:** taruh import DI DALAM fungsi (`from ... import ...` sebagai baris pertama body), bukan di level top file |
| `doc.save()` | Selalu gagal di production **kecuali `developer_mode=1` sedang aktif** (perlu untuk memicu export fixture Workspace/Workspace Sidebar — lihat §1.B & §1.C) atau untuk `doc.insert()` pada custom DocType baru yang memang perlu validasi Frappe. Untuk update data biasa tanpa kebutuhan trigger hook, tetap pakai SQL UPDATE + `frappe.db.commit()` |
| **Field Link yang wajib diisi (`reqd=1`)** | Cek dulu via `frappe.get_meta(doctype)` — filter `f.reqd or f.fieldtype == "Link"`. Contoh: `NextHD Ticket` butuh `subject` dan `requested_by` — kalau test insert via console lupa isi ini, akan kena `MandatoryError` meski `calculate_sla()` sendiri sudah terpanggil dan sukses |
| **Field Link ke master doctype** | Master record harus **sudah ada duluan** sebelum insert dokumen yang mereferensikannya |
| Perubahan DB langsung | Export fixture → git commit → git push |
| `bench migrate` | Bisa hapus Desktop Icon dan Workspace Sidebar yang tidak di fixtures |
| Cek schema tabel | `DESCRIBE tabNama` dulu sebelum INSERT |
| **Fixtures export sebelum data ada** | `bench export-fixtures` membaca DARI database — kalau dijalankan saat tabel masih kosong, fixture JSON yang dihasilkan JUGA kosong (`[]`) dan akan menimpa file manual yang lengkap. **Catatan 27 Agustus:** command ini juga sama sekali tidak menyentuh `Workspace`/`Workspace Sidebar` — lihat §1.D |
| MariaDB subquery | Versi lama tidak support `LIMIT` di subquery `IN` |
| JSON content workspace | Generate via `json.dumps()` Python, BUKAN string literal manual |
| Workspace number card block | Type HARUS `"number_card"` (bukan `"card"`), key HARUS `"number_card_name"` (bukan `"card_name"`) |
| **Workspace shortcut block bertipe Report** | Kolom `report_ref_doctype` di `tabWorkspace Shortcut` WAJIB diisi, kalau tidak kartu di-skip diam-diam dari dashboard (lihat §1.B) |
| **Update `Workspace.content` via SQL langsung** | Tidak auto-invalidate cache Redis — WAJIB `bench clear-cache` + `bench clear-website-cache` setelahnya, baru hard refresh browser |
| **Workspace baru dibuat via insert manual/script (bukan UI)** | File fixture JSON-nya TIDAK otomatis ter-generate — sidebar/dashboard bisa "kelihatan benar di database" tapi tidak pernah muncul di UI. Selalu buat Workspace baru lewat UI (New Workspace), atau kalau terlanjur via script, paksa `doc.save()` manual dengan `developer_mode=1` aktif (lihat §1.B & §4 sesi 27 Agustus) |
| **Menambah item baru ke sidebar kiri** | HARUS lewat UI "⋯ → Edit Sidebar", BUKAN hanya mengedit `Workspace.links`. Setelah itu, verifikasi file fixture `Workspace Sidebar` ter-update di LOKASI YANG BENAR: `nexthd/nexthd/workspace_sidebar/<judul>.json` (bukan di dalam folder `next_helpdesk/`, lihat §1.C) |
| **`Workspace Sidebar.app`/`.standard` kosong atau salah** | `export_sidebar()` hanya menulis file kalau `app` terisi nama app DAN `standard=1` DAN `developer_mode=1`. Cek ketiganya kalau file fixture tidak kunjung berubah meski `.save()` sudah dipanggil tanpa error |
| **Menyembunyikan Workspace (`is_hidden=1`) yang diakses lewat sidebar link biasa** | JANGAN. Pola `hidden=1` pada workspace pendukung lain (Ticket Center, Asset Center, dll.) punya mekanisme akses berbeda yang belum sepenuhnya dipahami — menerapkannya ke workspace baru yang diakses via link sidebar biasa akan membuat link tersebut hilang total dari sidebar (terverifikasi 27 Agustus) |
| `Workflow State` (fixtures) | Tidak punya kolom `workflow` — jangan filter berdasarkan itu. Master global, TIDAK masuk fixtures per-app |
| Role assignment ke user | Via UI (User → Roles), TIDAK perlu SQL |
| **Workflow State → `Update Field`** | Jangan isi sama dengan `workflow_state_field` kecuali `Update Value` juga diisi benar — kalau kosong, status akan tertimpa `None` setelah transisi. Lihat `WORKFLOW.md` |
| **`bench console` beda sesi = beda state Python** | Import/variable dari sesi sebelumnya TIDAK terbawa — harus import ulang |
| **Dua jalur ke satu state yang butuh side-effect** | Hapus transisi workflow polos yang bisa mencapai state itu tanpa lewat tombol/method custom |
| **Property Setter — filter fixture** | Tidak punya kolom `app`. Filter yang benar: `doc_type` (`=` atau `LIKE`), bukan `app =` |
| **DocField baru via raw SQL INSERT ke `tabDocField`** | **Wajib** diikuti `ALTER TABLE \`tabNamaDocType\` ADD COLUMN` manual. Insert ke `tabDocField` cuma daftar metadata, TIDAK otomatis membuat kolom fisik di tabel data — beda dari `doc.save()`/migrate yang auto-sync. Lupa langkah ini → error `Unknown column 'xxx' in 'INSERT INTO'` atau `'in SET'` saat field dipakai |
| **Field/meta baru tidak muncul di UI meski data DB sudah benar** | Coba `bench clear-cache` + `bench clear-website-cache` + `bench restart` dulu sebelum curiga bug struktur data. Sering kali murni cache boot info server, bukan masalah field/kolom. **Catatan 27 Agustus:** kalau sudah clear-cache + restart + Incognito browser TETAP tidak berubah, curigai dulu apakah memang ADA file fixture yang benar-benar dibaca di lokasi yang benar (lihat §1.C) sebelum curiga ke arah lain (Service Worker, dsb.) |
| **`bench --site X mariadb -e "..."` tiap panggilan buka KONEKSI BARU** | `SET SQL_SAFE_UPDATES=0` di command `-e` terpisah TIDAK terbawa ke command `-e` berikutnya (safe update mode akan error lagi). WAJIB gabung dalam satu koneksi: `bench --site X mariadb << 'SQL' ... SQL` |
| **`bench migrate` — urutan wajib saat menambah kolom BARU lalu langsung mengisi datanya** | Migrate dulu (agar kolom fisik tercipta di DB) BARU UPDATE data. Kalau dibalik → `ERROR 1054 Unknown column` |
| **`__pycache__` basi setelah edit file `.py`** | Kadang perubahan logic Python tidak langsung kepakai meski file sudah diedit dan `bench restart` dijalankan. Kalau hasil eksekusi masih mengikuti kode versi lama, hapus `find <app_path> -type d -name "__pycache__" -exec rm -rf {} +` lalu restart lagi |
| **Selalu verifikasi isi file DI DISK dengan `grep`/`cat` sebelum asumsi kode sudah ter-replace** | Kasus nyata (2026-08-20): sesi sebelumnya "mengaku" sudah menulis ulang `calculate_sla()`, tapi `grep` di sesi berikutnya membuktikan file masih versi lama (`add_to_date`, bukan `add_working_time`). Root cause: perubahan tidak pernah benar-benar tersimpan ke disk sesi sebelumnya. **Kasus serupa lagi 27 Agustus** dengan file fixture `Workspace Sidebar` — ternyata ada DUA file dengan nama sama di dua path berbeda, dan yang dicek selama ini adalah yang salah/usang. **Jangan percaya catatan dokumentasi 100% — selalu cross-check langsung ke file (dan pastikan path-nya benar) sebelum lanjut debug** |
| **Counter `tabSeries` bisa TIDAK SINKRON dari data fisik** | Kasus nyata (2026-08-20): `tabSeries` untuk `PRB-2608-` nyangkut di `current=2` padahal data fisik `NextHD Problem` sudah sampai `PRB-2608-0005` — insert baru selalu tabrakan `DuplicateEntryError`. Kemungkinan penyebab: insert manual/import yang tidak lewat jalur normal penomoran Frappe. **Kalau ketemu `DuplicateEntryError` saat insert padahal nomor "terlihat aman"**, cek dulu `SELECT MAX(...) FROM tabDocType` vs `SELECT current FROM tabSeries WHERE name = 'PREFIX-'` — kalau beda, sinkronkan `tabSeries.current` ke nilai `MAX()` data fisik sebelum lanjut |
| **`frappe.db.get_single_value(doctype, field)` HANYA jalan untuk Single DocType** | Kasus nyata (2026-08-20): `NextHD Settings` `issingle=0` (BUKAN Single, punya nama record biasa spt `3jn1jihj28`), tapi kode lama pakai `get_single_value()` — selalu return `None` walau data sudah diisi & disave di UI, karena fungsi itu baca dari tabel khusus `tabSingles` yang kosong untuk DocType non-Single. **Sebelum pakai `get_single_value()`, cek dulu `frappe.db.get_value("DocType", "<nama>", "issingle")`** — kalau `0`, pakai `frappe.db.get_value(doctype, {}, field)` (ambil record pertama/satu-satunya) sebagai gantinya |
| **`frappe.logger` vs `frappe.logger()`** | `frappe.logger` adalah fungsi, BUKAN objek logger — harus dipanggil dulu `frappe.logger()` baru bisa `.info(...)`/`.error(...)` dst. Salah tulis `frappe.logger.info(...)` (tanpa kurung) akan lolos saat ditulis tapi meledak saat dieksekusi: `AttributeError: 'function' object has no attribute 'info'`. Cek SEMUA pemakaian `frappe.logger` di file yang sama kalau nemu satu instance salah — kemungkinan ada yang lain juga ke-copy-paste dari pattern salah yang sama |
| **DocType dengan `"permissions": []` kosong total di JSON** | **Ditemukan 2026-08-22 (lihat §4 bug session terkait).** Kalau array `permissions` benar-benar kosong (bukan cuma minim), DocType HANYA bisa diakses Administrator — semua role lain (termasuk System Manager) kena `PermissionError`/404 saat akses UI. Selalu tambahkan minimal 1 baris permission (`System Manager` atau role relevan) untuk setiap DocType baru, walau cuma untuk data master yang jarang diedit. **Fix diterapkan (commit `31f35da`) untuk `NextHD SLA Policy` & `NextHD Business Hours`.** |
| **Pola aman untuk logic side-effect di `on_update()`** | Kasus nyata (PR #8, 2026-08-22): logic pause/resume SLA + recalculate butuh update field di dalam `on_update()`. Devin menggunakan `self.db_set(...)` / `frappe.db.set_value(...)` langsung, BUKAN `self.save()`, sehingga tidak memicu infinite recursion (`on_update()` terpanggil lagi). Pola ini jadi referensi wajib untuk hook `on_update()`/`validate()` berikutnya yang butuh side-effect DB |
| **Report shortcut URL selalu `/desk/query-report/<Nama Report>`** | Ini route standar Frappe untuk semua Query Report (dipakai sama persis oleh ERPNext dan app lain) — TIDAK bisa diubah jadi `/desk/nexthd/...` tanpa menulis ulang report sebagai custom Page (kehilangan fitur bawaan: filter builder, export, chart). Bukan bug, ini pola standar Frappe — jangan dianggap "belum sepenuhnya dari NextHD" |
| **Memanggil fungsi backend asli untuk diagnosa "kenapa X tidak muncul di UI"** | Kasus nyata 27 Agustus: daripada terus menebak-nebak field mana yang salah, memanggil langsung `frappe.call(get_workspaces)` (fungsi asli `frappe.desk.desktop` yang dipakai untuk membangun sidebar) membuktikan backend sebenarnya sudah 100% benar — mempersempit pencarian ke arah frontend/lokasi file, bukan lagi ke data. **Pola ini berguna untuk kasus serupa lain**: cari fungsi resmi yang benar-benar dipanggil UI, panggil manual via console, baru simpulkan di lapisan mana masalahnya (backend vs frontend/cache/file) |

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

### ✅ SELESAI — Bug Session 2026-08-20 (SLA Enforcement Business Hours) — DITUTUP TOTAL

Root cause awal: `calculate_sla()` lama pakai `add_to_date()` mentah, sama sekali tidak menghitung jam kerja/hari libur.

**Yang dikerjakan:**
- `business_hours.py` (utils) — bug lama: `WEEKDAY_MAP` pakai nama Inggris (Monday dst) padahal `tabNextHD Business Hours` isinya nama Indonesia (Senin dst), jadi `get_business_hours()` selalu `None`. Diperbaiki ke nama Indonesia.
- `add_working_time()` ditulis ulang jadi versi loop all-or-nothing (kalau durasi tidak muat sebelum jam pulang, seluruh durasi diulang dari jam kerja berikutnya) — menangani durasi multi-hari (Sedang 2 hari, Rendah 1 minggu).
- `NextHD SLA Policy` — field diubah jadi `response_value`+`response_unit` dan `resolution_value`+`resolution_unit` (Menit/Jam/Hari), auto-terhitung ke `response_time_minutes`/`resolution_time_minutes` via controller `validate()`.
- Data SOP final: Kritis response 15 menit/resolusi 1 jam, Tinggi response 30 menit/resolusi 4 jam, Sedang response 60 menit/resolusi 2 hari kerja, Rendah response 120 menit/resolusi 7 hari kerja. `is_24x7 = 0` untuk semua priority.
- Fix final: tambah import `from nexthd.next_helpdesk.utils.business_hours import add_working_time`, replace body `calculate_sla()` agar memanggil `add_working_time(now, minutes, is_24x7=...)`.

**Verifikasi test (2026-08-20 05:32 WIB):**

| Field | Hasil | Status |
|---|---|---|
| Waktu insert | 2026-08-20 05:32 (di luar jam kerja) | — |
| `sla_response_by` | 2026-08-20 09:00 (jam buka 08:00 + 60 menit, prioritas Sedang) | ✅ Benar |
| `sla_resolution_by` | 2026-08-26 12:30 (+2 hari kerja dari jam buka) | ✅ Benar |

Ticket test: `TKT-2608-0004`. Sudah di-commit (`8d3f26d`) dan push ke `origin/main`.

> ✅ **Diverifikasi ulang dari kode di repo (2026-08-22):** `business_hours.py` dan `nexthd_ticket.py` dikonfirmasi sudah sesuai — `add_working_time()` dengan loop per-hari, dan `calculate_sla()` sudah memanggil `add_working_time()` dengan benar.
>
> ✅ **Gap titik-mulai resolution (item T) sudah difix via PR #8** (2026-08-22, lihat entri di bawah) — `sla_resolution_by` kini direcalculate saat status pindah ke "Sedang Dikerjakan", bukan hanya sekali saat insert.

### ✅ SELESAI — Bug Session 2026-08-20 (Dedup Transisi Workflow — Kedua Kalinya) & Regression Test

**Temuan:** Seluruh 21 transisi di 3 workflow terduplikasi 2x (total 42 baris) — semua baris duplikat punya **`idx = 0`**.

**Fix:**
```python
frappe.db.sql("DELETE FROM `tabWorkflow Transition` WHERE parent IN ('NextHD Ticket','NextHD Problem','NextHD Change Request') AND idx = 0")
frappe.db.commit()
```
Hasil: 42 → 21 baris. Breakdown final: Ticket 7, Problem 6, Change Request 8. Fixture di-export ulang dan di-push ke `main`.

**Regression test `apply_workflow()` — semua LULUS:**

| Workflow | Jalur Ditest | Hasil |
|---|---|---|
| NextHD Ticket | Baru → Sedang Dikerjakan → Selesai → Ditutup | ✅ |
| NextHD Problem (jalur investigasi) | Terbuka → Investigasi → Selesai → Ditutup | ✅ |
| NextHD Problem (jalur langsung) | Terbuka → Selesai (Selesaikan Langsung) | ✅ |
| NextHD Change Request | Draft → Diajukan → Direview → Disetujui → Implementasi → Selesai → Ditutup | ✅ |
| Transisi tidak valid (skip step) | Ditolak dengan `WorkflowTransitionError` sesuai harapan | ✅ |

### ✅ SELESAI (FIX DI-COMMIT) — Bug Session 2026-08-20 (Bot Telegram Tidak Balas)

**Root cause #1 (kritis) — sudah difix, sudah di-commit (`fb9369c`):**
`get_bot_token()` dan `is_telegram_enabled()` di `telegram.py` pakai `frappe.db.get_single_value("NextHD Settings", ...)`. Tapi `NextHD Settings` `issingle=0` (BUKAN Single DocType) — `get_single_value()` selalu return `None`. Fix: ganti ke `frappe.db.get_value("NextHD Settings", {}, field)`.

**Root cause #2 (flooding error log) — sudah difix bersamaan:**
`frappe.logger.info(...)` (kurang kurung) di `check_sla_response_breach()` → `tasks.py`. Fix ke `frappe.logger().info(...)`.

**Bug ke-3 (prioritas rendah, belum difix):**
Pesan "Peringatan SLA Response" di `tasks.py` masih pakai f-string mentah (bukan `frappe._()`). Luput dari scope PR #6 karena ada di `tasks.py`, bukan `telegram.py`.

**⚠️ STATUS AKHIR:** Fix sudah di-commit ke repo. **Belum ada konfirmasi retest end-to-end** (bot balas `/start` di Telegram nyata setelah `bench restart`). Lihat item E di `SUMMARY.md §2` untuk next steps verifikasi.

**Catatan penting:**
- User test `test.requester@ciptamebel.co.id` (role Requester) sudah ada, password sudah di-set
- **Token bot Telegram tidak dicatat di dokumentasi/GitHub** — hanya ada di NextHD Settings di server

### ✅ SELESAI (via Devin PR #7 & #8) — Bug Session 2026-08-22 (Verifikasi Kode Kedua Putaran — Permission & SLA Recalc)

Sesi ini melakukan verifikasi tambahan (di luar 4 file yang sudah dicek sebelumnya): `nexthd_ticket_waiting_log.json`, `nexthd_ticket.json` (permissions), `nexthd_sla_policy.json`, `nexthd_business_hours.json`, `nexthd_holiday.json`, `nexthd_team.json`, `nexthd_ticket_workflow.json`.

**Temuan 1 — `permissions: []` kosong total di 2 DocType master:**
`NextHD SLA Policy` dan `NextHD Business Hours` sama-sama punya array `permissions` kosong di JSON. **Fix: commit `31f35da` (2026-08-22 09:48 WIB), langsung push ke `main`** (dikerjakan manual, bukan lewat Devin). Ini kandidat kuat root cause item G (404 halaman NextHD SLA Policy). Belum di-`bench migrate` di server produksi — lihat `SUMMARY.md §2` item U dan G.

**Temuan 2 — Permission `reply` Waiting Log dikonfirmasi BENAR di JSON:**
`nexthd_ticket_waiting_log.json` sudah tepat, tidak perlu fix kode. Status "belum ditest" di item F murni soal verifikasi UI produksi.

**Temuan 3 — Field `priority` `read_only` di level field, bukan `permlevel`:**
**Fix: [PR #7](https://github.com/silverefendy/nexthd/pull/7), merged 2026-08-22 10:13 WIB.** Devin mengimplementasikan:
- `nexthd_ticket.json`: field `priority` diubah dari `"read_only": 1` ke `"permlevel": 1`, ditambah baris permission `{"role": "Agent Manager", "permlevel": 1, "read": 1, "write": 1}` dan sama untuk `IT Manager`.
- Field baru `priority_manually_set` (Check, hidden, default 0) — dipakai `set_priority_from_matrix()` untuk mendeteksi kalau `priority` sudah diubah manual (`has_value_changed("priority")` di luar proses matrix), supaya matrix tidak menimpa override manual lagi di save berikutnya.
- `nexthd_ticket.py`: `set_priority_from_matrix()` dipanggil di awal `validate()`. Logic matrix: Tinggi+Tinggi→Kritis, Tinggi+Rendah→Tinggi, Rendah+Tinggi→Sedang, Rendah+Rendah→Rendah. Hanya jalan kalau `impact` dan `urgency` dua-duanya terisi.
- 8 test case baru di `test_nexthd_ticket.py`, mencakup semua kombinasi matrix, kasus blank, dan skenario override manual — sudah direview kode-nya oleh Claude, terlihat solid (belum dijalankan langsung di server oleh Claude, karena Claude tidak boleh eksekusi kode di server produksi).

**Fix item B+T (SLA pause/resume): [PR #8](https://github.com/silverefendy/nexthd/pull/8), merged 2026-08-22 10:31 WIB.** Devin mengimplementasikan:
- `on_update()` sekarang memanggil `handle_workflow_sla_transitions()`, yang mengecek `self.has_value_changed("status")` + `self.get_doc_before_save()` untuk menentukan transisi lama→baru.
- 4 skenario: **Baru→Sedang Dikerjakan** (`_recalculate_sla_resolution_on_start()`: hitung ulang `sla_resolution_by` dari `now_datetime()` pakai `add_working_time()`, set `responded_on`), **Sedang Dikerjakan→Menunggu User** (`_create_waiting_log_entry()`: insert child table baru), **Menunggu User→Sedang Dikerjakan** (`_close_waiting_log_and_extend_sla()`: tutup log, hitung durasi pause dalam menit (dibulatkan ke atas), extend `sla_resolution_by` sebesar durasi pause — pakai penambahan waktu lurus, BUKAN `add_working_time()`), **Menunggu User→Selesai** (`_close_waiting_log_on_resolve()`: tutup log tanpa extend SLA).
- **Risiko infinite recursion yang diwanti-wanti sebelumnya sudah ditangani dengan benar** — semua update pakai `self.db_set(...)` / `frappe.db.set_value(...)` langsung, BUKAN `self.save()` di dalam `on_update()`. Ada test khusus `test_workflow_sla_no_infinite_recursion` yang mengonfirmasi ini tidak macet.
- 6 test case baru mencakup semua transisi + siklus pause berulang.
- Catatan kecil dari Devin di komentar kode: field `question` di waiting log masih hardcoded placeholder ("Menunggu respons dari user") — UI prompt supaya agent bisa isi alasan custom adalah task terpisah di masa depan (belum ada di scope T/B).

**Status akhir sesi ini:** Kedua PR sudah di-review levelnya kode oleh Claude (diff, logic, dan pola anti-recursion) dan terlihat sesuai spesifikasi yang diminta ke Devin. **Belum ada test end-to-end manual di server produksi** — itu jadi langkah berikutnya untuk Efendy (lihat panduan test CLI di pesan chat terkait / `SUMMARY.md §2`). Item A, B, C, T dipindah dari "belum ada di kode" ke "kode selesai, menunggu deploy" di `SUMMARY.md §2`.

### ✅ SELESAI — Bug Session 2026-08-26 (Dashboard Shortcut "NextHD Photo" & 6 Report — `report_ref_doctype` & Cache)

**Konteks:** Menambahkan 7 kartu shortcut baru ke dashboard `/desk/nexthd` — 1 shortcut DocType (`NextHD Photo`) ke section "Konfigurasi", dan 6 shortcut Report (`Tiket per Bulan`, `Tiket per Agent`, `Tiket per Prioritas`, `Tiket per Kategori`, `SLA Compliance Bulanan`, `Aset Bermasalah`) ke section baru "Laporan". Insert dilakukan via SQL langsung ke `tabWorkspace Shortcut` + update `Workspace.content` — **ini pekerjaan terpisah dari item AA (25 Agustus, sidebar kiri via `Workspace.links`)**, jangan disatukan meski sama-sama menyangkut "Report" dan "Photo". Lihat §1.B dan §1.C untuk penjelasan lengkap perbedaan ketiga tabel Workspace.

**Gejala:** Setelah insert (7 shortcut baru terkonfirmasi ada di `tabWorkspace Shortcut`, `content` JSON terkonfirmasi 32 blok), halaman `/desk/nexthd-photo` bisa dibuka manual via URL langsung, tapi kartu "NextHD Photo" **tidak muncul** di dashboard. 6 kartu Report juga tidak muncul sama sekali.

**Investigasi:**
1. Role Efendy (`support@ciptamebel.co.id`) dicek — punya `IT Manager` **dan** `System Manager`, jadi permission BUKAN penyebab (baik untuk DocType `NextHD Photo` maupun ke-6 Report).
2. Kolom `report_ref_doctype` di `tabWorkspace Shortcut` untuk ke-6 shortcut Report ternyata **kosong (`NULL`)** — tidak diisi saat insert awal.

**Root cause & fix:**
- **6 shortcut Report:** `report_ref_doctype` kosong membuat Frappe kemungkinan besar gagal resolve konfigurasi kartu saat render, sehingga di-skip diam-diam. Fix: `UPDATE tabWorkspace Shortcut SET report_ref_doctype=... WHERE label=... AND type='Report'` — 5 report (Tiket per Bulan/Agent/Prioritas/Kategori, SLA Compliance Bulanan) → `NextHD Ticket`, 1 report (Aset Bermasalah) → `NextHD Asset`.
- **Shortcut "NextHD Photo":** data & permission sudah benar dari awal, jadi penyebabnya cache Redis — `Workspace.content` diupdate via SQL langsung (bukan `doc.save()`), yang tidak memicu invalidasi cache otomatis (lihat aturan baru di §3).
- Fix gabungan: isi `report_ref_doctype` + `bench clear-cache` + `bench clear-website-cache`, lalu hard refresh browser (Ctrl+Shift+R, bukan reload biasa — karena cache boot info browser juga bisa menyimpan versi lama).

**Catatan tambahan:** URL report tetap `/desk/query-report/<nama>` — ini standar Frappe untuk semua Query Report (sama seperti ERPNext), bukan bug, dan tidak bisa diubah jadi rute `/desk/nexthd/...` tanpa menulis ulang report sebagai custom Page. Modul report sudah benar (`Next Helpdesk`), jadi tetap terhubung ke NextHD lewat breadcrumb/pencarian meski URL bar-nya rute standar Frappe.

**Status:** Fix sudah dijalankan di server, menunggu konfirmasi visual Efendy (kartu Photo + 6 Report muncul di dashboard setelah hard refresh) sebelum export ke fixture JSON `nexthd/next_helpdesk/workspace/nexthd/nexthd.json` (pola: DB dulu → verifikasi UI → fixture → push).

### ✅ SELESAI — Bug Session 2026-08-27 (Workspace "NextHD Report" Tidak Muncul di Sidebar — 4 Lapis Masalah)

**Konteks:** Workspace baru "NextHD Report" (11 shortcut ke report Detail Tiket/Aset/Known Error/Problem/Change Request Lengkap) dibuat via script `bench console` (insert langsung ke DB), bukan lewat UI. Datanya valid 100% di database (content JSON 12 blok, semua field cocok format dengan workspace "NextHD" yang sudah berhasil), tapi **tidak pernah muncul** di sidebar kiri workspace "NextHD" — bertahan meski sudah clear-cache, build, restart, bahkan dicoba di Incognito.

**Root cause ternyata berlapis 4, ditemukan berurutan:**

1. **Workspace tidak punya file fixture JSON sama sekali** — karena dibuat via insert manual, hook `on_update()` yang biasanya generate file fixture tidak pernah terpanggil. **Fix:** aktifkan `developer_mode=1`, panggil `doc.save()` manual sekali → file fixture `workspace/nexthd_report/nexthd_report.json` berhasil ter-generate.

2. **`Workspace.roles` kosong** (`[]`) sedangkan workspace "NextHD" lama punya 6 role. Disamakan manual — **ternyata bukan penyebab utama** kasus ini (sidebar tetap tidak muncul setelah fix ini), meski tetap perlu dibereskan untuk alasan akses.

3. **Backend sebenarnya sudah benar sejak awal** — dibuktikan dengan memanggil langsung `frappe.call(get_workspaces)` (fungsi asli `frappe.desk.desktop` yang dipakai membangun sidebar): "NextHD Report" **sudah muncul** di hasilnya. Ini mempersempit masalah dari "data workspace salah" ke "mekanisme UI untuk menambah sidebar item belum dipakai dengan benar".

4. **Item sidebar harus ditambah lewat UI "⋯ → Edit Sidebar"**, bukan hanya mengandalkan `Workspace.links`. Setelah ditambah manual lewat UI (item "NextHD Reporting" → link ke Workspace "NextHD Report"), sidebar langsung tampil normal untuk pertama kali. **Tapi** verifikasi export ke file fixture sempat berputar-putar karena **root cause tersembunyi kelima**: file fixture `Workspace Sidebar` ternyata ditulis ke lokasi **berbeda** dari yang selama ini dicek —
   ```
   ✅ Lokasi benar (aktif, terus di-update): nexthd/nexthd/workspace_sidebar/nexthd.json
   ❌ Lokasi salah/usang (peninggalan lama, tidak pernah ditulis ulang): nexthd/nexthd/next_helpdesk/workspace_sidebar/nexthd.json
   ```
   File lama di lokasi salah dihapus, dan dikonfirmasi file yang benar sudah berisi "NextHD Reporting".

**Kesalahan sampingan yang sempat terjadi (sudah di-undo):** sempat dicoba set `Workspace.public=0` + `is_hidden=1` pada "NextHD Report" berdasarkan dugaan harus disembunyikan seperti workspace pendukung lain (Ticket Center, dll). **Efeknya link sidebar malah hilang total** — membuktikan dugaan itu salah untuk kasus workspace yang diakses lewat sidebar link biasa. Sudah dikembalikan ke `public=1`, `is_hidden=0`.

**Status akhir:** Sidebar "NextHD Reporting" tampil normal, mengarah ke Workspace "NextHD Report" berisi 11 shortcut report. §1.C di atas sudah direvisi total untuk mencerminkan pemahaman yang benar soal 4 lapisan doctype sidebar dan lokasi file fixture yang benar. Detail kronologi lengkap (termasuk semua script diagnostik yang dipakai) ada di riwayat chat sesi 26–27 Agustus.

**Langkah lanjutan yang masih tertunda:**
- [ ] Commit & push semua file `.json` yang berubah (fixture Workspace baru, fixture Workspace Sidebar terupdate, penghapusan file lama)
- [ ] Jalankan `bench migrate` untuk uji tahan (pastikan sidebar tidak hilang lagi setelah migrate)
- [ ] Putuskan apakah `developer_mode` perlu dimatikan kembali di server produksi
- [ ] Tindak lanjut terpisah: pembersihan "Desktop Icon" Frappe terkait workspace ini (disinggung di akhir sesi, belum dibahas tuntas)

---

*Dokumen ini dikelola oleh Claude. Update terakhir: 2026-08-27.*
