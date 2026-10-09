# NextHD Web — Riwayat Bug Portal

> Khusus bug portal web (`www/nexthd`, `public/*/nexthd*`, `api/portal.py`) dan Web Form `/tiket-saya`.
> Bug Desk/DocType/workflow ada di `docs/BUG_HISTORY.md` dan file terkait.
>
> **Last updated:** 2026-10-09 17:20 WIB (entri 7–8 Okt disusun dari catatan sesi, bukan dari diff; akar penyebab yang belum dibuktikan ditandai)

## Format Entri

```
### YYYY-MM-DD — judul singkat
- Gejala:
- Root cause:
- Fix:
- Pelajaran:
```

## Riwayat

### 2026-10-08 — Dropdown Aset Terdampak kosong di Web Form (SELESAI)
- Gejala: field Aset Terdampak di `/tiket-saya/new` kosong dan tidak bisa dipilih untuk Requester.
- Root cause: `get_link_options` Web Form dengan `login_required=1` hanya memuat record milik (`owner`) user itu dan mengabaikan `aset_izin.py`; aset dimiliki `support@`, jadi untuk Requester hasilnya kosong. Kontrolnya ternyata Autocomplete (bukan Select), `after_load` tidak terpanggil otomatis, dan mengganti `fieldtype` dari browser tidak membangun ulang kontrol.
- Fix: endpoint `get_my_assets()` (`utils/aset_filter.py`) + client script IIFE dengan retry `setTimeout` di field `client_script` Web Form (commit `d583cd4`). Terbukti: tiket `TKT-2610-0009` tersimpan dengan `affected_asset`.
- Pelajaran: rincian dan 7 butir pelajaran Web Form v16 ada di `docs/BUG_ASET_LOKASI_WEBFORM.md` §3.

### 2026-10-08 — Dropdown Link Web Form tidak peka izin per-user (TEMUAN dari kode Frappe)
- Gejala: aturan `aset_izin.py` (Requester hanya melihat asetnya) tidak berlaku di dropdown Web Form.
- Dari kode (diverifikasi 8 Okt): `get_link_options` memfilter `owner` bila `allow_read_on_all_link_options=0`, dan memakai `frappe.get_all` (melewati permission_query_conditions) bila 1. Jadi izin per-user hanya berlaku di Desk/API, bukan dropdown Web Form.
- Dampak: untuk Category, Tim, Service Catalog dipakai `allow_read_on_all_link_options=1` (data master, aman). Untuk Aset dipakai endpoint sendiri. Jangan memberi izin baca Requester ke Category/Team hanya demi dropdown.

### 2026-10-07 — Web Form Tiket Saya 500 `ModuleNotFoundError` (SELESAI)
- Gejala: `/tiket-saya` mengembalikan 500.
- Root cause: Web Form berstatus `is_standard=1` tanpa folder `web_form/<nama>/` di modul. Cek `published: 1` di console (22 Agustus) tidak membuktikan halaman berfungsi, jadi klaim "Web Form live" sebelumnya tidak benar.
- Fix: `is_standard 0` di DB dan di fixture `web_form.json` (commit `881084c`); keduanya wajib diubah sekaligus, kalau tidak `bench migrate` mengembalikannya.
- Pelajaran: verifikasi Web Form di browser, bukan hanya lewat console.

### 2026-10-07 — `/tiket-saya/new` terbuka tanpa login (SELESAI)
- Gejala: uji Incognito: halaman buat tiket terbuka tanpa login (`login_required=0`).
- Fix: `login_required 1` di DB dan fixture (commit `c2a2a3e`), keputusan Efendy 7 Okt.

### 2026-10-07 — `/nexthd/tentang`: `NX is not defined` dan CSS dasar tidak termuat (SELESAI)
- Gejala: skrip inline di `/nexthd/tentang` gagal `NX is not defined`; halaman non-IT tampil tanpa variabel warna (`--a`, `--line` tidak terdefinisi).
- Root cause: `api.js`/`ui.js` dimuat dengan `defer`, sedangkan skrip inline berjalan lebih dulu; CSS dasar (`base.css`, `layout.css`, `components.css`) hanya dimuat untuk IT padahal dipakai halaman non-IT.
- Fix: `renderNav` menunggu `DOMContentLoaded`; CSS dasar dimuat untuk semua pengguna (commit `e823e77`); tautan Tiket Saya untuk non-IT dikembalikan (`3f97dbf`). Sempat disembunyikan sementara (lihat pesan commit `e823e77`).
- Pelajaran: skrip inline yang memakai `NX` wajib menunggu DOM siap; CSS bersama dimuat untuk semua peran yang memakai halaman itu.
- Terbuka: non-IT belum punya tombol Keluar di `/nexthd/tentang`.

