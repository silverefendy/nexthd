# NextHD — Session Notes & Handover Document
**Tanggal:** 9–11 Agustus 2026  
**Repo:** https://github.com/silverefendy/nexthd  
**Branch:** main  
**Dibuat untuk:** Serah terima ke sesi Claude/Devin berikutnya

---

## 1. Infrastruktur & Stack

| Komponen | Detail |
|---|---|
| VM | erpnext — Tailscale IP 100.64.0.14 |
| User | it — working dir `/home/it/frappe` |
| Frappe | v16.30.0 |
| Custom App | nexthd v0.0.1 |
| Site | desk.ciptamebel.co.id |
| Route | nginx di CML-VPS 103.103.22.231 → VM erpnext via Tailscale |
| SSL | certbot, valid sampai 5 Nov 2026 |
| Node.js | nvm di `/home/it/.nvm/versions/node/v24.19.0/bin/node` — hardcoded di supervisor |
| Akun operasional | support@ciptamebel.co.id |
| Akun admin | Administrator — email: admin@example.com |
| Pemakai sistem | Hanya IT (satu orang) sebagai Administrator |

---

## 2. DocType yang Ada

### Non-Child DocType (12) — semua punya route dan permission

| DocType | Route |
|---|---|
| NextHD Asset | nexthd-asset |
| NextHD Business Hours | nexthd-business-hours |
| NextHD Category | nexthd-category |
| NextHD Change Request | nexthd-change-request |
| NextHD Known Error | nexthd-known-error |
| NextHD Problem | nexthd-problem |
| NextHD Service Catalog | nexthd-service-catalog |
| NextHD Settings | nexthd-settings |
| NextHD SLA Policy | nexthd-sla-policy |
| NextHD Team | nexthd-team |
| NextHD Ticket | nexthd-ticket |
| NextHD User Profile | nexthd-user-profile |

### Child DocType (2) — istable=1, TIDAK perlu di sidebar

| DocType | Parent |
|---|---|
| NextHD Team Member | NextHD Team |
| NextHD Problem Ticket | NextHD Problem |

---

## 3. Field Penting per DocType

### NextHD Ticket
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
affected_asset        → Link: NextHD Asset  ← DITAMBAHKAN sesi ini
sla_response_by       → Datetime (read_only)
sla_resolution_by     → Datetime (read_only)
sla_warning_sent      → Check (read_only)
resolved_on           → Datetime (read_only)
closed_on             → Datetime (read_only)
related_problem       → Link: NextHD Problem
attachments           → Attach
```

### NextHD Problem
```
naming_series         → PRB-2026-####
title                 → Data (required)
status                → Select: Terbuka / Investigasi / Known Error / Selesai / Ditutup
priority              → Select: Kritis / Tinggi / Sedang / Rendah  ← DITAMBAHKAN
category              → Link: NextHD Category  ← DITAMBAHKAN
root_cause            → Text Editor
workaround            → Text Editor  ← DITAMBAHKAN
known_error           → Link: NextHD Known Error (depends_on: status = Known Error)  ← DITAMBAHKAN
change_request        → Link: NextHD Change Request  ← DITAMBAHKAN
related_tickets       → Table: NextHD Problem Ticket
```

### NextHD Asset
```
naming_series         → AST-2026-####
asset_name            → Data (required)
asset_type            → Select: Laptop / PC / Server / Network Device / Printer / Lainnya
location              → Data
assigned_to           → Link: User
status                → Select: Aktif / Rusak / Diperbaiki / Dihapus
purchase_date         → Date
warranty_until        → Date

# Field dinamis — muncul sesuai asset_type:
[PC / Laptop / Server]
  brand, model, serial_number, cpu, ram, storage, os, peripheral_notes

[Network Device]
  net_brand, net_model, net_serial_number, ip_address, mac_address, device_role, net_notes

[Printer]
  printer_brand, printer_model, printer_serial_number, printer_type, printer_notes

[Lainnya]
  other_description
