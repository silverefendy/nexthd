# NextHD Web - Index Dokumentasi Portal

> Folder ini khusus dokumentasi **portal web NextHD** (halaman `www/` di dalam Frappe),
> terpisah dari dokumentasi aplikasi Desk di `docs/`. Sementara hanya tim IT yang memegang.
>
> **Last updated:** 2026-10-09 17:20 WIB

## Isi Folder

| File | Isi |
|---|---|
| `README.md` | File ini: index, alamat akses, aturan umum |
| `SPEC_PORTAL.md` | Spesifikasi teknis: struktur file, peran, keamanan, tahap, keputusan. Acuan Devin |
| `TASK_DEVIN_TAHAP_1_2.md` | Dokumen tugas rinci untuk Devin: PR 1 (fondasi) dan PR 2 (antrian, detail, buat tiket) |
| `TUGAS_TAHAP_3.md`, `TUGAS_TAHAP_3C.md`, `TUGAS_TAHAP_4.md`, `TUGAS_TAHAP_5.md` | Tugas rinci per tahap berikutnya (aksi workflow/worklog, polesan, dashboard Beranda, Problem/Known Error/Change Request/Asset) |
| `PRASYARAT_PR2.md`, `REVIEW_PR14.md`, `REVIEW_TAHAP_3.md` | Catatan prasyarat dan hasil review PR |
| `FITUR_WEB.md` | Checklist fitur portal per tahap (selesai / dikerjakan / rencana) |
| `LOG_WEB.md` | Log sesi ringkas pengerjaan portal |
| `BUG_WEB.md` | Riwayat bug portal dan Web Form `/tiket-saya`, serta pelajarannya |
| `TEMUAN_DOKUMEN_LAIN.md` | Catatan isi dokumen di luar `docs/web/` yang salah/usang (untuk diperbaiki belakangan) |

Terkait di luar folder ini: `docs/BUG_ASET_LOKASI_WEBFORM.md` (Lokasi, Pengguna Aset, dropdown Aset Terdampak di Web Form, 8–9 Okt 2026) dan `docs/TEMUAN_SLA_2026-10-02.md`.

## Aturan Dokumentasi

- Dokumen di luar `docs/web/` = sumber kebenaran, dibaca saja saat mengerjakan portal.
- Perubahan dokumen terkait portal hanya di `docs/web/`.
- Kalau menemukan isi dokumen lain yang salah/usang, catat di `TEMUAN_DOKUMEN_LAIN.md`; jangan diperbaiki langsung.

## Alamat Akses

Halaman `www/` disajikan oleh site Frappe yang sama dengan Desk, jadi tidak ada port atau domain lain.

| Lingkungan | Desk | Portal web |
|---|---|---|
| Lewat IP lokal | `http://10.1.0.16:8001/desk/nexthd` | `http://10.1.0.16:8001/nexthd` |
| Lewat domain | `https://desk.ciptamebel.co.id/desk/nexthd` | `https://desk.ciptamebel.co.id/nexthd` |

Kalau portal tidak terbuka lewat IP tetapi Desk terbuka, cek pemetaan site (Host header) dan
jalankan `bench --site desk.ciptamebel.co.id clear-website-cache`.

Halaman utama: `/nexthd` (Beranda/dashboard untuk IT), `/nexthd/kerja` (List Ticket), `/nexthd/problem`, `/nexthd/tentang` (landing lama). Web Form Requester: `/tiket-saya` (login wajib).

## Pembagian Kerja Portal

| Siapa | Tugas |
|---|---|
| Claude | Merancang spesifikasi, mereview PR (terutama keamanan), debug di server, dokumentasi `.md`, perubahan kecil lewat skrip patch/heredoc |
| Devin | Membangun implementasi (`.py/.js/.css/.html`) lewat PR (pekerjaan besar) |
| Efendy | Merge, pull, `bench build`, uji manual, keputusan bisnis |

Aturan repo tetap berlaku: Claude hanya push `.md`; kode lewat Devin atau dijalankan manual di server.

## Prinsip

1. Desk tetap ada untuk administrasi (SLA Policy, Team, Settings, Holiday). Portal untuk kerja harian.
2. Logika bisnis tetap di backend Frappe (workflow, SLA, Telegram). Portal hanya tampilan + endpoint tipis.
3. Tanpa framework frontend (tidak pakai frappe-ui/Vue/React). HTML + CSS + JS biasa (jalur A).
4. Aturan navigasi terkunci di `docs/FAQ_DEVELOPER.md` Q1 tidak boleh disentuh.
