# NextHD — Catatan: Template Atribut Asset

> Catatan sementara. Setelah dipindahkan ke `SUMMARY.md` dan `POLA_KERJA_DAN_BUG.md`,
> file ini boleh dihapus.
>
> **Dibuat:** 2026-10-10 | **Diperbarui:** 2026-10-10 (sore, setelah data lama dirapikan)

---

## Keputusan

- Komponen (RAM, PSU, SSD) **tidak dijadikan Asset sendiri**; tetap atribut di Asset induk.
- Semua nilai atribut **diisi bebas (teks)**, tanpa dropdown, termasuk Socket CPU (LGA).
- **RAM dan Storage satu baris per keping/disk**, nilai gabungan (mis. `SSD SATA 512 GB`,
  `DDR3 8 GB`). Menambah disk = Add row, nama `Storage`.
- `NextHD Asset Relationship` dipakai untuk relasi antar-aset, bukan komponen.

## Sudah Selesai

| Item | Bukti |
|---|---|
| DocType `NextHD Asset Category Attribute` + `attribute_template` | Commit `ba5dfc6` |
| Template 6 kategori (semua tipe Teks) | PC/Server 9, Laptop 5, Monitor/Printer/Network 3 |
| Handler JS ganti atribut saat kategori berubah (`nexthd_asset.js`) | Commit `78f8b59`, diuji |
| Lebar kolom grid atribut, `attribute_value` tidak wajib | Commit `8726605` dst |
| Form Asset dua kolom (`kolom_kanan_info`) | Diverifikasi di form |
| Perapian data lama 11 aset | Diverifikasi lewat query, 10 Okt 2026 |

## Perapian Data Lama (Ringkas)

Tiga skrip dijalankan berurutan: `rapikan_atribut.py` (pemetaan nama), `gabung_storage_ram.py`
(RAM/Storage satu baris), `perbaiki_storage.py` (koreksi 3 aset dua-disk). Backup sebelum
tahap gabung: `20261010_162742-desk_ciptamebel_co_id-database.sql.gz`.

**Pelajaran:** data disk ganda lama tersimpan berurutan Jenis, Jenis, Kapasitas, Kapasitas
(bukan berpasangan), sehingga penggabungan otomatis salah untuk 3 aset. Selalu cek teliti
output preview sebelum apply.

## Pending

1. `nexthd/api.py` (Reset Data Demo ikut menghapus `NextHD Asset Relationship`, prefix `REL-`)
   dan `nexthd/workspace_sidebar/nexthd.json` berstatus modified di server, belum di-diff
   atau di-commit. Jangan `git add -A`.
2. Template atribut adalah data database, bukan file repo. Server baru perlu mengisi ulang;
   skrip `isi_template_atribut.py` versi lama sudah usang (masih Jenis/Tipe terpisah).
3. Pindahkan isi catatan ini ke `SUMMARY.md` dan `POLA_KERJA_DAN_BUG.md`.

## Catatan Eksekusi

- `bench restart` meminta password sudo, jalankan di akhir blok atau terpisah.
- DocType via script: `naming_rule = 'By fieldname'` bila `autoname = field:...`.
- Heredoc JS bertab di terminal memicu tab-completion (hanya tampilan, isi file aman).
- `node --check` menolak ekstensi selain `.js`; gunakan nama sementara berakhiran `.js`.
