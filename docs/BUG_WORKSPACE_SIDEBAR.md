# NextHD — Riwayat Bug: Workspace, Desktop Icon, Sidebar, Dashboard Shortcut

> **File hasil pemecahan dari `POLA_KERJA_DAN_BUG.md` (30 Agustus 2026)** — khusus riwayat bug
> yang temanya Workspace/Desktop Icon/Sidebar/Dashboard Shortcut (topik paling sering berulang
> di project ini). Untuk aturan/pola kerja umum, lihat `docs/POLA_KERJA.md`. Untuk riwayat bug
> lain (SLA, Telegram, naming series, dll), lihat `docs/BUG_HISTORY.md`.
>
> **Last updated:** 2026-09-02

---

## ✅ Bug Infrastructure & UI (2026-08-09 s/d 11)

| # | Masalah | Penyelesaian |
|---|---|---|
| 1 | Duplikasi folder `nexthd/doctype/` dan `nexthd/utils/` di root app | Hapus, pertahankan path di `next_helpdesk/` |
| 2 | "Next Helpdesk" workspace muncul di sidebar (tidak diinginkan) | Patch Python hapus via `frappe.db.delete()` |
| 3 | hooks.py syntax error setelah `sed` | Fix dengan script Python |
| 4 | nexthd.json terpotong saat `cat EOF` | Tulis ulang via `json.dumps()` Python |
| 5 | patches.txt dua patch tergabung satu baris | Python `str.replace()` tambah newline |
| 6 | `add_to_apps_screen` di-comment, desktop kosong | Un-comment, tambah logo.svg |
| 7 | Logo tidak ada → hook tidak terbaca | Buat `nexthd/public/logo.svg` |
| 8 | Desktop Icon dihapus tiap `bench migrate` | Tambah ke fixtures di hooks.py |
| 9 | Workspace Sidebar dihapus tiap `bench migrate` | Tambah ke fixtures di hooks.py |
| 10 | Workspace Sidebar `standard=1` tidak bisa diedit | `UPDATE tabWorkspace Sidebar SET standard=0` |
| 11 | Permission missing — 4 DocType tidak bisa dibuka | SQL INSERT ke `tabDocPerm` |
| 12 | Desktop icon NextHD buka tab baru | `link_type = Workspace Sidebar`, `link = NULL` |
| 13 | Number Card tidak muncul di workspace | UPDATE `tabWorkspace Number Card` SET `number_card_name` |
| 14 | Workspace content double escape → SyntaxError browser | Generate via `json.dumps()` |
| 15 | Fixtures Workflow State error kolom 'workflow' | Hapus Workflow State dari fixtures |

> ⚠️ **Catatan silang (29 Agustus):** item #10 di atas (`standard=0` sengaja diset 2026-08-09/11
> supaya sidebar bisa diedit) kemungkinan besar adalah **asal-usul** kondisi `standard=0` yang
> ditemukan lagi sebagai penyebab regresi di bug session 29 Agustus (lihat di bawah) — nilai
> ini sepertinya tidak pernah dikembalikan ke `1` setelah edit selesai di sesi lama tsb.
> **Pelajaran:** kalau sengaja set `standard=0` untuk keperluan edit sementara, selalu
> kembalikan ke `1` begitu edit selesai.

---

## ✅ Bug Session 2026-08-11 (lanjutan) — Number Card & Desktop Icon

| # | Item | Masalah | Fix |
|---|---|---|---|
| 1 | Number cards "Statistik Tiket" | Tidak render di `/desk/nexthd` | Block `content` JSON pakai `type: "card"` salah, seharusnya `"number_card"` + key `number_card_name` |
| 2 | Desktop icon routing | Klik icon → sempat ke `/desk/nexthd-ticket` | Ternyata cuma cache — `clear-cache` + `build` + restart + hard refresh |

> Item lain di sesi ini (Workflow kosong, `update_field` bug, transisi redundan) adalah bug
> Workflow, bukan Workspace/Sidebar — lihat `docs/WORKFLOW.md §5` untuk detail lengkap.

---

## ✅ Bug Session 2026-08-24 (Sidebar Photo Fix — Root Cause Awal, Kemudian Dikoreksi)

