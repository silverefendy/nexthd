# NextHD — Arsitektur & Referensi Teknis

> Referensi statis: infrastruktur, struktur app, DocType/field, permissions, schema DB, label ID.
> Jarang berubah kecuali ada penambahan DocType atau perubahan infrastruktur.
>
> **Last updated:** 2026-08-20 12:20 WIB

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

### Non-Child DocType (12)

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

> ⚠️ **Naming series diseragamkan ke format `YY.MM` (reset bulanan) pada 2026-08-15**, termasuk
> NextHD Ticket yang sebelumnya sengaja tidak diubah (keputusan 14 Agustus dibatalkan). Dokumen
> lama dengan format sebelumnya (`YYYY` atau `2026` statis) dibiarkan apa adanya, tidak di-rename.
> Detail lengkap di `HANDOFF.md`.

### Child DocType (2) — istable=1, tidak perlu di sidebar

| DocType | Parent |
|---|---|
| NextHD Team Member | NextHD Team |
| NextHD Problem Ticket | NextHD Problem |

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

### Detail Field: NextHD Asset (dengan field dinamis)

```
naming_series         → AST-.YY.MM.-.####.
asset_name            → Data (required)
asset_type            → Select: Laptop / PC / Server / Network Device / Printer / Lainnya
location               → Data
assigned_to            → Link: User
status                 → Select: Aktif / Rusak / Diperbaiki / Dihapus
purchase_date          → Date
warranty_until          → Date

# Field dinamis — muncul sesuai asset_type (depends_on):
[PC / Laptop / Server]
  brand, model, serial_number, cpu, ram, storage, os, peripheral_notes

[Network Device]
  net_brand, net_model, net_serial_number, ip_address, mac_address, device_role, net_notes

[Printer]
  printer_brand, printer_model, printer_serial_number, printer_type, printer_notes

[Lainnya]
  other_description
```

> **Property Setter `search_fields`** (ditambahkan 2026-08-15): `asset_name,assigned_to,serial_number`
> — dropdown Link ke NextHD Asset (di Ticket/Problem/Change Request) sekarang bisa dicari lewat nama
> aset, nama user pemakai, atau serial number, tidak cuma nama aset saja.

> ⚠️ **Struktur ini berencana direstrukturisasi** kalau generalisasi ke domain non-IT
> dieksekusi — lihat §8 untuk desain lengkap sebelum menambah field IT-spesifik baru lagi.

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
Sistem hanya untuk karyawan internal. Frappe mewajibkan field email, tapi email nyata tidak dipakai.

### Pendekatan Teknis

```
1. Saat buat User baru:
   - Field "email" diisi otomatis via hook:
     format: {username}@noemail.internal
     contoh: efendy@noemail.internal
   - Set "Send Welcome Email" = False

2. Login:
   - User login pakai Username (bukan email)
   - Frappe native support ini via field "username" di User doctype

3. Reset Password:
   - TIDAK bisa via "forgot password" email (karena email dummy)
   - Solusi: Admin reset manual dari backend:
     bench --site desk.ciptamebel.co.id set-password <username>
   - Alternatif lanjutan: OTP reset via Telegram bot
```

**File:** `nexthd/next_helpdesk/utils/email_helper.py` (sudah ada, sudah benar)
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

## 8. Pertimbangan Generalisasi ke Domain Lain (Non-IT)

**Status:** Rencana teknis disusun (2026-08-15), **belum ada jadwal eksekusi**. Bagian ini
adalah draft siap-pakai kalau suatu saat dieksekusi — supaya tidak perlu mikir ulang struktur
dari nol.

Inti NextHD sebenarnya bukan "IT helpdesk" secara sempit — polanya adalah **ITSM generik**:
Ticket (laporan masalah) → Problem (akar masalah berulang) → Change Request (perubahan
terencana) → Known Error (basis pengetahuan solusi), semua terhubung ke Asset (objek fisik
apapun). Pola ini bisa dipakai untuk domain non-IT: bengkel/otomotif (Asset = kendaraan),
maintenance pabrik (Asset = mesin produksi), fasilitas gedung/stasiun (Asset = peralatan/unit).

**Cakupan perubahan kalau dieksekusi: TERBATAS ke seputar `NextHD Asset` saja.** Ticket,
Problem, Change Request, Known Error — 11 dari 12 DocType non-child — **tidak perlu disentuh
sama sekali**, karena strukturnya sudah generik sejak awal (tidak berasumsi IT).