### 2026-10-06 — `?v=` aset belum dinaikkan setelah A1 dan B1 (STATUS TIDAK DIKONFIRMASI setelah 6 Okt)
- Gejala: belum ada keluhan; ditemukan saat review. `www/nexthd/*.html` masih memuat `ui.js?v=3`, `layout.css?v=2`, `kerja.js?v=3`, dst. Pengguna yang pernah membuka portal bisa tetap memakai `ui.js`/`layout.css` lama (tanpa dropdown) sampai cache habis; uji Efendy lolos karena hard refresh.
- Root cause: perubahan `.js`/`.css` tidak diikuti penaikan parameter versi di html.
- Fix: skrip patch menaikkan semua `?v=` aset `/assets/nexthd/(css|js)/nexthd/...` di `www/nexthd/*.html` sebanyak 1 (landing `nexthd_landing.*` tidak tersentuh). Skrip disiapkan 6 Okt; **belum tercatat apakah sudah dijalankan dan di-commit**. Tahap 4 dan menu bersama (7 Okt) menambah perubahan `.js`/`.css` baru yang juga perlu penaikan `?v=`.
- Pelajaran: setiap perubahan aset portal harus disertai penaikan `?v=`; sudah tercatat di tabel "Titik Rawan" di bawah dan di `LOG_WEB.md`.

### 2026-10-06 — Check CI "Frappe Linter" gagal (TERBUKA, tidak memblokir merge)
- Gejala: tanda silang merah pada PR #19 dan (dugaan) commit `4d5bee0` yang hanya mengubah dokumentasi.
- Dari log: trailing whitespace gagal; ruff import sorter gagal ("38 errors (38 fixed)" di mesin CI, perbaikan tidak masuk repo); ruff linter gagal; eslint gagal (file tidak diketahui). Check python ast, json, yaml, toml, merge conflict lolos. Check "Server" belum diketahui hasil akhirnya.
- Root cause (dugaan, belum terbukti): kerapian gaya yang menumpuk di seluruh repo, bukan dari PR #19 (hanya mengubah dua file JS). Keterlibatan eslint terhadap file JS kita belum bisa dipastikan.
- Fix: PR "pembersihan lint" terpisah untuk Devin (`pre-commit run --all-files`, periksa `git --no-pager diff --stat` sebelum commit).
- Pelajaran: kegagalan lint bukan kegagalan fungsi; jangan campur pembersihan lint dengan PR fitur.

### 2026-10-06 — Penanganan `page` di B1 longgar (TEMUAN, kosmetik)
- Gejala: `?page=2abc` diterima sebagai halaman 2 (`parseInt`); `?page=99` pada data satu halaman menampilkan daftar kosong dengan tombol "Sebelumnya" yang mundur satu per satu.
- Dampak: kecil; tautan dashboard tidak memakai `page`. Tidak diperbaiki.

### 2026-10-06 — Angka `view=unassigned` dan `view=mine` ikut tiket Selesai/Ditutup (KEPUTUSAN #9 FINAL 7 Okt)
- Gejala: tab "Belum ditugaskan" di antrian ikut menampilkan tiket Selesai/Ditutup yang tidak punya penanggung jawab; `view=mine` menampilkan semua tiket milik user sepanjang waktu.
- Keputusan 7 Okt: `unassigned` hanya tiket aktif (dipakai kartu dashboard Tahap 4); `mine` tidak diubah, tidak ada kartu "Ditugaskan ke saya". Bukti perbaikan di kode `list_tickets` tidak dicatat di sini; verifikasi dari angka kartu dashboard yang cocok dengan halaman tujuan (uji 7 Okt).

