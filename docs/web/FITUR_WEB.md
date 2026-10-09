# NextHD Web — Checklist Fitur

> Status: ✅ Selesai | 🟧 Dikerjakan | ⬜ Rencana
>
> **Last updated:** 2026-10-09 17:20 WIB
>
> Catatan: entri 7–8 Okt disusun dari catatan sesi, bukan dari diff PR. Cek GitHub bila butuh rincian file.

## Yang Sudah Ada

| Fitur | Status | Keterangan |
|---|---|---|
| Landing page (kini di `/nexthd/tentang`) | ✅ | HTML/CSS/JS terpisah (`www/nexthd/`, `public/css|js/nexthd_landing.*`). Statistik agregat (Tiket, Problem, Known Error, Aset). Sejak Tahap 4 dipindah dari `/nexthd` ke `/nexthd/tentang` |
| Mode privat | ✅ | `PRIVATE_MODE = True` di `index.py`: Guest dialihkan ke login (terverifikasi `curl`, 30 Sept) |
| Tema vintage + dark mode otomatis | ✅ | Token warna di `:root` |
| Commit landing page ke repo | ✅ | Sinkron dengan `origin/main` (30 Sept) |
| Fondasi portal (Tahap 1, PR #13) | ✅ | Terverifikasi 30 Sept. Patch `nx-nav` sudah di `main` (`bb99c79`) |
| Antrian tiket `/nexthd/kerja` (Tahap 2, PR #14) | ✅ | Tampil di browser 1 Okt setelah patch `count` (`63a01a4`). Menu "Tiket Baru" muncul. Label menu antrian diganti **"List Ticket"** (7 Okt) |
| Buat tiket + detail tiket (Tahap 2) | ✅ | Terverifikasi 2 Okt: tiket terbentuk setelah patch CSRF (`44ef6b4`), detail tampil, XSS lulus. Uji tombol Keluar dan field Aset belum dilaporkan |
| Aksi workflow, catatan (worklog), penugasan (Tahap 3, PR #15) | ✅ | Terverifikasi 2 Okt di server `erpnext`: Mulai Kerjakan, Tunggu User (tepat satu baris waiting log), Lanjut Kerjakan, Selesaikan, Buka Kembali, catatan setelah Selesai, penugasan oleh manajer. **Akun Agent biasa belum teruji** (diasumsikan beres, dicek ulang nanti) |
| Perbaikan tampilan tabel log tiket | ✅ | Sudah di `main` (PR #16, branch `fix/web-tampilan-log`), tampil rapi di server |
| Menu "Problem" di navigasi portal | ✅ | Commit `6181935` (3 Okt), menu ada di `ui.js` (`renderNav`). 7 Okt: menjadi dropdown **Problem ▾** (List Problem + Problem Baru) |
| Filter dari URL di antrian Tiket dan daftar Problem (B1, PR #19) | ✅ | Terverifikasi 6 Okt: 6 URL contoh lolos (tab/filter terisi dari query string, nilai ngawur diabaikan). Dipakai tautan kartu dashboard. Kelemahan kecil: `page=2abc` diterima sebagai 2 |
| Menu dropdown **Tiket ▾** (A1, `0e29617`) | ✅ | Terverifikasi 6 Okt di desktop dan HP: "Antrian Tiket" (kini "List Ticket") dan "Tiket Baru"; hover (desktop), ketuk (layar sentuh), tertutup saat klik di luar; menu berbasis konfigurasi `children` |
| Filter Problem otomatis (A1) | ✅ | Daftar langsung memuat saat dropdown berubah, tombol "Terapkan Filter" dihapus (sama seperti Tiket) |
| Kosmetik A1: font nama user, kolom "Ditugaskan ke" | ✅ | Nama user monospace; kolom menampilkan bagian sebelum `@` |
| **Dashboard Beranda `/nexthd` (Tahap 4, PR #20)** | ✅ | Kartu klik-able untuk IT; lulus uji browser 7 Okt, angka kartu cocok dengan halaman tujuan. Kartu "Belum ditugaskan" hanya tiket aktif (keputusan #9 final) |
| **Problem Baru mandiri (Tahap 5a-2, PR #21)** | ✅ | Merged dan lulus uji server 7 Okt. Prioritas **wajib** diisi (tanpa default); Problem dari tiket mewarisi prioritas tiket (PR #22). Uji akun Auditor di `/nexthd/problem-baru` belum benar-benar dijalankan |
| **Menu Problem ▾ dan label "List Ticket" (patch Claude)** | ✅ | Lulus uji 7 Okt |
| **Menu bersama di `/nexthd/tentang` (PR #23 + patch)** | ✅ | Lulus uji 7 Okt. Peran IT (`IT_ROLES` di `tentang.py`) mendapat menu bersama; Guest dan non-IT mendapat bar sederhana (tautan Tiket Saya untuk non-IT dikembalikan). Belum ada tombol Keluar untuk non-IT |
| **Web Form `/tiket-saya` diperbaiki** | ✅ | 7 Okt: sempat 500 `ModuleNotFoundError` (`is_standard=1` tanpa folder modul), diubah ke `is_standard 0` (DB + fixture, commit `881084c`); `login_required 1` (`c2a2a3e`). 7–8 Okt: dropdown **Tim** opsional + `allow_multiple 1` (`9d34549`), opsi Link Category/Tim/Service Catalog dibuka (`b637dbc`). 8 Okt: dropdown **Aset Terdampak** per user (`d583cd4`, lihat `docs/BUG_ASET_LOKASI_WEBFORM.md`). Label masih berbahasa Inggris |

## Rencana per Tahap (lihat `SPEC_PORTAL.md` §6)

Cakupan awal: hanya tim IT. Requester di tahap 7.

| Tahap | Fitur | Status |
|---|---|---|
| 1 | Template dasar, `api.js`, `portal.py` kerangka, redirect per peran (IT) | ✅ |
| 2 | Antrian agent, detail tiket (baca), buat tiket | ✅ |
| 2b | Perbaikan tampilan (label ID, format SLA, lebar kolom, field Link) | 🟧 (mikrodetik SLA dan tabel log sudah; label filter ID dan kolom Kategori di antrian belum dicek) |
| 3 | Aksi workflow, worklog, penugasan | ✅ (kecuali uji Agent biasa) |
| 3c | Polesan: pesan galat bersih, tombol "Ambil untuk saya" | 🟧 (PR #17 sudah di `main` dan di-deploy 3 Okt; 4 skenario uji server belum dilaporkan) |
| 5a | Problem: halaman daftar/detail, tombol "Buat Problem dari Tiket", endpoint atomik | 🟧 (PR #18 sudah di `main`; perbaikan `4db1adb`; endpoint lolos uji server 3 Okt; dialog "Buat Problem" dan "Mulai Investigasi" terlihat berhasil di browser 6 Okt. **Belum diuji:** tombol hilang di tiket Ditutup, akun Agent biasa. Keputusan #8 final: tiket Selesai boleh dibuat Problem, hanya Ditutup yang ditolak) |
| 4 | Dashboard Beranda (kartu klik-able untuk IT, menu bersama; menggantikan rencana "Dashboard manajer") | ✅ (PR #20, uji 7 Okt) |
| 5a-2 | Problem Baru mandiri | ✅ (PR #21 dan #22, uji 7 Okt) |
| 5b | Known Error: daftar/detail, tombol "Buat Known Error dari Problem", formulir Baru | ⬜ (spesifikasi di `TUGAS_TAHAP_5.md`; urutan 5b-1, 5b-2) |
| 5c | Change Request: daftar/detail, tombol dari Problem/Known Error/Asset, formulir Baru | ⬜ (spesifikasi di `TUGAS_TAHAP_5.md`; urutan 5c-1, 5c-2) |
| 5d | Asset, tombol "Buat Change Request dari Asset" | ⬜ (spesifikasi di `TUGAS_TAHAP_5.md`. **Perlu direvisi:** spesifikasi menyebut struktur `asset_type`, padahal Asset sudah memakai `asset_category` + `asset_attributes` (EAV), `location` kini Link ke `NextHD Location`, dan ada tabel Pengguna Aset (`NextHD Asset User`), lihat `docs/BUG_ASET_LOKASI_WEBFORM.md`) |
| 6 | Laporan/grafik, lampiran & foto | ⬜ |
| 7 | Halaman Requester (menggantikan Web Form `/tiket-saya`), login bertema NextHD | ⬜ |
| Lint | PR "pembersihan lint" (trailing whitespace, ruff, eslint) agar check CI hijau | ⬜ (tidak memblokir; lihat `BUG_WEB.md`) |

## Tetap di Desk (tidak dipindah)

SLA Policy, Business Hours, Holiday, Team, Category, NextHD Settings, Workflow, Permission.

## Keputusan

- **SLA "hari kerja" (diputuskan 3 Okt 2026):** pilihan A, 1 hari = 1440 menit jam kerja (7 hari kerja = 168 jam kerja). Tidak ada perubahan kode/data. Tiga keputusan SLA lain di `docs/TEMUAN_SLA_2026-10-02.md` belum diputuskan. Keputusan A belum dicatat di file itu.
- Status Problem setelah Known Error dibuat tetap manual lewat tombol workflow (lihat `TUGAS_TAHAP_5.md`).
- **Beranda (6 Okt 2026):** opsi A, memakai menu bersama; landing lama dipindah ke `/nexthd/tentang`.
- Menu dropdown dan penambahan grup menu dikerjakan Claude di `ui.js`; Devin tidak mengubah `ui.js`.
- **#8 (final, 7 Okt 2026):** tiket berstatus Selesai boleh dibuat Problem; hanya Ditutup yang ditolak.
- **#9 (final, 7 Okt 2026):** kartu dashboard dan tab "Belum ditugaskan" hanya menghitung tiket aktif.
- **Problem Baru (7 Okt 2026):** prioritas wajib, tanpa default; Problem dari tiket mewarisi prioritas tiket.
- **`/nexthd/tentang` (7 Okt 2026):** menu bersama hanya untuk peran IT; Guest dan non-IT mendapat bar sederhana.
- **Web Form `/tiket-saya` (7–8 Okt 2026):** `login_required 1`; dropdown Tim opsional (boleh kosong). Aset Terdampak awalnya dikosongkan untuk Requester, lalu diganti dropdown aset milik/terdaftar atas requester (8 Okt malam).

## Keputusan menunggu

- Kunci penugasan setelah tiket Selesai/Ditutup (belum diputuskan, tidak dibangun).
- Tiga keputusan SLA lain (all-or-nothing vs carry-over, jeda kalender vs jam kerja, perilaku Buka Kembali): tidak mendesak.
