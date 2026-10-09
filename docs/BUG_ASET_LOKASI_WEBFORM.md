# NextHD — Lokasi & Pengguna Aset, Web Form Aset Terdampak (Sesi 8–9 Oktober 2026)

> Catatan sesi 8–9 Oktober 2026 (WIB). Menyangkut PR #24, PR #25, perbaikan Web Form `/tiket-saya`, kolom Pengguna Aset, dan sinkron data dari User Frappe.
> **Last updated:** 2026-10-09 16:30 WIB (koreksi §4: urutan kontak `mobile_no` dulu; commit `80cfcc0`)

---

## 1. Fitur

| Komponen | Isi | Status |
|---|---|---|
| DocType `NextHD Location` | Master lokasi, field `location` di Asset kini Link (Pabrik CML = 7, Sena = 1, kosong = 2) | ✅ Live |
| DocType `NextHD Asset User` | Child table `asset_users` di Asset (daftar Pengguna Aset), 6 kolom: User, Bagian, Kontak, Pengguna Utama, Tanggal Mulai, Keterangan | ✅ Live, commit `c2f29fc` |
| `utils/aset_izin.py` | Izin baca aset: assigned_to atau terdaftar di Pengguna Aset | ✅ Live |
| `utils/aset_filter.py` | `get_asset_list_for_ticket` (dropdown Desk) + `get_my_assets` (Web Form) | ✅ Live |
| Web Form `Tiket Saya` | Field `affected_asset` tampil (label "Aset Terdampak"), diisi lewat client script | ✅ Live, commit `d583cd4` |
| Bagian dan Kontak otomatis dari User Frappe | Custom Field `department` di User + helper `pengguna_aset_sync.py` + hook `User.on_update` | ✅ Live, commit `766feaf`; urutan kontak diubah di `80cfcc0` |

Commit terkait: `c612248` (controller, id.csv, format dropdown), `d583cd4` (`get_my_assets` + fixture Web Form), `c2f29fc` (kolom Pengguna Aset), `766feaf` (sinkron dari User), `80cfcc0` (kontak: `mobile_no` dulu, `phone` cadangan).

## 2. Bug dan Perbaikan

| # | Masalah | Root cause | Fix |
|---|---|---|---|
| 1 | `bench migrate` gagal `ImportError: NextHD Location` | Controller DocType baru tidak punya class | Tambah `class NextHDLocation(Document)` dan `class NextHDAssetUser(Document)` |
| 2 | `id.csv` tidak terbaca | File di `next_helpdesk/translations/` (salah tempat) | Pindah ke `nexthd/translations/id.csv`, format `"Source","Terjemahan"` tanpa header |
| 3 | Dropdown Desk `KeyError(0)` | Query Link mengembalikan dict | Kembalikan list tuple `(value, label)` |
| 4 | Pencarian teks mode "semua aset" kosong | `filters` dan `or_filters` berisi kondisi sama | Cukup `or_filters` |
| 5 | Aset Terdampak kosong di Web Form | `get_link_options` memfilter `owner` saat `login_required=1`, mengabaikan `aset_izin.py` | Endpoint `get_my_assets` + client script (lihat §3) |
| 6 | Bagian/Kontak Pengguna Aset kosong setelah kolom ditambah | (a) `NextHD User Profile` pengguna belum ada; (b) `validate` aset tidak jalan kalau form tidak berubah (Frappe tidak menyimpan dokumen tanpa perubahan) | Data ditarik dari User Frappe; simpan aset memicu `isi_info_pengguna()`; ubah User memicu hook sinkron |

## 3. Pelajaran Web Form v16

- Web Form merender field Link sebagai kontrol **Autocomplete** (awesomplete), bukan Select.
- Mengganti `df.fieldtype` dari browser TIDAK membangun ulang kontrol. Yang bekerja: isi `df.options` dengan array `{value, label}` dan `set_data` / `awesomplete.list`.
- `after_load` tidak terpanggil otomatis. Solusi: IIFE dengan percobaan ulang `setTimeout` (300 ms, maks 30 kali) sampai `get_field("affected_asset")` tersedia.
- Nilai yang tersimpan di tiket adalah `name` aset (`AST-2610-0002`), bukan label. Terverifikasi di `TKT-2610-0009`.
- `get_link_options` dengan `login_required=1` hanya memuat record milik (`owner`) user itu. Jangan pakai `allow_read_on_all_link_options=1` dan jangan beri izin baca Requester ke Category/Team.
- Field Web Form bisa `hidden=1` secara diam-diam di database.
- `export-fixtures` Web Form menghapus baris `idx` per field; urutan mengikuti urutan array.

