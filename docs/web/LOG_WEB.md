# NextHD Web - Log Sesi

> Log ringkas pengerjaan portal web. Entri terbaru di atas.

| Tanggal | Ringkasan |
|---|---|
| 30 Sept 2026 (verifikasi tahap 1) | PR #13 di-merge (`70afa26`) dan diuji di server. Lolos: tanpa login dialihkan ke login (#1), IT masuk (#2), Requester ditolak (#3), tombol "Ruang Kerja" muncul untuk IT dan tidak untuk Requester (#4, #5), `get_session_info` tanpa login 403 (#6), aset CSS/JS 200 (#8), landing privat dialihkan ke login. Review keamanan: tanpa `ignore_permissions`/SQL langsung/`allow_guest`, satu endpoint GET, 14 file berubah semuanya di area diizinkan. Bug tampilan: `<nav>` tidak punya kelas `nx-nav` sehingga menu tampil mentah. Ditambal di `ui.js` (`nav.className = "nx-nav"`), sintaks OK, `bench build` jalan; commit dan push oleh Efendy (belum terkonfirmasi). Review `api.js` menemukan 2 bug yang harus diperbaiki sebelum PR 2, lihat `PRASYARAT_PR2.md`. |
| 30 Sept 2026 (tugas Devin PR 1) | PR 1 (Tahap 1 fondasi) selesai dikerjakan: CSS (base, layout, components), JS (api, ui, pages/kerja), portal.py (endpoint get_session_info, page_guard), test_portal.py, halaman kerja (html+py), update landing (tombol Ruang Kerja). |
| 30 Sept 2026 (tugas Devin) | Dibuat `TASK_DEVIN_TAHAP_1_2.md` (PR 1 fondasi, PR 2 antrian/detail/buat tiket) dan `TEMUAN_DOKUMEN_LAIN.md`. Aturan: Devin hanya mengedit `docs/web/*`, dokumen lain hanya-baca sebagai sumber kebenaran. Koreksi: `portal.py` di `next_helpdesk/api/` (bukan `nexthd/api/`, bentrok dengan `api.py`) |
| 30 Sept 2026 (lanjutan) | Keputusan Efendy: (1) portal tahap awal hanya untuk IT; (2) Web Form lama `/tiket-saya` diganti halaman Requester portal, tetapi baru dimatikan setelah tahap 7 teruji; (3) landing page sudah ter-commit (`git status` bersih, sinkron `origin/main`). `SPEC_PORTAL.md` bagian 3, 6, 8 diperbarui, urutan tahap diubah (Agent dulu, Requester tahap 7) |
| 30 Sept 2026 | Diskusi arah portal. Keputusan: (1) semua kerja harian nantinya lewat web, Desk tetap untuk administrasi; (2) jalur A saja (`www/` di Frappe, tanpa Vue/React); (3) HTML, CSS, JS dipisah; (4) pola kerja Claude merancang, Devin membangun, Claude mereview; (5) dokumentasi portal dipisah ke `docs/web/`; (6) sementara hanya tim IT yang memegang. Landing page `/nexthd` (mode privat) sudah tampil di server. Akses lewat IP: `http://10.1.0.16:8001/nexthd` |

## Keputusan Terkait (non-teknis)

- Lisensi/distribusi ke pihak lain: kontrol teknis hilang setelah kode ada di server mereka; andalkan kontrak, repo privat, dan hosting di server sendiri. Belum ada tindakan.
- Tidak dipublikasikan ke LinkedIn atau publik selama aplikasi belum selesai.

## Berikutnya

1. Efendy: commit dan push patch `ui.js` (`nx-nav`), konfirmasi tampilan setelah hard refresh.
2. Perbaiki 2 bug `api.js` (lihat `PRASYARAT_PR2.md`), lalu PR 2 untuk Devin.
