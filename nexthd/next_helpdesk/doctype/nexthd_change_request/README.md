# NextHD Change Request

## Field
| Field | Fieldtype | Keterangan |
|---|---|---|
| title | Data | |
| status | Select | Draft / Diajukan / Direview / Disetujui / Ditolak / Implementasi / Selesai / Ditutup |
| change_type | Select | Standard / Normal / Emergency |
| risk_level | Select | Rendah / Sedang / Tinggi |
| related_problem | Link -> NextHD Problem | Opsional |
| implementation_plan | Text Editor | |
| rollback_plan | Text Editor | |

## Numbering
`CHG-2026-####`

## Catatan
- Workflow: lihat NEXTHD_SPEC.md bagian 6, Workflow 3
- Approval hanya bisa oleh role Agent Manager / IT Manager