**Root cause awal (SEMPAT SALAH, lihat koreksi di sesi 24 Agustus lanjutan #2 di bawah):**
`import_file_by_path(force=True, ignore_version=True)` berhasil menimpa field top-level seperti
`number_cards` dan `content`, tapi **tidak menyentuh child table `links`** (yang me-render
sidebar). Fix yang dicoba: append manual lewat ORM — `frappe.get_doc("Workspace", "NextHD")`,
`ws.append("links", {...})`, `ws.save(ignore_permissions=True)`.

**⚠️ KOREKSI (sesi 24 Agustus lanjutan #2):** analisis ini **TERNYATA SALAH ALAMAT**.
`Workspace.links` **bukan** yang merender sidebar kiri navigasi — sidebar kiri yang sebenarnya
dikontrol doctype terpisah **`Workspace Sidebar`**. Fix di atas kemungkinan besar tidak benar-benar
menyelesaikan masalah, hanya kebetulan terlihat solved sesaat karena reload cache.

**Ditemukan juga (bukan bug, tapi drift):** sidebar production sempat punya item "NextHD
Business Hours" yang tidak ada di `nexthd.json` repo — kemungkinan ditambahkan manual via UI.

---

## ✅ Bug Session 2026-08-24 (Duplikasi Workflow Transition Round 2) — Terkait Workspace via Investigasi

**Temuan:** setiap transisi di ketiga workflow terduplikasi persis 4× (Ticket 28→7, Problem
24→6, Change Request 32→8).

**Root cause (dugaan awal, KEMUDIAN DIKOREKSI 25 Agustus):** `Workflow Action Master` untuk
action "Convert to Known Error" tidak pernah dibuat sebagai record — diduga membuat validasi
Link gagal setiap kali proses dedup/reimport sebelumnya mencoba `wf.save()` di tengah jalan.

**Fix (sesi ini):** master `Workflow Action Master` dibuat, dedup ulang by-value untuk Problem
dan Change Request. Backup transisi lama tersimpan di `/home/it/workflow_transitions_backup.json`.

> ⚠️ Root cause sebenarnya (fixture di repo menumpuk generasi export lama) baru ditemukan
> 25 Agustus — lihat `docs/BUG_HISTORY.md` untuk detail lengkap dedup Workflow Transition.

---

## ✅ Bug Session 2026-08-24, Sesi Lanjutan #2 — Arsitektur Sidebar NextHD DITEMUKAN & DILURUSKAN

**Konteks:** Investigasi kenapa item "NextHD Photo" hilang lagi dari sidebar meski "sudah
diperbaiki" di sesi 24 Agustus sebelumnya. Sesi ini menemukan **akar masalah sesungguhnya**:
pemahaman sebelumnya tentang komponen mana yang mengontrol sidebar kiri navigasi **salah**.

> ⚠️ **KOREKSI LEBIH LANJUT (27 Agustus)** — analisis "3 komponen" di bawah ini juga
> **belum lengkap**, ditemukan lapisan ke-4 (`Workspace Sidebar Item`) dan lokasi file fixture
> yang benar. Jadikan sesi 27 Agustus (di bawah) sebagai rujukan final, bagian ini konteks
> historis saja.

**3 Komponen (versi 24 Agustus, sebagian sudah dikoreksi):**

| Komponen | Fungsi (versi 24 Agustus) |
|---|---|
| `Workspace Sidebar` + `Workspace Sidebar Item` | INI yang benar-benar merender sidebar kiri — nama record: `"NextHD"` |
| `Workspace.links` | BUKAN sidebar kiri — fungsi sebenarnya belum sepenuhnya dikonfirmasi saat itu |
| `nexthd/next_helpdesk/workspace/nexthd/nexthd.json` | Mengontrol ISI HALAMAN Workspace (cards, shortcut) — bukan sidebar kiri |
| `nexthd/fixtures/workspace_sidebar.json` | Skema benar tapi sengaja dinonaktifkan dari fixtures — TIDAK berpengaruh ke server |

**Kronologi kesalahan sesi ini:**
1. Edit `Workspace.links` → gagal `MandatoryError: [Workspace, NextHD]: type` (field `type` NULL, anomali data lama)
2. Field `type` diisi `"Workspace"`, save berhasil — **tapi sidebar kiri tetap tidak berubah** (sinyal `Workspace.links` bukan sumber benar)
3. Ditemukan doctype `Workspace Sidebar` (`tabWorkspace Sidebar` + `tabWorkspace Sidebar Item`)
4. **Kesalahan fatal:** query `SELECT name FROM tabWorkspace Sidebar` **tanpa filter**, ambil `rows[0].name` — ternyata hasil pertama adalah **`"Build"`** (workspace bawaan Frappe developer tools), bukan `"NextHD"`. Item "NextHD Photo"/"NextHD Report" sempat ke-append ke record **"Build"**, bukan **"NextHD"**
5. Fix final: hapus 2 item yang nyasar dari `Build`, tambahkan ke record `NextHD` yang benar

**Pelajaran kritis:** **JANGAN PERNAH** ambil hasil pertama dari query tanpa `WHERE name = '...'`
eksplisit saat mengedit dokumen apa pun via `bench console` — selalu filter nama spesifik dulu,
`print()` hasil query sebelum `.save()` apa pun.

**Status setelah sesi ini:** item live di database, TAPI **belum di-export/commit ke repo**
karena `Workspace Sidebar` sengaja dikeluarkan dari fixtures (pernah menyebabkan bug "orphan
workspace" saat migrate). Opsi permanen belum diputuskan saat itu.

---

## ✅ Bug Session 2026-08-25 — Root Cause Sidebar Dikoreksi Total: `Workspace.links` ADALAH Sumber Asli

**Kronologi insiden:** Sesi ini awalnya (lanjutan 24 Agustus) mengedit `Workspace Sidebar Item`
langsung + membuat file `nexthd/next_helpdesk/workspace_sidebar/nexthd.json` untuk
"mempermanenkan" 6 link report. Saat `bench migrate` dicoba sebagai uji coba:
- Sidebar turun dari 22 item jadi 14 item — "NextHD Photo" dan 6 report **hilang**, log
  menunjukkan `Removing orphan Workspace Sidebars`
- Workflow Transition ikut melonjak dari 7/6/8 jadi 35/30/40 (insiden `name` mismatch terpisah)

**Tindakan:** restore database dari backup pra-migrate — berhasil.

**Root cause sebenarnya (dari dokumentasi resmi Frappe):** dokumentasi migrasi resmi Frappe v16
menyatakan sidebar baru "powered by Workspace Sidebar doctype" dan **"autogenerated for the most
part"**. Artinya `Workspace Sidebar Item` **bukan sumber data asli** — itu hasil **auto-generate**
dari `Workspace.links` (child table field `links` di doctype stock `Workspace`). Setiap `bench
migrate`, Frappe meregenerasi ulang `Workspace Sidebar Item` berdasarkan `Workspace.links`, lalu
menghapus apa pun di `Workspace Sidebar Item` yang tidak berasal dari `Workspace.links`.

**Kesimpulan:** pendekatan edit `Workspace Sidebar Item` + file `workspace_sidebar/nexthd.json`
langsung (dipakai sejak 24 Agustus) **salah alamat**. Sumber kebenaran yang benar adalah
**`Workspace.links`** — untuk link bertipe DocType/Workspace saja (Report tidak ikut
auto-generate, dikonfirmasi 27 Agustus).

> **Catatan (27 Agustus):** kesimpulan ini valid **khusus untuk menambah link BARU ke sidebar
> workspace NextHD sendiri**. Kalau kasusnya menambah 1 entri sidebar yang mengarah ke
> **workspace lain**, jalurnya berbeda lagi — lihat sesi 27 Agustus di bawah.

> ⚠️ **KOREKSI LEBIH LANJUT (2 September) — kesimpulan "autogenerated dari Workspace.links" di
> atas TERBUKTI TIDAK SEPENUHNYA AKURAT.** Investigasi mendalam 2 September (lihat bug session
> 2 September di bagian paling bawah dokumen ini) menemukan bahwa mekanisme sebenarnya yang
> menghapus/menimpa item sidebar saat migrate adalah **`sync_fixtures()` mengimpor file usang
> `nexthd/fixtures/workspace_sidebar.json`** — bukan proses auto-generate dari `Workspace.links`.
> Kesimpulan sesi ini dipertahankan sebagai konteks historis karena langkah perbaikannya (isi
> `Workspace.links` dengan benar) tetap bermanfaat, tapi root cause utamanya baru benar-benar
> ditemukan 2 September.

**Perbaikan:** item "NextHD Report" generic dihapus dari `tabWorkspace Link`, diganti 6 link
report langsung (`link_type: Report`, `report_ref_doctype` terisi). Total `Workspace.links`
jadi 19 item (13 lama + 6 report baru). **`bench migrate` konfirmasi final belum dijalankan
saat itu** (lihat item AA di `SUMMARY.md` — masih pending per 30 Agustus).

---

## ✅ Bug Session 2026-08-26 — Dashboard Shortcut "NextHD Photo" & 6 Report (`report_ref_doctype` & Cache)

**Konteks:** Menambahkan 7 kartu shortcut baru ke dashboard `/desk/nexthd` — 1 shortcut DocType
(`NextHD Photo`) ke section "Konfigurasi", 6 shortcut Report ke section baru "Laporan". Insert
via SQL ke `tabWorkspace Shortcut` + update `Workspace.content` — **terpisah total** dari item
AA (25 Agustus, sidebar kiri via `Workspace.links`).

**Gejala:** Setelah insert (7 shortcut baru terkonfirmasi ada, `content` JSON 32 blok), kartu
"NextHD Photo" **tidak muncul** di dashboard. 6 kartu Report juga tidak muncul.

**Root cause & fix:**
- **6 shortcut Report:** kolom `report_ref_doctype` kosong (`NULL`) membuat Frappe gagal resolve
  config kartu saat render, di-skip diam-diam. Fix: `UPDATE tabWorkspace Shortcut SET
  report_ref_doctype=...` — 5 report → `NextHD Ticket`, 1 report (Aset Bermasalah) → `NextHD Asset`.
- **Shortcut "NextHD Photo":** data & permission sudah benar, penyebabnya cache Redis —
  `Workspace.content` diupdate via SQL langsung yang tidak memicu invalidasi cache otomatis.
  Fix: isi `report_ref_doctype` + `bench clear-cache` + `bench clear-website-cache` + hard
  refresh browser.

**Catatan:** URL report tetap `/desk/query-report/<nama>` — standar Frappe, bukan bug, tidak
bisa diubah jadi `/desk/nexthd/...` tanpa menulis ulang report sebagai custom Page.

---

## ✅ Bug Session 2026-08-26 (Lanjutan) — 5 Workspace "Center" Tersembunyi + Insiden Sidebar Hilang Total + Limitasi Frappe v16

**Temuan:** 5 workspace tambahan yang sebelumnya tidak pernah muncul di audit manapun, semua
`module: Next Helpdesk` (kemungkinan dibuat Devin/Codex/sesi AI lain di luar riwayat chat):
`Ticket Center`, `Asset Center`, `Service Management`, `Configuration Center`, `Reports Center`.
Sempat tampil (`public=1, hidden=0`) di sidebar, membuat sidebar ramai/berantakan. **Sekarang
`public=0, hidden=1`** (disembunyikan, TIDAK dihapus) — data internalnya masih utuh.

**⚠️ Insiden: Mengosongkan `Workspace.links` Tanpa Isi Ulang Langsung = Sidebar Hilang Total**

Percobaan pertama merapikan sidebar sempat `DELETE FROM tabWorkspace Link WHERE parent='NextHD'`
**tanpa langsung insert ulang isi barunya**. Begitu cache dibersihkan, **seluruh sidebar NextHD
hilang total** — karena `Workspace Sidebar Item` di-regenerate dari `Workspace.links`.

**PELAJARAN KRITIS:** jangan pernah `DELETE` isi `Workspace.links` tanpa `INSERT` pengganti di
**transaksi/script yang sama**. Selalu hapus-dan-isi-ulang sekaligus dalam satu script.

**Perbaikan:** script restore mengisi ulang 19 `Workspace Link` (13 DocType + 6 Report)
sekaligus menyembunyikan 5 workspace "Center" + legacy "Next Helpdesk" — lewat
`frappe.db.sql()`/`frappe.db.set_value()` langsung (bukan `.save()`, karena Workspace lama
sempat memicu `MandatoryError`/`DocType View cannot be "Form"`).

**Konfirmasi Resmi — Sidebar Pendek di Halaman Report/DocType Adalah Limitasi Frappe v16:**
Saat masuk halaman report (`/desk/query-report/...`) atau DocType dari module "Next Helpdesk",
sidebar otomatis berganti jadi versi pendek/generic ("Module Sidebar" — daftar DocType/Report
auto berdasarkan field `module`), BUKAN sidebar lengkap Workspace NextHD. **Dikonfirmasi sebagai
known limitation Frappe v16** (GitHub Issue #36317, forum resmi Frappe) — sidebar Workspace
lengkap memang didesain hanya tampil di halaman Workspace itu sendiri. Belum ada fix resmi dari
tim Frappe. Percobaan override `set_breadcrumbs()` gagal karena `query_report.js` memanggil
ulang fungsi bawaan setelah `onload`.

**Yang berhasil sebagai kompensasi:** breadcrumb 2-level ("NextHD / <Nama Report>") di tiap
file `.js` report NextHD.

**✅ Keputusan final 30 Agustus (lihat item KK di `SUMMARY.md`):** Module Sidebar ini
dikonfirmasi ulang bukan Route History, murni auto-generate dari field `module`. **Dibiarkan
apa adanya, tidak dikejar lagi.**

---

## ✅ Bug Session 2026-08-27 — Workspace "NextHD Report" Tidak Muncul di Sidebar (4 Lapis Masalah)

**Konteks:** Workspace baru "NextHD Report" (11 shortcut report) dibuat via script `bench
console` (insert langsung ke DB), bukan lewat UI. Datanya valid 100% di database, tapi **tidak
pernah muncul** di sidebar kiri workspace "NextHD" — bertahan meski clear-cache, build, restart,
Incognito.

**Root cause berlapis 4, ditemukan berurutan:**

1. **Workspace tidak punya file fixture JSON** — dibuat via insert manual, hook `on_update()`
   yang biasanya generate fixture tidak pernah terpanggil. **Fix:** `developer_mode=1`, panggil
   `doc.save()` manual sekali → fixture `workspace/nexthd_report/nexthd_report.json` ter-generate.
2. **`Workspace.roles` kosong** (`[]`) — disamakan manual, **ternyata bukan penyebab utama**.
3. **Backend sebenarnya sudah benar sejak awal** — dibuktikan `frappe.call(get_workspaces)`
   (fungsi asli `frappe.desk.desktop`): "NextHD Report" **sudah muncul** di hasilnya.
4. **Item sidebar harus ditambah lewat UI "⋯ → Edit Sidebar"**, bukan hanya mengandalkan
   `Workspace.links`. Setelah ditambah manual (item "NextHD Reporting" → link ke Workspace
   "NextHD Report"), sidebar langsung tampil normal.

**Root cause tersembunyi ke-5 — Lokasi File Fixture `Workspace Sidebar` yang Sebenarnya:**

Fungsi `export_sidebar()` di controller `workspace_sidebar.py` menulis file ke
`<app_root>/<app>/workspace_sidebar/<judul_scrub>.json`:

```
✅ BENAR (aktif dipakai): nexthd/nexthd/workspace_sidebar/nexthd.json
❌ SALAH (usang, tidak pernah ditulis ulang): nexthd/next_helpdesk/workspace_sidebar/nexthd.json
```

**BUKAN** di dalam folder module seperti diasumsikan sesi-sesi sebelumnya. File di lokasi salah
sudah dihapus, dikonfirmasi file yang benar sudah berisi "NextHD Reporting".

**Prasyarat lain wajib benar sebelum `export_sidebar()` mau menulis file:** field `app` (harus
diisi nama app scrub, mis. `nexthd`) dan `standard` (harus `1`) pada dokumen `Workspace Sidebar`
terkait.

**Kesalahan sampingan (sudah di-undo):** sempat dicoba set `Workspace.public=0` + `is_hidden=1`
pada "NextHD Report" (dugaan harus disembunyikan seperti workspace "Center"). **Efeknya link
sidebar hilang total** — membuktikan dugaan itu salah untuk workspace yang diakses lewat sidebar
link biasa. Dikembalikan ke `public=1`, `is_hidden=0`.

**Catatan tambahan — Workspace Baru via Insert Tidak Trigger Export Fixture:** Workspace yang
dibuat lewat insert langsung ke database **tidak memicu** proses otomatis yang menulis file
fixture-nya. Baru setelah `developer_mode=1` + `doc.save()` manual, file fixture benar-benar
tertulis. **Implikasi audit:** kalau ada Workspace di database tapi tidak punya file fixture
yang sesuai, curigai workspace itu pernah dibuat via insert manual.

**Status akhir:** Sidebar "NextHD Reporting" tampil normal, mengarah ke Workspace "NextHD
Report" berisi 11 shortcut report.

---

## ✅ Bug Session 2026-08-28 — Bug #2 & #3: Shortcut Workspace "Admin" Tidak Muncul + `Link Type must be set first`

**Konteks:** Tombol admin "Reset Data Demo" (Custom Page `nexthd-reset-data`) perlu shortcut
section baru "Admin" di Workspace NextHD.

**Bug #2 — Shortcut Workspace "Admin" tidak muncul di UI:**

**Gejala:** Row berhasil ter-insert ke `tabWorkspace Shortcut`, tapi tombol tidak muncul.

**Root cause:** Tampilan Workspace dikontrol field `content` (JSON blocks) di `tabWorkspace`,
bukan otomatis mengambil semua row `tabWorkspace Shortcut` — row ada di database tapi tidak
direferensikan di `content`.

**Percobaan pertama gagal:** `ws.save()` via `frappe.get_doc()` melempar `ValidationError:
Link Type must be set first` — disebabkan bug lama tidak terkait, lihat Bug #3 di bawah.

**Fix final:** Update field `content` langsung lewat `frappe.db.set_value()` (skip validasi
dokumen penuh), dijalankan via `bench execute` (bukan `bench console` interaktif, supaya cabang
`if/else` tidak salah parse indentasi).

**Bug #3 — `Link Type must be set first` pada Workspace NextHD (root cause awal ditemukan, fix final di sesi 29 Agustus):**

**Penyebab terkonfirmasi (28 Agustus):** Row `tabWorkspace Link` (`name=u6nb1c41c1`, label
"Reporting Data", `link_to=/app/nexthd-report`, `link_type` **kosong**) — link ganjil sudah
teridentifikasi sesi pagi 28 Agustus, belum diperbaiki saat itu. **Dampak:** setiap
`frappe.get_doc().save()` pada Workspace NextHD gagal karena validasi ini. Workaround sementara
`frappe.db.set_value()` (skip validasi) dipakai untuk Bug #2. **Fix tuntas: lihat bug session
29 Agustus di bawah (item DD).**

---

## ✅ Bug Session 2026-08-29, ~17:45 WIB — Item DD: `Link Type must be set first` + Regresi Sidebar "NextHD Reporting"

**Konteks:** Menindaklanjuti Bug #3 (pending sejak 28 Agustus).

**Kronologi diagnosa & fix root cause asli:**

1. Row bermasalah dicek ulang: `tabWorkspace Link` (`name=u6nb1c41c1`, `type=URL`, `link_type=""`).
2. **Percobaan 1 (gagal):** set `link_type="Workspace"` → `Link Type cannot be "Workspace". It
   should be one of "DocType", "Page", "Report"`.
3. **Percobaan 2 (gagal):** set `link_type="Page"`, `link_to` tetap `/app/nexthd-report` →
   `LinkValidationError: Could not find Row #20: Link To: /app/nexthd-report` — `link_type=Page`
   membuat Frappe memvalidasi `link_to` sebagai nama record `Page`, bukan path URL.
4. **Verifikasi:** Page `nexthd-report` **tidak pernah ada** di `tabPage` (yang eksis cuma
   `nexthd-reset-data`) — baris ini memang sejak awal tidak pernah valid.
5. **Fix final:** baris "Reporting Data" **dihapus total** via `DELETE FROM tabWorkspace Link
   WHERE name = 'u6nb1c41c1'` — fungsinya sudah digantikan sidebar "NextHD Reporting" (27
   Agustus, mengarah ke Workspace "NextHD Report").
6. Setelah dihapus, `frappe.get_doc("Workspace", "NextHD").save(ignore_permissions=True)`
   **berhasil** — fixture `nexthd/next_helpdesk/workspace/nexthd/nexthd.json` ter-tulis ulang.

**🐛 Regresi ditemukan dalam sesi yang sama:** setelah `doc.save()` di atas, item sidebar
manual **"NextHD Reporting" hilang** dari `Workspace Sidebar Item` (15 item tersisa, semuanya
auto-generate dari `Workspace.links`).

**Root cause regresi (dugaan sesi ini, KOREKSI FINAL lihat sesi 2 September di bawah):**
`Workspace Sidebar.standard` untuk record "NextHD" ternyata `0` (bukan `1`). Sesuai
`POLA_KERJA.md §1.C`, `standard` harus `1` agar perubahan sidebar permanen — kondisi
`standard=0` diduga membuat sidebar rawan diregenerasi ulang murni dari `Workspace.links`.

**Fix regresi (sesi ini):**
1. `Workspace Sidebar.standard` diset `0` → `1` via `frappe.db.set_value()` + commit.
2. "NextHD Reporting" (`link_type: Workspace`, `link_to: NextHD Report`) ditambahkan kembali
   lewat UI.
3. Verifikasi berulang (2×): `doc.save()` Workspace NextHD dipanggil lagi — sidebar tetap
   **16 item lengkap** (termasuk "NextHD Reporting") di kedua percobaan.
4. Fixture `nexthd/nexthd/workspace_sidebar/nexthd.json` dikonfirmasi berisi "NextHD Reporting".

**Catatan tambahan (bukan bug):** saat "NextHD Reporting" diklik, tampilan berpindah ke
Workspace "NextHD Report" yang sidebar-nya sendiri cuma 2 item — perilaku normal Frappe v16
(sidebar per-Workspace, bukan gabungan).

**Status:** Item DD ditutup tuntas pada sesi ini. Namun regresi sejenis **muncul kembali** di
sesi-sesi berikutnya (30 Agustus, 31 Agustus, dan 2 September) — lihat sesi 2 September untuk
root cause final yang sesungguhnya (bukan `standard=0`, melainkan file fixture usang).

---

## ✅ Bug Session 2026-08-30 — Item KK: Sidebar "NextHD" +Asset Category, Sidebar "NextHD Report" Diperkaya, Klarifikasi Module Sidebar

**Konteks:** Efendy mengirim 3 screenshot menunjukkan sidebar berubah tergantung halaman: (1)
`/desk/nexthd` — 16 item lengkap, (2) `/desk/nexthd-report` — cuma 2 item, (3)
`/desk/query-report/...` — sidebar pendek berbeda lagi. Minta ditambahkan "NextHD Asset
Category" (DocType baru dari migrasi EAV) ke sidebar "NextHD".

**Investigasi 3 jenis sidebar:**
- Sidebar (1) & (2): sama-sama `Workspace Sidebar` sungguhan — beda isi karena beda Workspace.
- Sidebar (3): awalnya diduga "Route History" — **dicek via `tabRoute History`, TERBUKTI TIDAK
  COCOK**. Kesimpulan final: **"Module Sidebar"**, auto-generate real-time dari field
  `module='Next Helpdesk'` di semua Workspace+DocType+Report. **Bukan file, tidak bisa diedit**
  tanpa override core Frappe. **Keputusan final Efendy: dibiarkan apa adanya.**

**Eksekusi Bagian 1 — Sidebar "NextHD" +Asset Category:**
Via UI Edit Sidebar (panah kiri atas). Ditambahkan idx=8 (setelah "NextHD Asset"), icon
`copy-check`. Total sidebar **17 item**.

**Eksekusi Bagian 2 — Sidebar "NextHD Report" 2→8 item:**
- Keputusan isi (Efendy): DocType utama saja (Ticket, Problem, Change Request, Known Error,
  Asset, Asset Category) — laporan tidak perlu ditambahkan, karena 11 shortcut report sudah
  otomatis muncul di body Workspace "NextHD Report".
- **Temuan sebelum eksekusi:** `Workspace Sidebar.app` untuk "NextHD Report" ternyata `None`
  (beda dari "NextHD" yang sudah `nexthd`) — **wajib diperbaiki dulu** sebelum insert, karena
  `app` terisi + `standard=1` adalah dua syarat wajib supaya `export_sidebar()` permanen.
  **Pelajaran baru:** `app` dan `standard` harus dicek TERPISAH, salah satu benar tidak berarti
  keduanya benar.
- **Metode insert (banyak item sekaligus):** `doc = frappe.get_doc("Workspace Sidebar", "NextHD
  Report")`, `doc.append("items", {...})` per item, `doc.save(ignore_permissions=True)` — pola
  ini setara tombol UI "Edit Sidebar", risiko regresi jauh lebih rendah dibanding `doc.save()`
  pada `Workspace` (beda doctype dari kasus regresi item DD).
- Icon disamakan dengan sidebar "NextHD" (Ticket=`ticket`, Problem=`bug`, Change Request=`tool`,
  Known Error=`alert-circle`, Asset=`package`, Asset Category=`copy-check`).
- **Verifikasi:** sidebar "NextHD" (17 item) TIDAK terpengaruh oleh perubahan ini.

**Temuan saat commit:** `nexthd/workspace_sidebar/nexthd_report.json` ternyata **belum pernah
ter-commit ke git sama sekali** sejak Workspace "NextHD Report" dibuat 27 Agustus (`untracked`
di `git status`) — sesi ini sekaligus melengkapi kekurangan lama itu.

**Commit:** `beec05c` — `nexthd.json` (modified) + `nexthd_report.json` (baru pertama kali
ter-commit).

**⚠️ PENDING (saat itu):** `bench migrate` uji tahan belum pernah dijalankan sejak fix item DD
& KK. **Update 2 September:** ternyata memang belum aman — lihat sesi di bawah, item ini
regresi lagi berulang kali sampai akhirnya ditemukan root cause finalnya.

---

## ✅ Bug Session 2026-09-02 — ROOT CAUSE FINAL: Regresi Sidebar "NextHD" 17→15 Setiap `bench migrate`

**Konteks:** Setelah beberapa sesi (29–31 Agustus) mencoba menambahkan "NextHD Asset Category"
dan "NextHD Reporting" ke sidebar "NextHD" via `doc.append("items", ...)` + `doc.save()`, item
tersebut **selalu hilang lagi** setiap kali `bench migrate` dijalankan — turun dari 17 item
kembali ke 15 item "inti" (Dashboard + 13 DocType lama, sudah termasuk "NextHD Business Hours"
tapi tanpa "NextHD Asset Category"/"NextHD Reporting"). Pola ini terjadi berulang kali dan
sempat dikira disebabkan oleh beberapa teori berbeda di sesi-sesi sebelumnya (`standard=0`,
proses restore database, script debug lama yang tidak sengaja dijalankan ulang) — semuanya
sudah dikonfirmasi **BUKAN** penyebab sebenarnya lewat investigasi sistematis sesi ini.

### Metodologi Investigasi (Eliminasi Bertahap)

1. **Cross-check bash history dengan timestamp** — ditemukan `HISTTIMEFORMAT` tidak aktif
   sebelumnya, membuat sebagian besar timestamp history yang dicurigai (`31 Agustus 15:13:18`)
   **tidak bisa dipercaya** (backfilled saat history di-flush, bukan waktu eksekusi asli).
   **Pelajaran baru:** forensik `bash history` tidak valid tanpa `HISTTIMEFORMAT` aktif sejak
   awal sesi.
2. **Cek kode `nexthd` sendiri** (hooks.py, patches) — dipastikan TIDAK ada kode yang menyentuh
   `Workspace Sidebar` sama sekali. Kedua patch (`create_custom_roles`,
   `remove_next_helpdesk_workspace`) sudah tercatat di `tabPatch Log` (pernah jalan 8 Agustus)
   sehingga tidak akan re-run.
3. **Baca source `remove_orphan_entities()`** (`frappe/model/sync.py`) — fungsi ini beroperasi
   di level DOKUMEN PENUH (hapus/simpan seluruh `Workspace Sidebar`), BUKAN per-item child
   table. `check_if_record_exists()` yang dipakainya hanya cek **keberadaan file**, tidak
   membaca isi `items`. **Fungsi ini dibuktikan BUKAN penyebabnya** — dites langsung, dijalankan
   sendirian, tidak mengubah apa pun.
4. **Isolasi SEMUA fungsi individual di pipeline `migrate.py`** — `sync_for()`, `sync_all()`
   (bahkan dengan `frappe.flags.in_migrate=True`), `sync_jobs()`, `create_missing_sequences()`,
   `sync_dashboards()`, `sync_customizations()`, `sync_languages()`, `flush_deferred_inserts()`,
   `remove_orphan_doctypes()`, `remove_orphan_entities()`, `delete_duplicate_icons()`, `Portal
   Settings.sync_menu()`, `Installed Applications.update_versions()`, semua `after_migrate`
   hooks, dan patch handler (`pre_model_sync`/`post_model_sync`) — **satu per satu dan
   berurutan, TIDAK SATU PUN mereproduksi bug** saat dipanggil manual via `bench console`.
   Namun `bench migrate` CLI penuh **selalu** mereproduksi bug 100% dari beberapa kali percobaan.
5. **Trigger MySQL untuk audit `DELETE`** (karena `general_log` MariaDB butuh privilege SUPER
   yang tidak tersedia) — dipasang `BEFORE DELETE` trigger pada `tabWorkspace Sidebar Item` yang
   mencatat row yang dihapus + timestamp presisi mikrodetik. **Hasil kunci:** ditemukan **DUA
   gelombang DELETE** dalam satu proses migrate (gelombang 1: hapus 15 baris; ~1.4 detik
   kemudian, gelombang 2: hapus 17 baris, termasuk 2 item yang seharusnya sudah tidak ada lagi
   sejak gelombang 1) — membuktikan ada proses **hapus-lalu-regenerasi-lalu-hapus-lagi** yang
   terjadi di dalam satu migrate, bukan cuma satu operasi DELETE sederhana.
6. **Cek isi `Workspace.links`** — hanya berisi 13 DocType + 6 Report (19 total), **TIDAK
   mengandung "NextHD Business Hours"** yang justru selalu muncul di hasil akhir 15-item.
   Ini **membantah teori lama** ("item di-regenerate dari `Workspace.links`", yang tercatat di
   sesi 25 Agustus) — set 15-item final TIDAK cocok dengan isi `Workspace.links` mana pun.

### Root Cause Final (Terkonfirmasi 100%)

**File `nexthd/fixtures/workspace_sidebar.json` masih ada secara fisik di disk**, meski sudah
lama dihapus dari **daftar array** `fixtures = [...]` di `hooks.py` (dengan komentar "Workspace
Sidebar SENGAJA DIHAPUS dari fixtures"). Ternyata menghapus entri dari array `hooks.py` **TIDAK
CUKUP** — fungsi `import_fixtures()` di `frappe/utils/fixtures.py` (dipanggil oleh
`sync_fixtures()`, langkah "Syncing fixtures..." di setiap `bench migrate`) bekerja seperti ini:

```python
def import_fixtures(app):
    fixtures_path = frappe.get_app_path(app, "fixtures")
    fixture_files = sorted(os.listdir(fixtures_path))   # <- SCAN SEMUA FILE .json DI FOLDER
    for fname in fixture_files:
        if not fname.endswith(".json"):
            continue
        import_doc(file_path, sort=True)   # <- import/timpa data dari SETIAP file yang ditemukan
```

**`os.listdir()` men-scan SELURUH folder `fixtures/` berdasarkan nama file fisik di disk — TIDAK
peduli sama sekali apakah file tersebut terdaftar di variabel `fixtures` dalam `hooks.py`.**
Ini bertentangan dengan asumsi umum bahwa `hooks.py` adalah satu-satunya "sumber kebenaran" —
untuk proses IMPORT (bukan export), Frappe percaya pada isi folder, bukan hooks.

Isi file usang tersebut adalah **snapshot 15 item persis** (Dashboard + 14 DocType, termasuk
"NextHD Business Hours", TANPA "NextHD Asset Category"/"NextHD Reporting") dengan
`"modified": "2026-08-19 20:00:00"` — cocok 100% dengan timestamp `modified` parent dokumen
"NextHD" yang selalu terlihat "beku" di 19 Agustus meski child table-nya sudah berkali-kali
diedit via `doc.save()` di sesi-sesi berikutnya. File ini kemungkinan besar adalah hasil export
manual/`bench export-fixtures` yang dijalankan sekali di sekitar 19 Agustus, sebelum item
Reporting (27 Agustus) dan Asset Category (30 Agustus) pernah ditambahkan — dan sejak saat itu
diam-diam menimpa ulang data setiap kali `bench migrate` dijalankan.

**Pola "dua gelombang delete" (temuan #5 di atas) kemungkinan besar adalah representasi dari
satu siklus delete-lalu-insert-ulang milik `import_doc()` saat mengimpor fixture ini** (hapus
child table lama, insert ulang sesuai isi file) — bukan dua sumber terpisah.

### Fix Permanen

```bash
rm /home/it/frappe/apps/nexthd/nexthd/fixtures/workspace_sidebar.json
```

Lalu tambahkan kembali 2 item yang hilang via `doc.append("items", ...)` + `doc.save()` seperti
biasa. **Diverifikasi stabil lintas 2× `bench migrate` berturut-turut** — total tetap 17 item,
tidak ada regresi, file usang tidak ter-generate ulang dengan sendirinya.

### Pelajaran Kritis untuk Fixture Apa Pun ke Depan

- **Menghapus entri dari array `fixtures = [...]` di `hooks.py` TIDAK CUKUP** untuk
  "menonaktifkan" sebuah fixture — file fisik `.json` yang bersangkutan di folder
  `nexthd/fixtures/` **HARUS ikut dihapus dari disk**, karena proses import (`sync_fixtures()`
  → `import_fixtures()`) membaca folder secara generik via `os.listdir()`, bukan membaca daftar
  di `hooks.py`. Hooks.py hanya dipakai untuk proses **export** (`export_fixtures()`), bukan
  import.
- **Kalau menemukan pola "item hilang tiap migrate" yang sudah dicoba fix berkali-kali di
  level database/ORM tapi selalu kembali rusak**, curigai dulu **file fixture usang yang masih
  tersisa di disk** untuk DocType yang sama — cek `ls nexthd/fixtures/` secara langsung,
  jangan hanya percaya komentar/dokumentasi di `hooks.py` yang bilang suatu fixture "sudah
  dinonaktifkan".
- **Field `modified` pada dokumen yang "beku" di tanggal lama meski sering di-edit** adalah
  sinyal kuat bahwa proses lain (bukan `doc.save()` biasa) sedang menimpa data tersebut secara
  berkala — pola ini terbukti berguna sebagai petunjuk diagnostik di kasus ini.
- **Kalau `general_log` MariaDB tidak bisa diaktifkan** (butuh privilege `SUPER` yang sering
  tidak tersedia di managed/shared DB), gunakan **trigger `BEFORE DELETE`/`BEFORE UPDATE`**
  pada tabel yang dicurigai sebagai alternatif audit ringan — cukup privilege `TRIGGER` biasa,
  dan bisa menangkap `CONNECTION_ID()`, `CURRENT_USER()`, serta timestamp presisi mikrodetik
  tanpa overhead log seluruh query database.
- **Forensik `bash history` tidak valid tanpa `HISTTIMEFORMAT` diaktifkan SEJAK AWAL sesi** —
  timestamp yang muncul tanpa itu adalah waktu flush-ke-disk, bukan waktu eksekusi asli, dan
  bisa menyesatkan kesimpulan (seperti sempat terjadi di sesi ini sebelum root cause final
  ditemukan).

**Status:** Item KK (sidebar "NextHD" 17 item) dan status sidebar "NextHD Report" dinyatakan
**tuntas dan stabil** per sesi ini. Rekomendasi ke depan: verifikasi ulang isi folder
`nexthd/fixtures/` secara berkala (`ls -la`) dibandingkan dengan `hooks.py` untuk DocType lain
yang pernah "dinonaktifkan dari fixtures" (misal `Workflow Transition`, lihat `WORKFLOW.md §5`
dan `BUG_HISTORY.md`) — pastikan tidak ada file fisik usang serupa yang masih tertinggal.

---

*Dokumen ini dikelola oleh Claude. Update terakhir: 2026-09-02.*
