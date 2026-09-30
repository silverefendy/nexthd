# Prasyarat PR 2 — Temuan Review PR 1

> Dibuat 2026-09-30 dari review `api.js`, `portal.py`, `ui.js`. Kerjakan sebelum atau di awal PR 2 (Devin boleh memasukkannya sebagai commit pertama PR 2 atau PR kecil terpisah `fix/web-api-js`).

## A. Bug di `public/js/nexthd/api.js` (wajib)

1. **`NX.api.get` mengirim semua parameter lewat `JSON.stringify`.** String seperti id tiket terkirim dengan tanda kutip literal (`"TKT-2609-0001"`), sehingga endpoint yang menerima string (mis. `get_ticket(id)`) menerima nilai salah. Frappe hanya mem-parse JSON untuk objek/array. Perbaikan: `JSON.stringify` hanya bila nilai bertipe object (array/dict); string, angka, boolean dikirim apa adanya. Verifikasi perilaku ini ke source Frappe v16 (`frappe/app.py`/`frappe/handler.py`) sebelum mengubah.
2. **Pesan error server tidak terbaca.** `_server_messages` adalah JSON list yang isinya string JSON lagi. Kode memakai `messages[0].message` (undefined) sehingga selalu jatuh ke "Terjadi kesalahan". Perbaikan: `JSON.parse(messages[0]).message`. Tambahkan juga pembacaan `exc_type` untuk ValidationError agar pesan bisnis tampil ke pengguna.
3. **Semua status 403 dialihkan ke login.** Untuk user yang sudah login tetapi tidak berhak atas satu aksi, ini membuat pengguna terlempar ke login. Pisahkan: 401 atau sesi tidak valid -> login; 403 saat sudah login -> tampilkan pesan "tidak berizin" lewat toast.

## B. Catatan untuk endpoint dan halaman baru

- **IT Auditor** ada di `IT_ROLES` tetapi hanya boleh membaca. Tombol aksi tulis (tahap 3) harus dijaga lewat `frappe.has_permission` per DocType, bukan lewat `IT_ROLES`.
- **`redirect-to` belum di-URL-encode** di `page_guard` (`portal.py`). Aman untuk path polos, tetapi halaman dengan query string (`/nexthd/tiket?id=...`) harus di-encode (`urllib.parse.quote`) dan hanya menerima path internal yang diawali `/nexthd`.
- Endpoint logout (`NX.api.post("logout")` di `ui.js`) belum terbukti jalan. Uji manual tombol "Keluar" dan verifikasi nama endpoint di Frappe v16.

## C. Sisa pending non-kode

- Efendy: commit dan push patch `ui.js` (`nav.className = "nx-nav"`), saran pesan `fix(web): pasang kelas nx-nav pada nav portal`.
- Efendy: uji tombol "Keluar" di portal.
