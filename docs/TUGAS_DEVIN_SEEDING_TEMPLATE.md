# TUGAS DEVIN — Seeding Template Atribut Asset untuk Instalasi Baru

> **Dibuat:** 2026-10-11 | **Pemberi tugas:** Efendy | **Penyusun spesifikasi:** Claude
> **Wajib baca dulu:** `docs/FAQ_DEVELOPER.md`, `docs/ASET_ATRIBUT.md`

---

## 1. Latar Belakang

Template atribut per kategori Asset (`NextHD Asset Category` + child table `attribute_template`,
DocType `NextHD Asset Category Attribute`) saat ini hanya ada sebagai **data di database
produksi**, diisi lewat skrip manual. Server baru, atau database yang dikosongkan, tidak punya
template, sehingga form Asset tidak mengisi atribut otomatis saat kategori dipilih.

## 2. Tujuan

Template standar terisi otomatis lewat **patch** (untuk site yang sudah ada) dan **install.py**
(untuk instalasi baru), tanpa menimpa template yang sudah diubah pengguna.

## 3. Data yang Diisi (6 Kategori)

Semua atribut: `field_type = "Teks"`, `options` kosong, `is_required = 0`.

| Kategori | Atribut (urut) | Unit |
|---|---|---|
| PC | Brand, Processor, Socket CPU, Motherboard, RAM, Storage, PSU, Casing, OS | — |
| Server | sama dengan PC | — |
| Laptop | Brand, Processor, RAM, Storage, OS | — |
| Monitor | Brand, Ukuran, Resolusi | Ukuran: `inci` |
| Printer | Brand, Tipe, IP Address | — |
| Network Device | Brand, Tipe, IP Address | — |

## 4. Perilaku yang Diminta

1. **Idempoten:** aman dijalankan berkali-kali.
2. Kategori belum ada: buat (`category_name` saja).
3. Kategori ada dan `attribute_template` **sudah berisi baris**: **jangan diubah sama sekali.**
4. Kategori ada dan `attribute_template` kosong: isi dengan daftar di atas.
5. Kategori selain enam di atas: **jangan disentuh.**
6. Cetak ringkasan per kategori: `dibuat`, `diisi`, atau `dilewati (sudah ada template)`.

## 5. Implementasi

- Patch baru di `nexthd/patches/`, didaftarkan di `nexthd/patches.txt`. **Ikuti pola patch yang
  sudah ada** (contoh: `migrate_asset_location` dari PR #24).
- Daftar template ditaruh sebagai konstanta di satu tempat (mis. `nexthd/next_helpdesk/utils/`),
  dipakai bersama oleh patch dan `install.py` supaya tidak ada dua sumber kebenaran.
- `install.py` memanggil fungsi yang sama setelah instalasi.
- Gunakan API dokumen standar (`frappe.get_doc(...).insert()` / `.save()`), bukan SQL mentah.

## 6. Batasan (WAJIB)

- Jangan ubah navigasi, sidebar, Workspace, Desktop Icon, `hooks.py` bagian fixtures.
- Jangan ubah struktur DocType (field, naming) kecuali diperlukan secara eksplisit.
- Jangan rapikan hal lain "sekalian" di PR yang sama (lihat `FAQ_DEVELOPER.md` Q7).
- Tidak menambah dependency baru.
- Jangan menjalankan perubahan di server produksi; hasil kerja berupa PR.

## 7. Pengujian

1. Site kosong + `bench migrate`: 6 kategori terbuat dan terisi; jumlah atribut sesuai tabel.
2. Jalankan patch kedua kali: tidak ada perubahan, semua `dilewati`.
3. Kategori yang template-nya sudah diedit manual tidak berubah.
4. Test otomatis untuk fungsi seeding (idempoten dan tidak menimpa).

## 8. Di Luar Lingkup

`test_nexthd_asset.py` (item W2) dan audit `naming_rule` DocType baru dikerjakan terpisah.

## 9. Catatan untuk Reviewer (Claude/Efendy)

Setelah merge: `git pull`, `bench migrate`, `bench restart`. Pada server produksi yang template-nya
sudah terisi, patch harus mencetak `dilewati` untuk semua kategori.