### 2026-10-02 — Tabel log meluber keluar kartu (SELESAI)
- Gejala: tabel Riwayat Progress dan Riwayat Menunggu User keluar dari kartu, kolom terpotong, header patah, tombol Aksi menempel, waktu bermikrodetik.
- Root cause: aturan `.nx-table th/td:nth-child(1,3..8) { white-space: nowrap }` dan `min-width` kolom ke-2 ditulis untuk tabel antrian tetapi berlaku untuk semua `.nx-table`; tabel di `tiket.js` juga tidak dibungkus `.nx-table-wrap`.
- Fix: kelas khusus `nx-table--log` (wrap teks, kolom pertama dan header tidak patah), pembungkus `nx-table-wrap`, `fmtDateTime` membuang mikrodetik, CSS jarak panel Aksi. Diterapkan lewat skrip patch di server; commit di branch `fix/web-tampilan-log`.
- Pelajaran: CSS per-tabel jangan global; ukur tabel dengan teks panjang sungguhan, bukan data pendek.

### 2026-10-02 — Semua POST gagal "Invalid Request" (SELESAI, akar penyebab belum dikonfirmasi)
- Gejala: buat tiket dan semua aksi POST gagal.
- Root cause langsung: meta `csrf-token` berisi teks mentah `{{ csrf_token }}` (template `www/` tidak mengisinya), sehingga header `X-Frappe-CSRF-Token` salah. Kenapa tidak terisi belum dikonfirmasi dari source Frappe v16.
- Fix: `get_session_info` mengembalikan `csrf_token`; `api.js` memakai `getCsrfToken()` dengan fallback ke endpoint itu (commit `44ef6b4`). Terbukti: buat tiket berhasil di browser 2 Okt.
- Pelajaran: review kode tidak menangkap ini; wajib satu POST nyata di site tiap tahap.

### 2026-10-01 — Antrian gagal `count(name)` (SELESAI)
- Gejala: antrian error `SQL functions are not allowed as strings in SELECT: count(name)`.
- Root cause: Frappe v16 menolak fungsi SQL sebagai string di `fields`; tes Devin tidak menyentuh database.
- Fix: `len(frappe.get_list(pluck="name", limit_page_length=0))` (commit `63a01a4`). Catatan skala: memuat semua nama yang cocok; ganti hitung SQL bila tiket puluhan ribu.

### 2026-10-02 — Pesan galat memuat tag HTML (SELESAI)
- Gejala: toast menampilkan `Error: <strong>NextHD Ticket Worklog</strong> Row #1: Value missing for: Aktivitas` saat catatan hanya berisi satu tag HTML (isi dibuang sanitasi sehingga kosong).
- Dugaan: Frappe membuang tag dari kolom teks lalu validasi wajib gagal; perilaku aman, hanya pesannya kurang rapi. Belum diverifikasi.
- Fix: Tahap 3c, bersihkan tag dari pesan di `api.js` memakai `DOMParser.parseFromString().body.textContent` (commit feat/web-tahap-3c).

### 2026-10-02 — Buka Kembali meninggalkan cap waktu lama (TEMUAN, Desk, belum diputuskan)
- Gejala (terlihat): setelah Buka Kembali, status Baru tetapi "Selesai Pada" dan "Direspon Pada" masih terisi.
- Dari kode (belum diuji setelah Buka Kembali): `update_timestamps` hanya mengisi `resolved_on`/`closed_on` jika kosong, dan transisi Baru -> Sedang Dikerjakan menghitung ulang SLA dari awal serta menimpa `responded_on`.
- Detail dan pilihan: `docs/TEMUAN_SLA_2026-10-02.md`.

## Titik Rawan yang Perlu Diuji Tiap Tahap

| Area | Cek |
|---|---|
| Izin | Requester tidak bisa membaca tiket orang lain; Guest dialihkan ke login |
| Workflow | Perubahan status lewat `apply_workflow`, bukan set field |
| Side-effect | SLA dan notifikasi Telegram terpicu dari tiket buatan portal |
| Cache | Setelah ubah CSS/JS: `bench build --app nexthd`, **naikkan `?v=` di semua html yang memuatnya**, hard refresh |
| Aset | Cek `curl -I /assets/nexthd/css/...` harus 200 bila halaman tampil polos |
| POST nyata | Satu POST sungguhan (buat tiket) di site, bukan hanya baca kode |
| Layout | Isi tabel dengan teks panjang dan email panjang, lihat di browser |
| Web Form | Uji di browser (Incognito untuk cek login), bukan hanya `published: 1` di console; ubah DB dan fixture `web_form.json` sekaligus |
| Dropdown Link Web Form | `get_link_options` tidak peka izin per-user; pakai endpoint sendiri bila perlu filter per user |
| Skrip inline | Tunggu `DOMContentLoaded` bila `api.js`/`ui.js` dimuat `defer` |
