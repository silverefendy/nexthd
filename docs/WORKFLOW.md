# NextHD — Workflow & Notifikasi

> State machine untuk Ticket, Problem, Change Request + sistem notifikasi Telegram.
> File ini paling sering dirujuk saat debugging workflow.
>
> **Last updated:** 2026-08-12 10:00 WIB

---

## 1. Sistem Notifikasi Telegram

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

### Catatan i18n (belum dikerjakan, prioritas rendah)

Pesan Telegram saat ini **hardcoded Bahasa Indonesia** di `telegram.py`. Untuk multi-bahasa, perlu dibungkus `frappe._("...")` + file terjemahan `en.csv`. Field `preferred_language` di NextHD User Profile sudah ada tapi belum dipakai.

---

## 2. Workflow (State Machine)

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
Terbuka → Investigasi ──[tombol custom "Convert to Known Error"]──▶ Known Error → Selesai → Ditutup
   │                                                                                  ▲
   └──Selesaikan Langsung──────────────────────────────────────────────────────────┘
                    Investigasi ──Selesaikan──▶ Selesai (juga tersedia langsung)
```

> ⚠️ Transisi workflow polos `Investigasi → Known Error` **sudah dihapus** (2026-08-11).
> Satu-satunya jalan ke status `Known Error` sekarang adalah tombol custom **"Convert to Known Error"
> di `nexthd_problem.js`**, yang membuat record Known Error + mengisi relasi sekaligus.

**Sisa transitions NextHD Problem (5):**
```
Terbuka -> Mulai Investigasi -> Investigasi
Terbuka -> Selesaikan Langsung -> Selesai
Investigasi -> Selesaikan -> Selesai
Known Error -> Selesaikan -> Selesai
Selesai -> Tutup -> Ditutup
```

### Workflow 3: NextHD Change Request

```
Draft → Diajukan → Direview → [Disetujui/Ditolak] → Implementasi → Selesai → Ditutup
                                      ↓
                              Ditolak → Draft (bisa resubmit)
```

### Alur End-to-End (Ticket → Problem → Change Request)

```
Ticket (berulang/insiden besar)
   └─ dikaitkan via field `related_problem` → Problem dibuat
        └─ Problem investigasi, root cause ditemukan
             └─ jika perlu fix permanen → Change Request dibuat via field `change_request`
                  └─ Change Request disetujui → Implementasi → Selesai
                       └─ Problem ditutup → Ticket-ticket terkait bisa ditutup
