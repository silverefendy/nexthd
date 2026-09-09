# NextHD — Arsitektur & Referensi Teknis

> Referensi statis: infrastruktur, struktur app, DocType/field, permissions, schema DB, label ID.
> Jarang berubah kecuali ada penambahan DocType atau perubahan infrastruktur.
>
> **Last updated:** 2026-09-09 12:10 WIB

---

## 1. Infrastruktur & Stack

| Komponen | Detail |
|---|---|
| VM | `erpnext` — Tailscale IP `100.64.0.14` |
| User | `it` — working dir `/home/it/frappe` |
| Frappe | v16.30.0 |
| Python | 3.14 |
| Custom App | nexthd v0.0.1 |
| Site | `desk.ciptamebel.co.id` |
| Route | nginx di CML-VPS `103.103.22.231` → VM erpnext via Tailscale |
| SSL | certbot, valid sampai 5 Nov 2026 |
| Node.js | nvm di `/home/it/.nvm/versions/node/v24.19.0/bin/node` — hardcoded di supervisor |
| Database | MariaDB 10.11+ |
| Akun operasional | `support@ciptamebel.co.id` |
| Akun admin | `Administrator` — email: `admin@example.com` |
| Pemakai saat ini | Hanya IT (satu orang) sebagai Administrator |
| VM lama `cml-helpdesk` (100.64.0.13) | ✅ **Sudah didecommission dari VPS** (dikonfirmasi 2026-08-11) |

### Diagram Infrastruktur

```
Internet → CML-VPS (nginx + SSL) → VM erpnext (via Tailscale)
                                          ↓
                               Frappe Framework (bench)
                                          ↓
                             Site: desk.ciptamebel.co.id
                                          ↓
                              App: nexthd (custom)
                                          ↓
                                  MariaDB
                                          ↓
                    Notifikasi keluar → Telegram Bot API
```

### Kebutuhan Server

- Ubuntu Server 24.04 LTS
- RAM: minimal 4GB + swap 4GB
- Disk: 40GB (sementara)
- Supervisor untuk process management
- Nginx + Certbot untuk SSL
- **Firewall: outbound HTTPS ke `api.telegram.org` harus tidak diblok**

---

## 2. Struktur App

```
nexthd/
├── hooks.py                          ← doc_events, scheduler, fixtures, add_to_apps_screen, doctype_list_js
├── modules.txt                        ← berisi: Next Helpdesk
├── patches.txt
├── public/
│   ├── logo.svg                      ← WAJIB ADA untuk add_to_apps_screen hook
│   └── js/
│       ├── nexthd_ticket_list.js     ← get_indicator (Status) + formatters (Priority, Ticket Type — item PP, 9 Sept)
│       ├── nexthd_asset_list.js      ← formatters (Status, Asset Category — item PP, baru 9 Sept)
│       └── nexthd_photo_list.js      ← formatters (Kategori, hash-color — item PP, baru 9 Sept)
└── next_helpdesk/
    ├── api/
    │   ├── __init__.py               ← WAJIB ADA (Python package)
    │   └── telegram_webhook.py       ← endpoint webhook Telegram
    ├── doctype/
    │   └── nexthd_*/                 ← lihat §3 untuk daftar lengkap DocType
    ├── tasks.py                      ← scheduled jobs (SLA checker)
    ├── translations/
    │   └── id.csv                    ← terjemahan Bahasa Indonesia
    ├── utils/
    │   ├── email_helper.py           ← hook auto-generate email dummy
    │   └── telegram.py               ← fungsi notifikasi Telegram
    └── workspace/
        └── nexthd/nexthd.json        ← workspace page definition
```

> **Module name:** `Next Helpdesk` (folder: `next_helpdesk`)
> Semua import menggunakan path dari root: `from nexthd.next_helpdesk.utils.telegram import ...`

---

## 3. DocType & Field Penting

### Non-Child DocType (13+1 EAV, lihat catatan)

| DocType | Route | Naming Series | `naming_rule` |
|---|---|---|---|
| NextHD Asset | nexthd-asset | `AST-.YY.MM.-.####.` | `By "Naming Series" field` |
| NextHD Business Hours | nexthd-business-hours | — | — |
| NextHD Category | nexthd-category | — | — |
| NextHD Change Request | nexthd-change-request | `CHG-.YY.MM.-.####.` | `By "Naming Series" field` |
| NextHD Known Error | nexthd-known-error | `KE-.YY.MM.-.####.` | `By "Naming Series" field` |
| NextHD Problem | nexthd-problem | `PRB-.YY.MM.-.####.` | `By "Naming Series" field` |
| NextHD Service Catalog | nexthd-service-catalog | `SVC-2026-####` | `By "Naming Series" field` |
| NextHD Settings | nexthd-settings | — (Single) | — |
| NextHD SLA Policy | nexthd-sla-policy | — | — |
| NextHD Team | nexthd-team | — | — |
| NextHD Ticket | nexthd-ticket | `TKT-.YY.MM.-.####.` | `By "Naming Series" field` |
| NextHD Photo | nexthd-photo | `IMG-.YY.MM.-.####` | `By "Naming Series" field` |
| NextHD User Profile | nexthd-user-profile | — | — |
| NextHD Asset Category | — (master, Link target dari `NextHD Asset.asset_category`) | — | — |

