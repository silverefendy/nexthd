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
