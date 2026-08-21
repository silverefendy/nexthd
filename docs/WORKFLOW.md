# NextHD — Workflow & Notifikasi

> State machine untuk Ticket, Problem, Change Request + sistem notifikasi Telegram.
> File ini paling sering dirujuk saat debugging workflow.
>
> **Last updated:** 2026-08-22 00:45 WIB

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

> ⚠️ **Belum ada trigger notifikasi untuk NextHD Problem dan NextHD Change Request**
> selain baris terakhir di atas (approval CR). Dicatat sebagai kandidat fitur tambahan
> di `HANDOFF.md` sesi 2026-08-15.

> ⚠️ **Pesan "Peringatan SLA Response"** di `check_sla_response_breach()` (`tasks.py`) masih pakai
> f-string mentah — belum dibungkus `frappe._()`. Luput dari scope PR #6 karena ada di `tasks.py`,
> bukan `telegram.py`. Dicatat sebagai open item prioritas rendah.

### Implementasi Teknis

- File: `nexthd/next_helpdesk/utils/telegram.py`
- Fungsi kirim: `send_telegram_message(chat_id, message)` → `requests.post()` ke `https://api.telegram.org/bot{TOKEN}/sendMessage`
- Semua notifikasi async via `frappe.enqueue()` (background jobs)
- Guard `is_telegram_enabled()` ada di semua fungsi publik
- Webhook URL: `POST /api/method/nexthd.next_helpdesk.api.telegram_webhook.telegram_webhook`

### Catatan i18n

