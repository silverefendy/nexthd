# NextHD — Index Dokumentasi

> **Entry point.** Baca ini dulu — berisi overview dan pointer ke file detail.
>
> **Last updated:** 2026-08-12 10:00 WIB | **Repo:** `silverefendy/nexthd` | **Branch:** `main`

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
| 1 | SLA Policy enforcement | Scheduler ada tapi logika Python belum diverifikasi end-to-end | Claude (verifikasi) |
| 2 | Custom reports | Per kategori, prioritas, bulan — butuh Query Report Python. Export Word tidak diprioritaskan | Devin |
| 3 | User portal Requester | Via Frappe Web Form. Keputusan dulu: requester punya akun atau tidak, bisa lihat status tiket sendiri atau cuma submit | Efendy (keputusan) → Devin |
| 4 | Workflow — testing end-to-end di UI | **Dikonfirmasi Efendy:** `Terbuka→Selesai` dan `Known Error→Selesai` di Problem OK. **Masih perlu:** test jalur `Selesai→Tutup→Ditutup` (state Ditutup punya `doc_status=1`/Submitted), test end-to-end Change Request via UI | Efendy (test) |
| 5 | Role assignment ke user spesifik | `support@ciptamebel.co.id` belum punya role IT Manager/Agent — via UI (User → Roles) | Efendy |
| 6 | Pesan notifikasi Telegram i18n | Hardcoded di `telegram.py`, belum pakai `frappe._()`. Prioritas rendah | Devin (nanti) |
| 7 | SLA Policy — angka response/resolution time | Belum ditentukan SOP-nya | Efendy (keputusan) → Claude (buat record) |
| 8 | Regression test `apply_workflow()` | Belum ada test otomatis seluruh jalur transisi | Claude/Devin |
| 9 | Hapus dokumen test workflow dari produksi | `PRB-2026-####00003`, `00004`, `00006` — perlu dihapus kalau bukan data asli | Efendy |
| 10 | Bereskan transitions terduplikasi di NextHD Change Request | Beberapa action muncul dua kali dengan role tumpang tindih — tidak error, tapi longgar | Claude |

---

*Dokumen ini dikelola oleh Claude. Update terakhir: 2026-08-12 10:00 WIB.*