```

---

## 4. Permissions (tabDocPerm)

Semua 12 DocType sudah punya permission. Role standar:

| Role | Read | Write | Create | Delete |
|---|---|---|---|---|
| IT Manager | ✅ | ✅ | ✅ | ✅ |
| Agent Manager | ✅ | ✅ | ✅ | ❌ |
| Agent | ✅ | ✅ | ❌ | ❌ |
| IT Auditor | ✅ | ❌ | ❌ | ❌ |

**Khusus NextHD Ticket:** Requester (rwc dengan if_owner=1)

> ⚠️ **PENTING:** Permission di `tabDocPerm` di DB saja — TIDAK bisa disimpan ke fixtures JSON
> karena production bukan developer_mode. `doc.save()` akan throw `CannotCreateStandardDoctypeError`.
> Selalu pakai SQL INSERT langsung ke `tabDocPerm`.

---

## 5. Frappe v16 — Desktop vs Workspace (KRITIS)

Ini bagian yang paling membingungkan di v16 karena ada 3 sistem berbeda:

### A. `/desk/desktop` — Halaman Desktop (App Icons)

Dikontrol oleh **`tabDesktop Icon`** dan **`add_to_apps_screen`** hook.

```
tabDesktop Icon — kolom penting:
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

**Untuk child icon (isi folder):**
```python
icon_type   = 'Link'
link_type   = 'Workspace Sidebar'
link_to     = 'NextHD'            # nama Workspace Sidebar tujuan
parent_icon = 'NextHD'            # nama Desktop Icon kepala
app         = 'nexthd'
standard    = 0
```

**`add_to_apps_screen` hook — WAJIB ADA** di `hooks.py`:
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
Hook ini dipakai oleh `frappe/boot.py` `load_desktop_data()` untuk generate `bootinfo.app_data`.
Tanpa hook ini, nexthd tidak muncul sama sekali di desktop meski ada di `tabDesktop Icon`.

**Logo WAJIB ADA** di `/home/it/frappe/apps/nexthd/nexthd/public/logo.svg`.
Tanpa file logo, hook tidak terbaca oleh Frappe.

### B. `/desk/nexthd` — Workspace Page

Dikontrol oleh **`tabWorkspace`** dan file JSON di `nexthd/next_helpdesk/workspace/nexthd/nexthd.json`.

```
tabWorkspace — field penting:
  name, title, module, app, public, is_hidden, sequence_id,
  content (JSON string), roles (via tabHas Role)
```

**`content` field** adalah JSON string yang dikontrol via UI atau langsung DB.
Format: array of objects dengan type: `header`, `shortcut`, `card`, `quick_list`

> ⚠️ **JANGAN** generate content sebagai string literal dengan escape manual.
> **SELALU** build sebagai Python dict/list lalu `json.dumps()` sekali.
> Double-escape (`\\\\"h4\\\\"`) akan menyebabkan `SyntaxError` di browser.

**Number Cards di workspace:**
- Buat dulu di `tabNumber Card` (via SQL)
- Referensikan di `content` via `card_name`
- Isi juga `number_card_name` di `tabWorkspace Number Card` (child table)
- Kolom di `tabWorkspace Number Card`: `name, number_card_name, label, parent, parentfield, parenttype`

### C. Sidebar Kiri — `tabWorkspace Sidebar`

Dikontrol oleh **`tabWorkspace Sidebar`** dan **`tabWorkspace Sidebar Item`**.

```
tabWorkspace Sidebar — kolom:
  name, title, app, module, standard, for_user

tabWorkspace Sidebar Item — kolom:
  name, idx, label, link_type, icon, type, link_to,
  child, collapsible, indent, parent, parentfield, parenttype
```

> `standard=1` → sidebar tidak bisa diedit via UI. Set `standard=0` via SQL.

### D. Fixtures — WAJIB untuk mencegah penghapusan saat `bench migrate`

`bench migrate` akan hapus Desktop Icon dan Workspace Sidebar yang tidak ada di fixtures.
Tambahkan ke `hooks.py`:

```python
fixtures = [
    {"dt": "Workflow", "filters": [["name", "in", [
        "NextHD Ticket", "NextHD Problem", "NextHD Change Request"
    ]]]},
    {"dt": "Workflow Transition", "filters": [["parent", "in", [
        "NextHD Ticket", "NextHD Problem", "NextHD Change Request"
    ]]]},
    {"dt": "Desktop Icon", "filters": [["app", "=", "nexthd"]]},
    {"dt": "Workspace Sidebar", "filters": [["name", "=", "NextHD"]]}
]
```

