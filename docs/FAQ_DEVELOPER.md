# NextHD — FAQ & Pembagian Kerja untuk Developer (Devin/Claude)

> **BACA FILE INI DULU, SEBELUM MENYENTUH `hooks.py`, fixture JSON manapun, Workspace,
> Desktop Icon, atau menjalankan `bench migrate`.**
>
> File ini kurasi khusus untuk masalah yang **sudah berulang kali terjadi** di project ini
> (Workspace rusak pasca-migrate, Desktop Icon hilang, dst), plus pembagian kerja antar
> Claude/Devin/Efendy. Kalau kamu (Devin) sedang mengerjakan task yang menyentuh area ini,
> WAJIB baca dulu — jangan cuma andalkan deskripsi prompt task.
>
> **Last updated:** 2026-08-23 18:10 WIB (digabung dari `FAQ.md` +
> bagian "Pembagian Kerja" yang sebelumnya di `SETUP_DAN_ROADMAP.md`)

---

## Bagian A — Pembagian Kerja: Claude vs Devin vs Efendy

| Siapa | Kapan dipakai |
|---|---|
| **Efendy** | Verifikasi manual UI, keputusan SOP/bisnis (SLA, portal requester), akses infra langsung (SSH, DNS, decommission VM), role assignment individual |
| **Claude** | Kerja di server produksi (SQL, console script, fixtures export), debugging bug produksi, verifikasi teknis (workflow, SLA scheduler), tulis spec/prompt untuk Devin, push `.md` file ke repo |
| **Devin** | Implementasi fitur baru di repo (kode Python/JS baru) via PR — tidak punya akses server produksi, hasil kerjanya wajib di-pull manual + `bench migrate` setelah merge |

### Batasan Push ke Repo

| Siapa | Boleh push langsung | Harus lewat script lokal |
|---|---|---|
| Claude | File `.md` saja | `.py`, `.js`, `.json` |
| Devin | Semua file via PR | — |

---

## Bagian B — FAQ Masalah Berulang

### Q1: Saya perlu ubah struktur navigasi/sidebar/desktop icon NextHD. Boleh?

**TIDAK — kecuali diminta eksplisit oleh Efendy di task/prompt.**

4 komponen berikut **DIKUNCI**, jangan diubah walau "kelihatannya" perlu diperbaiki atau dirapikan:

| Komponen | Nilai yang Dikunci | File |
|---|---|---|
| `add_to_apps_screen.route` | `/desk/nexthd` | `hooks.py` |
| Item pertama di sidebar | `Dashboard → link_to: NextHD (Workspace)`, posisi PALING ATAS | `fixtures/workspace_sidebar.json` |
| System Settings `default_app` | `nexthd` | Database (bukan file) |
| User `support@ciptamebel.co.id` → `default_app` | `nexthd` | Database (bukan file) |

**Kenapa:** kombinasi 4 hal ini yang memastikan user selalu masuk ke Workspace dashboard
(bukan list Ticket biasa) begitu login atau klik icon NextHD. Riwayat lengkap perbaikannya
ada di `HANDOFF.md` bagian "ATURAN WAJIB". Kalau task kamu tidak menyebutkan navigasi sama
sekali, JANGAN sentuh 4 hal ini meski secara tidak sengaja ke-generate ulang oleh
`bench export-fixtures` atau semacamnya — cek dulu diff-nya sebelum commit.

---

### Q2: Setelah saya ubah `hooks.py`/tambah field baru terus `bench migrate`, kenapa Workspace/Desktop Icon NextHD hilang atau rusak?

**Root cause paling umum: `bench migrate` menghapus record yang tidak terdaftar di fixtures.**

Kalau kamu menambah/mengubah apapun yang menyentuh `Desktop Icon`, `Workspace`,
`Workspace Sidebar`, atau `Workspace Sidebar Item` secara manual (lewat SQL/console, bukan
lewat fixture JSON di repo), perubahan itu **akan hilang** saat `bench migrate` berikutnya
dijalankan — kecuali sudah di-export dulu ke fixture dan di-commit.