### 8.1. Dua Pendekatan Teknis untuk Field Detail per Kategori

| Pendekatan | Cara Kerja | Nambah Kategori Baru |
|---|---|---|
| **A — Section per kategori** (pola yang dipakai sekarang untuk IT/Network/Printer) | Tiap kategori punya DocField tetap sendiri dengan `depends_on` | Butuh tambah DocField + edit struktur tiap kali ada kategori baru |
| **B — Atribut dinamis (key-value / EAV)** | 1 child table generik berisi baris "Nama Atribut" + "Nilai", diisi bebas sesuai kategori | **Tidak butuh perubahan struktur** — kategori baru tinggal isi atribut baru di data |

**Rekomendasi: Pendekatan B**, karena tujuan generalisasi adalah supaya nambah domain baru
(bengkel, mesin, dst) **tidak berulang kali butuh kerja teknis** seperti pendekatan A.

### 8.2. Rancangan DocType Baru

**`NextHD Asset Category`** (master, baru)
```
category_name    → Data (required) — misal: "Komputer & IT", "Kendaraan", "Mesin Produksi",
                     "Infrastruktur & Fasilitas", "Lainnya"
description       → Small Text (opsional)
```
Menggantikan `asset_type` yang sekarang Select tertutup — jadi Link ke master ini, supaya
kategori baru bisa ditambah dari UI (buat record baru), **tanpa edit kode/DocField**.

**`NextHD Asset Attribute`** (child table, baru, parent = NextHD Asset)
```
attribute_name    → Data (required) — misal: "CPU", "Plat Nomor", "Kapasitas Produksi"
attribute_value   → Data (required) — nilai bebas
unit              → Data (opsional) — misal: "GB", "Ton/Jam", "KM"
```
Setiap baris = 1 spesifikasi. Contoh isi untuk Asset kategori "Kendaraan":
```
Plat Nomor    | B 1234 CD  |
Tahun         | 2023       |
KM Terakhir   | 45000      | KM
```
Contoh isi untuk Asset kategori "Mesin Produksi":
```
Kapasitas     | 500        | unit/jam
Jam Operasi   | 12400      | jam
```

**`NextHD Asset` disederhanakan** — sisakan field yang benar-benar universal:
```
naming_series, asset_name, asset_category (Link → NextHD Asset Category, ganti asset_type),
location, assigned_to, status, purchase_date, warranty_until,
asset_attributes (Table → NextHD Asset Attribute)
```
Field IT-spesifik yang sekarang menempel langsung (`cpu`, `ram`, `os`, `mac_address`,
`printer_type`, dst) **dipindah isinya** menjadi baris-baris di `asset_attributes`, bukan
DocField terpisah lagi.

### 8.3. Rencana Migrasi Data Existing

Saat ini baru **1 record Asset live** (`AST-2608-0001`, kategori Printer) — migrasinya ringan:

1. Buat `NextHD Asset Category` dan isi kategori awal (Komputer & IT, Kendaraan, Mesin Produksi,
   Infrastruktur & Fasilitas, Lainnya)
2. Buat DocType `NextHD Asset Attribute` (child table)
3. Tambah field `asset_category` (Link) dan `asset_attributes` (Table) ke `NextHD Asset` — via
   raw SQL + `ALTER TABLE` (ikuti aturan wajib di `POLA_KERJA_DAN_BUG.md`)
4. Script migrasi: untuk tiap Asset existing, baca field lama yang terisi (`cpu`, `ram`, dst),
   insert sebagai baris `NextHD Asset Attribute`, set `asset_category` sesuai `asset_type` lama
5. Setelah data beres dan terverifikasi, hapus DocField lama yang IT-spesifik (`cpu`, `ram`,
   `mac_address`, dst) dari `NextHD Asset`
6. Export fixture (DocType baru, DocField Asset yang berubah), commit

### 8.4. Yang Tidak Berubah

- Semua field relasi ke Asset di DocType lain (`affected_asset`, `related_asset`) — tetap Link
  ke `NextHD Asset`, tidak perlu diubah sama sekali
- Ticket, Problem, Change Request, Known Error, workflow-nya, semua Client Script tombol
  otomatis — logic-nya generik (buat dokumen + isi relasi), tidak menyentuh field
  spesifik-domain

