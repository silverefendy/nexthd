# NextHD — Daftar Fitur (Checklist Lengkap)

> **Satu tempat untuk cek semua fitur** — sudah selesai, sedang dikerjakan, atau masih
> rencana. (Sebelumnya `ROADMAP_FITUR.md`, sekarang termasuk juga desain yang sebelumnya
> nyasar di `ARSITEKTUR.md §8` dan `§9`).
>
> Status: ✅ Selesai & Live | 🔶 Sedang Dikerjakan/Menunggu Konfirmasi | ⬜ Belum Dikerjakan (Rencana)
>
> **Last updated:** 2026-08-30 (tambah spec Devin: Guard Duplikasi Workflow Transition — lihat Tier 1)

---

## Fitur Inti (Sudah Selesai & Live)

| Fitur | Status | Keterangan | Bukti/Referensi |
|---|---|---|---|
| SLA sadar jam kerja (all-or-nothing) | ✅ | `business_hours.py`, resolusi diulang penuh dari jam kerja berikutnya kalau tidak muat | `docs/BUG_HISTORY.md`, 20 Agustus |
| Tombol workflow "Mulai Kerjakan" | ✅ | Baru → Sedang Dikerjakan, catat `responded_on` | `nexthd_ticket_workflow.json` |
| Field impact/urgency/waiting_log di form Ticket | ✅ | Ada di `field_order` | `nexthd_ticket.json` |
| Priority matrix otomatis (Impact × Urgency) | ✅ | + override manual Agent Manager/IT Manager | [PR #7](https://github.com/silverefendy/nexthd/pull/7) |
| Pause/resume SLA saat "Menunggu User" | ✅ | + recalculate saat "Mulai Kerjakan" | [PR #8](https://github.com/silverefendy/nexthd/pull/8), bugfix `76ce3e9` |
| Permission NextHD SLA Policy & Business Hours | ✅ | Agent Manager/IT Manager override | Commit `31f35da` |
| Halaman NextHD SLA Policy 404 | ✅ | Root cause = permission, sudah fix | — |
| Web Form self-service `/tiket-saya` | ✅ | Requester bisa submit tiket sendiri | [PR #6](https://github.com/silverefendy/nexthd/pull/6), live 22 Agustus |
| Notifikasi Telegram (i18n) | ✅ | Bot terkonfirmasi balas pesan nyata | PR #6, verifikasi manual 22 Agustus |
| Permission `reply` di Waiting Log | ✅ | Requester bisa isi reply sendiri | Terverifikasi `bench console`, 22 Agustus |
| Sidebar Holiday di Workspace | ✅ | Terverifikasi via query | 22 Agustus |
| Regression test 3 workflow | ✅ | Ticket, Problem, Change Request semua lulus | 20 Agustus |
| Dedup transisi workflow duplikat | ✅ | 42 → 21 baris bersih (dedup pertama, 20 Agustus). **Duplikasi muncul lagi dan dibersihkan ulang 24 & 25 Agustus — lihat `docs/BUG_HISTORY.md` & `docs/WORKFLOW.md §5`. Guard pencegahan otomatis sekarang jadi task Devin, lihat Tier 1** | 20 Agustus |
| Number Card dashboard | ✅ | Fix `number_card_name` | 21 Agustus |
| Naming series seragam YY.MM | ✅ | Semua 6 DocType | 19 Agustus |
| `FAQ_DEVELOPER.md` | ✅ | Kurasi masalah berulang untuk Devin | 22 Agustus |
| `AUDIT_SISTEM.md` | ✅ | Script audit lengkap kesehatan server/repo | 23 Agustus |
| Fitur foto reusable (Ticket/Problem/Asset/Known Error) | ✅ | DocType `NextHD Photo` + `NextHD Photo Link`, galeri swipe, kompresi otomatis (Pillow), auto-copy saat convert Ticket→Problem/Problem→Known Error | PR #9, commit `03a3c5d`, merged 24 Agustus |
| NextHD Photo di sidebar Workspace + dashboard Number Card | ✅ | Link sidebar setelah Known Error, card "Total Foto Terupload" di dashboard, fixture Number Card lengkap (9 card, sebelumnya 0 ter-fixture). **Sempat tidak muncul di UI meski data sudah benar — root cause & fix di bawah** | Commit `a69df61`, 24 Agustus |
| Bug SLA Kritis `is_24x7` tidak sesuai SOP | ✅ | Diperbaiki langsung di DB via `bench console`, `is_24x7` Kritis: 0→1 | 24 Agustus |
| Business Hours Minggu (hari libur) | ✅ | Record ke-7 dibuat, `is_working_day=0` | 24 Agustus |
| NextHD Holiday 2026 — 17 hari libur nasional | ✅ | Diisi sesuai SKB 3 Menteri No. 1497/2025, 2/2025, 5/2025 (resmi Setneg) | 24 Agustus |
| `install.py` — nilai SLA default diperbaiki | ✅ | `create_default_sla_policies()` diupdate ke nilai SOP final 19 Agustus (Kritis 15/60 `is_24x7=1`, Tinggi 30/240, Sedang 60/2880, Rendah 120/10080) — instalasi baru sekarang otomatis dapat nilai benar | Commit `b3a24b2` → `2d795b9`, 24 Agustus |
| Sidebar "NextHD Photo" tidak muncul di UI meski data sudah live | ✅ | **Root cause:** `import_file_by_path(force=True)` berhasil sync field `number_cards`/`content` tapi TIDAK sync child table `links` (sidebar). **Fix:** append manual via `Workspace` doc ORM (`doc.append("links", ...)` + `doc.save()`), bukan reimport JSON | 24 Agustus |
| Duplikasi Workflow Transition (round 2) — Ticket/Problem/Change Request | ✅ | Ditemukan tiap transisi terduplikasi persis 4× (Ticket 28→7, Problem 24→6, CR 32→8). **Root cause dugaan awal:** `Workflow Action Master` "Convert to Known Error" tidak pernah dibuat. **Root cause sebenarnya (dikonfirmasi 25 Agustus):** fixture `workflow_transition.json` di repo menumpuk beberapa generasi export lama — lihat `docs/BUG_HISTORY.md` | 24–25 Agustus |
| Cuti Bersama 2026 — 8 hari | ✅ | Ditambahkan ke `NextHD Holiday` (total jadi 25 record: 17 nasional + 8 cuti bersama). **⚠️ Pemetaan tanggal↔nama event asumsi Claude berdasar pola umum, belum dicek silang ke teks SKB asli** | 24 Agustus |
| Script verifikasi ringan pasca-perbaikan | ✅ | Ditambahkan ke `AUDIT_SISTEM.md` — smoke test 9 titik spesifik (workflow, sidebar, number card, SLA, business hours, holiday, roles, photo doctype) | 24 Agustus |
| Naming Series `NextHD Photo` → `IMG-YYMM-####` | ✅ | `autoname: hash` → `naming_series:`, `naming_rule` → "By Naming Series field", field `naming_series` (Select, hidden, opsi `IMG-.YY.MM.-.####`). Terverifikasi: dokumen baru `IMG-2608-0001` dst | 28 Agustus |
| Field baru `NextHD Photo` — Judul Foto, Lokasi, Kategori | ✅ | `photo_title` (Data, jadi `title_field`), `location` (Data), `category` (Link → `NextHD Category`, reuse DocType existing). **Keputusan desain:** referensi balik "dipakai di dokumen mana" sengaja TIDAK disimpan sebagai field tunggal (`reference_doctype`/`reference_name`) karena 1 foto bisa dipakai ulang di >1 dokumen — field tunggal akan tertimpa. Solusi dipindah ke Dashboard Connections (baris di bawah) | 28 Agustus |
| Dashboard Connections "Dipakai Di" pada `NextHD Photo` | ✅ | `get_dashboard_data()` di `nexthd_photo.py` — badge "Connections" real-time dihitung dari child table `NextHD Photo Link` di 4 parent (Ticket/Asset/Problem/Known Error), bukan field statis tersimpan. Trade-off: tidak bisa dipakai untuk filter/Report View (bukan field DB) — kalau nanti butuh laporan semacam itu perlu solusi tambahan terpisah. **Terpasang, perlu re-test dengan foto baru** (foto contoh lama sudah ikut terhapus tombol Reset Data Demo) | 28 Agustus |
| Tombol admin "Reset Data Demo" | ✅ | Custom Page `nexthd-reset-data` (shortcut section "Admin" di Workspace NextHD) memanggil `reset_demo_data()` di `nexthd/api.py`. Hapus 6 DocType transaksional (Ticket, Problem, Change Request, Known Error, Asset, Photo) + child table terkait, pertahankan data master (Category, Team, SLA Policy). Akses System Manager only (dicek di backend via `frappe.get_roles`), 2x konfirmasi (dialog + ketik `RESET` persis), backup otomatis (`frappe.utils.backups.new_backup()`), counter `tabSeries` ikut direset. **Test sungguhan berhasil:** 14 Ticket, 15 Problem, 3 Change Request, 2 Known Error, 6 Asset, 4 Photo terhapus, backup terbuat, data master utuh | 28 Agustus |
| Generalisasi NextHD Asset ke pola EAV | ✅ | `NextHD Asset Category` + `NextHD Asset Attribute` — lihat `docs/ARSITEKTUR.md §3` untuk detail lengkap | 28–29 Agustus |
| Bug `Link Type must be set first` pada Workspace NextHD | ✅ | Row "Reporting Data" bermasalah dihapus dari `tabWorkspace Link` — lihat `docs/BUG_WORKSPACE_SIDEBAR.md` item DD | 29 Agustus |

---

## 🔴 Bug Perlu Diperbaiki

| Bug | Status | Keterangan | PIC |
|---|---|---|---|
| Rename Module "Next Helpdesk" → "NextHD" belum dieksekusi | 🔴 | `tabModule Def` masih "Next Helpdesk" — sidebar module-based (Report page, Page kustom) masih menampilkan header lama. Dikonfirmasi 28 Agustus bukan Workspace nyasar. Perlu rename `Module Def` + update `modules.txt`, risiko menengah, sesi terpisah dengan backup — lihat `docs/SUMMARY.md` item EE | Claude + Efendy |

> **Catatan 30 Agustus:** dua bug lain yang sebelumnya tercatat di sini (Business Hours Sabtu, `Link Type must be set first`) **sudah selesai** — dipindah ke tabel "Fitur Inti" di atas / `docs/SUMMARY.md`. Cek `docs/SUMMARY.md §2` untuk daftar item pending terkini yang paling update (file ini diupdate lebih jarang dari `SUMMARY.md`).

---

## Tier 1 — Rencana Prioritas Berikutnya (Quick Win)

| Fitur | Status | Keterangan | Bergantung Pada |
|---|---|---|---|
| **Guard Duplikasi Workflow Transition** | ⬜ | Validasi otomatis di `Workflow.validate()` supaya duplikasi transisi tidak bisa tersimpan lagi — sudah 3× terjadi manual (20, 24, 25 Agustus). Spec lengkap di bawah | — |
| Knowledge Article (`NextHD Knowledge Article`) | ⬜ | DocType baru, field `visibility` (Publik/Internal) — solusi mandiri untuk requester, terpisah dari Known Error (yang teknis, untuk Agent). Lihat detail desain di bawah | — |
| Tag di Tiket | ⬜ | Pakai sistem tag bawaan Frappe (`Tag` + `_user_tags`), bukan field custom | — |
| CSAT — survei kepuasan pasca-tiket | ⬜ | Field `csat_rating`, `csat_comment` di Ticket, trigger Telegram saat status "Selesai" | — |
| Merge tiket duplikat | ⬜ | Field `merged_into`, status "Digabung" | — |
| Auto-suggest Knowledge Article saat bikin tiket | ⬜ | Search artikel Publik yang cocok sebelum tiket disubmit | Knowledge Article |
| Dashboard trend chart | ⬜ | Tren volume tiket per minggu, breakdown kategori | — |
| Wipe Data Testing Tool — versi lengkap (UI checkbox per DocType) | ⬜ | Versi ringkas sudah live sebagai tombol "Reset Data Demo" (28 Agustus, lihat tabel Fitur Inti) — desain lengkap dengan granularitas per-DocType di bawah masih opsional kalau dibutuhkan | Reset Data Demo |

### Detail Desain: Guard Duplikasi Workflow Transition (Spec untuk Devin — ditambahkan 30 Agustus 2026)

**Latar belakang:** Duplikasi `Workflow Transition` (kombinasi `state`+`action`+`next_state`
sama muncul berkali-kali dalam satu Workflow) sudah terjadi 3× — 20, 24, dan 25 Agustus 2026.
Root cause final (dikonfirmasi 25 Agustus, lihat `docs/BUG_HISTORY.md`) adalah fixture JSON
di repo yang menumpuk beberapa generasi export lama, sudah dibersihkan permanen. Guard ini
adalah **lapisan pencegahan tambahan** supaya kalaupun duplikasi tersebab hal lain di masa
depan (reimport tidak sengaja, edit manual, dll), sistem menolak otomatis alih-alih diam-diam
menyimpan data rusak.

**Keputusan desain (Efendy, 30 Agustus):** dipilih dibanding alternatif "script deteksi manual
periodik" (yang sudah ada di `docs/AUDIT_SISTEM.md`) karena guard otomatis tidak bergantung
pada seseorang ingat menjalankan script — validasi terjadi di titik penyimpanan, permanen
untuk semua jalur (UI, `bench console`, migrate, PR Devin lain).

**Cakupan:** berlaku untuk ketiga Workflow custom project ini — `NextHD Ticket`,
`NextHD Problem`, `NextHD Change Request`. **Tidak berlaku** untuk Workflow bawaan/DocType
lain di luar NextHD (supaya tidak mempengaruhi bagian Frappe yang tidak terkait).

**Implementasi yang disarankan — via `doc_events` hook (BUKAN modifikasi core Frappe):**

Tambahkan validasi Python baru, didaftarkan di `hooks.py`:

```python
doc_events = {
    # ... hook existing lainnya, jangan dihapus ...
    "Workflow": {
        "validate": "nexthd.next_helpdesk.utils.workflow_guard.validate_no_duplicate_transitions"
    }
}
```

File baru: `nexthd/next_helpdesk/utils/workflow_guard.py`

```python
import frappe

NEXTHD_WORKFLOWS = {"NextHD Ticket", "NextHD Problem", "NextHD Change Request"}


def validate_no_duplicate_transitions(doc, method):
    """Cegah Workflow Transition duplikat tersimpan untuk 3 workflow NextHD.
    Duplikat didefinisikan sebagai baris dengan kombinasi
    (state, action, next_state) yang sama persis dalam satu Workflow.
    """
    if doc.name not in NEXTHD_WORKFLOWS:
        return

    seen = set()
    duplicates = []
    for row in doc.transitions:
        key = (row.state, row.action, row.next_state)
        if key in seen:
            duplicates.append(f"{row.state} -> [{row.action}] -> {row.next_state}")
        seen.add(key)

    if duplicates:
        frappe.throw(
            frappe._(
                "Ditemukan Workflow Transition duplikat, penyimpanan dibatalkan: {0}. "
                "Hapus baris duplikat sebelum menyimpan ulang."
            ).format(", ".join(duplicates))
        )
```

**Kenapa `validate` (bukan `before_save`/`on_update`):** `validate` dijalankan sebelum data
ditulis ke DB, jadi kalau ada duplikat, `frappe.throw()` membatalkan seluruh transaksi save —
tidak ada data setengah-tersimpan.

**⚠️ Risiko yang WAJIB ditest sebelum merge (bukan sekadar tempel kode):**
1. **Proses fixture import saat `bench migrate`** — pastikan guard ini tidak memblokir
   reimport fixture `workflow_transition.json` yang sah (fixture sekarang sudah bersih,
   tapi perlu dipastikan proses reimport tidak secara sementara membuat state duplikat
   di tengah proses sebelum akhirnya bersih).
2. **`bench console` manual save** — pastikan pesan error `frappe.throw()` jelas dan
   actionable buat Claude/Efendy saat debug via `bench console`, bukan traceback mentah.
3. **Regression test 3 workflow** (sudah ada dari sesi 20 Agustus) — jalankan ulang setelah
   guard terpasang, pastikan semua transisi valid existing tetap tersimpan normal.
4. **Test simulasi duplikat sengaja** — di `bench console`, coba `doc.append("transitions", {...})`
   dengan kombinasi yang sudah ada, panggil `doc.save()`, pastikan `frappe.throw()` terpicu
   dengan pesan yang menyebutkan transisi mana yang duplikat.

**Definition of Done:**
- [ ] File `workflow_guard.py` dibuat, hook terdaftar di `hooks.py`
- [ ] Test manual: simpan Workflow existing (Ticket/Problem/CR) tanpa perubahan — harus tetap sukses
- [ ] Test manual: coba append transisi duplikat lalu save — harus gagal dengan pesan jelas
- [ ] `bench migrate` uji tahan tidak menunjukkan error terkait guard ini
- [ ] Regression test 3 workflow (dari sesi 20 Agustus) tetap lulus semua
- [ ] Setelah merge & migrate di server, jalankan `check_workflow_transition_clean.py`
      (`docs/AUDIT_SISTEM.md`) sekali lagi untuk konfirmasi tidak ada regresi

### Detail Desain: Knowledge Article

**Keputusan (23 Agustus 2026):** DocType terpisah dari Known Error — Known Error ditulis
teknis untuk Agent (boleh detail infra), Knowledge Article ditulis untuk orang awam
(requester), campur keduanya berisiko bocorkan detail sensitif ke publik.

| Fieldname | Fieldtype | Keterangan |
|---|---|---|
| `title` | Data | Judul bahasa awam |
| `category` | Link (NextHD Category) | Reuse kategori existing |
| `content` | Text Editor | Langkah-langkah, boleh gambar |
| `visibility` | Select: Publik / Internal | Publik = baca tanpa login, Internal = role tertentu |
| `related_known_error` | Link (NextHD Known Error), opsional | Kalau lahir dari insiden nyata |
| `related_problem` | Link (NextHD Problem), opsional | Sama, opsional |
| `status` | Select: Draft / Published / Perlu Ditinjau Ulang | Approval sebelum tampil publik |
| `view_count` | Int, read-only | Tracking artikel paling sering dibaca |
| `author` | Link (User), read-only | Auto-fill |
| `last_reviewed_on` | Date | Penanda artikel perlu dicek relevansinya |

Artikel `visibility=Publik` perlu di-render lewat Frappe Web Page/Website Route (bukan Desk
form biasa) supaya bisa diakses tanpa login — pola mirip Web Form `/tiket-saya` tapi untuk
baca, bukan submit. Detail teknis dicek saat implementasi.

---

## Tier 2 — Struktural, Butuh Desain Lebih Matang

| Fitur | Status | Keterangan |
|---|---|---|
| Eskalasi otomatis | ⬜ | Bukan cuma warning H-30 menit — kalau SLA breach dan tiket belum direspon, auto-reassign/notify Agent Manager |
| Approval matrix Change Request (CAB sederhana) | ⬜ | 2 level: Agent Manager dulu, IT Manager kalau risiko tinggi |
| Bulk actions | ⬜ | Assign/tutup banyak tiket sekaligus |
| Integrasi PRTG → auto-create tiket | ⬜ | PRTG deteksi server down → otomatis bikin tiket |
| Arsip/retensi tiket lama | ⬜ | Tiket ditutup >1 tahun di-archive, bukan dihapus |
| **Generalisasi ke domain non-IT** | ✅ **sebagian sudah live** | EAV Asset (`NextHD Asset Category`+`Attribute`) sudah live 28-29 Agustus — lihat tabel Fitur Inti. Rencana perluasan ke DocType lain di luar Asset masih rencana |
| **Wipe Data Testing Tool (versi lengkap)** | ⬜ | `NextHD Data Wipe Tool`, whitelist DocType per-checkbox, konfirmasi eksplisit, dry-run preview — desain lengkap di bawah. **Versi ringkas (tanpa checkbox, hapus semua sekaligus) sudah live sebagai tombol "Reset Data Demo", 28 Agustus** — lihat tabel Fitur Inti |

### Detail Desain: Wipe Data Testing Tool (Versi Lengkap)

**Status:** Desain final disepakati 20 Agustus 2026, belum diimplementasi sepenuhnya —
**versi ringkas** (tombol "Reset Data Demo", hapus semua DocType transaksional sekaligus,
tanpa checkbox per-DocType) **sudah live 28 Agustus** dan mencakup sebagian besar prinsip
di bawah (whitelist hardcoded, backup otomatis, konfirmasi eksplisit, reset `tabSeries`).
Bagian yang **belum** ada di versi live: UI checkbox pilih DocType satu-satu, dry-run/preview
jumlah record sebelum hapus, dan log audit terpisah (siapa/kapan reset dijalankan).

**Tujuan:** hapus data transaksional testing (Ticket, Problem, CR, Asset, Known Error)
tanpa menyentuh data konfigurasi/master (Business Hours, Holiday, SLA Policy, Team,
Category, Settings, Workflow, Permission, User, Workspace).

**Prinsip desain:**
- UI checkbox per DocType (bukan tombol "Wipe All")
- **Whitelist**, bukan blacklist — DocType baru yang lupa didaftarkan otomatis TIDAK
  terhapus (fail-safe)
- Prefix naming_series dibaca dinamis dari DocType meta
- Konfirmasi eksplisit: ketik `HAPUS DATA TESTING` persis
- Dry-run/preview jumlah record dulu sebelum hapus beneran
- Log hasil wipe (DocType, jumlah, waktu, siapa eksekusi)

**Whitelist (boleh dihapus):** NextHD Ticket (TKT), NextHD Problem (PRB), NextHD Change
Request (CHG), NextHD Asset (AST), NextHD Known Error (KE), NextHD Service Catalog (SVC).

**Selalu dikecualikan:** Business Hours, Holiday, SLA Policy, Team, Category, Settings,
User Profile, semua Workflow/Permission, User, Workspace.

**Rancangan:** Single DocType `NextHD Data Wipe Tool` — field `target_doctypes` (checklist),
`confirmation_text`, `preview_only` (Check, default 1), `last_wipe_log` (read-only). Tombol
"Preview Jumlah Data" dan "Hapus Sekarang" (aktif hanya kalau `preview_only` tidak dicentang
DAN teks konfirmasi cocok).

**Whitelist HARDCODED di kode Python** (`ALLOWED_DOCTYPES` list), bukan dibaca dinamis dari
input UI — supaya tidak bisa diakali lewat manipulasi request. Setelah wipe, `tabSeries`
untuk prefix terkait juga direset supaya penomoran mulai bersih (berkaca dari bug counter
tidak sinkron, 20 Agustus).

**Belum diputuskan sebelum implementasi (bagian yang belum ada di versi ringkas 28 Agustus):**
- Perlu checkbox per-DocType (bukan hapus semua sekaligus)?
- Perlu log aktivitas reset (siapa, kapan) ke DocType audit terpisah?
- Perlu kunci tambahan supaya reset tidak sengaja dipakai di luar konteks demo/testing?

---

## Tier 3 — Nice to Have, Belum Prioritas

| Fitur | Status | Kenapa Bisa Nunggu |
|---|---|---|
| Multi-channel (email-to-ticket, WhatsApp bot) | ⬜ | Telegram cukup untuk internal — relevan kalau ada requester eksternal |
| Custom SLA per Team | ⬜ | Baru dibutuhkan kalau tiap tim beda jauh standarnya |
| Gamification (leaderboard Agent) | ⬜ | Fun tapi bukan esensial untuk tim kecil |
| Dashboard "Aset Bermasalah" (Number Card) | ⬜ | Usulan lama, belum dikerjakan |
| SLA otomatis untuk Problem/Change Request | ⬜ | Saat ini SLA hanya untuk Ticket |
| Notifikasi Telegram untuk Problem/CR | ⬜ | Sengaja ditunda |
| Laporan bulanan otomatis (jumlah tiket, MTTR) | ⬜ | Usulan, belum dikerjakan |

---

## Item Housekeeping (Bukan Fitur, Tapi Perlu Ditindaklanjuti)

| Item | Status | Keterangan | PIC |
|---|---|---|---|
| Testing end-to-end workflow di UI browser | ⬜ | Backend sudah lulus 100% (20 Agustus), belum ditest klik manual | Efendy |
| Role assignment `support@ciptamebel.co.id` → IT Manager | ⬜ | Keputusan: sementara 1 akun shared dulu | Efendy |
| File `HANDOFF_SLA_NextHD_2026-08-19.md` belum ter-commit | ⬜ | Cek di server, `git add` kalau masih ada | Efendy |
| **Guard permanen duplikasi workflow transition** | 🔶 | **Naik status jadi task konkret 30 Agustus** — spec lengkap ditulis di Tier 1 di atas, siap untuk PR Devin | Devin |
| Link Telegram untuk user test `test.requester` | ⬜ | Belum pernah kirim `/start`+`/link`, bukan bug | Efendy |
| Pemetaan tanggal Cuti Bersama 2026 belum dicek silang ke SKB asli | ⬜ | Data ditambahkan berdasar asumsi pola umum kalender cuti bersama Indonesia, bukan dibaca langsung dari teks SKB 3 Menteri | Efendy |
| Re-test Dashboard Connections "Dipakai Di" dengan foto baru | ⬜ | Foto contoh lama ikut terhapus tombol Reset Data Demo sebelum sempat ditest ulang — perlu buat foto baru → pakai di 1 Ticket → cek badge muncul di form Photo | Efendy |
| Rename Module "Next Helpdesk" → "NextHD" | 🔴 | Lihat tabel Bug Perlu Diperbaiki di atas | Claude + Efendy |
| `bench migrate` uji tahan (item KK/AA) | 🔴 | Belum pernah dijalankan sejak fix sidebar 29-30 Agustus — lihat `docs/SUMMARY.md §2` untuk detail | Efendy |

---

## Urutan Eksekusi yang Disarankan (Tier 1)

1. **Guard Duplikasi Workflow Transition** — spec sudah siap, quick win teknis, mengurangi risiko utang lama
2. **Knowledge Article + Tag** — fondasi dulu, karena Auto-Suggest bergantung ke Knowledge Article
3. **CSAT** — independen, bisa paralel dengan #2
4. **Dashboard Trend Chart** — independen, quick win terpisah
5. **Merge Tiket Duplikat** — bisa nunggu sampai ada kejadian nyata yang butuh ini
6. Tier 2 — nunggu sinyal nyata dibutuhkan, jangan dikerjakan preventif dulu

---

*Dokumen ini dikelola oleh Claude. Update status ✅/🔶/⬜ begitu ada progres — pindahkan
baris ke bagian "Sudah Selesai" begitu terverifikasi live, jangan dihapus dari sini
supaya riwayat lengkap tetap tercatat.*
