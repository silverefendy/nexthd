# NextHD — Arsitektur & Referensi Teknis

> Referensi statis: infrastruktur, struktur app, DocType/field, permissions, schema DB, label ID.
> Jarang berubah kecuali ada penambahan DocType atau perubahan infrastruktur.
>
> **Last updated:** 2026-08-29 09:50 WIB

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
├── hooks.py                          ← doc_events, scheduler, fixtures, add_to_apps_screen
├── modules.txt                        ← berisi: Next Helpdesk
├── patches.txt
├── public/
│   └── logo.svg                      ← WAJIB ADA untuk add_to_apps_screen hook
└── next_helpdesk/
    ├── api/
    │   ├── __init__.py               ← WAJIB ADA (Python package)
    │   └── telegram_webhook.py       ← endpoint webhook Telegram
    ├── doctype/
    │   └── nexthd_*/                 ← 14 doctype (12 non-child + 2 child)
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

### Non-Child DocType (12+2 EAV, lihat catatan)

| DocType | Route | Naming Series |
|---|---|---|
| NextHD Asset | nexthd-asset | `AST-.YY.MM.-.####.` |
| NextHD Business Hours | nexthd-business-hours | — |
| NextHD Category | nexthd-category | — |
| NextHD Change Request | nexthd-change-request | `CHG-.YY.MM.-.####.` |
| NextHD Known Error | nexthd-known-error | `KE-.YY.MM.-.####.` |
| NextHD Problem | nexthd-problem | `PRB-.YY.MM.-.####.` |
| NextHD Service Catalog | nexthd-service-catalog | `SVC-2026-####` |
| NextHD Settings | nexthd-settings | — (Single) |
| NextHD SLA Policy | nexthd-sla-policy | — |
| NextHD Team | nexthd-team | — |
| NextHD Ticket | nexthd-ticket | `TKT-.YY.MM.-.####.` |
| NextHD User Profile | nexthd-user-profile | — |
| NextHD Asset Category | — (master, Link target dari `NextHD Asset.asset_category`) | — |

> ⚠️ **Naming series diseragamkan ke format `YY.MM` (reset bulanan) pada 2026-08-15**, termasuk
> NextHD Ticket yang sebelumnya sengaja tidak diubah (keputusan 14 Agustus dibatalkan). Dokumen
> lama dengan format sebelumnya (`YYYY` atau `2026` statis) dibiarkan apa adanya, tidak di-rename.
> Detail lengkap di `HANDOFF.md`.

> **28 Agustus 2026 (malam):** `NextHD Asset Category` (master) ditambahkan sebagai bagian dari
> migrasi `NextHD Asset` ke pola EAV. Dikerjakan oleh Efendy/Devin (commit `281072a`+`81889c0`),
> terverifikasi aman 29 Agustus. Lihat §3.1 Detail Field NextHD Asset di bawah untuk detail lengkap.

### Child DocType (3) — istable=1, tidak perlu di sidebar

| DocType | Parent |
|---|---|
| NextHD Team Member | NextHD Team |
| NextHD Problem Ticket | NextHD Problem |
| NextHD Asset Attribute | NextHD Asset (EAV, ditambahkan 28 Agustus 2026) |

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
requested_by          → Link: User (required)
assigned_to           → Link: User
team                  → Link: NextHD Team
affected_asset        → Link: NextHD Asset
sla_response_by       → Datetime (read_only)
sla_resolution_by     → Datetime (read_only)
sla_warning_sent      → Check (read_only)
resolved_on           → Datetime (read_only)
closed_on             → Datetime (read_only)
related_problem       → Link: NextHD Problem
attachments           → Attach
```

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
```

> ⚠️ **Posisi field penting:** `related_asset` sengaja diletakkan **sejajar dengan Priority/Category**
> (idx 7, sebelum section "Detail & Relasi"), BUKAN setelah field Table `related_tickets`. Field biasa
> yang ditempatkan langsung setelah field bertipe Table kadang tidak ter-render di UI meski datanya
> valid — ditemukan sebagai bug pada 2026-08-15. Lihat `POLA_KERJA_DAN_BUG.md`.

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

### Detail Field: NextHD Asset (pola EAV — direvisi total 29 Agustus 2026)

> ⚠️ **Riwayat perubahan struktur (baca dulu sebelum mengasumsikan field apa pun ada/tidak ada):**
> 1. **Awal (7 Agustus – 28 Agustus siang):** field terstruktur statis per `asset_type`
>    (`brand`, `model`, `serial_number`, `cpu`, `ram`, dst — lihat riwayat di git kalau perlu).
> 2. **28 Agustus malam (commit `281072a`+`81889c0`, Efendy/Devin):** ditambahkan field
>    `asset_category` (Link, `reqd=1`) dan `asset_attributes` (Table → `NextHD Asset Attribute`,
>    EAV) **di samping** field lama — sempat tumpang tindih.
> 3. **29 Agustus (commit `d964531`, item JJ):** field terstruktur lama **dihapus total** dari
>    form karena sudah duplikat dengan EAV. Field catatan bebas dipertahankan.
>
> **Struktur final (29 Agustus 2026 dan seterusnya):**