### 8.5. Kapan Layak Dieksekusi

Belum mendesak — direkomendasikan ditunda sampai ada kebutuhan nyata (misal benar-benar mau
pakai NextHD untuk domain lain), supaya struktur atribut yang dirancang benar-benar sesuai
kebutuhan real, bukan tebakan di muka. Data live yang masih sedikit sekarang (1 Asset) membuat
migrasi tetap ringan kapan pun dieksekusi — menunda tidak menambah risiko migrasi jadi lebih
berat.

---

## 9. Desain Wipe Data Testing

**Status:** Desain final disepakati 2026-08-20, **belum diimplementasi**. Bagian ini spek siap
pakai untuk Devin atau untuk Claude eksekusi langsung kapan pun kamu siap.

### 9.1. Tujuan

Sediakan cara aman menghapus data transaksional hasil testing (Ticket, Problem, Change
Request, Asset, Known Error) **tanpa** menyentuh data konfigurasi/master (Business Hours,
Holiday, SLA Policy, Team, Category, Settings, Workflow, Permission, User, Workspace) —
supaya bisa mulai "bersih" sebelum go-live produksi, tanpa perlu setup ulang dari nol.

### 9.2. Prinsip Desain

| Prinsip | Alasan |
|---|---|
| **UI checkbox per DocType**, bukan tombol "Wipe All" | Mencegah salah klik menghapus semuanya sekaligus tanpa sadar |
| **Whitelist DocType yang boleh dihapus** — bukan blacklist | Lebih aman: kalau lupa update daftar saat ada DocType baru, defaultnya TIDAK terhapus (fail-safe), bukan malah ikut terhapus |
| **Baca prefix naming_series dari DocType meta secara dinamis** | Supaya kalau prefix berubah nanti (misal `TKT` jadi sesuatu yang lain), tool tidak perlu diedit ulang |
| **Konfirmasi eksplisit sebelum eksekusi** (ketik nama DocType atau centang "saya paham ini permanen") | Aksi destruktif butuh friction sengaja |
| **Dry-run dulu (preview jumlah record) sebelum hapus beneran** | User bisa lihat dampak sebelum commit |
| **Log hasil wipe** (DocType, jumlah terhapus, waktu, siapa yang eksekusi) | Jejak audit kalau ada yang tidak sengaja |

### 9.3. DocType yang BOLEH Dihapus (Whitelist)

| DocType | Prefix naming_series |
|---|---|
| NextHD Ticket | `TKT` |
| NextHD Problem | `PRB` |
| NextHD Change Request | `CHG` |
| NextHD Asset | `AST` |
| NextHD Known Error | `KE` |
| NextHD Service Catalog | `SVC` |

### 9.4. DocType yang TIDAK BOLEH Dihapus (Selalu Dikecualikan)

NextHD Business Hours, NextHD Holiday, NextHD SLA Policy, NextHD Team, NextHD Category,
NextHD Settings, NextHD User Profile, semua Workflow/Workflow Transition/Workflow State,
semua DocPerm, User, Workspace/Workspace Sidebar. Tool **tidak diberi akses sama sekali**
ke DocType ini — bukan sekadar "tidak dicentang default", tapi memang di luar whitelist
kode, jadi tidak bisa dipilih lewat UI sekalipun.

### 9.5. Rancangan DocType Baru: `NextHD Data Wipe Tool`

Single DocType (seperti NextHD Settings) — hanya 1 record, berfungsi sebagai halaman UI.

```
doctype: Single

Field:
  target_doctypes    → Table MultiSelect / child table checklist, isi = 6 DocType whitelist di atas
  confirmation_text   → Data — user harus ketik "HAPUS DATA TESTING" persis untuk validasi
  preview_only        → Check, default 1 — kalau dicentang, tombol jalan cuma hitung tanpa hapus
  last_wipe_log        → Long Text, read_only — hasil eksekusi terakhir (JSON: doctype, jumlah, waktu, user)

Tombol (Client Script):
  "Preview Jumlah Data"  → hitung frappe.db.count() tiap DocType yang dicentang, tampilkan di dialog
  "Hapus Sekarang"        → aktif HANYA kalau confirmation_text cocok DAN preview_only tidak dicentang
```

### 9.6. Logic Python (Server-Side, Whitelist Hardcoded di Kode — BUKAN dari Input User)