## 4. Sumber Data Bagian dan Kontak (Keputusan 9 Oktober)

| Data | Sumber | Catatan |
|---|---|---|
| Bagian | `User.department` (Custom Field baru, label "Departemen", setelah `location`) | Fixture `custom_field.json`, filter `dt=User` dan `fieldname=department` di `hooks.py` |
| Kontak | `User.mobile_no` dulu, cadangan `User.phone` | Keputusan Efendy 9 Oktober ("semua sudah pakai mobile"), commit `80cfcc0`. Kalau hanya salah satu yang diisi, itu yang tampil. (Versi awal commit `766feaf` memakai `phone` dulu — sudah tidak berlaku.) |

Mekanisme:
- `ambil_info_user(user)` di `utils/pengguna_aset_sync.py` mengembalikan `(bagian, kontak)`.
- `NextHDAsset.validate` -> `isi_info_pengguna()` mengisi tiap baris Pengguna Aset saat aset disimpan.
- Hook `User.on_update` -> `sync_pengguna_aset` memperbarui `bagian` dan `kontak` di semua baris `tabNextHD Asset User` milik user itu (SQL UPDATE langsung, tanpa membuka aset).
- Ini tetap **salinan**, bukan link live: `fetch_from` pun bersifat salinan. Hook membuat salinan itu ikut diperbarui.
- Field `department` dan `phone_internal` di `NextHD User Profile` **belum dihapus** (Tahap 6 ditunda); nilainya tidak lagi dipakai untuk Pengguna Aset.

## 5. Aturan Teknis Baru

- DocType baru wajib punya class controller, kalau tidak `migrate` gagal `ImportError`.
- Query Link kustom harus mengembalikan list tuple, bukan dict.
- Script JS yang dipasang lewat Python ditulis ke file `.js` terpisah lalu dibaca (`open().read()`), supaya tidak ada masalah escaping `\n`.
- `validate` pada child table tidak dijamin terpanggil saat parent disimpan; isi data turunan child di controller parent. (Belum dibuktikan apakah v16 memanggilnya otomatis; dihindari dengan mengisi dari controller parent.)
- Sebelum `git push`, kalau ada commit dokumentasi dari sisi lain, `git pull` dulu (push ditolak `fetch first`).
- Pesan `cleanup_old_syncs is not a valid method` saat migrate berasal dari Frappe, abaikan.

## 6. Hasil Uji (8–9 Oktober 2026)

| Uji | Hasil |
|---|---|
| maymunah melihat `Printer HP 3110 (AST-2610-0002)` di Web Form | ✅ |
| Submit tiket dari Web Form, `affected_asset` tersimpan benar | ✅ `TKT-2610-0009` |
| User tanpa aset (`maya.pltb@`) mendapat dropdown kosong | ✅ |
| Ubah Departemen User maymunah, Bagian di aset ikut berubah tanpa menyimpan aset | ✅ |
| Kontak diambil dari User (`phone` pada uji awal; kini `mobile_no` dulu) | ✅ |
| Isi data User rika, baris rika di aset ikut terisi | ✅ |
| Dropdown Web Form masih berfungsi setelah perubahan | ✅ |
| Urutan field Web Form setelah export fixture | ✅ Normal secara visual (screenshot). Belum dicek ulang setelah `migrate` berikutnya |
| Aset bersama untuk rika.suhari di Web Form | ⬜ Belum diuji eksplisit (datanya sudah terisi di aset) |

## 7. Pending

1. Tahap 6 (opsional, setelah stabil beberapa hari): hapus `department` dan `phone_internal` dari `NextHD User Profile`.
2. Isi Departemen dan HP/Telepon untuk user lain di User Frappe (Efendy).
3. 2 aset tanpa lokasi (Efendy akan cek).
4. Uji aset bersama untuk rika.suhari di Web Form.
5. Item lama: DD (`Link Type` kosong di Workspace Link "Reporting Data" — di `SUMMARY.md` sudah tercatat selesai 29 Agustus, verifikasi ulang kalau perlu), EE (rename Module "Next Helpdesk" menjadi "NextHD").
6. Sinkronisasi dokumen: `SUMMARY.md` dan `DAFTAR_FITUR.md` ✅ diperbarui 9 Oktober 16:30 WIB; `ARSITEKTUR.md` (§3 Asset, DocType baru, Custom Field `department`), `POLA_KERJA.md` dan `BUG_HISTORY.md` masih menyusul.
