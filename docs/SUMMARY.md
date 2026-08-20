# NextHD — Index Dokumentasi

> **Entry point.** Baca ini dulu — berisi overview dan pointer ke file detail.
>
> **Last updated:** 2026-08-20 13:00 WIB | **Repo:** `silverefendy/nexthd` | **Branch:** `main`

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
- Web Form self-service untuk Requester di `/tiket-saya` (merged 2026-08-20, PR #6) — **belum di-deploy ke server produksi**, perlu `bench migrate` + testing manual
- Workflow approval untuk Change Request (state machine terverifikasi via regression test, 2026-08-20)
- Manajemen Problem dan Known Error (ITIL-lite)
- Notifikasi real-time via Telegram Bot (string sudah i18n-ready via `frappe._()`, PR #6)
- SLA monitoring otomatis (warning 30 menit sebelum breach)
- Multi-tim dengan assignment agent
- Custom reports: Tiket per Bulan, Tiket per Kategori, Tiket per Prioritas (breach SLA)

---

## 2. Status Item Belum Dikerjakan

> Bagian ini yang **paling sering diupdate tiap sesi**. Item selesai dipindah ke `POLA_KERJA_DAN_BUG.md`.

| # | Fitur | Keterangan | PIC |
|---|---|---|---|
| 1 | User portal Requester | **Kode sudah merged (PR #6, 2026-08-20)** — Web Form `/tiket-saya` di `main`. **BELUM di-deploy** ke `desk.ciptamebel.co.id`: perlu `git pull` + `bench migrate` di server + testing manual (buat user Requester test, akses `/tiket-saya`, verifikasi field tersembunyi/terlihat sesuai spek, verifikasi isolasi data antar Requester) | Claude (deploy+test) |
| 2 | Workflow — testing end-to-end di UI (browser) | Regression test backend (`apply_workflow()`) sudah lulus 100% (2026-08-20) — tapi belum ditest klik manual di browser untuk memastikan tombol Actions & permission per role tampil benar | Efendy |
| 3 | Role assignment ke user spesifik | `support@ciptamebel.co.id` → role IT Manager. **Keputusan:** sementara 1 akun shared dulu untuk IT Manager, akun terpisah per orang menyusul nanti | Efendy |
| 4 | Pesan notifikasi Telegram i18n | **Kode sudah merged (PR #6, 2026-08-20)** — semua string di `telegram.py` sudah dibungkus `frappe._()`. **BELUM di-deploy** ke server produksi, perlu `git pull` di server + smoke-test kirim notif Telegram beneran (pastikan format pesan tidak berubah/rusak) | Claude (deploy+test) |
| 5 | Wipe data testing | **Desain sudah disepakati:** UI checkbox per DocType (bukan wipe semua sekaligus), hanya data transaksional (Ticket/Problem/CR/Asset dst) yang boleh terhapus — Business Hours/Holiday/SLA Policy/Team/Category/Settings/Workflow/Permission/User/Workspace TIDAK ikut terhapus. Desain harus baca prefix naming_series dari DocType meta secara dinamis (bukan hardcode), supaya tahan kalau prefix diganti nanti. Belum diimplementasi, waktu eksekusi masih "nanti saja" | Claude (desain), Efendy (waktu eksekusi) |

### GitHub Issues & PR — Riwayat Devin

| # | Judul | Status |
|---|---|---|
| [Issue #4](https://github.com/silverefendy/nexthd/issues/4) | User Portal Requester via Frappe Web Form | Selesai via PR #6 |
| [Issue #5](https://github.com/silverefendy/nexthd/issues/5) | Telegram Notification — i18n (`frappe._()`) | Selesai via PR #6 |
| [PR #6](https://github.com/silverefendy/nexthd/pull/6) | feat: Add Web Form for Requester role and Telegram i18n | **Merged ke main** 2026-08-20 06:59 UTC — belum dideploy ke server produksi |

---

*Dokumen ini dikelola oleh Claude. Update terakhir: 2026-08-20 13:00 WIB.*