```python
# nexthd/next_helpdesk/utils/data_wipe.py

ALLOWED_DOCTYPES = [
    "NextHD Ticket",
    "NextHD Problem",
    "NextHD Change Request",
    "NextHD Asset",
    "NextHD Known Error",
    "NextHD Service Catalog",
]

def get_naming_prefix(doctype):
    meta = frappe.get_meta(doctype)
    series = meta.autoname or ""
    # autoname format contoh: "naming_series:" atau field lain
    # ambil dari field naming_series di DocType meta, bukan dari data
    df = meta.get_field("naming_series")
    if df and df.options:
        first_option = df.options.split("\n")[0]
        prefix = first_option.split("-")[0].replace(".", "")
        return prefix
    return None

def preview_wipe(doctype_list):
    result = {}
    for dt in doctype_list:
        if dt not in ALLOWED_DOCTYPES:
            continue
        result[dt] = frappe.db.count(dt)
    return result

def execute_wipe(doctype_list, confirmation_text, user):
    if confirmation_text != "HAPUS DATA TESTING":
        frappe.throw("Konfirmasi tidak sesuai")
    log = []
    for dt in doctype_list:
        if dt not in ALLOWED_DOCTYPES:
            continue
        count_before = frappe.db.count(dt)
        frappe.db.sql("DELETE FROM `tab{0}`".format(dt))
        log.append({"doctype": dt, "deleted": count_before, "time": str(frappe.utils.now_datetime()), "user": user})
    frappe.db.commit()
    return log
```

> ⚠️ **`ALLOWED_DOCTYPES` sengaja HARDCODED di kode Python**, bukan dibaca dinamis dari
> input UI — supaya tidak ada cara user (bahkan admin) mengakali whitelist lewat manipulasi
> request. UI checkbox cuma bisa memilih SUBSET dari list ini, tidak bisa menambah di luar list.

> ⚠️ **Field `naming_series` dibaca dari meta DocType** (`frappe.get_meta(doctype).get_field(...)`)
> untuk keperluan tampilan info di UI (misal "akan hapus semua TKT-xxxx"), bukan untuk
> menentukan boleh-tidaknya dihapus — itu murni dari `ALLOWED_DOCTYPES` di atas.

### 9.7. Setelah Wipe — Reset Counter `tabSeries`

Berkaca dari bug 2026-08-20 (counter tidak sinkron), wipe **wajib** sekalian reset `tabSeries`
untuk prefix yang datanya baru saja dihapus, supaya penomoran mulai bersih dari awal:

```python
def reset_series_after_wipe(doctype_list):
    prefix_map = {
        "NextHD Ticket": "TKT",
        "NextHD Problem": "PRB",
        "NextHD Change Request": "CHG",
        "NextHD Asset": "AST",
        "NextHD Known Error": "KE",
        "NextHD Service Catalog": "SVC",
    }
    for dt in doctype_list:
        prefix = prefix_map.get(dt)
        if prefix:
            frappe.db.sql("DELETE FROM tabSeries WHERE name LIKE %s", (prefix + "%",))
    frappe.db.commit()
```

### 9.8. Alur Pemakaian (User-Facing)

1. Buka `NextHD Data Wipe Tool` dari Workspace
2. Centang DocType yang mau dikosongkan (misal cuma Ticket & Problem, atau semua)
3. Klik **"Preview Jumlah Data"** — dialog muncul: "Ticket: 12 record, Problem: 5 record"
4. Kalau yakin, uncentang **preview_only**, ketik `HAPUS DATA TESTING` di field konfirmasi
5. Klik **"Hapus Sekarang"** — sistem hapus data + reset counter + simpan log ke `last_wipe_log`
6. Notifikasi Telegram (opsional) ke Administrator sebagai jejak audit tambahan

### 9.9. Yang Perlu Diputuskan Sebelum Implementasi

- [ ] Siapa saja yang boleh akses `NextHD Data Wipe Tool`? (rekomendasi: hanya role IT Manager)
- [ ] Apakah butuh backup otomatis (`bench --site X backup`) sebelum wipe dieksekusi?
- [ ] Kapan waktu eksekusi pertama kali (belum ditentukan — status "nanti saja" per keputusan 2026-08-20)

---

*Dokumen ini dikelola oleh Claude. Update terakhir: 2026-08-20 12:20 WIB.*
