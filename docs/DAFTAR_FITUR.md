# NextHD — Daftar Fitur (Checklist Lengkap)

> **Satu tempat untuk cek semua fitur** — sudah selesai, sedang dikerjakan, atau masih
> rencana. (Sebelumnya `ROADMAP_FITUR.md`, sekarang termasuk juga desain yang sebelumnya
> nyasar di `ARSITEKTUR.md §8` dan `§9`).
>
> Status: ✅ Selesai & Live | 🔶 Sedang Dikerjakan/Menunggu Konfirmasi | ⬜ Belum Dikerjakan (Rencana)
>
> **Last updated:** 2026-08-24 (sesi lanjutan — verifikasi & dedup workflow)

---

## Fitur Inti (Sudah Selesai & Live)

| Fitur | Status | Keterangan | Bukti/Referensi |
|---|---|---|---|
| SLA sadar jam kerja (all-or-nothing) | ✅ | `business_hours.py`, resolusi diulang penuh dari jam kerja berikutnya kalau tidak muat | `POLA_KERJA_DAN_BUG.md §4`, 20 Agustus |
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
| Dedup transisi workflow duplikat | ✅ | 42 → 21 baris bersih (dedup pertama, 20 Agustus). **Duplikasi muncul lagi dan dibersihkan ulang 24 Agustus — lihat baris terpisah di bawah** | 20 Agustus |
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
| Duplikasi Workflow Transition (round 2) — Ticket/Problem/Change Request | ✅ | Ditemukan tiap transisi terduplikasi persis 4× (Ticket 28→7, Problem 24→6, CR 32→8). **Root cause:** `Workflow Action Master` "Convert to Known Error" tidak pernah dibuat, membuat `wf.save()` gagal validasi di tengah proses dedup sebelumnya (data lama sempat masuk lewat jalur yang bypass validasi ORM). Master dibuat ulang, lalu dedup by-value (bukan cuma by-idx) berhasil untuk ketiganya. Backup tersimpan di `/home/it/workflow_transitions_backup.json` di server | 24 Agustus |
| Cuti Bersama 2026 — 8 hari | ✅ | Ditambahkan ke `NextHD Holiday` (total jadi 25 record: 17 nasional + 8 cuti bersama). **⚠️ Pemetaan tanggal↔nama event asumsi Claude berdasar pola umum, belum dicek silang ke teks SKB asli** | 24 Agustus |
| Script verifikasi ringan pasca-perbaikan | ✅ | Ditambahkan ke `AUDIT_SISTEM.md` — smoke test 9 titik spesifik (workflow, sidebar, number card, SLA, business hours, holiday, roles, photo doctype) | 24 Agustus |

---

## 🔴 Bug Perlu Diperbaiki

| Bug | Status | Keterangan | PIC |
|---|---|---|---|
| Business Hours "Sabtu" — `is_working_day=1` tidak konsisten dengan default `install.py` | 🔴 | Audit 24 Agustus menemukan production punya Sabtu sebagai hari kerja (`is_working_day=1`), padahal `install.py` (setelah patch hari yang sama) men-set default Sabtu **bukan** hari kerja (`0`). Belum diketahui mana yang benar — kalau Sabtu memang sengaja jadi hari kerja, `install.py` perlu disesuaikan lagi; kalau tidak, data production perlu dikoreksi ke `0`. **Belum ada tindakan diambil, menunggu keputusan Efendy** | Efendy (keputusan) → Claude (eksekusi) |

---

## Tier 1 — Rencana Prioritas Berikutnya (Quick Win)

| Fitur | Status | Keterangan | Bergantung Pada |
|---|---|---|---|
| Knowledge Article (`NextHD Knowledge Article`) | ⬜ | DocType baru, field `visibility` (Publik/Internal) — solusi mandiri untuk requester, terpisah dari Known Error (yang teknis, untuk Agent). Lihat detail desain di bawah | — |
| Tag di Tiket | ⬜ | Pakai sistem tag bawaan Frappe (`Tag` + `_user_tags`), bukan field custom | — |
| CSAT — survei kepuasan pasca-tiket | ⬜ | Field `csat_rating`, `csat_comment` di Ticket, trigger Telegram saat status "Selesai" | — |
| Merge tiket duplikat | ⬜ | Field `merged_into`, status "Digabung" | — |
| Auto-suggest Knowledge Article saat bikin tiket | ⬜ | Search artikel Publik yang cocok sebelum tiket disubmit | Knowledge Article |
| Dashboard trend chart | ⬜ | Tren volume tiket per minggu, breakdown kategori | — |

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
| **Generalisasi ke domain non-IT** | ⬜ | Asset Category/Attribute jadi EAV supaya bisa dipakai domain lain (bengkel, mesin pabrik, dst) — desain lengkap di bawah. *(Dipindah dari `ARSITEKTUR.md §8`, 23 Agustus)* |
| **Wipe Data Testing Tool** | ⬜ | `NextHD Data Wipe Tool`, whitelist DocType, konfirmasi eksplisit — desain lengkap di bawah. *(Dipindah dari `ARSITEKTUR.md §9`, 23 Agustus)* |

