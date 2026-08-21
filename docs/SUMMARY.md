# NextHD — Index Dokumentasi

> **Entry point.** Baca ini dulu — berisi overview dan pointer ke file detail.
>
> **Last updated:** 2026-08-22 01:00 WIB | **Repo:** `silverefendy/nexthd` | **Branch:** `main`

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
- SLA monitoring otomatis berbasis jam kerja (warning 30 menit sebelum breach) — **verifikasi kode: sudah benar di repo, TAPI lihat item T untuk gap titik-mulai resolution**
- Multi-tim dengan assignment agent
- Custom reports: Tiket per Bulan, Tiket per Kategori, Tiket per Prioritas (breach SLA)

---

## 2. Status Item Belum Dikerjakan

> Bagian ini yang **paling sering diupdate tiap sesi**. Item selesai dipindah ke `POLA_KERJA_DAN_BUG.md`.
>
> **Verifikasi kode langsung ke repo dilakukan 2026-08-22** — status di bawah mencerminkan kondisi aktual kode, bukan catatan sesi sebelumnya.

### 🔴 Prioritas Tinggi — Belum Ada di Kode

| # | Fitur | Keterangan | PIC |
|---|---|---|---|
| A | Logic priority otomatis (Impact × Urgency) | Field `impact` & `urgency` sudah ada di `nexthd_ticket.json`, tapi `nexthd_ticket.py` **belum punya logic matriks sama sekali** — `priority` saat ini `read_only=1` tapi tidak pernah diisi otomatis. Desain: Tinggi+Tinggi=Kritis, Tinggi+Rendah=Tinggi, Rendah+Tinggi=Sedang, Rendah+Rendah=Rendah | Devin / Claude |
| B | Pause/resume SLA saat "Menunggu User" | Child table `NextHD Ticket Waiting Log` sudah ada di JSON, tapi **tidak ada hook** di `nexthd_ticket.py` yang menghitung durasi pause dan menambahkannya ke `sla_resolution_by` saat transisi "Lanjut Kerjakan" | Devin / Claude |
| C | Override permission `priority` untuk Agent Manager / IT Manager | Field `priority` saat ini `read_only=1` global (di JSON). Belum ada mekanisme `permlevel` yang mengizinkan Agent Manager / IT Manager untuk override | Devin / Claude |
| T | `sla_resolution_by` tidak recalculate saat "Mulai Kerjakan" diklik | **BARU DITEMUKAN 2026-08-22, verifikasi langsung `nexthd_ticket.py`.** Keputusan desain 19 Agustus: titik mulai `sla_resolution_by` seharusnya saat tombol "Mulai Kerjakan" diklik, bukan saat tiket dibuat. Tapi `calculate_sla()` di kode HANYA dipanggil di `validate()` saat `self.is_new()` — dihitung sekali dari `now_datetime()` saat insert, dan TIDAK ada hook `on_update`/workflow transition yang recalculate saat status berubah ke "Sedang Dikerjakan". Efeknya: tiket yang lama menunggu di status "Baru" sebelum dikerjakan akan salah hitung SLA resolution (mundur dari waktu insert, bukan waktu mulai kerja). Terkait erat dengan item B (pause/resume) — sebaiknya dikerjakan sekaligus | Devin / Claude |

### 🟡 Prioritas Sedang — Kode Sudah Ada, Perlu Deploy/Verifikasi

| # | Fitur | Keterangan | PIC |
|---|---|---|---|
| D | Deploy PR #6 ke server produksi | Web Form `/tiket-saya` + Telegram i18n sudah merged ke `main` (2026-08-20). **Belum di-`bench migrate`** di `desk.ciptamebel.co.id` — perlu `git pull` + `bench migrate` + testing manual (Web Form muncul, bisa dipakai role Requester, isolasi data antar Requester benar) | Claude / Efendy |
| E | Verifikasi end-to-end Telegram di produksi | Source code sudah benar (`get_bot_token()` & `is_telegram_enabled()` sudah pakai `frappe.db.get_value()`, bukan `get_single_value()`), sudah di-commit. **Belum ada bukti retest setelah `bench restart`** — perlu dikonfirmasi apakah bot sudah balas `/start` di Telegram nyata | Efendy |
| F | Permission `reply` di Waiting Log | Field `reply` di `NextHD Ticket Waiting Log` sudah di-set `permlevel=1` supaya hanya Requester yang bisa isi. **Belum pernah ditest** apakah benar-benar jalan | Efendy |
| G | Halaman NextHD SLA Policy 404 | Error 404 saat akses langsung via URL. Dugaan: perlu `bench build` penuh, bukan cuma `clear-cache`. **Belum dicoba** | Efendy |
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

---

## 3. Hal-hal yang SUDAH Selesai (Ringkasan)

> Detail lengkap ada di `POLA_KERJA_DAN_BUG.md §4` dan riwayat update `HANDOFF.md`.

| Item | Selesai |
|---|---|
| `business_hours.py` — logic all-or-nothing | ✅ 2026-08-20 (diverifikasi langsung dari kode di repo 2026-08-22) |
| Tombol workflow "Mulai Kerjakan" (Baru → Sedang Dikerjakan) | ✅ Ada di `nexthd_ticket_workflow.json` (diverifikasi 2026-08-22) |
| Field `impact`, `urgency`, `waiting_log` di form Ticket | ✅ Sudah ada di `field_order` dan `fields` di `nexthd_ticket.json` (diverifikasi 2026-08-22) |
| SLA enforcement jam kerja (`calculate_sla()` + `add_working_time()`) | ✅ 2026-08-20, ditest manual (TKT-2608-0004) — **titik mulai resolution masih dari insert, bukan "Mulai Kerjakan", lihat item T** |
| Regression test workflow (Ticket, Problem, Change Request) | ✅ 2026-08-20, semua lulus |
| Dedup 21 transisi workflow duplikat | ✅ 2026-08-20 |
| Bug Telegram `get_single_value` | ✅ Fix di-commit, perlu retest di produksi (lihat item E) |
| Number Card dashboard (kolom `number_card_name`) | ✅ 2026-08-21 |
| Shortcut `doc_view` NextHD Settings | ✅ 2026-08-21 |
| Naming series seragam YY.MM semua DocType | ✅ 2026-08-19 |
| Export fixture + commit semua perubahan besar | ✅ Konsisten sejak 2026-08-15 |

---

*Dokumen ini dikelola oleh Claude. Update terakhir: 2026-08-22 01:00 WIB.*
