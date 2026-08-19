# NextHD — Index Dokumentasi

> **Entry point.** Baca ini dulu — berisi overview dan pointer ke file detail.
>
> **Last updated:** 2026-08-20 10:00 WIB | **Repo:** `silverefendy/nexthd` | **Branch:** `main`

---

## Struktur Dokumentasi

| File | Isi |
|---|---|
| `docs/SUMMARY.md` | **File ini** — index + project overview + status item belum dikerjakan |
| `docs/ARSITEKTUR.md` | Infrastruktur, struktur app, DocType/field lengkap, permissions, schema tabel, label ID |
| `docs/WORKFLOW.md` | Notifikasi Telegram + semua state machine + riwayat bug workflow |
| `docs/POLA_KERJA_DAN_BUG.md` | Frappe quirks (Desktop/Workspace), aturan wajib saat coding/debug, riwayat bug lengkap |
| `docs/SETUP_DAN_ROADMAP.md` | Instalasi, setup Telegram/SLA, alur deploy, pembagian kerja, referensi |

---

## 1. Project Overview

| Item | Detail |
|---|---|
| **Nama App** | NextHD |
| **Tujuan** | Sistem ITSM internal (Incident, Problem, Change, Asset, Known Error, Service Catalog) untuk tim IT CML |
| **Basis** | Frappe Framework v16 murni (BUKAN ERPNext) |
| **User** | Karyawan internal saja |
| **Autentikasi** | Username-based login, TANPA email asli (email dummy `@noemail.internal`) |
| **Notifikasi** | Telegram Bot (utama) + In-app notification bawaan Frappe — TIDAK pakai email |
| **Bahasa UI** | Bahasa Indonesia (default) |
| **Cakupan ITIL** | Incident, Problem, Change, Known Error, Asset/CMDB, Service Catalog |
| **Repo Git** | `silverefendy/nexthd`, branch `main` |
| **Alur Development** | Claude (kerangka & spesifikasi) → Devin (implementasi) → Claude (finishing, bugfix, review) |

### Modul Aplikasi

- Manajemen tiket insiden dan permintaan layanan
- Workflow approval untuk Change Request
- Manajemen Problem dan Known Error (ITIL-lite)
- Notifikasi real-time via Telegram Bot
- SLA monitoring otomatis (warning 30 menit sebelum breach)
- Multi-tim dengan assignment agent

---

## 2. Status Item Belum Dikerjakan

> Bagian ini yang **paling sering diupdate tiap sesi**. Item selesai dipindah ke `POLA_KERJA_DAN_BUG.md`.

| # | Fitur | Keterangan | PIC |
|---|---|---|---|
| 1 | Custom reports — verifikasi produksi | Per kategori, prioritas, bulan — **SELESAI** (PR #1 Devin, commit b4e326f). Sekarang `sla_resolution_by` sudah terisi benar (business hours fix beres) — tinggal test jalan di produksi | Efendy (testing) |
| 2 | User portal Requester | Via Frappe Web Form. **Keputusan sudah ada:** akun baru khusus per karyawan (bukan email kantor existing), reset password manual oleh IT dari Frappe. Belum diimplementasi | Devin |
| 3 | Workflow — testing end-to-end di UI | Belum ditest: jalur `Selesai→Tutup→Ditutup`, end-to-end Change Request. **Keputusan:** boleh test kapan saja, server online terus | Efendy |
| 4 | Role assignment ke user spesifik | `support@ciptamebel.co.id` → role IT Manager. **Keputusan:** sementara 1 akun shared dulu untuk IT Manager, akun terpisah per orang menyusul nanti | Efendy |
| 5 | Pesan notifikasi Telegram i18n | Hardcoded di `telegram.py`, belum pakai `frappe._()`. Dikerjakan sekalian bareng task lain (tidak di-skip lagi) | Devin |
| 6 | Regression test `apply_workflow()` | Belum ada test otomatis seluruh jalur transisi. Baru masuk akal dikerjakan sekarang karena dedup workflow (item selesai) sudah beres | Claude |
| 7 | Wipe data testing | **Desain sudah disepakati:** UI checkbox per DocType (bukan wipe semua sekaligus), hanya data transaksional (Ticket/Problem/CR/Asset dst) yang boleh terhapus — Business Hours/Holiday/SLA Policy/Team/Category/Settings/Workflow/Permission/User/Workspace TIDAK ikut terhapus. Desain harus baca prefix naming_series dari DocType meta secara dinamis (bukan hardcode), supaya tahan kalau prefix diganti nanti. Belum diimplementasi, waktu eksekusi masih "nanti saja" | Claude (desain), Efendy (waktu eksekusi) |

---

*Dokumen ini dikelola oleh Claude. Update terakhir: 2026-08-20 10:00 WIB.*
