# NextHD Web — Spesifikasi Portal

> Acuan teknis untuk Devin. Baca `docs/FAQ_DEVELOPER.md` dulu sebelum mengerjakan.
> Ikuti scope task secara ketat; jangan merapikan hal di luar scope.
>
> **Status:** DRAFT awal, 2026-09-30. Perlu dilengkapi sebelum tahap 1 diserahkan ke Devin.

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

| Peran | Halaman awal | Isi |
|---|---|---|
| Requester | `/nexthd/tiket-saya` | Tiket miliknya, buat tiket |
| Agent | `/nexthd/kerja` | Antrian, detail, aksi workflow, worklog |
| Agent Manager / IT Manager | `/nexthd/manajer` | Semua tiket, SLA, penugasan, laporan |
| IT Auditor | `/nexthd/audit` | Read-only |

Catatan: route `/tiket-saya` (Web Form) sudah ada dan terpisah dari `/nexthd/tiket-saya`.
Hindari bentrok nama; tentukan di tahap 2.

## 4. Aturan Keamanan (WAJIB)

1. Setiap halaman dan endpoint memeriksa `frappe.session.user != "Guest"` dan peran.
2. **Dilarang** `ignore_permissions=True` di endpoint yang melayani user biasa.
3. **Dilarang** SQL langsung untuk membaca/menulis data tiket. Pakai `frappe.get_list` / `frappe.get_doc`
   supaya izin (termasuk `if_owner` untuk Requester) tetap berlaku.
4. Perubahan status wajib lewat `apply_workflow`, bukan set field `status`.
5. Membuat/menyimpan dokumen lewat `doc.insert()` / `doc.save()` agar hook (SLA, Telegram) jalan.
6. Requester tidak boleh melihat tiket orang lain; uji eksplisit.
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

| Tahap | Isi | Diserahkan ke |
|---|---|---|
| 1 | Fondasi: template dasar, `api.js`, `portal.py` kerangka, redirect per peran | Devin |
| 2 | Requester: daftar tiket sendiri + buat tiket | Devin |
| 3 | Agent: antrian, detail, aksi workflow, worklog | Devin |
| 4 | Manajer: dashboard, penugasan | Devin |
| 5 | Problem / Known Error / Change Request / Asset (EAV) | Devin |
| 6 | Laporan/grafik, lampiran & foto | Devin |

Satu tahap per PR. Tiap PR direview Claude sebelum merge, lalu Efendy pull + `bench build` + uji.

## 7. Definisi Selesai per Tahap

- Tidak ada `ignore_permissions=True` / SQL langsung pada data tiket (dicek review).
- Uji peran: Requester tidak bisa membuka tiket orang lain; Guest dialihkan ke login.
- SLA dan notifikasi Telegram tetap terpicu dari tiket yang dibuat lewat portal.
- Dokumen `docs/web/*` diperbarui (FITUR_WEB, LOG_WEB, BUG_WEB bila ada).

## 8. Pertanyaan Terbuka

| # | Pertanyaan | Keputusan |
|---|---|---|
| 1 | Apakah Requester ikut memakai portal sejak tahap awal, atau tahap awal hanya Agent IT? | Belum diputuskan (sementara hanya IT yang memegang) |
| 2 | Halaman login bertema NextHD (`www/login` kustom) | Ditunda, setelah tahap 2 |
| 3 | Nama route Requester vs Web Form `/tiket-saya` | Belum diputuskan |
