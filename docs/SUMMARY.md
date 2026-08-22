# NextHD — Index Dokumentasi

> **Entry point.** Baca ini dulu — berisi overview dan pointer ke file detail.
>
> **Last updated:** 2026-08-22 10:35 WIB | **Repo:** `silverefendy/nexthd` | **Branch:** `main`

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
- SLA monitoring otomatis berbasis jam kerja (warning 30 menit sebelum breach), termasuk **titik-mulai resolution saat "Mulai Kerjakan" + pause/resume saat "Menunggu User"** (PR #8, merged 2026-08-22) — **kode sudah di `main`, belum di-deploy ke server produksi**
- Priority otomatis dari matriks Impact × Urgency, dengan override manual untuk Agent Manager/IT Manager (PR #7, merged 2026-08-22) — **kode sudah di `main`, belum di-deploy ke server produksi**
- Multi-tim dengan assignment agent
- Custom reports: Tiket per Bulan, Tiket per Kategori, Tiket per Prioritas (breach SLA)

---

## 2. Status Item Belum Dikerjakan

> Bagian ini yang **paling sering diupdate tiap sesi**. Item selesai dipindah ke `POLA_KERJA_DAN_BUG.md`.
>
> **Update 2026-08-22 10:35 WIB** — PR #7 dan PR #8 dari Devin sudah **merged ke `main`**. Item A, B, C, T (dan U, yang sebelumnya sudah dicommit langsung 2026-08-22 02:48 WIB) kini berstatus "kode selesai, menunggu deploy + test manual di server produksi", BUKAN lagi "belum ada di kode". Lihat §3 di bawah untuk cara test.

### 🔴 Prioritas Tinggi — Belum Ada di Kode

_Tidak ada item di kategori ini saat ini — seluruh item A, B, C, T, U sudah punya implementasi di `main` (lihat tabel Prioritas Sedang di bawah untuk status deploy)._

### 🟡 Prioritas Sedang — Kode Sudah Ada, Perlu Deploy/Verifikasi

| # | Fitur | Keterangan | PIC |
|---|---|---|---|
| A+C | Priority matrix otomatis + override permission | **Merged via [PR #7](https://github.com/silverefendy/nexthd/pull/7)** (2026-08-22 10:13 WIB). `set_priority_from_matrix()` di `validate()`: Tinggi+Tinggi=Kritis, Tinggi+Rendah=Tinggi, Rendah+Tinggi=Sedang, Rendah+Rendah=Rendah. Field `priority` diubah dari `read_only=1` ke `permlevel=1` + permission `write:1` untuk Agent Manager & IT Manager di permlevel itu. Field baru `priority_manually_set` (Check, hidden) mencegah override manual tertimpa matrix lagi. 8 test case baru, semua skenario matrix + override tercover. **Belum di-`bench migrate`+test manual di server produksi** | Efendy |
| B+T | Pause/resume SLA + recalculate saat "Mulai Kerjakan" | **Merged via [PR #8](https://github.com/silverefendy/nexthd/pull/8)** (2026-08-22 10:31 WIB). `on_update()` memanggil `handle_workflow_sla_transitions()`, deteksi `has_value_changed("status")` + `get_doc_before_save()`, 4 skenario: Baru→Sedang Dikerjakan (recalculate `sla_resolution_by` + set `responded_on`), Sedang Dikerjakan→Menunggu User (buat `waiting_log` entry), Menunggu User→Sedang Dikerjakan (tutup `waiting_log` + extend `sla_resolution_by` sebesar durasi pause), Menunggu User→Selesai (tutup `waiting_log` tanpa extend). Pakai `self.db_set(...)` (bukan `self.save()`) di dalam `on_update()` — risiko infinite recursion yang diwanti-wanti sebelumnya sudah ditangani dengan benar, ada test khusus `test_workflow_sla_no_infinite_recursion`. 6 test case baru. **Belum di-`bench migrate`+test manual di server produksi** | Efendy |
| U | `NextHD SLA Policy` & `NextHD Business Hours` — permission kosong (root cause 404 item G) | Sudah di-commit & push langsung ke `main` 2026-08-22 09:48 WIB (commit `31f35da`, sebelum PR #7/#8): tambah baris `permissions` untuk kedua DocType. **Belum diverifikasi ulang diff-nya secara detail sebelumnya oleh Claude** (catatan sesi lama) — sudah dicek ulang sesi ini via commit history, konsisten dengan yang dimaksud. **Belum di-`bench migrate` di server produksi** | Efendy |
| D | Deploy PR #6 ke server produksi | Web Form `/tiket-saya` + Telegram i18n sudah merged ke `main` (2026-08-20). **Belum di-`bench migrate`** di `desk.ciptamebel.co.id` — perlu `git pull` + `bench migrate` + testing manual (Web Form muncul, bisa dipakai role Requester, isolasi data antar Requester benar) | Claude / Efendy |
| E | Verifikasi end-to-end Telegram di produksi | Source code sudah benar (`get_bot_token()` & `is_telegram_enabled()` sudah pakai `frappe.db.get_value()`, bukan `get_single_value()`), sudah di-commit. **Belum ada bukti retest setelah `bench restart`** — perlu dikonfirmasi apakah bot sudah balas `/start` di Telegram nyata | Efendy |
| F | Permission `reply` di Waiting Log | Diverifikasi 2026-08-22: `nexthd_ticket_waiting_log.json` sudah benar — `reply` field `permlevel=1`, ada baris permission `Requester, permlevel:1, write:1` terpisah dari baris `permlevel:0`. Konfigurasi JSON sudah tepat. **Masih belum pernah ditest end-to-end di UI produksi** | Efendy |
| G | Halaman NextHD SLA Policy 404 | Root cause kemungkinan besar sudah difix via item U (commit `31f35da`, 2026-08-22 09:48 WIB). **Belum di-deploy (`bench migrate`) ke server produksi** — setelah deploy, coba akses ulang halaman ini untuk konfirmasi 404 hilang | Efendy |
| H | `NextHD Holiday` di sidebar Workspace | Sudah ada di fixture `workspace_sidebar.json` (difix 2026-08-19), tapi belum dikonfirmasi tampil di sidebar UI produksi setelah deploy | Efendy |

### 🟢 Prioritas Rendah — Belum Mendesak / Masih Wacana

| # | Fitur | Keterangan | PIC |
|---|---|---|---|
| I | Wipe data testing | Desain sudah disepakati: UI checkbox per DocType, hanya data transaksional, prefix naming_series dibaca dinamis dari meta. Belum diimplementasi | Claude (desain), Efendy (waktu eksekusi) |
| J | Workflow — testing end-to-end di UI browser | Regression test backend sudah lulus 100% (2026-08-20). Belum ditest klik manual di browser untuk verifikasi tombol Actions & permission per role tampil benar | Efendy |
| K | Role assignment ke user spesifik | `support@ciptamebel.co.id` → role IT Manager. Keputusan: sementara 1 akun shared dulu | Efendy |
| L | File `HANDOFF_SLA_NextHD_2026-08-19.md` | Disebut di HANDOFF.md tapi tidak ada di repo. Kalau masih ada di server, perlu `git add` + commit sebelum hilang | Efendy |
| M | Guard permanen duplikasi workflow transition | Root cause re-import belum dikonfirmasi pasti, belum ada mekanisme pencegahan | Claude |
| N | Fitur Attach Image + kompresi otomatis | Direncanakan tapi belum dikerjakan — perlu sesi tersendiri | Devin |
| O | Dashboard "Aset Bermasalah" (Number Card) | Usulan, belum dikerjakan | - |
| P | SLA otomatis untuk Problem/Change Request | Saat ini SLA hanya untuk Ticket | - |
| Q | Notifikasi Telegram untuk Problem/CR | Sengaja ditunda, fokus ke fitur lain dulu | - |
| R | Laporan bulanan otomatis (jumlah tiket, MTTR) | Usulan, belum dikerjakan | - |
| S | Generalisasi ke domain non-IT (Asset Category/Attribute EAV) | Rencana teknis ada di `ARSITEKTUR.md §8`, masih wacana | - |

### GitHub Issues & PR — Riwayat Devin

| # | Judul | Status |
|---|---|---|
| [Issue #4](https://github.com/silverefendy/nexthd/issues/4) | User Portal Requester via Frappe Web Form | Selesai via PR #6 |
| [Issue #5](https://github.com/silverefendy/nexthd/issues/5) | Telegram Notification — i18n (`frappe._()`) | Selesai via PR #6 |
| [PR #6](https://github.com/silverefendy/nexthd/pull/6) | feat: Add Web Form for Requester role and Telegram i18n | **Merged ke main** 2026-08-20 06:59 UTC — **belum dideploy ke server produksi** |
| [PR #7](https://github.com/silverefendy/nexthd/pull/7) | Task 1: Implement automatic priority calculation (Impact × Urgency) and role-based override permission | **Merged ke main** 2026-08-22 03:13 UTC (10:13 WIB) — **belum dideploy ke server produksi** |
| [PR #8](https://github.com/silverefendy/nexthd/pull/8) | Task 2: Fix SLA resolution timing — start clock at "Mulai Kerjakan", pause during "Menunggu User" | **Merged ke main** 2026-08-22 03:31 UTC (10:31 WIB) — **belum dideploy ke server produksi** |

---

## 3. Hal-hal yang SUDAH Selesai (Ringkasan)

> Detail lengkap ada di `POLA_KERJA_DAN_BUG.md §4` dan riwayat update `HANDOFF.md`.

| Item | Selesai |
|---|---|
| `business_hours.py` — logic all-or-nothing | ✅ 2026-08-20 (diverifikasi langsung dari kode di repo 2026-08-22) |
| Tombol workflow "Mulai Kerjakan" (Baru → Sedang Dikerjakan) | ✅ Ada di `nexthd_ticket_workflow.json` (diverifikasi 2026-08-22) — total 7 transisi terverifikasi sesuai `WORKFLOW.md` |
| Field `impact`, `urgency`, `waiting_log` di form Ticket | ✅ Sudah ada di `field_order` dan `fields` di `nexthd_ticket.json` (diverifikasi 2026-08-22) |
| Permission `reply` di Waiting Log (JSON) | ✅ Konfigurasi `permlevel` sudah benar (diverifikasi 2026-08-22) — lihat item F untuk status test produksi |
| SLA enforcement jam kerja (`calculate_sla()` + `add_working_time()`) | ✅ 2026-08-20, ditest manual (TKT-2608-0004) — titik mulai resolution kini sudah direcalculate saat "Mulai Kerjakan" via PR #8 (lihat §2, belum di-deploy) |
| Priority matrix otomatis + override manual (item A+C) | ✅ Kode merged via PR #7 (2026-08-22) — lihat §2 untuk status deploy |
| Pause/resume SLA saat "Menunggu User" (item B+T) | ✅ Kode merged via PR #8 (2026-08-22) — lihat §2 untuk status deploy |
| Permission `NextHD SLA Policy` & `NextHD Business Hours` (item U) | ✅ Commit `31f35da` (2026-08-22) — lihat §2 untuk status deploy |
| Regression test workflow (Ticket, Problem, Change Request) | ✅ 2026-08-20, semua lulus |
| Dedup 21 transisi workflow duplikat | ✅ 2026-08-20 |
| Bug Telegram `get_single_value` | ✅ Fix di-commit, perlu retest di produksi (lihat item E) |
| Number Card dashboard (kolom `number_card_name`) | ✅ 2026-08-21 |
| Shortcut `doc_view` NextHD Settings | ✅ 2026-08-21 |
| Naming series seragam YY.MM semua DocType | ✅ 2026-08-19 |
| Export fixture + commit semua perubahan besar | ✅ Konsisten sejak 2026-08-15 |

---

*Dokumen ini dikelola oleh Claude. Update terakhir: 2026-08-22 10:35 WIB.*
