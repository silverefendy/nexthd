# NextHD Web — Checklist Fitur

> Status: ✅ Selesai | 🟧 Dikerjakan | ⬜ Rencana
>
> **Last updated:** 2026-10-01

## Yang Sudah Ada

| Fitur | Status | Keterangan |
|---|---|---|
| Landing page `/nexthd` | ✅ | HTML/CSS/JS terpisah (`www/nexthd/`, `public/css|js/nexthd_landing.*`). Statistik agregat (Tiket, Problem, Known Error, Aset) |
| Mode privat | ✅ | `PRIVATE_MODE = True` di `index.py`: Guest dialihkan ke login (terverifikasi `curl`, 30 Sept) |
| Tema vintage + dark mode otomatis | ✅ | Token warna di `:root` |
| Commit landing page ke repo | ✅ | Sinkron dengan `origin/main` (30 Sept) |
| Fondasi portal (Tahap 1, PR #13) | ✅ | Terverifikasi 30 Sept. Patch `nx-nav` sudah di `main` (`bb99c79`) |
| Antrian tiket `/nexthd/kerja` (Tahap 2, PR #14) | ✅ | Tampil di browser 1 Okt setelah patch `count` (`63a01a4`). Menu "Tiket Baru" muncul |
| Detail tiket, buat tiket (Tahap 2) | 🟧 | Sudah ter-merge. Uji browser (buat tiket, detail, XSS, Keluar, field Link) belum dilaporkan |

## Rencana per Tahap (lihat `SPEC_PORTAL.md` §6)

Cakupan awal: hanya tim IT. Requester di tahap 7.

| Tahap | Fitur | Status |
|---|---|---|
| 1 | Template dasar, `api.js`, `portal.py` kerangka, redirect per peran (IT) | ✅ |
| 2 | Antrian agent, detail tiket (baca), buat tiket | 🟧 (ter-merge, uji browser berjalan) |
| 2b | Perbaikan tampilan (label ID, format SLA, lebar kolom, field Link) | ⬜ (ikut PR Tahap 3, lihat `TUGAS_TAHAP_3.md` §5) |
| 3 | Aksi workflow, worklog, penugasan | ⬜ (spesifikasi siap: `TUGAS_TAHAP_3.md`) |
| 4 | Dashboard manajer | ⬜ |
| 5 | Problem, Known Error, Change Request, Asset (EAV) | ⬜ |
| 6 | Laporan/grafik, lampiran & foto | ⬜ |
| 7 | Halaman Requester (menggantikan Web Form `/tiket-saya`), login bertema NextHD | ⬜ |

## Tetap di Desk (tidak dipindah)

SLA Policy, Business Hours, Holiday, Team, Category, NextHD Settings, Workflow, Permission.