> ⚠️ **Naming series diseragamkan ke format `YY.MM` (reset bulanan) pada 2026-08-15**, termasuk
> NextHD Ticket yang sebelumnya sengaja tidak diubah. Dokumen lama dengan format sebelumnya
> dibiarkan apa adanya, tidak di-rename.

> ⚠️ **Bug `naming_rule` usang, ditemukan & diperbaiki 9 September 2026 (item PP):** kolom
> `naming_rule` di `tabDocType` untuk **5 DocType** (Asset, Problem, Change Request, Known
> Error, Service Catalog) tersimpan sebagai nilai `"By Series"` — nilai ini **tidak valid**
> lagi di Frappe v16 (opsi yang diterima cuma `""`, `"Set by user"`, `"Autoincrement"`,
> `"By fieldname"`, `"By \"Naming Series\" field"`, `"Expression"`, `"Expression (old
> style)"`, `"Random"`, `"UUID"`, `"By script"`). Bug ini **tidak pernah muncul sebagai
> error** sampai ada `doc.save()` penuh dijalankan ke DocType tersebut (biasanya hanya
> disentuh via SQL/`ALTER TABLE` yang skip validasi ini) — baru ketahuan saat percobaan
> hapus field `asset_type` (lihat catatan Asset di bawah). Diperbaiki ke
> `By "Naming Series" field` (sesuai `autoname: naming_series:` yang dipakai kelima
> DocType ini). Kalau menambah DocType baru dengan pola serupa (copy dari DocType lama),
> **cek dulu nilai `naming_rule` via `frappe.db.get_value("DocType", dt, "naming_rule")`**
> sebelum melakukan `doc.save()` penuh apa pun.

> **28 Agustus 2026 (malam):** `NextHD Asset Category` (master) ditambahkan sebagai bagian dari
> migrasi `NextHD Asset` ke pola EAV. Lihat §3.1 Detail Field NextHD Asset di bawah.

### Child DocType (5) — istable=1, tidak perlu di sidebar

