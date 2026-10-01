# Review Tahap 3 (branch `feat/web-tahap-3`, commit `489e53a`)

> 1 Okt 2026. Dasar: membaca `portal.py` dan `tiket.js` langsung dari branch, plus laporan Devin.
> Status: BELUM BOLEH MERGE. Tes dan uji site nyata belum ada (diakui Devin).

## Sudah benar

- `WRITER_ROLES`/`MANAGER_ROLES` ada. Aturan penulis memakai irisan peran, bukan "punya IT Auditor".
- `do_ticket_action` memvalidasi aksi terhadap `get_transitions`, tidak menyisipkan baris `waiting_log` baru (hanya mengubah `question`).
- Tanpa `ignore_permissions`. Teks dari server dirender dengan `textContent`. `innerHTML` hanya untuk judul statis dan deskripsi yang sudah disanitasi.
- Sintaks, BOM, dan tab OK menurut laporan.

## Perlu diperbaiki sebelum merge

| # | Berat | Temuan | Perbaikan |
|---|---|---|---|
| 1 | Tinggi | `page_guard`: `frappe.request.query_string` bertipe bytes di Werkzeug. Untuk Guest di halaman ber-query (`/nexthd/tiket?id=...`), `str + bytes` memicu `TypeError` (500), dan pemisah `?` juga tidak ada | Pakai `frappe.request.full_path` (str, sudah memuat `?`), buang `?` di ujung bila kosong, lalu `quote()` |
| 2 | Tinggi | `do_ticket_action`: `apply_workflow` dijalankan SEBELUM `question` divalidasi. Aksi `Tunggu User` tanpa pertanyaan baru ditolak setelah status berubah (bergantung rollback) | Validasi dan sanitasi `question` sebelum `apply_workflow` |
| 3 | Tinggi (belum terbukti) | Klien mengirim `user: null`, `hasil: null`, `durasi_menit: null`. Bergantung `api.js`, nilai `null` bisa terkirim sebagai string `"null"`. Akibatnya: "Ambil untuk saya" memperlakukan `user="null"`, worklog menolak `hasil` | Di JS, jangan kirim kunci yang kosong. Di server, perlakukan `"null"` dan string kosong sebagai tidak ada |
| 4 | Sedang (belum terbukti) | `frappe.db.get_list` pada child table `NextHD Ticket Waiting Log` tanpa `parent_doctype`: Frappe v15+ bisa menolak akses child table. Juga `limit=1` perlu dipastikan didukung | Pakai `frappe.get_all(..., parent_doctype="NextHD Ticket", limit_page_length=1)` |
| 5 | Sedang | `search_assets` hanya mencari di `name` (kode `AST-2609-0001`), sehingga mencari nama aset tidak menemukan apa pun. `search_users` hanya di `name` | Gunakan `or_filters` termasuk `asset_name` / `full_name` |
| 6 | Sedang | `get_ticket_actions` mengembalikan transisi mentah (field internal workflow) | Kembalikan hanya `action` dan `next_state` |
| 7 | Rendah | `add_worklog` menolak juga status `Selesai`, spesifikasi hanya `Ditutup`. Keputusan Efendy: boleh catat setelah selesai atau tidak | Tanyakan ke Efendy, lalu samakan |
| 8 | Rendah | Tombol aksi tidak dinonaktifkan selama permintaan (klik ganda). `prompt()` dipakai untuk pertanyaan, spesifikasi meminta kotak isian | Nonaktifkan tombol, ganti `prompt` dengan kotak isian di halaman |
| 9 | Rendah | `get_ticket` dipanggil ulang di dalam `do_ticket_action` lalu klien memuat ulang lagi (dua kali kerja) | Cukup salah satu |

## Belum dikerjakan dari spesifikasi

- Tes di `test_portal.py` (8 skenario, asersi nyata) dan bukti uji di site nyata.
- Perbaikan 2b: lebar kolom Subjek, penyelidikan kolom Kategori selalu `-`, dropdown Kategori/Tim di form buat tiket, uji XSS, hapus file `*.bak_*`.

## Cara uji karena tidak ada site kedua

Devin tidak punya akses site. Pengujian dilakukan Efendy di server `erpnext` (cek `hostname`): backup dulu (`bench --site desk.ciptamebel.co.id backup`), uji memakai satu tiket khusus uji, jangan gunakan tombol Reset Data Demo.