Export fixtures setelah perubahan:
```bash
bench --site desk.ciptamebel.co.id export-fixtures --app nexthd
```

> ⚠️ `Workflow State` TIDAK perlu di fixtures — tidak punya kolom `workflow`, sifatnya global.

---

## 6. Workspace Dashboard — Konfigurasi Saat Ini

```
Sections:
  [Operasional]
    Shortcuts: New Ticket, All Tickets, NextHD Problem, NextHD Change Request

  [Statistik Tiket]
    Number Cards (6):
      Tiket Baru           → COUNT NextHD Ticket WHERE status = Baru
      Tiket Sedang Dikerjakan → COUNT WHERE status = Sedang Dikerjakan
      Menunggu User        → COUNT WHERE status = Menunggu User
      Tiket Selesai Bulan Ini → COUNT WHERE status = Selesai AND modified = this month
      Tiket Prioritas Kritis → COUNT WHERE priority = Kritis AND status NOT IN Selesai,Ditutup
      Problem Terbuka      → COUNT NextHD Problem WHERE status NOT IN Selesai,Ditutup

  [Tiket Terbaru]
    Quick Lists (2):
      Open Tickets   → NextHD Ticket WHERE status NOT IN Selesai,Ditutup
      Critical Tickets → NextHD Ticket WHERE priority = Kritis AND status NOT IN Selesai,Ditutup

  [Konfigurasi]
    Shortcuts: NextHD Settings, NextHD SLA Policy, NextHD Team, NextHD Category
```

---

## 7. Pola Kerja Kritis — WAJIB DIIKUTI

### ✅ BENAR — Selalu pakai file script + redirect
```bash
# Langkah 1: tulis ke file
cat > /home/it/nama_script.py << 'EOF'
import frappe

results = []
for item in list_data:
    results.append(str(item))

# WAJIB: statement di level 0 setelah loop
print("\n".join(results))
print("DONE")
EOF

# Langkah 2: jalankan via redirect
bench --site desk.ciptamebel.co.id console < /home/it/nama_script.py
```

### ❌ SALAH — Jangan paste langsung ke console interaktif
IPython akan error IndentationError atau loop tidak jalan sama sekali.

### Aturan lain yang wajib:
- `continue` / `break` dalam loop di console → error. Gunakan kondisi if/else sebagai gantinya
- `doc.save()` → selalu gagal di production. Pakai SQL INSERT/UPDATE + `frappe.db.commit()`
- Setelah perubahan DB langsung: **export fixture → git commit → git push**
- `bench migrate` → bisa hapus Desktop Icon dan Workspace Sidebar yang tidak di fixtures
- Cek schema tabel dulu (`DESCRIBE tabNama`) sebelum INSERT — jangan asumsikan kolom
- MariaDB versi lama tidak support `LIMIT` di subquery `IN`
- JSON content workspace: generate via `json.dumps()` Python, BUKAN string literal manual
- `Workflow State` tidak punya kolom `workflow` — jangan filter berdasarkan itu

---

## 8. Bug & Status Penyelesaian

### ✅ SELESAI

