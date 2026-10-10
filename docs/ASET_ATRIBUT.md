# NextHD — Template Atribut Asset & Perapian Data (EAV)

> Dokumen tematik untuk fitur template atribut per kategori Asset. Menggantikan
> `CATATAN_ASET_ATRIBUT.md` (catatan sementara 10 Oktober 2026).
>
> **Dibuat:** 2026-10-10 | **Status:** live, terverifikasi di server dan form

---

## 1. Keputusan Desain

| Keputusan | Alasan |
|---|---|
| Komponen (RAM, PSU, SSD) **tidak dijadikan Asset sendiri**; tetap atribut di Asset induk | Daftar aset tetap ringkas; relasi antar-aset dipakai untuk hal lain (aplikasi di server, server ke switch) |
| Semua nilai atribut **diisi bebas (teks)**, tanpa dropdown, termasuk Socket CPU | Grid Frappe tidak mendukung dropdown per baris; keputusan Efendy 10 Oktober |
| **RAM dan Storage satu baris per keping/disk**, nilai gabungan (`SSD SATA 512 GB`, `DDR3 8 GB`) | Disk/keping ganda cukup tambah baris; jelas disk mana yang mana |

## 2. Struktur

| Komponen | Keterangan |
|---|---|
| Child DocType `NextHD Asset Category Attribute` (parent: `NextHD Asset Category`) | Field: `attribute_name`, `field_type`, `options`, `unit`, `is_required`. Commit `ba5dfc6`. Semua `field_type` kini `Teks` |
| Field `attribute_template` (Table) di `NextHD Asset Category` | Daftar atribut standar per kategori |
| Handler JS di `nexthd_asset.js` (commit `78f8b59`) | Saat `asset_category` berubah: baris kosong milik kategori lama dibuang, baris berisi dipertahankan, atribut template baru ditambahkan |
| Grid `NextHD Asset Attribute` | Kolom Nama 3, Nilai 2, lainnya 1; `attribute_value` tidak wajib (commit `8726605`, `3b86321`) |
| Form Asset dua kolom | Column Break `kolom_kanan_info` setelah `assigned_to` |

**Template per kategori:** PC dan Server 9 atribut (Brand, Processor, Socket CPU, Motherboard,
RAM, Storage, PSU, Casing, OS), Laptop 5 (Brand, Processor, RAM, Storage, OS), Monitor 3 (Brand,
Ukuran, Resolusi), Printer 3 dan Network Device 3 (Brand, Tipe, IP Address).

> ⚠️ **Template adalah DATA di database, bukan file repo.** Server baru atau database kosong
> tidak punya template sampai diisi ulang. Reset Data Demo mempertahankan master Category,
> tetapi instalasi baru tidak. Perlu patch/seeding (lihat §5).

## 3. Perapian Data Lama (10 Oktober 2026)

11 aset dirapikan lewat tiga skrip berurutan (di server, `/home/it/`): `rapikan_atribut.py`
(pemetaan nama: CPU→Processor, Power Supply→PSU, dst, RAM/Storage dipecah), `gabung_storage_ram.py`
(RAM/Storage satu baris per item, template digabung dan tipe Pilihan diubah ke Teks), dan
`perbaiki_storage.py` (koreksi 3 aset dua-disk). Backup sebelum tahap gabung:
`20261010_162742-desk_ciptamebel_co_id-database.sql.gz`. Hasil diverifikasi lewat query.

## 4. Pelajaran Teknis

1. **Atribut `attribute_value` wajib membuat penyimpanan gagal.** Baris template yang belum
   diisi tidak lolos validasi; field dibuat tidak wajib, kewajiban per atribut ada di
   `is_required` template.
2. **Urutan disk ganda di data lama bukan berpasangan** (Jenis, Jenis, Kapasitas, Kapasitas),
   sehingga penggabungan otomatis salah untuk 3 aset (Server Data, PRTG Networking, Server PLTB).
   Dikoreksi dengan skrip eksplisit per aset. **Preview wajib dicek teliti sebelum apply**;
   backup dibuat sebelum apply, perbaikan dilakukan maju (bukan restore) agar isian manual
   setelah backup tidak hilang.
3. **`naming_rule` DocType buatan skrip** harus `By fieldname` bila `autoname = field:...`
   (nilai `By Field Name` ditolak). Skrip pembuat struktur memeriksanya dan berhenti bila tidak cocok.
4. **Heredoc JS bertab di terminal** memicu tab-completion (hanya tampilan; isi file aman).
   `node --check` menolak ekstensi selain `.js`, jadi gunakan nama sementara berakhiran `.js`.
5. **`bench restart` meminta password sudo**; jalankan di akhir blok atau terpisah agar paste
   berikutnya tidak terbaca sebagai password.

## 5. Sisa Pekerjaan

| # | Item | Catatan |
|---|---|---|
| 1 | Seeding template untuk instalasi baru | Spesifikasi untuk Devin: patch/`install.py` mengisi 6 kategori di atas |
| 2 | `test_nexthd_asset.py` usang (item W2) | Masih meng-assert field lama |
| 3 | Audit `naming_rule` DocType baru | `NextHD Asset Relationship`, `NextHD Asset Category Attribute` |
| 4 | Isi manual Socket CPU, Motherboard, Casing | Oleh Efendy, bertahap |
| 5 | Label sidebar relasi (`Nexthd Asset Relation`) | Opsional, ganti lewat Edit Sidebar |

## 6. Relasi Aset (CMDB Tahap 1)

DocType `NextHD Asset Relationship` (commit `711015f`), dashboard "Relasi" di form Asset via
`get_dashboard_data()` (`fieldname: source_asset`, commit `9667175`), item sidebar (commit
`d7570f7`), dan ikut dihapus oleh Reset Data Demo beserta prefix `REL-` (commit `5a2ff61`).
Isi relasi adalah data (tidak ikut fixture). Rincian field dokumen ini belum ditulis; sumbernya
file `nexthd_asset_relationship.json` di repo.