✅ **Sudah dikerjakan (PR #6, merged 2026-08-20):** semua string notifikasi di `telegram.py` sudah dibungkus `frappe._()`, terjemahan ditambahkan ke `id.csv`. **Belum di-deploy ke server produksi** — perlu `git pull` + `bench migrate` terlebih dulu.

### Bug yang Sudah Difix di telegram.py

1. `frappe.requests.post()` → `requests.post()` (`frappe.requests` tidak ada)
2. `frappe.enqueue("_send_ticket_created_notification")` → wajib full path: `"nexthd.next_helpdesk.utils.telegram._send_ticket_created_notification"` (berlaku untuk 6 fungsi)
3. Parameter `link_telegram_account(user, telegram_username, verification_code)` → renamed ke `chat_id`
4. `frappe.db.get_single_value("NextHD Settings", ...)` → `frappe.db.get_value("NextHD Settings", {}, ...)` karena `NextHD Settings` bukan Single DocType (`issingle=0`) — fix di-commit `fb9369c`

---

## 2. Workflow (State Machine)

### Workflow 1: NextHD Ticket

```
Baru → [Mulai Kerjakan] → Sedang Dikerjakan → [Tunggu User] → Menunggu User
                                │                                    │
                                │ [Lanjut Kerjakan] ←────────────────┘
                                │
                                ↓ [Selesaikan]
                              Selesai → [Konfirmasi Selesai] → Ditutup
                                ↑           │
                                │           └→ [Buka Kembali] → Baru
```

| Role | Aksi yang Diizinkan |
|---|---|
| Agent | Mulai Kerjakan, Tunggu User, Lanjut Kerjakan, Selesaikan |
| Requester | Konfirmasi Selesai (→ Ditutup) ATAU Buka Kembali (→ Baru) |
| Agent Manager | Bisa override semua transisi |

> ✅ **Diverifikasi dari kode repo (2026-08-22):** Semua 7 transisi ada di `nexthd_ticket_workflow.json`,
> termasuk "Mulai Kerjakan" (Baru → Sedang Dikerjakan). State "Ditutup" memiliki `doc_status: "1"`.

> **Ticket tidak wajib berhubungan dengan Problem.** Kebanyakan tiket (misal reset password,
> permintaan layanan rutin) selesai dan ditutup langsung tanpa pernah melalui alur Problem.
> Field `related_problem` di Ticket sifatnya opsional — hanya diisi untuk insiden
> berulang/besar yang butuh investigasi root cause. Diklarifikasi 2026-08-15.

### Workflow 2: NextHD Problem

```
Terbuka → Investigasi ──[kondisi: known_error terisi]──▶ Known Error → Selesai → Ditutup
   │                                                                                  ▲
   └──Selesaikan Langsung──────────────────────────────────────────────────────────┘
                    Investigasi ──Selesaikan──▶ Selesai (juga tersedia langsung)
```

> ⚠️ Transisi workflow polos `Investigasi → Known Error` **sudah dihapus** (2026-08-11), lalu
> **muncul kembali secara tidak sengaja** (kemungkinan re-import atau edit manual yang tidak
> tercatat) dan ditemukan lagi pada 2026-08-15 saat review fixture. Alih-alih dihapus lagi,
> transisi ini **diberi `condition: doc.known_error`** — sekarang tombol transisi hanya muncul
> di Actions kalau field `known_error` di Problem sudah terisi. Ini menutup celah jebakan §4
> tanpa perlu menghapus transisi selamanya (lebih robust terhadap re-import tidak sengaja di
> masa depan). Detail teknis fix di `POLA_KERJA_DAN_BUG.md`.
>
> **Dua cara mencapai status Known Error yang sekarang valid:**
> 1. Tombol custom **"Buat Known Error dari Problem"** (Client Script) — kalau Known Error
>    belum ada, otomatis dibuatkan + `known_error` terisi otomatis
> 2. Kalau Known Error yang cocok **sudah ada** sebelumnya — pilih manual di field
>    `known_error`, baru transisi status via Actions

**Sisa transitions NextHD Problem (5):**
```
Terbuka -> Mulai Investigasi -> Investigasi
Terbuka -> Selesaikan Langsung -> Selesai
Investigasi -> Selesaikan -> Selesai
Known Error -> Selesaikan -> Selesai
Selesai -> Tutup -> Ditutup
```
*(+1 transisi "Convert to Known Error" dengan condition, lihat di atas — total 6)*

### Workflow 3: NextHD Change Request

```
Draft → Diajukan → Direview → [Disetujui/Ditolak] → Implementasi → Selesai → Ditutup
                                      ↓
                              Ditolak → Draft (bisa resubmit)
```

### Kapan Problem Perlu Known Error Dulu vs Langsung Change Request

Tidak ada urutan wajib satu arah — tergantung situasi (diklarifikasi 2026-08-15):

| Situasi | Urutan Disarankan |
|---|---|
| Root cause ditemukan, ada solusi sementara (workaround), perbaikan permanen butuh waktu/approval | Problem → **Known Error dulu** → baru Change Request |
| Root cause ditemukan, solusi jelas dan bisa langsung dieksekusi | Problem → **Change Request langsung**, tanpa Known Error |
| Root cause sudah pernah terjadi, solusi sudah tercatat di Known Error lama | Problem → **pilih Known Error existing** (bukan buat baru) |

Known Error = "kita tahu solusinya, ini catatannya". Change Request = "kita akan eksekusi
perubahan permanen". Bisa salah satu saja atau dua-duanya.

### Alur End-to-End (Ticket → Problem → Change Request)

```
Ticket (berulang/insiden besar)
   └─ dikaitkan via field `related_problem` → Problem dibuat
        └─ Problem investigasi, root cause ditemukan
             └─ jika perlu fix permanen → Change Request dibuat via field `change_request`
                  └─ Change Request disetujui → Implementasi → Selesai
                       └─ Problem ditutup → Ticket-ticket terkait bisa ditutup
```

### Alur Relasi Asset (ditambahkan 2026-08-15)

```
Ticket → affected_asset ─────┐
                              ├──(auto-link saat "Buat Problem dari Tiket")──▶ Problem.related_asset
Problem (proaktif, tanpa Ticket) → related_asset diisi manual ──┘
                              │
                              ├──(tombol "Buat Change Request dari Problem")──▶ CR.related_asset (dari Problem)
Asset → (tombol "Buat Change Request dari Asset" di form Asset) ──────────────▶ CR.related_asset (langsung)

Known Error → TIDAK ada field asset langsung, ditelusuri lewat related_problem → Problem.related_asset
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
>
> **Update 2026-08-15:** solusi yang lebih tahan lama BUKAN sekadar menghapus transisi
> polosnya (transisi bisa muncul lagi lewat re-import/edit manual tidak sengaja, seperti yang
> terjadi), melainkan **tambahkan `condition`** pada transisi tersebut yang mensyaratkan field
> relasi sudah terisi (contoh: `condition = "doc.known_error"`). Ini membuat transisi polos
> tetap ada tapi tidak bisa dipakai sampai prasyaratnya terpenuhi — lebih robust terhadap
> perubahan tidak sengaja di masa depan.

### Jebakan 3: Field Link sebagai Action di Workflow Transition (Baru — 2026-08-15)

> ⚠️ Kolom `action` di `tabWorkflow Transition` adalah **Link ke master `Workflow Action
> Master`**, bukan teks bebas. Mengganti nilai `action` ke nama baru yang belum ada sebagai
> master record lewat `doc.save()` akan gagal dengan `LinkValidationError: Could not find
> Row #N: Action: <nama baru>`. Kalau memang perlu nama aksi baru, buat dulu master record-nya
> di `Workflow Action Master`, atau — kalau cuma perlu ubah `condition` tanpa ganti nama aksi —
> pakai **raw SQL UPDATE langsung**, hindari `doc.save()` yang menjalankan validasi link.

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

**Status akhir:** 3 Workflow live, `is_active=1`, transitions lengkap (Ticket 7, Problem 6+1cond, Change Request 8).

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

### ✅ RESOLVED (2026-08-15) — Transisi "Convert to Known Error" Muncul Lagi Tanpa Disengaja

Ditemukan saat review fixture: transisi `Investigasi → Known Error` (action: "Convert to Known
Error") yang sudah dihapus 2026-08-11 **muncul lagi** di `tabWorkflow Transition`, kemungkinan
lewat re-import atau edit manual yang tidak tercatat. Ini membuka kembali celah Jebakan #2 —
status bisa berubah "Known Error" tanpa field `known_error` terisi.

**Percobaan pertama gagal** — rename `action` ke "Tandai Known Error" via `doc.save()` kena
`LinkValidationError` karena `action` adalah Link ke `Workflow Action Master` (lihat Jebakan #3).

**Fix final (raw SQL, tidak ganti nama action):**
```python
frappe.db.sql("""
    UPDATE `tabWorkflow Transition`
    SET `condition` = 'doc.known_error'
    WHERE parent = 'NextHD Problem'
    AND state = 'Investigasi'
    AND next_state = 'Known Error'
""")
frappe.db.commit()
```

**Hasil:** transisi tetap bernama "Convert to Known Error", tapi hanya muncul di Actions kalau
`known_error` sudah terisi. Diverifikasi manual di browser — field kosong = tombol tidak
muncul, field terisi = tombol muncul.

### ✅ RESOLVED (2026-08-19 & 2026-08-20) — Dedup Workflow Transition (Dua Kali)

Ditemukan dua kali: pertama 2026-08-19 (prefix `ai9*`, filter per-nama), kedua 2026-08-20 (pola konsisten `idx = 0` di semua 3 workflow). Keduanya difix via SQL DELETE dan fixture di-export ulang. Regression test `apply_workflow()` lulus setelah fix kedua. Detail di `POLA_KERJA_DAN_BUG.md §4`.

---

*Dokumen ini dikelola oleh Claude. Update terakhir: 2026-08-22 00:45 WIB.*
