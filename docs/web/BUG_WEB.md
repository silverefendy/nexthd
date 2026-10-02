# NextHD Web — Riwayat Bug Portal

> Khusus bug portal web (`www/nexthd`, `public/*/nexthd*`, `api/portal.py`).
> Bug Desk/DocType/workflow ada di `docs/BUG_HISTORY.md` dan file terkait.
>
> **Last updated:** 2026-10-02

## Format Entri

```
### YYYY-MM-DD — judul singkat
- Gejala:
- Root cause:
- Fix:
- Pelajaran:
```

## Riwayat

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

### 2026-10-02 — Pesan galat memuat tag HTML (BELUM DIPERBAIKI, kosmetik)
- Gejala: toast menampilkan `Error: <strong>NextHD Ticket Worklog</strong> Row #1: Value missing for: Aktivitas` saat catatan hanya berisi satu tag HTML (isi dibuang sanitasi sehingga kosong).
- Dugaan: Frappe membuang tag dari kolom teks lalu validasi wajib gagal; perilaku aman, hanya pesannya kurang rapi. Belum diverifikasi.
- Rencana: Tahap 3c, bersihkan tag dari pesan di `api.js`.

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
| Cache | Setelah ubah CSS/JS: `bench build --app nexthd`, naikkan `?v=`, hard refresh |
| Aset | Cek `curl -I /assets/nexthd/css/...` harus 200 bila halaman tampil polos |
| POST nyata | Satu POST sungguhan (buat tiket) di site, bukan hanya baca kode |
| Layout | Isi tabel dengan teks panjang dan email panjang, lihat di browser |