### Detail Desain: Generalisasi ke Domain Non-IT

**Status:** Rencana teknis disusun 15 Agustus 2026, belum ada jadwal eksekusi. Cakupan
perubahan **terbatas ke seputar `NextHD Asset` saja** — 11 dari 12 DocType non-child
(Ticket, Problem, Change Request, Known Error, dst) tidak perlu disentuh karena strukturnya
sudah generik sejak awal.

**Dua pendekatan dipertimbangkan:**

| Pendekatan | Cara Kerja | Nambah Kategori Baru |
|---|---|---|
| A — Section per kategori (pola sekarang) | DocField tetap per kategori dengan `depends_on` | Butuh tambah DocField tiap kategori baru |
| **B — Atribut dinamis (EAV)** ✅ direkomendasikan | Child table generik "Nama Atribut" + "Nilai" | Tidak butuh perubahan struktur |

**Rancangan DocType baru:**

`NextHD Asset Category` (master) — `category_name`, `description`. Menggantikan `asset_type`
Select tertutup, jadi Link supaya kategori baru bisa ditambah dari UI tanpa edit kode.

`NextHD Asset Attribute` (child table, parent = NextHD Asset) — `attribute_name`,
`attribute_value`, `unit`. Contoh isi untuk kategori "Kendaraan": Plat Nomor, Tahun, KM
Terakhir. Untuk "Mesin Produksi": Kapasitas, Jam Operasi.

`NextHD Asset` disederhanakan jadi field universal saja (`asset_name`, `asset_category`,
`location`, `assigned_to`, `status`, `purchase_date`, `warranty_until`,
`asset_attributes` Table) — field IT-spesifik (`cpu`, `ram`, `mac_address`, dst) dipindah
isinya jadi baris `asset_attributes`, bukan DocField terpisah.

**Migrasi:** saat ini baru 1 record Asset live (`AST-2608-0001`) — migrasi ringan kapan
pun dieksekusi. Tidak mendesak, ditunda sampai ada kebutuhan nyata pakai domain lain.

**Yang tidak berubah:** semua field relasi ke Asset di DocType lain, Workflow, Client
Script tombol otomatis — logicnya generik, tidak menyentuh field spesifik-domain.

### Detail Desain: Wipe Data Testing Tool

**Status:** Desain final disepakati 20 Agustus 2026, belum diimplementasi.

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

**Belum diputuskan sebelum implementasi:**
- Siapa yang boleh akses tool ini? (rekomendasi: IT Manager saja)
- Perlu backup otomatis sebelum wipe?
- Kapan waktu eksekusi pertama (status "nanti saja" per keputusan 20 Agustus)

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
| Guard permanen duplikasi workflow transition | 🔶 | Root cause **sekarang terkonfirmasi**: master data (`Workflow Action Master`) yang hilang membuat proses save/reimport sebelumnya gagal di tengah jalan dan meninggalkan baris duplikat. Dedup manual sudah dilakukan 2× (20 Agustus, 24 Agustus) — tapi belum ada mekanisme pencegahan otomatis supaya tidak terulang lagi di masa depan | Claude |
| Link Telegram untuk user test `test.requester` | ⬜ | Belum pernah kirim `/start`+`/link`, bukan bug | Efendy |
| Konfirmasi `bench migrate` + `bench restart` sudah jalan pasca commit `a69df61` | ✅ | Terkonfirmasi 24 Agustus — sidebar & number card foto sudah muncul di production setelah fix tambahan (lihat root cause di tabel fitur di atas) | Efendy |
| Pemetaan tanggal Cuti Bersama 2026 belum dicek silang ke SKB asli | ⬜ | Data ditambahkan berdasar asumsi pola umum kalender cuti bersama Indonesia, bukan dibaca langsung dari teks SKB 3 Menteri | Efendy |

---

## Urutan Eksekusi yang Disarankan (Tier 1)

1. **Knowledge Article + Tag** — fondasi dulu, karena Auto-Suggest bergantung ke Knowledge Article
2. **CSAT** — independen, bisa paralel dengan #1
3. **Dashboard Trend Chart** — independen, quick win terpisah
4. **Merge Tiket Duplikat** — bisa nunggu sampai ada kejadian nyata yang butuh ini
5. Tier 2 — nunggu sinyal nyata dibutuhkan, jangan dikerjakan preventif dulu

---

*Dokumen ini dikelola oleh Claude. Update status ✅/🔶/⬜ begitu ada progres — pindahkan
baris ke bagian "Sudah Selesai" begitu terverifikasi live, jangan dihapus dari sini
supaya riwayat lengkap tetap tercatat.*
