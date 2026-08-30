# HANDOFF NextHD — Log Riwayat Sesi

> **File ini adalah log sesi aktif** (bukan arsip beku — kebijakan lama dicabut Efendy,
> 30 Agustus 2026). Dipakai untuk catatan singkat lintas-sesi yang belum sempat masuk ke
> dokumen tematik lain. Begitu suatu detail sudah sepenuhnya terwakili di dokumen di bawah,
> entrinya boleh dipangkas dari sini — jangan menumpuk selamanya.
>
> **Rujukan utama** (baca ini duluan, bukan file ini, untuk detail teknis):
> - `docs/SUMMARY.md` — index, status terkini, open items
> - `docs/FAQ_DEVELOPER.md` — aturan navigasi terkunci + pembagian kerja Claude/Devin/Efendy
> - `docs/POLA_KERJA.md` — aturan wajib coding/debug + Frappe quirks
> - `docs/BUG_WORKSPACE_SIDEBAR.md` — riwayat bug Workspace/Desktop Icon/Sidebar/Dashboard
> - `docs/BUG_HISTORY.md` — riwayat bug lain (SLA, Telegram, naming series, Asset EAV, dll)
> - `docs/WORKFLOW.md` — state machine + riwayat bug workflow
> - `docs/ARSITEKTUR.md` — infrastruktur, DocType/field, permission, schema DB

---

## Konteks Proyek (Ringkas)

| Item | Detail |
|---|---|
| App | NextHD (Frappe Framework v16, custom ITSM helpdesk) |
| Site | `desk.ciptamebel.co.id` |
| Server | VM `erpnext`, Tailscale IP `100.64.0.14`, SSH: `it@erpnext` |
| Repo | `silverefendy/nexthd` (GitHub, branch `main`) |
| Bench path | `/home/it/frappe` |
| Alur tim | Claude (debug/SQL/dokumentasi) → Devin (implementasi via PR) → Efendy (verifikasi UI, eksekusi SSH) |

Aturan navigasi terkunci (4 komponen — jangan diubah tanpa persetujuan Efendy) sudah
didokumentasikan lengkap di `docs/FAQ_DEVELOPER.md` Bagian B Q1 — tidak diulang di sini.

---

## Keputusan Final Historis (Jangan Diulang Tanya)

| Keputusan | Detail |
|---|---|
| Dokumen lama kena bug penomoran `####` (sebelum naming series diseragamkan) | **Tidak di-rename** — dibiarkan apa adanya |
| Format naming series | `YY.MM` (reset bulanan), berlaku semua DocType termasuk Ticket — diputuskan 15 Agustus, menggantikan keputusan 14 Agustus |
| Tombol "Aksi" (Workflow Actions) terpisah dari custom button | Bukan bug — perilaku normal Frappe |
| SLA di luar jam kerja | All-or-nothing — durasi penuh diulang dari jam kerja berikutnya kalau tidak muat (diputuskan 19 Agustus) |
| Titik mulai `sla_resolution_by` | Saat tombol "Mulai Kerjakan" diklik, bukan saat tiket dibuat |
| Business Hours Sabtu | Memang hari kerja (08:00–15:00) — dikonfirmasi 25 Agustus, bukan bug |

---

## Info Teknis Frappe v16 — Kolom Tabel yang Tidak Ada (Referensi Cepat)

Selain yang sudah ada di `docs/ARSITEKTUR.md §6`, catatan tambahan dari eksplorasi awal project:

| Tabel | Kolom yang TIDAK ADA (beda dari dokumentasi umum Frappe) |
|---|---|
| `tabWorkspace` | `route` |
| `tabWorkspace Link` | `url` |
| `tabWorkspace Shortcut` | `for_user` |
| `tabModule Onboarding` | `reference_doctype` |
| `tabDesktop Icon` | `module_name` |
| `tabDocField` | `insert_after` (urutan field murni via kolom `idx`) |

---

## Log Sesi Ringkas

Sesi-sesi berikut sudah terdokumentasi tuntas di file tematik terkait — hanya dicatat
sebagai penanda tanggal/urutan di sini, detail lengkap ada di file yang ditunjuk.

