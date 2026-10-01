# Review PR #14 (Tahap 2) — 1 Oktober 2026

Status: **BELUM BOLEH MERGE.** Dua blocker, enam temuan lain.

## Blocker

1. **Indentasi Python hilang total** di `portal.py`, `test_portal.py`, `tiket.py`, `tiket-baru.py` (semua baris berawal di kolom 0, termasuk isi `def`/`if`/`for`). Hasilnya `IndentationError` saat diimpor, sehingga seluruh portal (termasuk `get_session_info` dan halaman `kerja`) mati. File JS juga kehilangan indentasi (tidak fatal, tetapi merusak diff). Semua file juga diawali BOM. Perbaikan: tulis ulang dengan tab, tanpa BOM, lalu `python -m py_compile` dan `node --check` sebelum push, dan lampirkan hasilnya.
2. **`create_ticket` tidak akan menerima data.** `tiket-baru.js` memanggil `NX.api.post("...create_ticket", data)` sehingga body berisi field tiket di level atas, padahal endpoint mengharapkan parameter bernama `data`. Perbaikan: kirim `{ data: data }` (atau ubah signature endpoint), dan uji nyata dengan membuat satu tiket.

## Temuan lain

3. `kerja.js`: bila hasil kosong, `renderQueue` hanya menampilkan "Tidak ada tiket" tanpa tab dan filter, sehingga pengguna terjebak (mis. di tab "Lewat SLA"). Render tab dan filter dulu, baru tabel atau pesan kosong.
4. `create_ticket`: deskripsi tidak disanitasi saat disimpan (hanya saat ditampilkan), padahal spesifikasi meminta sanitasi di server. `requested_by` dapat diisi user lain tanpa batas. Pesan error memakai `_(f"...")` (f-string di terjemahan).
5. `tiket.js` memakai `innerHTML` untuk deskripsi. Aman hanya bila `sanitize_html` benar-benar bekerja. Uji dengan payload `<img src=x onerror=alert(1)>`.
6. Filter view "overdue" di `list_tickets` ditimpa bila parameter `status` juga diberikan.
7. `tiket-baru.js`: field Link (pelapor, aset, tim, ditugaskan) berupa kotak teks biasa tanpa pencarian; salah ketik baru ketahuan saat submit.
8. `test_portal.py`: semua test endpoint baru hanya `pass` dengan kode dikomentari, jadi tidak membuktikan apa pun. `LOG_WEB.md` bertanggal "10 Jan 2026" (salah, seharusnya 1 Okt 2026) dan `FITUR_WEB.md` memakai karakter emoji rusak.

Klaim "verifikasi source Frappe v16" di `LOG_WEB.md` tidak disertai bukti (nama file dan baris).
