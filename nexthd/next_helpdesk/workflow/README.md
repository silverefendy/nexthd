# NextHD Workflows

Workflow dibuat via UI Frappe (/app/workflow/new) atau via fixture JSON.
Referensi lengkap: NEXTHD_SPEC.md bagian 6

## 1. Workflow: NextHD Ticket
States: Baru -> Sedang Dikerjakan -> [Menunggu User <-> Sedang Dikerjakan] -> Selesai -> Ditutup
- Requester bisa: Selesai -> Ditutup (konfirmasi) ATAU Selesai -> Baru (buka kembali)
- Agent Manager: override semua transisi

## 2. Workflow: NextHD Problem
States: Terbuka -> Investigasi -> Known Error -> Selesai -> Ditutup
- Investigasi -> Selesai (langsung, bypass Known Error jika root cause langsung ditemukan)

## 3. Workflow: NextHD Change Request
States: Draft -> Diajukan -> Direview -> [Disetujui/Ditolak] -> Implementasi -> Selesai -> Ditutup
- Approval hanya role Agent Manager / IT Manager

## Catatan Implementasi
Simpan definisi workflow sebagai fixture (export via `bench export-fixtures`)
supaya ikut ter-track di git dan otomatis ter-install ulang saat `bench migrate`
di server lain.