| Tanggal | Ringkasan | Detail Lengkap Di |
|---|---|---|
| 14 Agustus | Navigasi icon NextHD → Workspace dashboard (4 komponen kunci) | `FAQ_DEVELOPER.md` Bagian B Q1 |
| 15 Agustus | Naming series diseragamkan `YY.MM` semua DocType; export fixture Client Script/Property Setter/DocField; relasi Asset ditambahkan | `BUG_HISTORY.md` sesi 15 Agustus |
| 16 Agustus | Data master diisi: Team, Category, Business Hours, SLA Policy | `ARSITEKTUR.md` §3 |
| 19 Agustus | Keputusan desain SLA sadar jam kerja + priority matrix; DocType `NextHD Holiday`/`NextHD Ticket Waiting Log` dibuat | `BUG_HISTORY.md` sesi 20 Agustus |
| 20–21 Agustus | Fix bug Telegram (`get_single_value`), PR #6 (Web Form Requester + i18n), dedup workflow round 1 | `BUG_HISTORY.md`, `WORKFLOW.md §5` |
| 22 Agustus | Verifikasi kode langsung dari repo; PR #7 (priority matrix) & PR #8 (pause/resume SLA) merged; bug waiting log hilang ditemukan & difix (`76ce3e9`) | `BUG_HISTORY.md` sesi 22 Agustus |
| 24 Agustus | Dedup workflow round 2, Cuti Bersama 2026, fix `install.py` SLA default, server ketinggalan commit (`git pull` report), root cause sidebar akhirnya ditemukan (`Workspace Sidebar` bukan `Workspace.links`) | `BUG_WORKSPACE_SIDEBAR.md`, `BUG_HISTORY.md` |
| 25 Agustus | Koreksi total: `Workspace.links` ternyata SUMBER ASLI sidebar (bukan `Workspace Sidebar Item`); dedup workflow round 3 (root cause: fixture repo menumpuk generasi lama) | `BUG_WORKSPACE_SIDEBAR.md`, `AUDIT_SISTEM.md` |
| 26 Agustus | Dashboard shortcut "NextHD Photo" + 6 Report; 5 workspace "Center" disembunyikan; konfirmasi Module Sidebar = limitasi Frappe v16 (GitHub Issue #36317) | `BUG_WORKSPACE_SIDEBAR.md` |
| 27 Agustus | Workspace "NextHD Report" (11 shortcut) — root cause 4 lapis kenapa tidak muncul di sidebar; lokasi fixture `Workspace Sidebar` yang benar ditemukan (`nexthd/nexthd/workspace_sidebar/`) | `BUG_WORKSPACE_SIDEBAR.md`, `POLA_KERJA.md §1.C` |
| 28 Agustus | Naming series `NextHD Photo`, Dashboard Connections "Dipakai Di", tombol "Reset Data Demo", EAV Asset (`NextHD Asset Category`+`Attribute`) live, schema drift `related_asset` ditemukan & difix | `BUG_HISTORY.md`, `DAFTAR_FITUR.md` |
| 29 Agustus | Item DD: bug `Link Type must be set first` pada Workspace NextHD + regresi sidebar "NextHD Reporting"; item JJ: cleanup field terstruktur Asset lama (duplikat EAV) | `SUMMARY.md` item DD/JJ, `BUG_WORKSPACE_SIDEBAR.md` |
| 30 Agustus | Item KK: sidebar "NextHD" +Asset Category (17 item), sidebar "NextHD Report" diperkaya 2→8 item; restrukturisasi dokumentasi — `POLA_KERJA_DAN_BUG.md` (82KB) dipecah jadi 3 file & dihapus dari repo; `HANDOFF.md` dirombak (file ini) | `SUMMARY.md` item KK |

---

*Dokumen ini dikelola oleh Claude. Dipangkas & dirombak total 30 Agustus 2026 — versi lama
(kronologi naratif penuh 14–24 Agustus, ~39KB) sudah sepenuhnya terwakili di file-file
tematik di atas dan tidak dipertahankan di sini.*
