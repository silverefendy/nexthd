# NextHD SLA Policy

## Field
| Field | Fieldtype | Keterangan |
|---|---|---|
| priority | Select | Kritis / Tinggi / Sedang / Rendah |
| response_time_minutes | Int | |
| resolution_time_minutes | Int | |
| business_hours | Link -> NextHD Business Hours | |

## Nilai Default (dari NEXTHD_SPEC.md)
| Priority | Response | Resolution |
|---|---|---|
| Kritis | 15 menit | 120 menit |
| Tinggi | 60 menit | 240 menit |
| Sedang | 240 menit | 480 menit |
| Rendah | 480 menit | 1440 menit |
