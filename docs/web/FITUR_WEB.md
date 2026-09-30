# NextHD Web — Checklist Fitur

> Status: ✅ Selesai | 🔶 Dikerjakan | ⬜ Rencana
>
> **Last updated:** 2026-09-30

## Yang Sudah Ada

| Fitur | Status | Keterangan |
|---|---|---|
| Landing page `/nexthd` | ✅ | HTML/CSS/JS terpisah (`www/nexthd/`, `public/css|js/nexthd_landing.*`). Tampil di server (dikonfirmasi Efendy 30 Sept). Statistik agregat (Tiket, Problem, Known Error, Aset) |
| Mode privat | ✅ | `PRIVATE_MODE = True` di `index.py`: Guest dialihkan ke login |
| Tema vintage + dark mode otomatis | ✅ | Token warna di `:root` `nexthd_landing.css` |
| Commit landing page ke repo | 🔶 | Belum dikonfirmasi apakah sudah di-commit dan di-push oleh Efendy |

## Rencana per Tahap (lihat `SPEC_PORTAL.md` §6)

| Tahap | Fitur | Status |
|---|---|---|
| 1 | Template dasar, `api.js`, `portal.py` kerangka, redirect per peran | ⬜ |
| 2 | Daftar tiket + buat tiket | ⬜ |
| 3 | Antrian agent, detail tiket, aksi workflow, worklog | ⬜ |
| 4 | Dashboard manajer, penugasan | ⬜ |
| 5 | Problem, Known Error, Change Request, Asset (EAV) | ⬜ |
| 6 | Laporan/grafik, lampiran & foto | ⬜ |
| Nanti | Halaman login bertema NextHD | ⬜ |

## Tetap di Desk (tidak dipindah)

SLA Policy, Business Hours, Holiday, Team, Category, NextHD Settings, Workflow, Permission.
