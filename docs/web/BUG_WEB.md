# NextHD Web — Riwayat Bug Portal

> Khusus bug portal web (`www/nexthd`, `public/*/nexthd*`, `api/portal.py`).
> Bug Desk/DocType/workflow ada di `docs/BUG_HISTORY.md` dan file terkait.
>
> **Last updated:** 2026-10-06

## Format Entri

```
### YYYY-MM-DD — judul singkat
- Gejala:
- Root cause:
- Fix:
- Pelajaran:
```

## Riwayat

### 2026-10-06 — `?v=` aset belum dinaikkan setelah A1 dan B1 (TERBUKA, skrip patch disiapkan)
- Gejala: belum ada keluhan; ditemukan saat review. `www/nexthd/*.html` masih memuat `ui.js?v=3`, `layout.css?v=2`, `kerja.js?v=3`, dst. Pengguna yang pernah membuka portal bisa tetap memakai `ui.js`/`layout.css` lama (tanpa dropdown) sampai cache habis; uji Efendy lolos karena hard refresh.
- Root cause: perubahan `.js`/`.css` tidak diikuti penaikan parameter versi di html.
- Fix: skrip patch menaikkan semua `?v=` aset `/assets/nexthd/(css|js)/nexthd/...` di `www/nexthd/*.html` sebanyak 1 (landing `nexthd_landing.*` tidak tersentuh).
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

### 2026-10-06 — Angka `view=unassigned` dan `view=mine` ikut tiket Selesai/Ditutup (TEMUAN, menunggu keputusan #9)
- Gejala: tab "Belum ditugaskan" di antrian ikut menampilkan tiket Selesai/Ditutup yang tidak punya penanggung jawab; `view=mine` menampilkan semua tiket milik user sepanjang waktu.
- Dampak: kartu dashboard "Belum ditugaskan" akan menyesatkan jika memakai filter yang sama. Rencana: `unassigned` hanya tiket aktif (Tahap 4); `mine` tidak diubah, tidak ada kartu "Ditugaskan ke saya".

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
