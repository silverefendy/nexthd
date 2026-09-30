# NextHD Web — Log Sesi

> Log ringkas pengerjaan portal web. Entri terbaru di atas.

| Tanggal | Ringkasan |
|---|---|
| 30 Sept 2026 (lanjutan) | Keputusan Efendy: (1) portal tahap awal hanya untuk IT; (2) Web Form lama `/tiket-saya` diganti halaman Requester portal, tetapi baru dimatikan setelah tahap 7 teruji; (3) landing page sudah ter-commit (`git status` bersih, sinkron `origin/main`). `SPEC_PORTAL.md` §3, §6, §8 diperbarui, urutan tahap diubah (Agent dulu, Requester tahap 7) |
| 30 Sept 2026 | Diskusi arah portal. Keputusan: (1) semua kerja harian nantinya lewat web, Desk tetap untuk administrasi; (2) jalur A saja (`www/` di Frappe, tanpa Vue/React); (3) HTML, CSS, JS dipisah; (4) pola kerja Claude merancang, Devin membangun, Claude mereview; (5) dokumentasi portal dipisah ke `docs/web/`; (6) sementara hanya tim IT yang memegang. Landing page `/nexthd` (mode privat) sudah tampil di server. Akses lewat IP: `http://10.1.0.16:8001/nexthd`. Dibuat 5 file di `docs/web/` |

## Keputusan Terkait (non-teknis)

- Lisensi/distribusi ke pihak lain: kontrol teknis hilang setelah kode ada di server mereka; andalkan kontrak, repo privat, dan hosting di server sendiri. Belum ada tindakan.
- Tidak dipublikasikan ke LinkedIn atau publik selama aplikasi belum selesai.

## Berikutnya

1. Tulis prompt tahap 1-2 untuk Devin berdasarkan `SPEC_PORTAL.md`.
2. Review PR Devin sebelum merge (fokus izin, `apply_workflow`, tanpa SQL langsung).
