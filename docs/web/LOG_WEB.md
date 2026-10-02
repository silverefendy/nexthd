# NextHD Web - Log Sesi

> Log ringkas pengerjaan portal web. Entri terbaru di atas.

| Tanggal | Ringkasan |
|---|---|
| 3 Okt 2026 (tahap 3b - CSRF) | Investigasi CSRF: meta tag `{{ csrf_token }}` di halaman `www/` tidak terisi oleh Frappe v16. Kemungkinan penyebab: Frappe v16 hanya merender `csrf_token` di template yang melalui Jinja context dari Frappe app (seperti `/desk` atau halaman DocType), sedangkan halaman `www/` statis tidak mendapatkan context ini. Fallback diimplementasikan: `getCsrfToken()` di `api.js` mengambil dari meta tag jika valid, jika tidak memanggil `get_session_info` sekali dan meng-cache. Fallback ini tetap dipertahankan. Catatan: investigasi sumber Frappe v16 (`frappe/website`, `frappe/templates`, `frappe/sessions.py`) diperlukan untuk konfirmasi akar penyebab. |
| 1 Okt 2026 (spesifikasi tahap 3) | Dibuat `TUGAS_TAHAP_3.md`. Temuan dari `nexthd_ticket.py`: hook `on_update` sudah menyisipkan baris `waiting_log` (pertanyaan tetap) saat `Sedang Dikerjakan -> Menunggu User`, jadi portal hanya mengubah `question`, tidak menyisipkan baris baru. Aturan peran: "IT Auditor hanya baca" ditentukan dari ketiadaan peran penulis (Agent, Agent Manager, IT Manager, System Manager), bukan dari adanya peran IT Auditor, karena akun Efendy memegang semua peran. Struktur worklog dan waiting log dikonfirmasi lewat `bench console`. DocType penugasan banyak orang (`NextHD Ticket Assignee`, dll.) ada, tetapi belum dipakai di Ticket. |
| 1 Okt 2026 (deploy tahap 2) | PR #14 di-merge. Review lima putaran: BOM dan indentasi hilang di beberapa file (termasuk `tiket-baru.py`, diperbaiki `dbd323c`). Setelah deploy, antrian gagal dengan galat `SQL functions are not allowed as strings in SELECT: count(name)` (Frappe v16), test Devin tidak menangkapnya karena tidak menyentuh database. Patch di `list_tickets` (`len(get_list(pluck="name"))`), commit `63a01a4`, antrian tampil. Catatan skala: `pluck` memuat semua nama tiket yang cocok, ganti ke hitung SQL jika tiket mencapai puluhan ribu. Temuan tampilan: label filter masih Inggris, SLA bermikrodetik, kolom Kategori kosong, SLA tampil pada tiket selesai. Dijadwalkan di Tahap 2b. Uji browser sisanya belum dilaporkan. |
| 30 Sept 2026 (verifikasi tahap 1) | PR #13 di-merge (`70afa26`) dan diuji di server. Lolos: tanpa login dialihkan ke login (#1), IT masuk (#2), Requester ditolak (#3), tombol "Ruang Kerja" muncul untuk IT dan tidak untuk Requester (#4, #5), `get_session_info` tanpa login 403 (#6), aset CSS/JS 200 (#8), landing privat dialihkan ke login. Review keamanan: tanpa `ignore_permissions`/SQL langsung/`allow_guest`, satu endpoint GET, 14 file berubah semuanya di area diizinkan. Bug tampilan: `<nav>` tidak punya kelas `nx-nav`, ditambal (`bb99c79`). Review `api.js` menemukan bug yang diperbaiki di PR 2, lihat `PRASYARAT_PR2.md`. |
| 30 Sept 2026 (tugas Devin PR 1) | PR 1 (Tahap 1 fondasi) selesai dikerjakan: CSS (base, layout, components), JS (api, ui, pages/kerja), portal.py (endpoint get_session_info, page_guard), test_portal.py, halaman kerja (html+py), update landing (tombol Ruang Kerja). |
| 30 Sept 2026 (tugas Devin) | Dibuat `TASK_DEVIN_TAHAP_1_2.md` (PR 1 fondasi, PR 2 antrian/detail/buat tiket) dan `TEMUAN_DOKUMEN_LAIN.md`. Aturan: Devin hanya mengedit `docs/web/*`, dokumen lain hanya-baca sebagai sumber kebenaran. Koreksi: `portal.py` di `next_helpdesk/api/` (bukan `nexthd/api/`, bentrok dengan `api.py`) |
| 30 Sept 2026 (lanjutan) | Keputusan Efendy: (1) portal tahap awal hanya untuk IT; (2) Web Form lama `/tiket-saya` diganti halaman Requester portal, tetapi baru dimatikan setelah tahap 7 teruji; (3) landing page sudah ter-commit. `SPEC_PORTAL.md` bagian 3, 6, 8 diperbarui, urutan tahap diubah (Agent dulu, Requester tahap 7) |
| 30 Sept 2026 | Diskusi arah portal. Keputusan: (1) semua kerja harian nantinya lewat web, Desk tetap untuk administrasi; (2) jalur A saja (`www/` di Frappe, tanpa Vue/React); (3) HTML, CSS, JS dipisah; (4) pola kerja Claude merancang, Devin membangun, Claude mereview; (5) dokumentasi portal dipisah ke `docs/web/`; (6) sementara hanya tim IT yang memegang. Akses lewat IP: `http://10.1.0.16:8001/nexthd` |

## Keputusan Terkait (non-teknis)

- Lisensi/distribusi ke pihak lain: kontrol teknis hilang setelah kode ada di server mereka; andalkan kontrak, repo privat, dan hosting di server sendiri. Belum ada tindakan.
- Tidak dipublikasikan ke LinkedIn atau publik selama aplikasi belum selesai.

## Aturan yang dipelajari (berlaku untuk semua PR Devin berikutnya)

- Klaim "selesai" dari Devin hanya diterima bersama output git mentah dan hasil menjalankan endpoint terhadap site nyata. Tiga putaran berturut-turut ringkasan tidak cocok dengan repo.
- Perbaikan `.py` kecil boleh ditulis Claude sebagai skrip patch untuk dijalankan Efendy, selalu dengan backup dan `py_compile`. Pastikan nama host (`erpnext`, bukan `cmlerp`) sebelum menjalankan.

## Berikutnya

1. Efendy: selesaikan uji browser Tahap 2 (buat tiket, detail, XSS, Keluar, field Link) dan kabari hasilnya.
2. Kirim `TUGAS_TAHAP_3.md` ke Devin.
3. Claude: review PR Tahap 3 dari output mentah, lalu perbarui dokumen ini.
