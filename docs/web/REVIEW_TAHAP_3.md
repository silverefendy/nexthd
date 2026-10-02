# Review Tahap 3 (branch `feat/web-tahap-3`)

> 2 Okt 2026. Dasar: membaca file langsung dari `origin/feat/web-tahap-3`.
> Putaran 1: `489e53a`. Putaran 2: `8ccf4e0`. Putaran 3: `8d61bef` (pesan commit hanya "test").

## Putaran 3: laporan Devin vs isi branch

Commit teratas branch dikonfirmasi `8d61bef` lewat API GitHub. File dibaca dari commit itu.

| Klaim di laporan Devin | Yang terbaca di branch | Status |
|---|---|---|
| A: CSRF dipertahankan | `getCsrfToken`/`csrf_token` ada (patch dari server sudah di `main`, `44ef6b4`) | Benar |
| B1: bug urutan dropdown "Tugaskan ke" diperbaiki | `tiket.js`: `loadActions()` masih memanggil `loadItUsers()` tanpa menunggu lalu langsung `renderActions()` | Tidak ditemukan |
| B2: tombol dinonaktifkan saat permintaan | Hanya tombol "Simpan" worklog. Tombol aksi workflow, "Ambil untuk saya", dan "Tugaskan" tidak | Sebagian |
| B3: `prompt()` diganti kotak isian | `tiket.js` masih memakai `prompt("Masukkan pertanyaan untuk user:")` | Tidak ditemukan |
| B4: worklog hanya ditolak pada `Ditutup` | `portal.py` masih menolak `Selesai` dan `Ditutup`, tanpa konstanta. Laporan tidak menyebut B4 | Tidak dikerjakan |
| C2: field Tim jadi `<select>` | `tiket-baru.js`: Tim masih `createLinkField` (kotak teks, placeholder "Cari NextHD Team..."). `get_ticket_options` tidak mengirim daftar tim | Tidak ditemukan |
| C: kolom Kategori "data issue" | `list_tickets` mengirim `category`. Perlu cek data, lihat skrip di bawah | Belum terbukti |
| D: 9 tes dengan `IntegrationTestCase`, termasuk tes csrf | `test_portal.py`: masih `FrappeTestCase`, mayoritas tes hanya `pass`, tidak ada tes csrf, tidak ada tes endpoint Tahap 3 | Tidak ditemukan |
| Hitungan baris bertab: portal 507, test 262, tiket.js 546 | Isi file yang terbaca jauh lebih pendek dari angka itu | Tidak cocok |

Kemungkinan: perubahan hanya ada di salinan lokal Devin dan belum ter-push. Belum bisa dipastikan dari sisi saya.

Yang benar dan sudah ada: perbaikan 1 sampai 6 putaran 1 tetap utuh, `get_ticket_actions` hanya mengirim `action` dan `next_state`, pencarian aset/pengguna di dua kolom, versi aset dinaikkan, BOM `.html` hilang (menurut laporan; file `.html` tidak saya baca).

## Cek kode statis lain

- `portal.py` Tahap 3 secara logika tidak berubah dari putaran 2 dan tetap sesuai spesifikasi. Belum ada bukti runtime untuk `do_ticket_action`, `add_worklog`, `assign_ticket`.
- Tes belum menguji satu pun endpoint baru. Kelas dasar yang benar untuk Frappe v16 belum dipastikan.

## Keputusan

Kode Tahap 3 sebagai fitur tidak berubah sejak putaran 2 dan aman diuji. Butir B1, B3, B4, C2 dan seluruh tes (D) belum dikerjakan walau dilaporkan selesai. Merge dan uji runtime boleh jalan, sisanya menjadi Tahap 3c. Pelaporan Devin tidak lagi dipercaya tanpa bukti: setiap butir harus disertai baris kode atau output mentah.
