# NextHD — Catatan Lanjutan: Template Atribut Asset

> Catatan sementara agar pekerjaan bisa dilanjutkan. Setelah semua item di bawah
> terverifikasi di repo/server, isinya dipindahkan ke `SUMMARY.md` dan
> `POLA_KERJA_DAN_BUG.md`, lalu file ini boleh dihapus.
>
> **Dibuat:** 2026-10-10 (hari ini; jam menyusul)

---

## Keputusan

- Komponen (RAM, PSU, SSD) **tidak dijadikan Asset sendiri**. Tetap sebagai atribut di
  Asset induk, hanya dirapikan penamaannya.
- `NextHD Asset Relationship` dipakai untuk relasi antar-aset (aplikasi di server,
  server ke switch), bukan untuk komponen.
- Atribut bertipe Pilihan (dropdown) didukung di template. Grid Frappe tidak mendukung
  dropdown per baris, jadi validasi server yang menjaga nilainya.

## Sudah Selesai (terverifikasi di server)

| Item | Bukti |
|---|---|
| DocType child `NextHD Asset Category Attribute` + field `attribute_template` di `NextHD Asset Category` | Commit `ba5dfc6` di `main` |
| Template terisi di 6 kategori | PC 11, Server 11, Laptop 7, Monitor 3, Printer 3, Network Device 3 |
| Bug `naming_rule` kategori | Diperbaiki ke `By fieldname` |

## Pending (cek repo/server dulu sebelum lanjut, sebagian mungkin sudah selesai)

1. **Pengisian otomatis atribut di form Asset** — saat `asset_category` dipilih, baris
   `asset_attributes` terisi dari template tanpa menimpa/menggandakan baris yang ada.
   Handler JS ditambahkan di akhir `nexthd_asset.js`.
2. **Validasi server di `nexthd_asset.py`** — nilai atribut Pilihan harus ada di daftar,
   Angka harus numerik, atribut wajib tidak boleh kosong.
3. **Perapian data lama (6 aset)** — daftar eksplisit per aset, mode preview dulu.
   Nama ganda: RAM/Memory/Ram, PSU/Power Supply, CPU/Processor, Storage/HDD/Harddisk.
   Nilai gabungan (mis. "512 GB SSD + 4 TB HDD") dipecah, satu baris per disk.
4. **Patch `nexthd/api.py`** — Reset Data Demo ikut menghapus `NextHD Asset Relationship`
   (prefix `REL-`). Hasil patch belum terkonfirmasi.
5. Commit hasilnya dengan path eksplisit (`git add` per folder), bukan `git add -A`.

## Catatan Eksekusi

- `bench restart` meminta password sudo — jalankan sebagai perintah terpisah.
- DocType yang dibuat lewat script wajib `naming_rule = 'By fieldname'` bila
  `autoname = field:...`.