**Checklist wajib SETELAH mengubah apapun terkait Workspace/Desktop Icon/Sidebar:**
```bash
bench --site desk.ciptamebel.co.id export-fixtures --app nexthd
git add nexthd/fixtures/
git commit -m "..."
```
Kalau kamu skip langkah ini, task kamu akan terlihat "berhasil" saat testing manual di
sesi yang sama, tapi **rusak lagi** di deploy berikutnya begitu ada `bench migrate` lain
(termasuk migrate yang dijalankan untuk task LAIN yang tidak berhubungan).

---

### Q3: Kenapa Number Card di Workspace tidak muncul padahal sudah saya buat?

**Root cause spesifik (sudah 2x terjadi):** block `content` JSON Workspace butuh:
- `"type"`: HARUS `"number_card"` (bukan `"card"` — ini salah paling umum)
- key referensi: HARUS `"number_card_name"` (bukan `"card_name"`)

Type yang tidak dikenal **di-skip diam-diam tanpa error** oleh Frappe — jadi kamu tidak
akan lihat exception apapun, cuma card-nya tidak muncul. Kalau kamu generate `content`
JSON secara manual/string, selalu double-check 2 hal di atas.

**Cara aman generate `content` JSON Workspace:** JANGAN tulis sebagai string literal
manual dengan escape karakter — build sebagai Python dict/list dulu, baru `json.dumps()`
sekali di akhir. Double-escape manual sering menghasilkan `SyntaxError` di browser yang
susah dilacak.

---

### Q4: Field baru yang saya tambah ke DocType tidak muncul di form/UI meski data sudah benar di database. Kenapa?

**Kemungkinan besar ini cache, bukan bug struktur data.** Sebelum curiga ada yang salah di
JSON/kode kamu, coba dulu:
```bash
bench --site desk.ciptamebel.co.id clear-cache
bench --site desk.ciptamebel.co.id clear-website-cache
bench build --app nexthd
bench restart
```
Kalau setelah ini masih tidak muncul, baru cek field_order/permlevel di JSON DocType-nya.

---

### Q5: Saya tambah DocField baru lewat SQL langsung (bukan lewat `doc.save()`), tapi kena error `Unknown column 'xxx'`. Kenapa?

**Insert ke `tabDocField` cuma daftar metadata — TIDAK otomatis membuat kolom fisik** di
tabel data DocType tersebut (beda dari `doc.save()`/migrate yang auto-sync struktur).
Kalau kamu insert manual ke `tabDocField`, WAJIB diikuti:
```sql
ALTER TABLE `tabNamaDocType` ADD COLUMN `nama_field` VARCHAR(140);
```
sebelum field itu dipakai untuk insert/update data.

> Catatan: kalau kamu menambah field lewat cara normal (edit file `.json` DocType lalu
> `bench migrate`), Frappe otomatis handle ini — masalah ini HANYA terjadi kalau ada yang
> insert manual langsung ke `tabDocField` via SQL/console (pola debug cepat yang dipakai
> Claude, bukan pola kerja normal Devin lewat PR). Kalau kamu (Devin) selalu kerja lewat
> edit file JSON DocType + `bench migrate`, kemungkinan besar tidak akan ketemu masalah ini.

---

### Q6: `doc.save()` saya gagal terus di server produksi. Kenapa?

`doc.save()` sering gagal di production (non-developer mode) untuk operasi tertentu.
Kalau kamu kerja lewat PR/kode normal (bukan console interaktif), ini **jarang jadi
masalah** — masalah ini lebih sering muncul untuk pola kerja debug cepat via `bench
console`. Kalau kamu memang perlu insert/update programatik di dalam kode DocType
(controller `.py`), gunakan `doc.insert()` untuk record baru (biasanya aman), dan kalau
memang perlu update field existing dari dalam hook, gunakan `frappe.db.set_value()` yang
lebih ringan daripada full `doc.save()`.

---

### Q7: Saya lihat ada field/logic yang kelihatan "aneh" atau "tidak konsisten" (misal naming series, field permission). Boleh saya rapikan sekalian?

**TIDAK, kecuali diminta eksplisit di task.** Banyak hal yang kelihatan "aneh" sebenarnya
adalah **keputusan desain yang disengaja** dan sudah didiskusikan panjang dengan Efendy
(contoh: `priority` field `permlevel=1` dengan override khusus Agent Manager/IT Manager,
`is_24x7` di SLA Policy, format naming series `YY.MM`). Kalau ragu apakah sesuatu itu bug
atau desain sengaja, cek dulu `docs/POLA_KERJA_DAN_BUG.md` (riwayat bug) dan
`docs/SUMMARY.md` (keputusan desain) — JANGAN asumsi sendiri dan ubah tanpa konfirmasi.