| # | Masalah | Penyelesaian |
|---|---|---|
| 1 | "Next Helpdesk" workspace muncul di sidebar | Patch Python hapus via `frappe.db.delete()` |
| 2 | hooks.py syntax error setelah `sed` | Fix dengan script Python yang comment semua baris blok |
| 3 | nexthd.json terpotong saat `cat EOF` | Tulis ulang via `json.dumps()` Python |
| 4 | patches.txt dua patch tergabung satu baris | Python `str.replace()` tambah newline |
| 5 | `add_to_apps_screen` di-comment, desktop kosong | Un-comment, tambah logo.svg |
| 6 | Logo tidak ada → hook tidak terbaca | Buat `nexthd/public/logo.svg` |
| 7 | Desktop Icon dihapus tiap `bench migrate` | Tambah ke fixtures di hooks.py |
| 8 | Workspace Sidebar dihapus tiap `bench migrate` | Tambah ke fixtures di hooks.py |
| 9 | Workspace Sidebar `standard=1` tidak bisa diedit | `UPDATE tabWorkspace Sidebar SET standard=0` |
| 10 | Permission missing — 4 DocType tidak bisa dibuka | SQL INSERT ke `tabDocPerm` |
| 11 | DocType error "Not found" saat diklik dari sidebar | Fix permission (no.10) |
| 12 | Desktop icon NextHD buka tab baru | `link_type = Workspace Sidebar`, `link = NULL` |
| 13 | Number Card tidak muncul di workspace | UPDATE `tabWorkspace Number Card` SET `number_card_name` |
| 14 | Workspace content double escape → SyntaxError browser | Generate via `json.dumps()` bukan string literal |
| 15 | Fixtures Workflow State error kolom 'workflow' | Hapus Workflow State dari fixtures |
| 16 | NextHD Asset field statis saja | Tambah field dinamis per asset_type dengan `depends_on` |
| 17 | NextHD Ticket tidak ada link ke Asset | Tambah field `affected_asset` → Link: NextHD Asset |
| 18 | NextHD Problem field terlalu minimal | Tambah priority, category, workaround, known_error, change_request |

### ⚠️ BELUM DIVERIFIKASI (cek pertama kali sesi berikutnya)

| # | Item | Yang Perlu Dicek |
|---|---|---|
| 1 | Number cards "Statistik Tiket" | Buka `/desk/nexthd` → apakah angka muncul di cards |
| 2 | Desktop icon tidak buka tab baru | Klik ikon NextHD di `/desk/desktop` |
| 3 | NextHD Ticket form baru | Buka New Ticket → cek field `affected_asset` dan `service_catalog` muncul |
| 4 | NextHD Problem form baru | Buka Problem → cek field `workaround`, `known_error`, `change_request` muncul |

### 🔴 BELUM DIKERJAKAN

| # | Fitur | Keterangan |
|---|---|---|
| 1 | Problem → spawn Known Error button | Butuh Python controller + JS client script |
| 2 | SLA Policy enforcement | Scheduler ada tapi logika Python belum diverifikasi |
| 3 | Custom reports | Per kategori, prioritas, bulan — butuh Query Report Python |
| 4 | Email notification templates | Belum ada |
| 5 | User portal Requester | Submit tiket sendiri via portal |
| 6 | Workflow verification | 3 Workflow di fixtures belum diverifikasi state machine-nya |
| 7 | Decommission VM cml-helpdesk lama | Tailscale IP 100.64.0.13 + cleanup nginx/Headscale di CML-VPS |
| 8 | Role assignment ke user spesifik | support@ciptamebel.co.id belum punya role IT Manager/Agent |

---

## 9. Schema Tabel Penting (Sudah Diverifikasi)

### tabDesktop Icon
```
name, label, icon_type, link_type, link_to, parent_icon,
sidebar, icon_image, standard, app, icon, logo_url, link,
hidden, restrict_removal, bg_color
```
> Tidak ada kolom: `color`, `_id`

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
> Kolom kunci: `number_card_name` (bukan `card_name`)

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

### tabWorkspace (relevant columns)
```
name, title, module, app, public, is_hidden, sequence_id,
content, for_user, parent_page, restrict_to_domain,
label, icon, indicator_color
```
> Tidak ada kolom: `number_cards` (disimpan di child table `tabWorkspace Number Card`)

---

## 10. Referensi

- Frappe v16 migration guide: https://github.com/frappe/frappe/wiki/Migrating-to-version-16
- Apps page hook docs: https://docs.frappe.io/framework/user/en/apps-page
- Frappe Discuss: https://discuss.frappe.io
- GitHub repo nexthd: https://github.com/silverefendy/nexthd
- GitHub repo visitor_management (referensi): https://github.com/silverefendy/visitor_management
  - VMS pakai `add_to_apps_screen` di-comment — desktop muncul karena mekanisme lain
  - Workspace JSON VMS punya `roles` terisi — inilah yang membuat workspace muncul di sidebar
