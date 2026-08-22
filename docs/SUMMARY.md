# NextHD — Index Dokumentasi

> **Entry point.** Baca ini dulu — berisi overview dan pointer ke file detail.
>
> **Last updated:** 2026-08-22 16:15 WIB | **Repo:** `silverefendy/nexthd` | **Branch:** `main`

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
| **Notifikasi** | Telegram Bot (utama, **terkonfirmasi live** 22 Agustus) + In-app notification bawaan Frappe — TIDAK pakai email |
| **Bahasa UI** | Bahasa Indonesia (default) |
| **Cakupan ITIL** | Incident, Problem, Change, Known Error, Asset/CMDB, Service Catalog |
| **Repo Git** | `silverefendy/nexthd`, branch `main` |
| **Alur Development** | Claude (kerangka & spesifikasi) → Devin (implementasi) → Claude (finishing, bugfix, review) |

### Modul Aplikasi

- Manajemen tiket insiden dan permintaan layanan
- Web Form self-service untuk Requester di `/tiket-saya` (PR #6) — **✅ terkonfirmasi live** di produksi 22 Agustus (`published: 1`, route `tiket-saya` aktif)
- Workflow approval untuk Change Request (state machine terverifikasi via regression test, 2026-08-20)
- Manajemen Problem dan Known Error (ITIL-lite)
- Notifikasi real-time via Telegram Bot — **✅ terkonfirmasi live**, bot sudah balas dan token/enable sudah terkonfirmasi di NextHD Settings
- SLA monitoring otomatis berbasis jam kerja (warning 30 menit sebelum breach), termasuk **titik-mulai resolution saat "Mulai Kerjakan" + pause/resume saat "Menunggu User"** (PR #8, bugfix `76ce3e9`) — **✅ live + terverifikasi**
- Priority otomatis dari matriks Impact × Urgency, dengan override manual untuk Agent Manager/IT Manager (PR #7) — **✅ live + terverifikasi**
- Multi-tim dengan assignment agent
- Custom reports: Tiket per Bulan, Tiket per Kategori, Tiket per Prioritas (breach SLA)

---

## 2. Status Item Belum Dikerjakan

> Bagian ini yang **paling sering diupdate tiap sesi**. Item selesai dipindah ke `POLA_KERJA_DAN_BUG.md`.
>
> **Update 2026-08-22 16:15 WIB** — Item D, E, F, H (deploy PR #6, Telegram, permission reply, sidebar Holiday) sudah **diverifikasi live** via `bench console` di server produksi. **Backlog SLA/priority/deploy sejak 19 Agustus dinyatakan TUNTAS 100%.** Sisa open items sekarang murni fitur baru/usulan (kategori 🟢), tidak ada lagi bug atau item setengah-jadi.

### ✅ Semua Item Utama SUDAH Live & Terverifikasi (Update Sesi Ini)

| # | Fitur | Bukti Verifikasi | PIC |
|---|---|---|---|
| A+C | Priority matrix otomatis + override permission | [PR #7](https://github.com/silverefendy/nexthd/pull/7). `bench console`: Impact=Tinggi+Urgency=Tinggi → `priority=Kritis` otomatis. `permlevel=1` + Agent Manager/IT Manager override terkonfirmasi | Efendy |
| B+T | Pause/resume SLA + recalculate saat "Mulai Kerjakan" | [PR #8](https://github.com/silverefendy/nexthd/pull/8) + bugfix `76ce3e9` (waiting_log sempat ke-wipe saat save berikutnya, sudah difix). `sla_resolution_by` ter-extend sesuai durasi pause, terverifikasi | Efendy |
| U | Permission `NextHD SLA Policy` & `Business Hours` | Commit `31f35da`. `has_permission()` role Agent Manager return `True` untuk read & write | Efendy |
| G | Halaman NextHD SLA Policy 404 | Root cause (item U) fix, halaman sudah bisa diakses non-Administrator | Efendy |
| D | Deploy PR #6 (Web Form + Telegram i18n) | `bench console`: Web Form `Tiket Saya` ditemukan, `route: tiket-saya`, `published: 1` | Efendy |
| E | Verifikasi end-to-end Telegram | Bot `@cmlhelpdesk_bot` terkonfirmasi balas pesan nyata (test manual 22 Agustus). `NextHD Settings`: token terisi, `enable_telegram_notification: 1` | Efendy |
| F | Permission `reply` di Waiting Log | `bench console`: field `reply` `permlevel=1`, role Requester `permlevel=1, write=1` — konfigurasi terkonfirmasi benar | Efendy |
| H | `NextHD Holiday` di sidebar Workspace | `bench console`: query `tabWorkspace Sidebar Item` → Holiday ditemukan (`True`) | Efendy |

> **Catatan Item E:** user test `test.requester@ciptamebel.co.id` sendiri belum pernah kirim `/start`+`/link` ke bot (field `telegram_chat_id` masih kosong untuk akun ini) — tapi ini bukan bug, cuma user dummy tsb memang belum di-link manual. Bot-nya sendiri sudah terbukti bekerja pakai akun Telegram lain.

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
| V | Link Telegram untuk user test `test.requester` | Belum pernah kirim `/start`+`/link` — kalau mau dites tuntas, tinggal eksekusi manual + rerun script verifikasi | Efendy |

### GitHub Issues & PR — Riwayat Devin

| # | Judul | Status |
|---|---|---|
| [Issue #4](https://github.com/silverefendy/nexthd/issues/4) | User Portal Requester via Frappe Web Form | Selesai via PR #6 |
| [Issue #5](https://github.com/silverefendy/nexthd/issues/5) | Telegram Notification — i18n (`frappe._()`) | Selesai via PR #6 |
| [PR #6](https://github.com/silverefendy/nexthd/pull/6) | feat: Add Web Form for Requester role and Telegram i18n | Merged 2026-08-20 — **✅ dideploy & terverifikasi live 22 Agustus** |
| [PR #7](https://github.com/silverefendy/nexthd/pull/7) | Task 1: Priority matrix otomatis + override permission | Merged 2026-08-22 10:13 WIB — **✅ live + terverifikasi** |
| [PR #8](https://github.com/silverefendy/nexthd/pull/8) | Task 2: SLA resolution timing — mulai "Mulai Kerjakan", pause "Menunggu User" | Merged 2026-08-22 10:31 WIB, bugfix `76ce3e9` — **✅ live + terverifikasi** |

---

## 3. Hal-hal yang SUDAH Selesai (Ringkasan)

> Detail lengkap ada di `POLA_KERJA_DAN_BUG.md §4` dan riwayat update `HANDOFF.md`.

| Item | Selesai |
|---|---|
| `business_hours.py` — logic all-or-nothing | ✅ 2026-08-20 |
| Tombol workflow "Mulai Kerjakan" (Baru → Sedang Dikerjakan) | ✅ Ada di `nexthd_ticket_workflow.json`, 7 transisi terverifikasi |
| Field `impact`, `urgency`, `waiting_log` di form Ticket | ✅ Ada di `field_order` `nexthd_ticket.json` |
| Priority matrix otomatis + override manual (item A+C) | ✅ PR #7, **live + terverifikasi 22 Agustus** |
| Pause/resume SLA saat "Menunggu User" (item B+T) | ✅ PR #8 + bugfix `76ce3e9`, **live + terverifikasi 22 Agustus** |
| Permission `NextHD SLA Policy` & `NextHD Business Hours` (item U) | ✅ Commit `31f35da`, **live + terverifikasi 22 Agustus** |
| Halaman NextHD SLA Policy 404 (item G) | ✅ Root cause (item U) fix, **live + terverifikasi 22 Agustus** |
| Deploy PR #6 ke produksi (item D) | ✅ **Live + terverifikasi 22 Agustus** — Web Form `tiket-saya` published |
| Verifikasi Telegram end-to-end (item E) | ✅ **Live + terverifikasi 22 Agustus** — bot balas, settings terkonfirmasi |
| Permission `reply` Waiting Log (item F) | ✅ **Terverifikasi 22 Agustus** — permlevel & role permission benar |
| `NextHD Holiday` di sidebar (item H) | ✅ **Terverifikasi 22 Agustus** — ditemukan di query sidebar |
| Regression test workflow (Ticket, Problem, Change Request) | ✅ 2026-08-20, semua lulus |
| Dedup 21 transisi workflow duplikat | ✅ 2026-08-20 |
| Bug Telegram `get_single_value` | ✅ Fix commit, dan sudah diverifikasi live (item E) |
| Number Card dashboard (kolom `number_card_name`) | ✅ 2026-08-21 |
| Shortcut `doc_view` NextHD Settings | ✅ 2026-08-21 |
| Naming series seragam YY.MM semua DocType | ✅ 2026-08-19 |

---

*Dokumen ini dikelola oleh Claude. Update terakhir: 2026-08-22 16:15 WIB.*
