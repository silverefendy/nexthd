# NextHD Web — Spesifikasi Portal

> Acuan teknis untuk Devin. Baca `docs/FAQ_DEVELOPER.md` dulu sebelum mengerjakan.
> Ikuti scope task secara ketat; jangan merapikan hal di luar scope.
>
> **Status:** DRAFT, diperbarui 2026-09-30 setelah keputusan Efendy (lihat §8). Siap diserahkan ke Devin untuk tahap 1-2.

## 1. Tujuan

Portal web kustom (jalur A: halaman `www/` di dalam Frappe) sebagai antarmuka kerja harian
NextHD. Tanpa Vue/React/frappe-ui. Desk tetap dipakai untuk administrasi data master.

## 2. Struktur File (target)

```
nexthd/nexthd/
├── public/css/nexthd/   base.css, layout.css, components.css, pages/*.css
├── public/js/nexthd/    api.js, ui.js, pages/*.js
├── www/nexthd/          index (pintu masuk), halaman per peran
└── api/portal.py        endpoint @frappe.whitelist() per fitur
```

Sudah ada (landing page): `public/css/nexthd_landing.css`, `public/js/nexthd_landing.js`,
`www/nexthd/index.html`, `www/nexthd/index.py` (`PRIVATE_MODE = True`).

Catatan: satu file `www/` melayani satu route. Detail dokumen memakai query string
(`/nexthd/tiket?id=TKT-...`), bukan satu file per dokumen.

## 3. Peran dan Halaman

Satu halaman login; setelah masuk, arahkan berdasarkan peran. Akses dijaga di backend, bukan URL.

**Cakupan saat ini: hanya tim IT.** Halaman Requester dibangun belakangan (lihat §8).

| Peran | Halaman awal | Isi | Tahap |
|---|---|---|---|
| Agent | `/nexthd/kerja` | Antrian, detail, aksi workflow, worklog | 1-3 |
| Agent Manager / IT Manager | `/nexthd/manajer` | Semua tiket, SLA, penugasan, laporan | 4 |
| IT Auditor | `/nexthd/audit` | Read-only | menyusul |
| Requester | `/nexthd/tiket-saya` | Tiket miliknya, buat tiket | ditunda (tahap 7), menggantikan Web Form `/tiket-saya` |

## 4. Aturan Keamanan (WAJIB)

1. Setiap halaman dan endpoint memeriksa `frappe.session.user != "Guest"` dan peran.
2. **Dilarang** `ignore_permissions=True` di endpoint yang melayani user biasa.
3. **Dilarang** SQL langsung untuk membaca/menulis data tiket. Pakai `frappe.get_list` / `frappe.get_doc`
   supaya izin (termasuk `if_owner` untuk Requester) tetap berlaku.
4. Perubahan status wajib lewat `apply_workflow`, bukan set field `status`.
5. Membuat/menyimpan dokumen lewat `doc.insert()` / `doc.save()` agar hook (SLA, Telegram) jalan.
6. Requester tidak boleh melihat tiket orang lain; uji eksplisit (berlaku saat halaman Requester dibangun).
7. Output ke HTML di-escape; jangan `innerHTML` dengan data mentah dari user.
8. Endpoint mengubah data: hanya POST.
9. `allow_guest=True` hanya untuk endpoint agregat publik (belum ada).

## 4b. Aturan Teknis Frappe yang Sudah Pernah Menjebak

- Event hook yang valid: `after_insert`, bukan `on_insert`.
- Field baru di DocType ditulis di JSON DocType, bukan hanya SQL/fixture terpisah.
- Fixture: jangan mendaftarkan dua fixture untuk child table yang sama.
- `export-fixtures` selalu diperiksa diff-nya sebelum commit; jangan `git add .` (pakai path eksplisit).
- Jangan sentuh 4 komponen navigasi terkunci (`FAQ_DEVELOPER.md` Q1).
- Cek `naming_rule` DocType sebelum `doc.save()` pertama pada DocType lama.

## 5. Gaya Visual

Retro-futuristik: kertas krem, tinta gelap, font monospace + serif sistem, aksen oranye-bakar
(`--a`) dan teal (`--b`), dark mode otomatis via `prefers-color-scheme`. Tanpa font/library luar.
Token warna ada di `nexthd_landing.css` (`:root`). Pakai ulang, jangan buat palet baru.
Aksesibilitas: hormati `prefers-reduced-motion`, kontras cukup, dapat dipakai di layar ponsel.

## 6. Tahap Pengerjaan

Urutan disesuaikan dengan keputusan "IT dulu": Agent didahulukan, Requester menyusul.

| Tahap | Isi | Diserahkan ke |
|---|---|---|
| 1 | Fondasi: template dasar, `api.js`, `portal.py` kerangka, redirect per peran (IT) | Devin |
| 2 | Agent: antrian tiket + detail tiket (baca) + buat tiket | Devin |
| 3 | Aksi workflow + worklog | Devin |
| 4 | Manajer: dashboard, penugasan | Devin |
| 5 | Problem / Known Error / Change Request / Asset (EAV) | Devin |
| 6 | Laporan/grafik, lampiran & foto | Devin |
| 7 | Halaman Requester (menggantikan Web Form `/tiket-saya`) + login bertema NextHD | Devin |

Satu tahap per PR. Tiap PR direview Claude sebelum merge, lalu Efendy pull + `bench build` + uji.

## 7. Definisi Selesai per Tahap

- Tidak ada `ignore_permissions=True` / SQL langsung pada data tiket (dicek review).
- Uji akses: Guest dialihkan ke login; peran tanpa hak ditolak di backend.
- SLA dan notifikasi Telegram tetap terpicu dari tiket yang dibuat lewat portal.
- Dokumen `docs/web/*` diperbarui (FITUR_WEB, LOG_WEB, BUG_WEB bila ada).

## 8. Keputusan (Efendy, 2026-09-30)

| # | Pertanyaan | Keputusan |
|---|---|---|
| 1 | Requester ikut sejak awal? | **Tidak.** Sementara hanya IT, karena masih tahap pengembangan walau Desk sudah production. Requester di tahap 7 |
| 2 | Web Form lama `/tiket-saya` | **Diganti** oleh halaman Requester portal. Web Form tetap hidup sampai tahap 7 selesai dan teruji. Jangan dihapus lebih awal (fixture `Web Form` di `hooks.py` dan cek di `AUDIT_SISTEM.md` §12 disesuaikan saat penggantian) |
| 3 | Halaman login bertema NextHD (`www/login` kustom) | Ditunda ke tahap 7 |
| 4 | Landing page ter-commit ke repo | Sudah: `git status` bersih dan sinkron dengan `origin/main` (30 Sept) |