| DocType | Parent |
|---|---|
| NextHD Team Member | NextHD Team |
| NextHD Problem Ticket | NextHD Problem |
| NextHD Asset Attribute | NextHD Asset (EAV, ditambahkan 28 Agustus 2026) |
| NextHD Ticket Worklog | NextHD Ticket (catatan progress teknisi, PR #11, live 31 Agustus 2026) |
| NextHD Activity Log | NextHD Problem, NextHD Change Request, NextHD Known Error (shared, pola sama seperti `NextHD Photo Link` — riwayat aktivitas otomatis+manual, PR #12, live 7-8 September 2026, item OO) |

---

### Detail Field: NextHD Ticket

```
naming_series         → TKT-.YY.MM.-.####.
ticket_type           → Select: Insiden / Permintaan Layanan
subject               → Data (required)
description           → Text Editor
status                → Select: Baru / Sedang Dikerjakan / Menunggu User / Selesai / Ditutup
priority              → Select: Kritis / Tinggi / Sedang / Rendah
category              → Link: NextHD Category
service_catalog       → Link: NextHD Service Catalog (depends_on: ticket_type = Permintaan Layanan)
impact                → Select
urgency               → Select
requested_by          → Link: User (required)
assigned_to           → Link: User
team                  → Link: NextHD Team
affected_asset        → Link: NextHD Asset
sla_response_by       → Datetime (read_only)
sla_resolution_by     → Datetime (read_only)
responded_on          → Datetime (read_only)
resolved_on           → Datetime (read_only)
closed_on             → Datetime (read_only)
sla_warning_sent      → Check (read_only)
related_problem       → Link: NextHD Problem
attachments           → Attach
waiting_log           → Table: NextHD Ticket Waiting Log
worklog               → Table: NextHD Ticket Worklog (ditambahkan PR #11, 31 Agustus 2026)
photos                → Table: NextHD Photo Link
priority_manually_set → Check (hidden)
tanggal_dibuat        → Datetime (hidden, read_only — ditambahkan 5-6 September 2026)
tanggal_diedit        → Datetime (hidden, read_only — idem)
```

**Warna List View (item PP, 9 September 2026):** `priority` dan `ticket_type` diberi
indicator pill via `formatters` di `nexthd_ticket_list.js` (`status` sudah lebih dulu
diwarnai via `get_indicator`, mapping fix — tidak dipakai `formatters`, dua mekanisme
berbeda yang hidup berdampingan di file yang sama):

| Field | Nilai | Warna |
|---|---|---|
| `priority` | Kritis / Tinggi / Sedang / Rendah | red / orange / yellow / grey |
| `ticket_type` | Insiden / Permintaan Layanan | red / blue |

#### Detail Field: NextHD Ticket Worklog (child table, ditambahkan PR #11, 31 Agustus 2026)

```
waktu          → Datetime
teknisi        → Link: User
aktivitas      → Small Text
hasil          → Select: Berhasil / Belum Berhasil / Perlu Eskalasi / Menunggu Sparepart
durasi_menit   → Int
```

> Field `durasi_menit` masih banyak diisi `0` di data existing — belum bisa diandalkan untuk
> laporan produktivitas/MTTR per teknisi. Dipakai sebagai kolom di report "Riwayat Progress
> Tiket" (§3.2) yang menggabungkan Worklog lintas semua tiket, sortable by `waktu`.

#### Detail Field: NextHD Activity Log (child table shared, PR #12, live 7-8 September 2026, item OO)

```
waktu               → Datetime
jenis               → Select: Otomatis (perubahan status) / Manual (catatan Agent)
catatan             → Small Text
dibuat_oleh         → Link: User
related_doctype     → Link: DocType (opsional — Dynamic Link target, diisi saat konversi dokumen)
related_document    → Dynamic Link (options: related_doctype, opsional)
```

> Parent: `NextHD Problem`, `NextHD Change Request`, `NextHD Known Error` (pola shared child
> table, sama seperti `NextHD Photo Link` dipakai 4 parent berbeda). Log otomatis dibuat saat
> status berubah (`on_update()`), plus catatan manual Agent. Link dua arah opsional
> (`related_doctype`+`related_document`) diisi oleh 4 Client Script existing saat konversi
> Problem↔CR↔Known Error↔Asset. **Bug ditemukan & diperbaiki (commit `7af8deb`, 8
> September):** `on_update()` di Problem/Change Request sempat tidak memanggil `self.reload()`
> setelah insert SQL child row — pola sama seperti bug lama `NextHD Ticket Waiting Log` (PR
> #8). **Belum ditest via UI browser:** skenario cross-document link dua arah — masuk
> prioritas sesi berikutnya (`docs/SUMMARY.md`).

### Catatan Field Meta: `tanggal_dibuat` / `tanggal_diedit` (ditambahkan 5-6 September 2026)

**Kenapa dibutuhkan:** Frappe **tidak expose** field meta bawaan `creation`/`modified` ke
dialog List View "+ Add/Remove Fields" (bukan DocField terdaftar) — jadi List View biasa
tidak bisa menampilkan tanggal absolut "Dibuat"/"Diedit", cuma kolom `modified` bawaan yang
formatnya di-hardcode relative time ("1d"/"2h").

**Solusi:** 2 Custom Field baru (`tanggal_dibuat`, `tanggal_diedit`, tipe Datetime,
`hidden=1`, `read_only=1`) ditambahkan ke **5 DocType**: NextHD Ticket, NextHD Problem,
NextHD Known Error, NextHD Change Request, NextHD Asset. Disinkron otomatis dari
`creation`/`modified` via method baru `sync_meta_dates()`:

```python
def sync_meta_dates(self):
    if not self.tanggal_dibuat:
        self.db_set("tanggal_dibuat", self.creation, update_modified=False)
    self.db_set("tanggal_diedit", now_datetime(), update_modified=False)
```

Dipanggil dari `on_update()` masing-masing controller.

> ⚠️ **Schema drift sempat terjadi 7-8 September (item OO):** field ini hilang dari metadata
> untuk 3 dari 5 DocType (Problem, Change Request, Known Error) saat PR #12 (`NextHD Activity
> Log`) memicu `bench migrate` — root cause: field ini awalnya cuma di-insert manual ke
> `tabDocField` tanpa pernah ditulis ke JSON DocType atau didaftarkan fixtures. Sudah
> diperbaiki permanen (ditulis ke `nexthd_problem.json`/`nexthd_change_request.json`/
> `nexthd_known_error.json`, commit `7af8deb`). **Pelajaran:** field custom yang cuma
> dilindungi SQL manual berisiko hilang setiap kali migrate dipicu untuk alasan APAPUN pada
> DocType yang sama — selalu tulis ke file JSON DocType-nya sendiri, bukan cuma fixture
> `DocField` terpisah.

**Temuan sampingan saat implementasi ini:** field `resolved_on`/`closed_on` di NextHD Ticket
ternyata **sudah otomatis terisi dengan benar sejak lama** (logic sudah ada di
`update_timestamps()`) — hanya belum dicentang di dialog List View, bukan bug kode.

### Detail Field: NextHD Problem

```
naming_series         → PRB-.YY.MM.-.####.
title                 → Data (required)
status                → Select: Terbuka / Investigasi / Known Error / Selesai / Ditutup
priority              → Select: Kritis / Tinggi / Sedang / Rendah
category              → Link: NextHD Category
related_asset         → Link: NextHD Asset   (ditambahkan 2026-08-15, opsional)
root_cause            → Text Editor
workaround            → Text Editor
known_error           → Link: NextHD Known Error (depends_on: status = Known Error)
change_request        → Link: NextHD Change Request
related_tickets       → Table: NextHD Problem Ticket
photos                → Table: NextHD Photo Link
activity_log          → Table: NextHD Activity Log (ditambahkan PR #12, 7-8 September 2026)
tanggal_dibuat        → Datetime (hidden, read_only — ditambahkan 5-6 September 2026)
tanggal_diedit        → Datetime (hidden, read_only — idem)
```

> ⚠️ **Posisi field penting:** `related_asset` sengaja diletakkan **sejajar dengan Priority/Category**
> (idx 7, sebelum section "Detail & Relasi"), BUKAN setelah field Table `related_tickets`. Field biasa
> yang ditempatkan langsung setelah field bertipe Table kadang tidak ter-render di UI meski datanya
> valid — ditemukan sebagai bug pada 2026-08-15. Lihat `docs/BUG_HISTORY.md`.

> **Cara resmi mencapai status `Known Error`:** dua jalur yang sama-sama valid —
> **(a)** tombol custom **"Buat Known Error dari Problem"** (Client Script, muncul saat field
> `known_error` masih kosong) yang otomatis membuat record Known Error baru dan mengisi
> `known_error`, atau **(b)** kalau Known Error yang cocok **sudah ada**, pilih manual di field
> `known_error`, lalu transisi status lewat Actions.
>
> Transisi workflow "Convert to Known Error" (Investigasi → Known Error) **diberi `condition:
> doc.known_error`** sejak 2026-08-15 — tombol transisi ini hanya muncul di Actions kalau field
> `known_error` sudah terisi (lewat cara a atau b), supaya tidak bisa pindah status tanpa Known
> Error yang benar-benar terhubung. Detail lengkap riwayat perbaikan ini di `WORKFLOW.md`.

**Warna List View:** `status` sudah diwarnai lewat `Workflow State.style` (mekanisme
Workflow bawaan, bukan `formatters`) — lihat `docs/WORKFLOW.md`.

### Detail Field: NextHD Asset (pola EAV — direvisi total 29 Agustus, `asset_type` DIHAPUS TOTAL 9 September 2026)

> ⚠️ **Riwayat perubahan struktur (baca dulu sebelum mengasumsikan field apa pun ada/tidak ada):**
> 1. **Awal (7 Agustus – 28 Agustus siang):** field terstruktur statis per `asset_type`
>    (`brand`, `model`, `serial_number`, `cpu`, `ram`, dst).
> 2. **28 Agustus malam (commit `281072a`+`81889c0`, Efendy/Devin):** ditambahkan field
>    `asset_category` (Link, `reqd=1`) dan `asset_attributes` (Table → `NextHD Asset Attribute`,
>    EAV) **di samping** field lama — sempat tumpang tindih.
> 3. **29 Agustus (commit `d964531`, item JJ):** field terstruktur lama (`brand`, `model`, `cpu`,
>    dst) **dihapus total** dari form karena sudah duplikat dengan EAV. Field catatan bebas
>    dipertahankan. `asset_type` (Select) sendiri belum disentuh di tahap ini.
> 4. **6 September 2026 (item NN):** field `asset_type` **disembunyikan** (`hidden=1`,
>    `read_only=1`, non-destruktif — kolom & data lama tetap ada di database). 8 `depends_on`
>    field dinamis dialihkan penuh dari `doc.asset_type` ke `doc.asset_category`.
> 5. **9 September 2026 (item PP):** field `asset_type` **dihapus TOTAL** — dari metadata
>    DocType (`nexthd_asset.json`, via regenerate `doc.save()` karena file JSON di repo sudah
>    sangat basi/tidak sinkron dengan DB) DAN dari kolom fisik database
>    (`ALTER TABLE ... DROP COLUMN asset_type`). Diverifikasi sebelum eksekusi: 0 field lain
>    masih `depends_on` ke field ini, 100% data (8/8 Asset) sudah punya `asset_category`
>    terisi. **Tidak reversibel** — kalau butuh data `asset_type` lama, cek backup database
>    sebelum 9 September 2026.
>
> **Struktur final (9 September 2026 dan seterusnya):**

```
naming_series         → AST-.YY.MM.-.####.
asset_name            → Data (required)
location              → Data
assigned_to           → Link: User
status                → Select: Aktif / Rusak / Diperbaiki / Dihapus
asset_category        → Link: NextHD Asset Category (required — SATU-SATUNYA sumber
                          kebenaran untuk kategori aset & depends_on field dinamis)
purchase_date         → Date
warranty_until        → Date

# Field catatan bebas — muncul sesuai asset_category (depends_on):
[PC / Laptop / Server]  → peripheral_notes (Small Text)
[Network Device]        → net_notes (Small Text)
[Printer]               → printer_notes (Small Text)
[Lainnya]               → other_description (Text Editor)

photos                 → Table: NextHD Photo Link (foto reusable, PR #9)
asset_attributes       → Table: NextHD Asset Attribute (EAV, semua spesifikasi terstruktur sekarang di sini)
tanggal_dibuat         → Datetime (hidden, read_only — ditambahkan 5-6 September 2026)
tanggal_diedit         → Datetime (hidden, read_only — idem)
```

> ❌ **`asset_type` DIHAPUS TOTAL 9 September 2026** — field ini sekarang tidak ada lagi
> sama sekali, baik di metadata DocType maupun kolom fisik database. **Jangan referensikan
> field ini di kode/report/script baru apa pun.**
>
> ❌ **DIHAPUS 29 Agustus 2026 (item JJ)** — field-field ini juga TIDAK ADA lagi (kolom fisik
> masih ada di DB untuk field-field ini, beda dari `asset_type` yang sudah drop kolom juga):
> `brand`, `model`, `serial_number`, `cpu`, `ram`, `storage`, `os` (section PC/Laptop/Server);
> `net_brand`, `net_model`, `net_serial_number`, `ip_address`, `mac_address`, `device_role`
> (section Network Device); `printer_brand`, `printer_model`, `printer_serial_number`,
> `printer_type` (section Printer). Data lama semua sudah ter-backfill ke `asset_attributes`
> sebelum field dihapus. **Jangan tambahkan field ini lagi** — kalau butuh spesifikasi baru,
> tambahkan sebagai baris di `asset_attributes` (EAV), bukan DocField statis baru.

**Warna List View (item PP, 9 September 2026):** `status` dan `asset_category` diberi
indicator pill via `formatters` di `nexthd_asset_list.js`:

| Field | Nilai/Pola | Warna |
|---|---|---|
| `status` | Aktif / Rusak / Diperbaiki / Dihapus | green / red / orange / grey |
| `asset_category` | (Link dinamis ke master) | hash-color — nama kategori di-hash jadi index warna dari palet 10 warna, konsisten tiap kali |

#### Detail Field: NextHD Asset Attribute (child table EAV)

```
attribute_name   → Data (nama atribut bebas, mis. "CPU", "RAM", "IP Address")
attribute_value  → Data (nilai atribut)
unit             → Data (opsional, mis. "GB")
brand            → Data
serial_number    → Data
sumber           → Data
catatan          → Text
```

> ⚠️ Skema child table ini **bukan cuma `attribute_name`/`attribute_value`/`unit`** generik
> seperti desain awal di `DAFTAR_FITUR.md` — punya kolom sendiri untuk
> `brand`/`serial_number`/`sumber`/`catatan` per baris. Diverifikasi langsung via
> `DESCRIBE tabNextHD Asset Attribute` pada 29 Agustus.

> **Property Setter `search_fields`** (diupdate 29 Agustus 2026): `asset_name,assigned_to`
> — field `serial_number` dihapus karena field-nya sendiri sudah pindah ke EAV. Field di
> child table (Table/EAV) **tidak bisa** dipakai di `search_fields` Link.

> **Report `Detail Aset Lengkap`** — riwayat perubahan: ditulis ulang 29 Agustus (LEFT JOIN
> ke EAV, kolom "Spesifikasi (EAV)"). **6 September:** kolom "Tipe" (`asset_type`) diganti
> "Kategori" (`asset_category`), filter dialihkan juga. **9 September (item PP):** query
> `.py` dibersihkan dari sisa `SELECT a.asset_type` (sudah tidak dipakai di kolom output,
> tapi tetap ikut dihapus supaya konsisten dengan field yang sudah tidak eksis), filter
> `.json` (`fieldname: "asset_type"`) diganti jadi filter `asset_category` (Link ke
> `NextHD Asset Category`). File: `nexthd/next_helpdesk/report/detail_aset_lengkap/`.

> ⚠️ **Pending:** `test_nexthd_asset.py` masih punya test method yang meng-assert field lama
> (`.brand`, `.model`, `.serial_number`, dan sejak 9 September juga `.asset_type` yang
> **sudah dihapus total**, bukan cuma hidden) — akan gagal kalau dijalankan. Belum direvisi
> (item W2 di `docs/SUMMARY.md`), cocok untuk task Devin terpisah, prioritas rendah karena
> tidak mempengaruhi produksi live.

### Detail Field: NextHD Change Request

```
naming_series         → CHG-.YY.MM.-.####.
title                 → Data
status                → Select: Draft / Diajukan / Direview / Disetujui / Ditolak / Implementasi / Selesai / Ditutup
change_type           → Select: Standard / Normal / Emergency
risk_level            → Select: Rendah / Sedang / Tinggi
related_problem       → Link: NextHD Problem
related_asset         → Link: NextHD Asset
implementation_plan   → Text Editor
rollback_plan         → Text Editor
activity_log          → Table: NextHD Activity Log (ditambahkan PR #12, 7-8 September 2026)
tanggal_dibuat        → Datetime (hidden, read_only — ditambahkan 5-6 September 2026)
tanggal_diedit        → Datetime (hidden, read_only — idem)
```

### Detail Field: NextHD Known Error

```
naming_series         → KE-.YY.MM.-.####.
title                 → Data (required)
symptom               → Text Editor   (BUKAN root_cause — nama field beda dari Problem)
workaround            → Text Editor
related_problem       → Link: NextHD Problem   (BUKAN "problem")
photos                → Table: NextHD Photo Link
activity_log          → Table: NextHD Activity Log (ditambahkan PR #12, 7-8 September 2026)
tanggal_dibuat        → Datetime (hidden, read_only — ditambahkan 5-6 September 2026)
tanggal_diedit        → Datetime (hidden, read_only — idem)
```

> ⚠️ **Tidak ada field `status`** di Known Error — jangan asumsikan ada.
> Field `root_cause` di Problem di-mapping ke `symptom` di Known Error (nama beda, isi sama).
>
> **Tidak ada field asset langsung** di Known Error — ini keputusan sengaja (2026-08-15). Asset
> terkait ditelusuri lewat `related_problem` → `related_asset` milik Problem tersebut.

### Detail Field: NextHD Photo

```
naming_series      → IMG-.YY.MM.-.####  (item FF, 28 Agustus 2026)
photo_title        → Data (title_field)
location           → Data
category           → Link: NextHD Category
```

> Referensi balik "dipakai di mana" **sengaja tidak** disimpan sebagai field statis (1 foto
> bisa dipakai ulang di >1 dokumen) — dipakai `get_dashboard_data()` (badge "Connections",
> real-time dari child table `NextHD Photo Link` di 4 parent: Ticket/Asset/Problem/Known
> Error) sebagai gantinya.

**Warna List View (item PP, 9 September 2026):** `category` diberi indicator pill via
`formatters` di `nexthd_photo_list.js` — hash-color sama seperti `asset_category` (Link ke
master yang bisa bertambah kapan saja, jadi tidak dipakai mapping fix).

### Detail Field: NextHD User Profile

```
user                  → Link: User (1-1 dengan User Frappe)
telegram_chat_id      → Data (diisi otomatis saat user link akun via bot /start)
telegram_username     → Data (opsional)
preferred_language    → Select: ID / EN
department            → Data
phone_internal        → Data
```

### Detail Field: NextHD SLA Policy

```
priority              → Select: Kritis / Tinggi / Sedang / Rendah
response_time_minutes → Int
resolution_time_minutes → Int
business_hours        → Link: NextHD Business Hours
```

---

## 3.2 Custom Report — Daftar Lengkap (diperbarui 9 September 2026)

| Report | Tipe | Sumber Data | Ditambahkan/Diubah Terakhir |
|---|---|---|---|
| Tiket per Bulan | Query/Script Report | NextHD Ticket | — |
| Tiket per Agent | Query/Script Report | NextHD Ticket | — |
| Tiket per Kategori | Query/Script Report | NextHD Ticket | — |
| Tiket per Prioritas | Query/Script Report | NextHD Ticket | — |
| SLA Compliance Bulanan | Query/Script Report | NextHD Ticket | — |
| Aset Bermasalah | Query/Script Report | NextHD Asset | — |
| Detail Tiket Lengkap | Script Report | NextHD Ticket | 6 September (kolom Tag) |
| Detail Aset Lengkap | Script Report | NextHD Asset + NextHD Asset Attribute (EAV) | **9 September** (query & filter `asset_type` dihapus total, ganti `asset_category`) |
| Detail Problem Lengkap | Script Report | NextHD Problem | — |
| Detail Known Error Lengkap | Script Report | NextHD Known Error | — |
| Detail Change Request Lengkap | Script Report | NextHD Change Request | — |
| Riwayat Progress Tiket | Query Report (`is_standard=Yes`) | `JOIN` NextHD Ticket Worklog + NextHD Ticket | 6 September |

**Detail "Riwayat Progress Tiket":** menggabungkan semua baris `NextHD Ticket Worklog`
lintas semua tiket dalam satu tabel — kolom No Tiket, Subjek, Status, Waktu, Teknisi,
Aktivitas, Hasil, Durasi Menit. Default `ORDER BY waktu DESC`. File:
`nexthd/next_helpdesk/report/riwayat_progress_tiket/`. Muncul juga sebagai shortcut
dashboard di Workspace "NextHD Report".

**Kolom "Tag" di "Detail Tiket Lengkap":** via `LEFT JOIN tabTag Link` + `GROUP_CONCAT` —
menampilkan tag native Frappe (bukan field kustom). Filter `tag` tersedia di UI report.

---

## 4. Permissions

| Role | Read | Write | Create | Delete |
|---|---|---|---|---|
| IT Manager | ✅ | ✅ | ✅ | ✅ |
| Agent Manager | ✅ | ✅ | ✅ | ❌ |
| Agent | ✅ | ✅ | ❌ | ❌ |
| IT Auditor | ✅ | ❌ | ❌ | ❌ |

**Khusus NextHD Ticket:** Requester (read, write, create dengan `if_owner=1`)

> ⚠️ Permission di `tabDocPerm` di DB saja — TIDAK bisa disimpan ke fixtures JSON
> karena production bukan developer_mode. `doc.save()` akan throw `CannotCreateStandardDoctypeError`.
> **Selalu pakai SQL INSERT langsung ke `tabDocPerm`.**

> **Role assignment ke user individual** via UI: buka **User** → section **Roles** → centang role → Save.
> Ini beda dengan permission doctype di atas (yang wajib SQL).

---

## 5. Sistem User Tanpa Email

### Alasan
Sistem hanya untuk karyawan internal. Frappe mewajibkan field email, tapi email nyata tidak dipakai — hosting hanya menyediakan kuota terbatas untuk email asli, tidak cukup untuk seluruh karyawan.

### Pendekatan Teknis

```
1. Saat buat User baru:
   - Field "email" diisi otomatis via hook:
     format: {username}@ciptamebel.co.id   ← DIUBAH 2026-08-20, sebelumnya @noemail.internal
     contoh: efendy@ciptamebel.co.id
   - Domain SAMA dengan domain kantor asli, TAPI mailbox-nya dummy — tidak eksis, tidak bisa
     menerima mail sungguhan.
   - Set "Send Welcome Email" = False

2. Login:
   - User login pakai Username (bukan email)

3. Reset Password:
   - TIDAK bisa via "forgot password" email
   - Solusi: Admin reset manual dari backend:
     bench --site desk.ciptamebel.co.id set-password <username>
   - Alternatif lanjutan: OTP reset via Telegram bot
```

**File:** `nexthd/next_helpdesk/utils/email_helper.py`
**Hook:** `before_insert` pada Doctype **User**

---

## 6. Schema Tabel Penting

Schema ini sudah diverifikasi langsung dari `DESCRIBE tabNama` — jangan diasumsikan.

### tabDesktop Icon
```
name, label, icon_type, link_type, link_to, parent_icon,
sidebar, icon_image, standard, app, icon, logo_url, link,
hidden, restrict_removal, bg_color
```
> ❌ Tidak ada kolom: `color`, `_id`

### tabWorkspace Sidebar
```
name, title, app, module, standard, for_user,
header_icon, module_onboarding
```

### tabWorkspace Sidebar Item
```
name, idx, label, link_type, icon, type, link_to,
child, navigate_to_tab, url, collapsible, indent,
keep_closed, show_arrow, filters, route_options,
parent, parentfield, parenttype
```

### tabWorkspace Number Card
```
name, number_card_name, label,
parent, parentfield, parenttype
```
> ⚠️ Kolom kunci: `number_card_name` (BUKAN `card_name`)

### tabNumber Card
```
name, label, document_type, function, filters_json,
is_public, color, background_color, show_percentage_stats,
stats_time_interval, is_standard, module, type,
aggregate_function_based_on
```

### tabDocPerm
```
name, role, read, write, create, delete,
submit, cancel, amend, report, export, import,
share, print, email, permlevel,
parent, parentfield, parenttype
```

### tabWorkspace
```
name, title, module, app, public, is_hidden, sequence_id,
content, for_user, parent_page, restrict_to_domain,
label, icon, indicator_color
```
> ❌ Tidak ada kolom: `number_cards` (disimpan di child table `tabWorkspace Number Card`)

### tabDocType
> ❌ Tidak ada kolom: `field_order` — urutan field murni dikontrol lewat kolom `idx` di
> `tabDocField`, diambil via `frappe.get_meta(doctype).fields` diurutkan manual by `idx`.
>
> ⚠️ Kolom `naming_rule` — **HARUS** salah satu dari daftar opsi valid Frappe v16
> (`""`, `"Set by user"`, `"Autoincrement"`, `"By fieldname"`, `"By \"Naming Series\"
> field"`, `"Expression"`, `"Expression (old style)"`, `"Random"`, `"UUID"`, `"By
> script"`). Nilai `"By Series"` (tanpa tanda kutip di sekitar "Naming Series") adalah
> **peninggalan versi lama, tidak valid** — ditemukan di 5 DocType, diperbaiki 9 September
> 2026 (lihat §3 tabel DocType di atas). `doc.save()` penuh akan gagal `ValidationError`
> kalau kolom ini masih berisi nilai usang tersebut.

### tabDocField
> ❌ Tidak ada kolom: `insert_after` (berbeda dari dokumentasi umum Frappe). Urutan tampilan
> field murni dikontrol lewat kolom `idx` — angka lebih kecil tampil lebih dulu.

### tabSeries
```
name, current
```
> ⚠️ Counter penomoran dokumen (naming series). **Bisa tidak sinkron dari data fisik**
> kalau ada insert manual/import yang tidak lewat jalur normal Frappe. Cara cek & sinkron
> ada di `docs/BUG_HISTORY.md §3`.

### tabNextHD Asset Attribute (EAV, ditambahkan 28 Agustus 2026)
```
name, creation, modified, modified_by, owner, docstatus, idx,
attribute_name, attribute_value, unit,
parent, parentfield, parenttype,
brand, serial_number, sumber, catatan
```

### tabNextHD Ticket Worklog (ditambahkan PR #11, 31 Agustus 2026)
```
name, creation, modified, modified_by, owner, docstatus, idx,
waktu, teknisi, aktivitas, hasil, durasi_menit,
parent, parentfield, parenttype
```

### tabNextHD Activity Log (ditambahkan PR #12, 7-8 September 2026)
```
name, creation, modified, modified_by, owner, docstatus, idx,
waktu, jenis, catatan, dibuat_oleh, related_doctype, related_document,
parent, parentfield, parenttype
```
> Parent bisa `NextHD Problem`, `NextHD Change Request`, atau `NextHD Known Error` (dibedakan
> via kolom `parenttype`). Lihat §3 "Detail Field: NextHD Activity Log" untuk penjelasan
> tiap kolom, dan `docs/SUMMARY.md` item OO untuk riwayat bug yang sudah diperbaiki.

### tabTag Link (bawaan Frappe, dipakai untuk fitur Tag native — dikonfirmasi relevan 6 September 2026)
```
name, creation, modified, modified_by, owner, docstatus,
tag, document_type, document_name
```
> Tabel bawaan Frappe yang menyimpan tag native (`Tag Link` + `_user_tags`). Di-`JOIN` di
> report "Detail Tiket Lengkap" untuk kolom "Tag".

---

## 7. Bahasa Indonesia — Label Referensi

| Istilah Inggris (internal/dev) | Label Indonesia (tampil ke user) |
|---|---|
| Ticket | Tiket |
| Priority | Prioritas |
| Open | Baru |
| In Progress | Sedang Dikerjakan |
| Pending User | Menunggu User |
| Resolved | Selesai |
| Closed | Ditutup |
| Assigned To | Ditugaskan Ke |
| Requested By | Dilaporkan Oleh |
| Category | Kategori |
| Problem | Masalah |
| Root Cause | Akar Masalah |
| Known Error | Kesalahan yang Diketahui |
| Change Request | Permintaan Perubahan |
| Asset | Aset |
| Critical / High / Medium / Low | Kritis / Tinggi / Sedang / Rendah |
| NextHD Ticket | Tiket NextHD |
| NextHD Problem | Masalah NextHD |
| NextHD Change Request | Permintaan Perubahan NextHD |
| NextHD Settings | Pengaturan NextHD |
| NextHD Team | Tim NextHD |
| NextHD Asset | Aset NextHD |
| NextHD Category | Kategori NextHD |
| NextHD SLA Policy | Kebijakan SLA NextHD |
| NextHD Business Hours | Jam Kerja NextHD |
| NextHD User Profile | Profil Pengguna NextHD |
| NextHD Known Error | Kesalahan Dikenal NextHD |
| NextHD Service Catalog | Katalog Layanan NextHD |

> Gunakan Frappe Translation system (`bench --site [site] build-message-files` + file `.csv` di `nexthd/translations/id.csv`) untuk maintain terjemahan secara terpisah dari kode.

---

*Dokumen ini dikelola oleh Claude. Update terakhir: 2026-09-09 — item PP: `asset_type`
dihapus total (metadata+kolom fisik, sebelumnya cuma hidden sejak item NN), fix `naming_rule`
usang di 5 DocType, tabel `NextHD Activity Log` (item OO/PR #12) ditambahkan ke §3/§6, warna
List View (`formatters`) didokumentasikan per DocType, struktur folder `public/js/`
diperbarui.*

---

## Catatan Tambahan — Update 2026-08-28

### Field `related_asset` di NextHD Problem — Riwayat Schema Drift

Field ini **sempat hilang dari metadata** (28 Agustus 2026) meski kolom fisik & data di database tetap aman — root cause: sebelumnya hanya dilindungi fixture `DocField` terpisah yang sudah tidak terdaftar di `hooks.py`. Sekarang sudah dipindah permanen ke `nexthd_problem.json` (field_order + fields[], posisi setelah `category`), konsisten dengan field lain di DocType ini. Detail lengkap investigasi & fix di `docs/BUG_HISTORY.md`.

**Pelajaran untuk field custom baru:** field yang ditambahkan manual via SQL raw HARUS langsung ditulis juga ke file `.json` DocType-nya sendiri — jangan hanya mengandalkan fixture `DocField` global terpisah sebagai satu-satunya pelindung dari `bench migrate`. **Pola yang sama terulang untuk `tanggal_dibuat`/`tanggal_diedit` (7-8 September) — lihat catatan di §3.**

### Pola Navigasi Timbal-Balik Antar Dokumen (Forward-Link)

Karena `get_dashboard_data()`/`internal_links` Frappe **tidak mendukung** forward Link field biasa (dikonfirmasi 28 Agustus, lihat `docs/BUG_HISTORY.md`), navigasi antar dokumen yang berelasi one-to-one dipakai lewat tombol Client Script kustom (`frm.add_custom_button` + `frappe.set_route`), dan untuk relasi one-to-many (Problem → banyak Ticket) dipakai List View dengan filter. Daftar lengkap Client Script navigasi ada di `docs/BUG_HISTORY.md`.
