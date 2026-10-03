# NextHD Web — Checklist Fitur

> Status: ✅ Selesai | 🟧 Dikerjakan | ⬜ Rencana
>
> **Last updated:** 2026-10-03

## Yang Sudah Ada

| Fitur | Status | Keterangan |
|---|---|---|
| Landing page `/nexthd` | ✅ | HTML/CSS/JS terpisah (`www/nexthd/`, `public/css|js/nexthd_landing.*`). Statistik agregat (Tiket, Problem, Known Error, Aset) |
| Mode privat | ✅ | `PRIVATE_MODE = True` di `index.py`: Guest dialihkan ke login (terverifikasi `curl`, 30 Sept) |
| Tema vintage + dark mode otomatis | ✅ | Token warna di `:root` |
| Commit landing page ke repo | ✅ | Sinkron dengan `origin/main` (30 Sept) |
| Fondasi portal (Tahap 1, PR #13) | ✅ | Terverifikasi 30 Sept. Patch `nx-nav` sudah di `main` (`bb99c79`) |
| Antrian tiket `/nexthd/kerja` (Tahap 2, PR #14) | ✅ | Tampil di browser 1 Okt setelah patch `count` (`63a01a4`). Menu "Tiket Baru" muncul |
| Buat tiket + detail tiket (Tahap 2) | ✅ | Terverifikasi 2 Okt: tiket terbentuk setelah patch CSRF (`44ef6b4`), detail tampil, XSS lulus. Uji tombol Keluar dan field Aset belum dilaporkan |
| Aksi workflow, catatan (worklog), penugasan (Tahap 3, PR #15) | ✅ | Terverifikasi 2 Okt di server `erpnext`: Mulai Kerjakan, Tunggu User (tepat satu baris waiting log), Lanjut Kerjakan, Selesaikan, Buka Kembali, catatan setelah Selesai, penugasan oleh manajer. **Akun Agent biasa belum teruji** (diasumsikan beres, dicek ulang nanti) |
| Perbaikan tampilan tabel log tiket | 🟧 | Skrip patch sudah dijalankan di server (2 Okt), tampil rapi; menunggu commit branch `fix/web-tampilan-log` dan merge |

## Rencana per Tahap (lihat `SPEC_PORTAL.md` §6)

Cakupan awal: hanya tim IT. Requester di tahap 7.

| Tahap | Fitur | Status |
|---|---|---|
| 1 | Template dasar, `api.js`, `portal.py` kerangka, redirect per peran (IT) | ✅ |
| 2 | Antrian agent, detail tiket (baca), buat tiket | ✅ |
| 2b | Perbaikan tampilan (label ID, format SLA, lebar kolom, field Link) | 🟧 (mikrodetik SLA dan tabel log sudah; label filter ID dan kolom Kategori di antrian belum dicek) |
| 3 | Aksi workflow, worklog, penugasan | ✅ (kecuali uji Agent biasa) |
| 3c | Polesan: pesan galat bersih, tombol "Ambil untuk saya" | ✅ (PR feat/web-tahap-3c) |
| 5a | Problem: halaman daftar/detail, tombol "Buat Problem dari Tiket", endpoint atomik | 🟧 (PR feat/web-tahap-5a, belum diuji) |
| 4 | Dashboard manajer | ⬜ |
| 5 | Problem, Known Error, Change Request, Asset (EAV). Di Desk alurnya: Tiket -> Problem -> Known Error / Change Request | ⬜ (spesifikasi belum ditulis) |
| 6 | Laporan/grafik, lampiran & foto | ⬜ |
| 7 | Halaman Requester (menggantikan Web Form `/tiket-saya`), login bertema NextHD | ⬜ |

## Tetap di Desk (tidak dipindah)

SLA Policy, Business Hours, Holiday, Team, Category, NextHD Settings, Workflow, Permission.

## Keputusan menunggu

- Arti "7 hari kerja" pada SLA (lihat `docs/TEMUAN_SLA_2026-10-02.md`).
- Kunci penugasan setelah tiket Selesai/Ditutup (belum diputuskan, tidak dibangun).
