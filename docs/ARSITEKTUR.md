# NextHD — Arsitektur & Referensi Teknis

> Referensi statis: infrastruktur, struktur app, DocType/field, permissions, schema DB, label ID.
> Jarang berubah kecuali ada penambahan DocType atau perubahan infrastruktur.
>
> **Last updated:** 2026-08-12 10:00 WIB

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
| NextHD Asset | nexthd-asset | `AST-2026-####` |
| NextHD Business Hours | nexthd-business-hours | — |
| NextHD Category | nexthd-category | — |
| NextHD Change Request | nexthd-change-request | `CHG-2026-####` |
| NextHD Known Error | nexthd-known-error | `KE-2026-####` |
| NextHD Problem | nexthd-problem | `PRB-2026-####` |
| NextHD Service Catalog | nexthd-service-catalog | `SVC-2026-####` |
| NextHD Settings | nexthd-settings | — (Single) |
| NextHD SLA Policy | nexthd-sla-policy | — |
| NextHD Team | nexthd-team | — |
| NextHD Ticket | nexthd-ticket | `TKT-.YYYY.-.####` |
| NextHD User Profile | nexthd-user-profile | — |

### Child DocType (2) — istable=1, tidak perlu di sidebar

| DocType | Parent |
|---|---|
| NextHD Team Member | NextHD Team |
| NextHD Problem Ticket | NextHD Problem |

---

### Detail Field: NextHD Ticket

```
naming_series         → TKT-.YYYY.-.####
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
naming_series         → PRB-2026-####
title                 → Data (required)
status                → Select: Terbuka / Investigasi / Known Error / Selesai / Ditutup
priority              → Select: Kritis / Tinggi / Sedang / Rendah
category              → Link: NextHD Category
root_cause            → Text Editor
workaround            → Text Editor
known_error           → Link: NextHD Known Error (depends_on: status = Known Error)
change_request        → Link: NextHD Change Request
related_tickets       → Table: NextHD Problem Ticket
```

> **Cara resmi mencapai status `Known Error`:** WAJIB lewat tombol custom **"Convert to
> Known Error"** di grup Actions (muncul saat status = `Investigasi` & `root_cause` terisi),
> BUKAN lewat tombol workflow. Tombol ini otomatis membuat record NextHD Known Error +
> mengisi field `known_error` di atas. Transisi workflow polos `Investigasi → Known Error`
> sudah **dihapus** (2026-08-11). Detail lengkap di `WORKFLOW.md`.

### Detail Field: NextHD Asset (dengan field dinamis)

```
naming_series         → AST-2026-####
asset_name            → Data (required)
asset_type            → Select: Laptop / PC / Server / Network Device / Printer / Lainnya
location              → Data
assigned_to           → Link: User
status                → Select: Aktif / Rusak / Diperbaiki / Dihapus
purchase_date         → Date
warranty_until        → Date

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

### Detail Field: NextHD Change Request

```
naming_series         → CHG-2026-####
title                 → Data
status                → Select: Draft / Diajukan / Direview / Disetujui / Ditolak / Implementasi / Selesai / Ditutup
change_type           → Select: Standard / Normal / Emergency
risk_level            → Select: Rendah / Sedang / Tinggi
related_problem       → Link: NextHD Problem
implementation_plan   → Text Editor
rollback_plan         → Text Editor
```

### Detail Field: NextHD Known Error

```
naming_series         → KE-2026-####
title                 → Data (required)
symptom               → Text Editor   (BUKAN root_cause — nama field beda dari Problem)
workaround            → Text Editor
related_problem       → Link: NextHD Problem   (BUKAN "problem")
```

> ⚠️ **Tidak ada field `status`** di Known Error — jangan asumsikan ada.
> Field `root_cause` di Problem di-mapping ke `symptom` di Known Error (nama beda, isi sama).
> Diverifikasi langsung dari `nexthd_known_error.json` pada 2026-08-11.

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

*Dokumen ini dikelola oleh Claude. Update terakhir: 2026-08-12 10:00 WIB.*
