# NextHD Web — Checklist Fitur

> Status: ✅ Selesai | 🔶 Dikerjakan | ⬜ Rencana
>
> **Last updated:** 2026-09-30

## Yang Sudah Ada

| Fitur | Status | Keterangan |
|---|---|---|
| Landing page `/nexthd` | ✅ | HTML/CSS/JS terpisah (`www/nexthd/`, `public/css|js/nexthd_landing.*`). Statistik agregat (Tiket, Problem, Known Error, Aset) |
| Mode privat | ✅ | `PRIVATE_MODE = True` di `index.py`: Guest dialihkan ke login (terverifikasi `curl`, 30 Sept) |
| Tema vintage + dark mode otomatis | ✅ | Token warna di `:root` |
| Commit landing page ke repo | ✅ | Sinkron dengan `origin/main` (30 Sept) |
| Fondasi portal (Tahap 1, PR #13) | ✅ | Terverifikasi 30 Sept: penjaga akses (Guest dialihkan, non-IT 403), `get_session_info` GET-only, tombol "Ruang Kerja" kondisional per peran. Menunggu commit patch `nx-nav` di `ui.js` dan perbaikan `api.js` (`PRASYARAT_PR2.md`) |

## Rencana per Tahap (lihat `SPEC_PORTAL.md` §6)

Cakupan awal: hanya tim IT. Requester di tahap 7.

| Tahap | Fitur | Status |
|---|---|---|
| 1 | Template dasar, `api.js`, `portal.py` kerangka, redirect per peran (IT) | ✅ |
| 2 | Antrian agent, detail tiket (baca), buat tiket | 🟶 (dikerjakan) |
| 3 | Aksi workflow, worklog | ⬜ |
| 4 | Dashboard manajer, penugasan | ⬜ |
| 5 | Problem, Known Error, Change Request, Asset (EAV) | ⬜ |
| 6 | Laporan/grafik, lampiran & foto | ⬜ |
| 7 | Halaman Requester (menggantikan Web Form `/tiket-saya`), login bertema NextHD | ⬜ |

## Tetap di Desk (tidak dipindah)

SLA Policy, Business Hours, Holiday, Team, Category, NextHD Settings, Workflow, Permission.
