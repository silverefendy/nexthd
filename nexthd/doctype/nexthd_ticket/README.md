# NextHD Ticket

Doctype utama — pengganti konsep HD Ticket, mencakup Incident + Service Request.
Referensi lengkap: lihat NEXTHD_SPEC.md bagian 3.1

## Field yang harus dibuat
| Field | Fieldtype | Keterangan |
|---|---|---|
| ticket_type | Select | Insiden / Permintaan Layanan |
| subject | Data | Judul singkat, wajib |
| description | Text Editor | Detail masalah/permintaan |
| status | Select | Baru / Sedang Dikerjakan / Menunggu User / Selesai / Ditutup |
| priority | Select | Kritis / Tinggi / Sedang / Rendah |
| category | Link -> NextHD Category | |
| requested_by | Link -> User | Pelapor |
| assigned_to | Link -> User | Agent yang menangani |
| team | Link -> NextHD Team | |
| sla_response_by | Datetime | Auto-calculated dari SLA Policy |
| sla_resolution_by | Datetime | Auto-calculated dari SLA Policy |
| resolved_on | Datetime | Diisi otomatis saat status -> Selesai |
| closed_on | Datetime | Diisi otomatis saat status -> Ditutup |
| related_problem | Link -> NextHD Problem | Opsional |
| attachments | Attach | |

## Numbering
Autoname: `TKT-2026-####` (gunakan naming_series)

## Catatan Implementasi
- Reply/komunikasi pakai Frappe Comment/Timeline BAWAAN (jangan bikin child table sendiri untuk chat)
- Hook on_update untuk trigger notifikasi Telegram (lihat utils/telegram.py)
- Hook on_update untuk auto-set resolved_on/closed_on berdasarkan perubahan status
- Permission: lihat NEXTHD_SPEC.md bagian 7 (Role & Permission Matrix)
