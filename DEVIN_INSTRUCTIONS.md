# Instruksi untuk Devin — Implementasi NextHD

## Konteks
Repo `silverefendy/nexthd` sudah berisi skeleton app dasar dari `bench new-app`
(hooks.py, modules.txt, dst) plus folder tambahan dari paket ini yang berisi
kerangka struktur + spesifikasi tiap komponen.

**Dokumen acuan utama:** `NEXTHD_SPEC.md` di root repo — baca ini dulu secara
keseluruhan sebelum mulai coding, karena ini sumber kebenaran untuk semua
keputusan desain (arsitektur, workflow, permission, dst).

Folder `nexthd/next_helpdesk/doctype/` berisi README.md di tiap sub-folder doctype
yang merangkum field spesifik — gunakan ini sebagai referensi cepat saat
membuat tiap Doctype, tapi tetap cross-check ke NEXTHD_SPEC.md untuk konteks
lengkap (workflow, relasi antar-doctype, dst).

## Cara Kerja dengan File README.md di Folder Doctype
Setiap folder `doctype/nexthd_xxx/` saat ini HANYA berisi `README.md` berisi
spesifikasi field. Tugasmu adalah membuat file-file Frappe standar di folder
yang sama:
- `nexthd_xxx.json` (Doctype definition)
- `nexthd_xxx.py` (Controller class)
- `nexthd_xxx.js` (Client script, jika perlu logic di form)
- `test_nexthd_xxx.py` (Unit test dasar)

Setelah Doctype benar-benar dibuat (baik via UI Frappe lalu di-export, atau
langsung tulis JSON manual), README.md BOLEH dihapus atau diringkas jadi
comment di kode — tidak wajib dipertahankan.

## Urutan Implementasi (ikuti urutan ini, jangan lompat)

### Tahap 1 — Fondasi
1. Buat Doctype pendukung dulu (tidak punya dependency ke doctype lain):
   - NextHD Category
   - NextHD Team
   - NextHD Business Hours
   - NextHD SLA Policy
   - NextHD Settings (type: Single)
2. Buat Role custom: IT Manager, IT Auditor (Agent, Agent Manager biasanya
   sudah ada bawaan Frappe/Helpdesk pattern — cek dulu, buat baru jika belum ada)

### Tahap 2 — User Tanpa Email
1. Implementasikan `nexthd/next_helpdesk/utils/email_helper.py`
   (lihat TODO di dalam file)
2. Buat Doctype `NextHD User Profile`
3. Daftarkan hook di `hooks.py`:
   ```python
   doc_events = {
       "User": {
           "before_insert": "nexthd.next_helpdesk.utils.email_helper.before_insert_user_hook"
       }
   }
   ```
4. Test: buat User baru dari script/console, pastikan tidak error karena
   field email kosong dan username tetap bisa dipakai login

### Tahap 3 — Doctype Transaksional Inti
1. NextHD Ticket (paling prioritas)
2. NextHD Problem (+ child table NextHD Problem Ticket)
3. NextHD Change Request
4. NextHD Known Error
5. NextHD Asset
6. NextHD Service Catalog

### Tahap 4 — Workflow
Implementasikan 3 workflow sesuai `workflow/README.md` dan
NEXTHD_SPEC.md bagian 6. Export sebagai fixture setelah selesai:
```bash
bench --site [sitename] export-fixtures
```

### Tahap 5 — Permission
Implementasikan matrix permission sesuai NEXTHD_SPEC.md bagian 7,
via Role Permission Manager atau fixture.

### Tahap 6 — Telegram Integration
1. Implementasikan `nexthd/next_helpdesk/utils/telegram.py`
   (lihat TODO di dalam file — semua fungsi masih `raise NotImplementedError`)
2. Buat webhook endpoint di `api/` untuk terima update dari Telegram Bot API
3. Daftarkan `doc_events` di hooks.py untuk trigger tiap fungsi notify_*
   pada event yang sesuai (ticket dibuat, di-assign, ada reply, dst —
   lihat tabel trigger di NEXTHD_SPEC.md bagian 5)
4. Gunakan `frappe.enqueue()` untuk semua pemanggilan `send_telegram_message`
   — JANGAN kirim notifikasi secara synchronous di request utama

### Tahap 7 — UI & Bahasa Indonesia
1. Buat Workspace utama NextHD (dashboard ringkas)
2. Setup translation menggunakan `translations/id.csv` sebagai basis
   (lengkapi entry yang masih kurang)
3. List View / Kanban View untuk NextHD Ticket

### Tahap 8 — SLA Automation
1. Auto-calculate `sla_response_by` dan `sla_resolution_by` saat Ticket dibuat
   (berdasarkan priority -> NextHD SLA Policy -> NextHD Business Hours)
2. Scheduled job (daftarkan di `hooks.py` -> `scheduler_events`) untuk cek
   SLA yang mendekati breach (H-30 menit) dan trigger notifikasi

### Tahap 9 — Testing
Tulis test dasar untuk tiap Doctype (`test_nexthd_xxx.py`), minimal:
- Bisa create/update/delete
- Workflow transition sesuai role yang benar (dan gagal untuk role yang salah)
- Hook email dummy jalan dengan benar

## Batasan & Hal yang HARUS Diikuti
- JANGAN install app `erpnext` — project ini murni di atas Frappe Framework
- JANGAN gunakan email asli/SMTP untuk notifikasi — semua notifikasi lewat
  Telegram + in-app notification bawaan Frappe
- Label UI default HARUS Bahasa Indonesia (lihat translations/id.csv),
  Bahasa Inggris jadi opsi kedua via field preferred_language
- Semua nomor dokumen (Ticket, Problem, dst) HARUS pakai format yang sudah
  ditentukan di tiap README.md (contoh: TKT-2026-####)
- Ikuti Role & Permission Matrix di NEXTHD_SPEC.md bagian 7 secara ketat —
  jangan buat permission yang lebih longgar dari yang didefinisikan

## Setelah Selesai
Push semua perubahan ke branch `main` di `silverefendy/nexthd`. Sesi Claude
berikutnya akan melakukan review, testing end-to-end, dan bug fixing.
