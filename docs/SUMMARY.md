# NextHD — Master Documentation

> **Satu file untuk semua konteks.** Gabungan dari `README.md`, `NEXTHD_SPEC.md`, `CLAUDE_REVIEW_LOG.md`, `BUGFIX_SUMMARY.md`, dan `SESSION_NOTES.md`.
>
> **Last updated:** 2026-08-11 18:15 WIB | **Repo:** `silverefendy/nexthd` | **Branch:** `main`

---

## DAFTAR ISI

1. [Project Overview](#1-project-overview)
2. [Infrastruktur & Stack](#2-infrastruktur--stack)
3. [Arsitektur Aplikasi](#3-arsitektur-aplikasi)
4. [DocType & Field Penting](#4-doctype--field-penting)
5. [Permissions](#5-permissions)
6. [Sistem User Tanpa Email](#6-sistem-user-tanpa-email)
7. [Sistem Notifikasi Telegram](#7-sistem-notifikasi-telegram)
8. [Workflow (State Machine)](#8-workflow-state-machine)
9. [Frappe v16 — Desktop & Workspace (KRITIS)](#9-frappe-v16--desktop--workspace-kritis)
10. [Workspace Dashboard — Konfigurasi Saat Ini](#10-workspace-dashboard--konfigurasi-saat-ini)
11. [Pola Kerja Kritis — WAJIB DIIKUTI](#11-pola-kerja-kritis--wajib-diikuti)
12. [Riwayat Bug & Status Penyelesaian](#12-riwayat-bug--status-penyelesaian)
13. [Schema Tabel Penting](#13-schema-tabel-penting)
14. [Bahasa Indonesia — Label Referensi](#14-bahasa-indonesia--label-referensi)
15. [Instalasi & Setup Awal](#15-instalasi--setup-awal)
16. [Referensi](#16-referensi)

---

## 1. Project Overview

| Item | Detail |
|---|---|
| **Nama App** | NextHD |
| **Tujuan** | Sistem ITSM internal (Incident, Problem, Change, Asset, Known Error, Service Catalog) untuk tim IT CML |
| **Basis** | Frappe Framework v16 murni (BUKAN ERPNext — bisa ditambah ERPNext kapan saja tanpa migrasi) |
| **User** | Karyawan internal saja (belum ada customer eksternal) |
| **Autentikasi** | Username-based login, TANPA email asli (email dummy internal sebagai placeholder wajib Frappe) |
| **Notifikasi** | Telegram Bot (utama) + In-app notification (bawaan Frappe, pelengkap) — TIDAK pakai email |
| **Bahasa UI** | Bahasa Indonesia (default) + opsi English via Frappe Translation |
| **Cakupan ITIL** | Incident, Problem, Change, Known Error, Asset/CMDB, Service Catalog |
| **Repo Git** | `silverefendy/nexthd`, branch `main` |
| **Alur Development** | Claude (kerangka & spesifikasi) → Devin (implementasi) → Claude (finishing, bugfix, review) |

### Modul Aplikasi

- Manajemen tiket insiden dan permintaan layanan
- Workflow approval untuk Change Request
- Manajemen Problem dan Known Error (ITIL-lite)
- Notifikasi real-time via Telegram Bot
- SLA monitoring otomatis (warning 30 menit sebelum breach)
- Multi-tim dengan assignment agent

---

## 2. Infrastruktur & Stack

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

## 3. Arsitektur Aplikasi

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

## 4. DocType & Field Penting

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

## 5. Permissions

| Role | Read | Write | Create | Delete |
|---|---|---|---|---|
| IT Manager | ✅ | ✅ | ✅ | ✅ |
| Agent Manager | ✅ | ✅ | ✅ | ❌ |
| Agent | ✅ | ✅ | ❌ | ❌ |
| IT Auditor | ✅ | ❌ | ❌ | ❌ |

**Khusus NextHD Ticket:** Requester (read, write, create dengan `if_owner=1`)

> ⚠️ **PENTING:** Permission di `tabDocPerm` di DB saja — TIDAK bisa disimpan ke fixtures JSON
> karena production bukan developer_mode. `doc.save()` akan throw `CannotCreateStandardDoctypeError`.
> **Selalu pakai SQL INSERT langsung ke `tabDocPerm`.**

---

## 6. Sistem User Tanpa Email

### Alasan

Sistem ini hanya untuk karyawan internal. Frappe mewajibkan field email, tapi email nyata tidak dipakai.

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

### File

- `nexthd/next_helpdesk/utils/email_helper.py` (sudah ada, sudah benar)
- Hook: `before_insert` pada Doctype **User**

---

## 7. Sistem Notifikasi Telegram

### Alur Setup Bot

```
1. Buat bot via @BotFather → dapat Bot Token
2. Simpan token di NextHD Settings (field: telegram_bot_token)
3. User link akun:
   - User klik link t.me/NamaBotAnda dari halaman profile NextHD
   - User kirim /start ke bot
   - Bot minta masukkan Username NextHD untuk verifikasi
   - chat_id disimpan ke NextHD User Profile
4. Semua notifikasi otomatis terkirim ke Telegram user tsb
```

### Trigger Notifikasi

| Event | Notifikasi ke | Isi Pesan |
|---|---|---|
| Ticket baru dibuat | Agent/Team terkait | "Tiket baru: [subject] - Prioritas: [priority]" |
| Ticket di-assign | Agent yang di-assign | "Anda ditugaskan tiket TKT-2026-XXXX" |
| Ada reply/comment baru | Pihak lain (requester/agent) | "Ada balasan baru di tiket TKT-2026-XXXX" |
| Status berubah jadi Selesai | Requester | "Tiket Anda telah diselesaikan, mohon konfirmasi" |
| SLA mendekati breach (H-30 menit) | Agent + Manager | "⚠️ SLA tiket TKT-2026-XXXX akan terlampaui" |
| Change Request perlu approval | Approver terkait | "Ada Change Request menunggu persetujuan" |

### Implementasi Teknis

- File: `nexthd/next_helpdesk/utils/telegram.py`
- Fungsi kirim: `send_telegram_message(chat_id, message)` → `requests.post()` ke `https://api.telegram.org/bot{TOKEN}/sendMessage`
- Semua notifikasi async via `frappe.enqueue()` (background jobs)
- Guard `is_telegram_enabled()` ada di semua fungsi publik
- Webhook URL: `POST /api/method/nexthd.next_helpdesk.api.telegram_webhook.telegram_webhook`

### Bug yang Sudah Difix di telegram.py

1. `frappe.requests.post()` → `requests.post()` (`frappe.requests` tidak ada)
2. `frappe.enqueue("_send_ticket_created_notification")` → wajib full path: `"nexthd.next_helpdesk.utils.telegram._send_ticket_created_notification"` (berlaku untuk 6 fungsi)
3. Parameter `link_telegram_account(user, telegram_username, verification_code)` → renamed ke `chat_id`

---

## 8. Workflow (State Machine)

### Workflow 1: NextHD Ticket

```
Baru → Sedang Dikerjakan → [Menunggu User ⇄ Sedang Dikerjakan] → Selesai → Ditutup
                                                                       ↓
                                                             (User bisa Buka Kembali)
```

| Role | Aksi yang Diizinkan |
|---|---|
| Agent | Baru → Sedang Dikerjakan, → Menunggu User, → Selesai |
| Requester | Selesai → Ditutup (konfirmasi) ATAU Selesai → Baru (buka kembali) |
| Agent Manager | Bisa override semua transisi |

### Workflow 2: NextHD Problem

```
Terbuka → Investigasi → Known Error → Selesai → Ditutup
               ↓
          Selesai (langsung, jika root cause ditemukan)
```

### Workflow 3: NextHD Change Request

```
Draft → Diajukan → Direview → [Disetujui/Ditolak] → Implementasi → Selesai → Ditutup
                                      ↓
                              Ditolak → Draft (bisa resubmit)
```

### Fixture Workflow (di repo)

File JSON di `nexthd/next_helpdesk/workflow/`:
- `nexthd_ticket_workflow.json`
- `nexthd_problem_workflow.json`
- `nexthd_change_request_workflow.json`

Didaftarkan di `hooks.py`:

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

> ⚠️ `Workflow State` TIDAK perlu di fixtures — tidak punya kolom `workflow`, sifatnya global.

---

## 9. Frappe v16 — Desktop & Workspace (KRITIS)

Ini bagian paling membingungkan. Ada 3 sistem berbeda yang saling terhubung.

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
Tanpa hook ini, nexthd tidak muncul sama sekali di desktop meski ada di `tabDesktop Icon`.

**Logo WAJIB ADA** di `/home/it/frappe/apps/nexthd/nexthd/public/logo.svg`. Tanpa file logo, hook tidak terbaca.

### B. `/desk/nexthd` — Workspace Page

Dikontrol oleh **`tabWorkspace`** dan file `nexthd/next_helpdesk/workspace/nexthd/nexthd.json`.

> ⚠️ **JANGAN** generate `content` sebagai string literal dengan escape manual.
> **SELALU** build sebagai Python dict/list lalu `json.dumps()` sekali.
> Double-escape akan menyebabkan `SyntaxError` di browser.

**Number Cards di workspace:**
- Buat dulu di `tabNumber Card` (via SQL)
- Isi `number_card_name` di `tabWorkspace Number Card` (kolom kunci: `number_card_name`, bukan `card_name`)

### C. Sidebar Kiri — `tabWorkspace Sidebar`

Dikontrol oleh **`tabWorkspace Sidebar`** dan **`tabWorkspace Sidebar Item`**.

> `standard=1` → sidebar tidak bisa diedit via UI. Fix: `UPDATE tabWorkspace Sidebar SET standard=0`

### D. Aturan Fixtures — WAJIB

`bench migrate` akan hapus Desktop Icon dan Workspace Sidebar yang tidak ada di fixtures. Selalu export setelah perubahan:

```bash
bench --site desk.ciptamebel.co.id export-fixtures --app nexthd
```

---

## 10. Workspace Dashboard — Konfigurasi Saat Ini

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

## 11. Pola Kerja Kritis — WAJIB DIIKUTI

### ✅ BENAR — Selalu pakai file script + redirect

```bash
# Langkah 1: tulis ke file
cat > /home/it/nama_script.py << 'EOF'
import frappe

results = []
for item in list_data:
    results.append(str(item))

print("\n".join(results))
print("DONE")
EOF

# Langkah 2: jalankan via redirect
bench --site desk.ciptamebel.co.id console < /home/it/nama_script.py
```

### ❌ SALAH — Jangan paste langsung ke console interaktif

IPython akan error `IndentationError` atau loop tidak jalan sama sekali.

### Aturan Wajib Lainnya

| Aturan | Penjelasan |
|---|---|
| `continue`/`break` dalam loop di console | Error. Gunakan `if/else` sebagai gantinya |
| `doc.save()` | Selalu gagal di production. Pakai SQL INSERT/UPDATE + `frappe.db.commit()` |
| Perubahan DB langsung | Export fixture → git commit → git push |
| `bench migrate` | Bisa hapus Desktop Icon dan Workspace Sidebar yang tidak di fixtures |
| Cek schema tabel | `DESCRIBE tabNama` dulu sebelum INSERT |
| MariaDB subquery | Versi lama tidak support `LIMIT` di subquery `IN` |
| JSON content workspace | Generate via `json.dumps()` Python, BUKAN string literal manual |
| `Workflow State` | Tidak punya kolom `workflow` — jangan filter berdasarkan itu |

---

## 12. Riwayat Bug & Status Penyelesaian

### ✅ SELESAI — Bugfix dari Review Claude (2026-08-07)

| # | Severity | File | Masalah | Penyelesaian |
|---|---|---|---|---|
| 1 | High | `api/__init__.py` | File tidak ada → Frappe tidak bisa import `telegram_webhook.py` | Buat file kosong |
| 2 | High | `utils/telegram.py` | `frappe.requests.post()` — `frappe.requests` tidak ada | Ganti ke `requests.post()` |
| 3 | High | `utils/telegram.py` | `frappe.enqueue()` tanpa full module path | Ganti ke full dotted path (6 fungsi) |
| 4 | High | `tasks.py` | `frappe.utils.now()` return string, bukan datetime → `TypeError` saat + timedelta | Ganti ke `now_datetime()` |
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

---

### ⚠️ BELUM DIVERIFIKASI (cek di awal sesi berikutnya)

| # | Item | Yang Perlu Dicek |
|---|---|---|
| 1 | Number cards "Statistik Tiket" | Buka `/desk/nexthd` → apakah angka muncul di cards |
| 2 | Desktop icon tidak buka tab baru | Klik ikon NextHD di `/desk/desktop` |
| 3 | NextHD Ticket form baru | Buka New Ticket → cek field `affected_asset` dan `service_catalog` muncul |
| 4 | NextHD Problem form baru | Buka Problem → cek field `workaround`, `known_error`, `change_request` muncul |

---

### 🔴 BELUM DIKERJAKAN

| # | Fitur | Keterangan |
|---|---|---|
| 1 | Problem → spawn Known Error button | Butuh Python controller + JS client script |
| 2 | SLA Policy enforcement | Scheduler ada tapi logika Python belum diverifikasi end-to-end |
| 3 | Custom reports | Per kategori, prioritas, bulan — butuh Query Report Python |
| 4 | User portal Requester | Submit tiket sendiri via portal |
| 5 | Workflow verification | 3 Workflow di fixtures belum diverifikasi state machine-nya |
| 6 | Decommission VM cml-helpdesk lama | Tailscale IP `100.64.0.13` + cleanup nginx/Headscale di CML-VPS |
| 7 | Role assignment ke user spesifik | `support@ciptamebel.co.id` belum punya role IT Manager/Agent |
| 8 | Pesan notifikasi Telegram i18n | Hardcoded di `telegram.py`, belum pakai `frappe._()` |

---

## 13. Schema Tabel Penting

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

## 14. Bahasa Indonesia — Label Referensi

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

## 15. Instalasi & Setup Awal

### Install App

```bash
bench get-app nexthd https://github.com/silverefendy/nexthd
bench --site desk.ciptamebel.co.id install-app nexthd
bench --site desk.ciptamebel.co.id migrate
```

### Setup Telegram Bot

1. Buat bot baru via [@BotFather](https://t.me/BotFather), catat token-nya
2. Di Frappe desk, buka **NextHD Settings**
3. Isi field **Telegram Bot Token**
4. Centang **Enable Telegram Notification**
5. Set webhook:
   ```
   POST https://api.telegram.org/bot<TOKEN>/setWebhook
   Body: {"url": "https://desk.ciptamebel.co.id/api/method/nexthd.next_helpdesk.api.telegram_webhook.telegram_webhook"}
   ```
6. Setiap user harus kirim `/start` ke bot, lalu ikuti instruksi verifikasi

### Setup SLA Policy

1. Buka **NextHD Business Hours** → New → isi jam kerja Senin–Sabtu
2. Buka **NextHD SLA Policy** → New → buat 4 record: Kritis, Tinggi, Sedang, Rendah
3. Isi `response_time_minutes` dan `resolution_time_minutes` sesuai SOP
4. Hubungkan setiap SLA Policy ke Business Hours yang sudah dibuat

### Urutan Baca untuk Devin (Handover)

1. `docs/SUMMARY.md` ← **file ini**
2. `nexthd/next_helpdesk/doctype/*/README.md` (spek per-doctype)
3. `nexthd/next_helpdesk/utils/email_helper.py` & `telegram.py`
4. `nexthd/next_helpdesk/api/telegram_webhook.py`
5. `nexthd/next_helpdesk/tasks.py`
6. `nexthd/next_helpdesk/workflow/`

---

## 16. Referensi

- Frappe v16 migration guide: https://github.com/frappe/frappe/wiki/Migrating-to-version-16
- Apps page hook docs: https://docs.frappe.io/framework/user/en/apps-page
- Frappe Discuss: https://discuss.frappe.io
- GitHub repo nexthd: https://github.com/silverefendy/nexthd
- GitHub repo visitor_management (referensi pola): https://github.com/silverefendy/visitor_management

---

*Dokumen ini dikelola oleh Claude. Update terakhir: 2026-08-11 18:15 WIB.*
