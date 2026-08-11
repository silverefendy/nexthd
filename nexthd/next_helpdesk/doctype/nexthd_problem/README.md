# NextHD Problem

## Field
| Field | Fieldtype | Keterangan |
|---|---|---|
| title | Data | |
| status | Select | Terbuka / Investigasi / Known Error / Selesai / Ditutup |
| root_cause | Text Editor | |
| related_tickets | Table -> NextHD Problem Ticket (child table baru) | Link ke NextHD Ticket |

## Numbering
`PRB-2026-####`

## Catatan
- Child table "NextHD Problem Ticket" perlu dibuat terpisah (field: ticket -> Link ke NextHD Ticket)
- Workflow: lihat NEXTHD_SPEC.md bagian 6, Workflow 2

## Fitur: Convert to Known Error
Tombol "Convert to Known Error" tersedia di form NextHD Problem dengan ketentuan:
- **Tampil jika**: Status = "Investigasi", root_cause terisi, dan user memiliki role Agent/Agent Manager/IT Manager
- **Fungsi**: Membuat record NextHD Known Error baru dan mengubah status Problem menjadi "Known Error"
- **Mapping field**:
  - Problem.title → Known Error.title
  - Problem.root_cause → Known Error.symptom
  - Problem.workaround → Known Error.workaround
  - Problem.name → Known Error.related_problem
  - Known Error.name → Problem.known_error (link balik)
- Setelah konversi, user otomatis di-redirect ke form Known Error yang baru dibuat
