# NextHD — Lokasi & Pengguna Aset, Web Form Aset Terdampak (Sesi 8 Oktober 2026)

> Catatan sesi 8 Oktober 2026 (WIB). Menyangkut PR #24, PR #25, dan perbaikan Web Form `/tiket-saya`.
> **Last updated:** 2026-10-09

---

## 1. Fitur

| Komponen | Isi | Status |
|---|---|---|
| DocType `NextHD Location` | Master lokasi, field `location` di Asset kini Link (Pabrik CML = 7, Sena = 1, kosong = 2) | ✅ Live |
| DocType `NextHD Asset User` | Child table `asset_users` di Asset (daftar Pengguna Aset) | ✅ Live |
| `utils/aset_izin.py` | Izin baca aset: assigned_to atau terdaftar di Pengguna Aset | ✅ Live |
| `utils/aset_filter.py` | `get_asset_list_for_ticket` (dropdown Desk) + `get_my_assets` (Web Form) | ✅ Live |
| Web Form `Tiket Saya` | Field `affected_asset` tampil (label "Aset Terdampak"), diisi lewat client script | ✅ Live, commit `d583cd4` |

Commit terkait: `c612248` (controller, id.csv, format dropdown), `d583cd4` (`get_my_assets` + fixture Web Form).

## 2. Bug dan Perbaikan

| # | Masalah | Root cause | Fix |
|---|---|---|---|
| 1 | `bench migrate` gagal `ImportError: NextHD Location` | Controller DocType baru tidak punya class | Tambah `class NextHDLocation(Document)` dan `class NextHDAssetUser(Document)` |
| 2 | `id.csv` tidak terbaca | File di `next_helpdesk/translations/` (salah tempat) | Pindah ke `nexthd/translations/id.csv`, format `"Source","Terjemahan"` tanpa header |
| 3 | Dropdown Desk `KeyError(0)` | Query Link mengembalikan dict | Kembalikan list tuple `(value, label)` |
| 4 | Pencarian teks mode "semua aset" kosong | `filters` dan `or_filters` berisi kondisi sama | Cukup `or_filters` |
| 5 | Aset Terdampak kosong di Web Form | `get_link_options` memfilter `owner` saat `login_required=1`, mengabaikan `aset_izin.py` | Endpoint `get_my_assets` + client script (lihat §3) |

## 3. Pelajaran Web Form v16

- Web Form merender field Link sebagai kontrol **Autocomplete** (awesomplete), bukan Select.
- Mengganti `df.fieldtype` dari browser TIDAK membangun ulang kontrol. Yang bekerja: isi `df.options` dengan array `{value, label}` dan `set_data` / `awesomplete.list`.
- `after_load` tidak terpanggil otomatis (tidak ada request saat halaman dibuka). Solusi: IIFE dengan percobaan ulang `setTimeout` (300 ms, maks 30 kali) sampai `get_field("affected_asset")` tersedia.
- Nilai yang tersimpan di tiket adalah `name` aset (`AST-2610-0002`), bukan label. Terverifikasi di `TKT-2610-0009`.
- `get_link_options` dengan `login_required=1` hanya memuat record yang dimiliki (`owner`) user itu. Jangan pakai `allow_read_on_all_link_options=1` (membocorkan data) dan jangan beri izin baca Requester ke Category/Team.
- Field Web Form bisa `hidden=1` secara diam-diam di database.
- Client script disimpan di field `client_script` Web Form (fixture `web_form.json`). `export-fixtures` Web Form menghapus baris `idx` per field; urutan field mengikuti urutan array (perlu dicek visual, belum terbukti bermasalah).

## 4. Aturan Teknis Baru

- DocType baru wajib punya class controller, kalau tidak `migrate` gagal `ImportError`.
- Query Link kustom harus mengembalikan list tuple, bukan dict.
- Script JS yang dipasang lewat Python ditulis ke file `.js` terpisah lalu dibaca (`open().read()`), supaya tidak ada masalah escaping `\n` di dalam string Python.

## 5. Hasil Uji (8 Oktober 2026)

| Uji | Hasil |
|---|---|
| maymunah (pengguna printer) melihat `Printer HP 3110 (AST-2610-0002)` di Web Form | ✅ |
| Submit tiket dari Web Form, `affected_asset` tersimpan benar | ✅ `TKT-2610-0009` |
| User tanpa aset (`maya.pltb@`) mendapat dropdown kosong | ✅ |
| rika.suhari (pengguna printer) | ⬜ Belum diuji |
| Urutan field Web Form setelah export fixture | ⬜ Belum dicek visual |

## 6. Pending

1. Kolom tambahan tabel Pengguna Aset: `bagian`, `kontak` (otomatis dari `NextHD User Profile`), `keterangan`, `tanggal_mulai`, `pengguna_utama`.
2. Uji rika.suhari dan cek urutan field Web Form.
3. 2 aset tanpa lokasi.
4. Item lama: rename Module "Next Helpdesk" → "NextHD" (EE).
5. Sinkronkan `docs/ARSITEKTUR.md` dan `docs/SUMMARY.md` dengan fitur Lokasi/Pengguna Aset.
