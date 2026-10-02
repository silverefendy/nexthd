# Review Tahap 3 (branch `feat/web-tahap-3`)

> 1 Okt 2026. Dasar: membaca `portal.py` dan `tiket.js` langsung dari branch.
> Putaran 1: commit `489e53a`. Putaran 2: commit `8ccf4e0`.

## Putaran 2: status temuan putaran 1 (diverifikasi dari kode, bukan laporan)

| # | Temuan | Status |
|---|---|---|
| 1 | `page_guard` memakai `query_string` (bytes) | Selesai: kini `full_path`. Catatan: tanpa query, hasilnya berakhiran `?` (`%3F` di URL login), tidak merusak |
| 2 | `question` divalidasi sebelum `apply_workflow` | Selesai |
| 3 | Kunci kosong dan `"null"` | Selesai di JS (kunci tidak dikirim) dan server |
| 4 | Waiting Log lewat `get_all(parent_doctype=...)` | Selesai di kode. Belum terbukti di site |
| 5 | Pencarian aset dan pengguna di `name` dan `asset_name`/`full_name` | Selesai di kode. Belum terbukti di site |
| 6 | `get_ticket_actions` hanya `action` dan `next_state` | Selesai |
| 7 | Keputusan worklog pada status `Selesai` | Masih ditolak untuk `Selesai` dan `Ditutup`, menunggu keputusan Efendy |
| 8 | Tombol dinonaktifkan, kotak isian pengganti `prompt` | Belum |
| 9 | Pemanggilan ganda `get_ticket` | Selesai (endpoint hanya mengembalikan `status`) |

## Bug baru ditemukan putaran 2

- `tiket.js`: `loadActions()` memanggil `loadItUsers()` (asinkron) lalu langsung `renderActions()`. Saat render pertama `itUsers` masih kosong, jadi dropdown "Tugaskan ke" tidak muncul sampai halaman dimuat ulang. Perbaikan: render setelah `list_it_users` selesai.

## Belum dikerjakan

- Tes di `test_portal.py` (Devin tidak punya site, diakui jujur).
- Perbaikan 2b sisa: lebar kolom Subjek, dropdown Kategori/Tim, penyelidikan kolom Kategori `-`, uji XSS.

## Keputusan

Kode statis lolos. Perilaku runtime belum terbukti oleh siapa pun. Uji dilakukan Efendy di `erpnext` setelah backup, dengan satu tiket uji. Temuan 7, 8, bug dropdown, tes, dan 2b masuk Tahap 3b.