Kalau task kamu secara eksplisit hanya minta fitur tambahan/fix spesifik, **jangan
sertakan perubahan "sekalian dirapikan" di luar scope task tersebut** dalam PR yang sama
— itu bikin review jadi lebih sulit dan berisiko merusak hal lain yang tidak terkait.

---

### Q8: Ada dua transisi Workflow yang kelihatannya menuju state yang sama tapi salah satu "polos" (tidak lewat tombol custom). Boleh saya hapus salah satu?

**Hati-hati — ini pernah jadi bug berulang (lihat `docs/WORKFLOW.md §4 Jebakan 2`).**
Kalau ada state yang seharusnya SELALU diiringi pembuatan record lain (misal Problem →
Known Error harus selalu bikin record Known Error baru), transisi workflow "polos" yang
cuma ubah status tanpa efek samping itu **berbahaya**, tapi solusinya BUKAN selalu hapus
transisinya — bisa juga tambah `condition` di transisi tersebut. Baca dulu
`docs/WORKFLOW.md §4` sebelum menyentuh `Workflow Transition` apapun.

---

### Q9: Field `action` di Workflow Transition mau saya ganti namanya, tapi kena `LinkValidationError`. Kenapa?

Kolom `action` adalah **Link ke master `Workflow Action Master`**, bukan teks bebas.
Ganti nilai `action` ke nama baru yang belum ada sebagai master record via `doc.save()`
akan gagal. Kalau memang perlu nama aksi baru, buat dulu master record-nya di
`Workflow Action Master`. Kalau cuma perlu ubah `condition` tanpa ganti nama aksi, pakai
raw SQL UPDATE (hindari `doc.save()` yang menjalankan validasi link).

---

### Q10: Saya lihat field/DocType yang seharusnya masuk fixtures tapi filenya kosong (`[]`). Ini bug?

**Kemungkinan besar bukan bug, tapi export yang dijalankan saat database masih kosong.**
`bench export-fixtures` MEMBACA dari database — kalau dijalankan sebelum data ada,
hasilnya kosong dan **akan menimpa** fixture file lama yang sudah lengkap kalau di-commit
begitu saja. Selalu cek isi file yang di-export tidak tiba-tiba jadi kosong/lebih pendek
dari sebelumnya sebelum commit.

---

### Q11: Ke mana saya harus lihat kalau saya butuh tahu apakah sesuatu itu "bug yang perlu difix" atau "fitur yang memang belum ada"?

Urutan cek yang benar:
1. `docs/SUMMARY.md §2` — status item terkini (belum dikerjakan vs sudah selesai)
2. `docs/DAFTAR_FITUR.md` — checklist lengkap semua fitur (selesai/sedang/rencana)
3. `docs/POLA_KERJA_DAN_BUG.md §4` — riwayat bug lengkap, siapa tahu sudah pernah dibahas
4. Kalau task kamu berasal dari GitHub Issue/prompt Claude — ikuti scope yang tertulis di
   sana secara ketat, jangan improvisasi di luar itu

---

### Q12: Saya mau tambah dependency Python/npm baru untuk task saya. Boleh?

**Hindari kalau bisa.** Selalu cek dulu apakah kebutuhan itu sudah bisa dipenuhi library
yang sudah ada (misal Pillow untuk image processing — kemungkinan sudah ada karena dipakai
di project lain milik Efendy). Kalau memang perlu dependency baru, sebutkan eksplisit di
PR description supaya reviewer (Efendy/Claude) sadar ada instalasi tambahan yang perlu
dijalankan di server produksi.

---

*Dokumen ini dikelola oleh Claude, khusus untuk mengurangi pengulangan bug yang sama oleh
Devin dan menjelaskan pembagian peran tim. Kalau kamu (Devin) baru saja menemukan masalah
baru yang polanya mirip dengan salah satu di atas tapi belum tercatat, laporkan di PR
description supaya bisa ditambahkan ke sini oleh Claude/Efendy di sesi berikutnya.*

*Update terakhir: 2026-08-23 18:10 WIB.*