```

---

## 3. Fixture Workflow (di repo)

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

> ⚠️ **Fixture JSON = definisi saja, TIDAK otomatis aktif.** Wajib dicek manual:
> 1. `Workflow.is_active = 1` untuk ketiga workflow
> 2. Field `workflow_state` muncul di form (otomatis ditambah Frappe saat workflow aktif)
> 3. Role per transition harus sudah di-assign ke user terkait (lihat `ARSITEKTUR.md §4`)

---

## 4. Peringatan Kritis — Jebakan Workflow Frappe

### Jebakan 1: `Update Field` di Workflow State

> ⚠️ **Jangan isi `Update Field` di Workflow State** kecuali memang ingin mengubah field
> LAIN saat masuk ke state tersebut. Kalau `Update Field` diisi sama dengan `workflow_state_field`
> (di kasus kita: `status`) dengan `Update Value` kosong (`None`), maka setelah `apply_workflow()`
> berhasil set status ke state tujuan, Frappe akan menjalankan update tambahan —
> status akan tertimpa jadi `None`, lalu `validate_workflow()` fallback ke state pertama.
> **Ini penyebab bug #5 sesi 2026-08-11. Berlaku untuk ketiga workflow.**

### Jebakan 2: Dua Jalur ke State yang Butuh Side-Effect

> ⚠️ **Dua jalur ke state yang sama = risiko field relasi kosong.** Kalau ada state yang
> seharusnya selalu diiringi pembuatan record lain (seperti Problem → Known Error), JANGAN
> biarkan ada transisi workflow polos yang mengubah status tanpa membuat record itu.
> Hapus transisi polosnya, biarkan hanya tombol custom (`frappe.call()` ke method whitelisted)
> yang bisa mencapai state tersebut.

---

## 5. Riwayat Bug Workflow (Semua Selesai)

### ✅ RESOLVED (2026-08-11) — Import Workflow Gagal (7 Lapis Bug)

Workflow 0 di database meski file JSON ada di repo. Root cause utama: file
`nexthd/fixtures/workflow.json` berisi array kosong `[]` karena pernah di-`export-fixtures`
SAAT database belum punya data Workflow (export baca DARI database, bukan sebaliknya).

Setelah diimport manual, ketemu 7 bug field berlapis:

| # | Field | Masalah | Fix |
|---|---|---|---|
| 1 | `allow_edit` (child `states`) | Diisi `1` (integer) — field ini Link ke **Role**, wajib diisi | Isi `"All"` |
| 2 | `state` (child `states`) | Link ke master **Workflow State** — belum ada satupun record | Buat 14 record master |
| 3 | `action` (child `transitions`) | Link ke master **Workflow Action Master** — belum ada | Buat 16 record master |
| 4 | `workflow_name` | Field wajib terpisah dari `name`, tidak ada di JSON lama | Tambahkan, isi sama dengan `name` |
| 5 | `workflow_state_field` | Field wajib (nama field target, di kasus kita `status`), tidak ada | Tambahkan `"workflow_state_field": "status"` |
| 6 | `next_state` vs `transition` | JSON lama pakai key `"transition"`, Frappe expect `"next_state"` | Rename key |

**Tips:** pakai `frappe.get_meta("Workflow")` lalu filter `f.reqd or f.fieldtype == "Link"` untuk lihat semua field kritis sekaligus.

**Catatan penting:** Master data (`Workflow State`, `Workflow Action Master`) **tidak** masuk fixtures (ini master global Frappe, bukan per-app). Kalau install di server baru, harus dibuat ulang manual.

**Status akhir:** 3 Workflow live, `is_active=1`, transitions lengkap (Ticket 7, Problem 5, Change Request 11).

### ✅ RESOLVED (2026-08-11) — Bug `update_field` Overwrite Status jadi `None`

Error saat klik tombol transisi: `WorkflowPermissionError: Workflow State transition
not allowed from Investigasi to Terbuka` — padahal Workflow Transition sudah benar.

**Root cause:** Semua Workflow State NextHD Problem punya `Update Field = status` dengan
`Update Value = None`. Frappe menjalankan `doc.set("status", None)` setelah `apply_workflow()`
sukses, status tertimpa `None`, lalu `validate_workflow()` fallback ke state pertama (`Terbuka`).

**Fix:**
```python
wf = frappe.get_doc("Workflow", "NextHD Problem")
for state in wf.states:
    state.update_field = None
    state.update_value = None
wf.save()
frappe.db.commit()
```
Kemudian: `bench --site desk.ciptamebel.co.id export-fixtures`

### ✅ RESOLVED (2026-08-11) — Bug `update_field` yang Sama di Ticket & Change Request

Sama persis dengan bug di atas. Ticket dikonfirmasi error sama di UI; Change Request diperbaiki preventif.

**Fix sekaligus:**
```python
for wf_name in ["NextHD Ticket", "NextHD Change Request"]:
    wf = frappe.get_doc("Workflow", wf_name)
    for state in wf.states:
        state.update_field = None
        state.update_value = None
    wf.save()
    print(f"Fixed: {wf_name}")
frappe.db.commit()
```

**Catatan:** ditemukan juga transitions terduplikasi di NextHD Change Request (beberapa action muncul dua kali untuk role berbeda) — tidak error, belum dibereskan.

### ✅ RESOLVED (2026-08-11) — Hapus Transisi Redundan `Investigasi → Known Error`

Transisi ini redundan karena tombol custom "Convert to Known Error" sudah ada di `nexthd_problem.js`
(membuat record Known Error + isi relasi). Transisi workflow polos hanya ubah status tanpa buat record.

**Fix:**
```python
wf = frappe.get_doc("Workflow", "NextHD Problem")
wf.transitions = [
    t for t in wf.transitions
    if not (t.state == "Investigasi" and t.action == "Set sebagai Known Error")
]
wf.save()
frappe.db.commit()
```

**Diverifikasi:** `apply_workflow(doc, "Set sebagai Known Error")` sekarang melempar `WorkflowTransitionError`.

---

*Dokumen ini dikelola oleh Claude. Update terakhir: 2026-08-12 10:00 WIB.*