```
naming_series         → AST-.YY.MM.-.####.
asset_name            → Data (required)
asset_type            → Select: Laptop / PC / Server / Network Device / Printer / Lainnya
location              → Data
assigned_to           → Link: User
status                → Select: Aktif / Rusak / Diperbaiki / Dihapus
asset_category        → Link: NextHD Asset Category (required — ditambahkan 28 Agustus 2026)
purchase_date         → Date
warranty_until        → Date

# Field catatan bebas — muncul sesuai asset_type (depends_on), DIPERTAHANKAN saat cleanup 29 Agustus:
[PC / Laptop / Server]  → peripheral_notes (Small Text)
[Network Device]        → net_notes (Small Text)
[Printer]               → printer_notes (Small Text)
[Lainnya]               → other_description (Text Editor)

photos                 → Table: NextHD Photo Link (foto reusable, PR #9)
asset_attributes       → Table: NextHD Asset Attribute (EAV, semua spesifikasi terstruktur sekarang di sini)
```

> ❌ **DIHAPUS 29 Agustus 2026 (item JJ)** — field-field ini TIDAK ADA lagi di form, meski kolom
> fisik masih ada di database (pola lama project ini: hapus dari JSON tidak menghapus kolom
> fisik, lihat `POLA_KERJA_DAN_BUG.md`): `brand`, `model`, `serial_number`, `cpu`, `ram`,
> `storage`, `os` (section PC/Laptop/Server); `net_brand`, `net_model`, `net_serial_number`,
> `ip_address`, `mac_address`, `device_role` (section Network Device); `printer_brand`,
> `printer_model`, `printer_serial_number`, `printer_type` (section Printer). Data lama semua
> sudah ter-backfill ke `asset_attributes` sebelum field dihapus (diverifikasi 6/6 record).
> **Jangan tambahkan field ini lagi** — kalau butuh spesifikasi baru, tambahkan sebagai baris di
> `asset_attributes` (EAV), bukan DocField statis baru.

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
> seperti desain awal di `DAFTAR_FITUR.md` — sudah berevolusi (via Devin, 28 Agustus malam)
> punya kolom sendiri untuk `brand`/`serial_number`/`sumber`/`catatan` per baris. Diverifikasi
> langsung via `DESCRIBE tabNextHD Asset Attribute` pada 29 Agustus. Kalau butuh field EAV
> tambahan lagi, cek dulu skema aktual di database — jangan asumsikan dari dokumentasi desain
> awal yang sudah usang.

> **Property Setter `search_fields`** (ditambahkan 2026-08-15, **diupdate 29 Agustus 2026**):
> semula `asset_name,assigned_to,serial_number`, sekarang **`asset_name,assigned_to`** — field
> `serial_number` dihapus dari `search_fields` karena field-nya sendiri sudah dihapus dari
> NextHD Asset (pindah ke EAV). Field di child table (Table/EAV) **tidak bisa** dipakai di
> `search_fields` Link, jadi searchability by serial number untuk sementara tidak tersedia di
> dropdown Link — data serial number sendiri tetap ada & bisa dilihat di `asset_attributes`.

> **Report `Detail Aset Lengkap`** ditulis ulang 29 Agustus 2026 — sekarang `LEFT JOIN` ke
> `NextHD Asset Attribute` dan menampilkan kolom "Spesifikasi (EAV)" (agregat
> `attribute_name: attribute_value` per Asset via `GROUP_CONCAT`), plus kolom Brand/Serial
> Number/Sumber/Catatan langsung dari EAV. File: `nexthd/next_helpdesk/report/detail_aset_lengkap/detail_aset_lengkap.py`.

> ⚠️ **Pending:** `test_nexthd_asset.py` masih punya beberapa test method yang meng-assert
> field lama (`asset.brand`, `.model`, `.serial_number`, dst) — akan gagal kalau dijalankan.
> Belum direvisi (item W2 di `SUMMARY.md`), cocok untuk task Devin terpisah.

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
```

### Detail Field: NextHD Known Error

```
naming_series         → KE-.YY.MM.-.####.
title                 → Data (required)
symptom               → Text Editor   (BUKAN root_cause — nama field beda dari Problem)
workaround            → Text Editor
related_problem       → Link: NextHD Problem   (BUKAN "problem")
```

> ⚠️ **Tidak ada field `status`** di Known Error — jangan asumsikan ada.
> Field `root_cause` di Problem di-mapping ke `symptom` di Known Error (nama beda, isi sama).
> Diverifikasi langsung dari `nexthd_known_error.json` pada 2026-08-11.
>
> **Tidak ada field asset langsung** di Known Error — ini keputusan sengaja (2026-08-15). Asset
> terkait ditelusuri lewat `related_problem` → `related_asset` milik Problem tersebut. Berlaku
> untuk Known Error yang dibuat dari Problem. Known Error yang dibuat manual tanpa Problem
> (kasus jarang) tidak punya jejak Asset — bisa direvisi kalau ternyata sering dibutuhkan.

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
     menerima mail sungguhan. Dipilih supaya alamat terlihat seragam/resmi, bukan supaya
     berfungsi sebagai email beneran (kuota email asli dari hosting terbatas)
   - Set "Send Welcome Email" = False

2. Login:
   - User login pakai Username (bukan email)
   - Frappe native support ini via field "username" di User doctype

3. Reset Password:
   - TIDAK bisa via "forgot password" email (karena mailbox dummy tidak menerima mail)
   - Solusi: Admin reset manual dari backend:
     bench --site desk.ciptamebel.co.id set-password <username>
   - Alternatif lanjutan: OTP reset via Telegram bot
```

**File:** `nexthd/next_helpdesk/utils/email_helper.py` — perlu dicek/diupdate formatnya ke domain baru saat implementasi berikutnya (belum diverifikasi apakah sudah otomatis terupdate atau masih hardcode `@noemail.internal`)
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

### tabDocField
> ❌ Tidak ada kolom: `insert_after` (berbeda dari dokumentasi umum Frappe). Urutan tampilan
> field murni dikontrol lewat kolom `idx` — angka lebih kecil tampil lebih dulu. Ditemukan
> 2026-08-15 saat query `SELECT insert_after` gagal dengan `Unknown column`.

### tabSeries
```
name, current
```
> ⚠️ Counter penomoran dokumen (naming series). **Bisa tidak sinkron dari data fisik**
> kalau ada insert manual/import yang tidak lewat jalur normal Frappe. Ditemukan 2026-08-20
> — `PRB-2608-` nyangkut `current=2` padahal data fisik sudah sampai `0005`. Cara cek & sinkron
> ada di `POLA_KERJA_DAN_BUG.md §3`.

### tabNextHD Asset Attribute (EAV, ditambahkan 28 Agustus 2026)
```
name, creation, modified, modified_by, owner, docstatus, idx,
attribute_name, attribute_value, unit,
parent, parentfield, parenttype,
brand, serial_number, sumber, catatan
```
> Diverifikasi langsung via `DESCRIBE` pada 29 Agustus 2026. Lihat §3 "Detail Field: NextHD Asset Attribute" untuk penjelasan tiap kolom.

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

*Dokumen ini dikelola oleh Claude. Update terakhir: 2026-08-29 09:50 WIB — Detail Field NextHD
Asset direvisi total pasca cleanup EAV (item JJ): field terstruktur lama dihapus, ditambahkan
detail skema `NextHD Asset Attribute` dan `NextHD Asset Category`. §8/§9 lama (Generalisasi
Non-IT, Wipe Data Tool) tetap di `DAFTAR_FITUR.md`, sekarang sudah terealisasi sebagian
(EAV live) — lihat `SUMMARY.md` item II/JJ untuk status terkini.*

---

## Catatan Tambahan — Update 2026-08-28

### Field `related_asset` di NextHD Problem — Riwayat Schema Drift

Field ini **sempat hilang dari metadata** (28 Agustus 2026) meski kolom fisik & data di database tetap aman — root cause: sebelumnya hanya dilindungi fixture `DocField` terpisah yang sudah tidak terdaftar di `hooks.py`. Sekarang sudah dipindah permanen ke `nexthd_problem.json` (field_order + fields[], posisi setelah `category`), konsisten dengan field lain di DocType ini. Detail lengkap investigasi & fix di `POLA_KERJA_DAN_BUG.md §5`.

**Pelajaran untuk field custom baru:** field yang ditambahkan manual via SQL raw HARUS langsung ditulis juga ke file `.json` DocType-nya sendiri — jangan hanya mengandalkan fixture `DocField` global terpisah sebagai satu-satunya pelindung dari `bench migrate`.

### Pola Navigasi Timbal-Balik Antar Dokumen (Forward-Link)

Karena `get_dashboard_data()`/`internal_links` Frappe **tidak mendukung** forward Link field biasa (dikonfirmasi 28 Agustus, lihat `POLA_KERJA_DAN_BUG.md §5`), navigasi antar dokumen yang berelasi one-to-one dipakai lewat tombol Client Script kustom (`frm.add_custom_button` + `frappe.set_route`), dan untuk relasi one-to-many (Problem → banyak Ticket) dipakai List View dengan filter. Daftar lengkap Client Script navigasi ada di `POLA_KERJA_DAN_BUG.md §5`.
