# NextHD Web - Tugas Tahap 5 (Problem, Known Error, Change Request, Asset)

> Untuk Devin. Baca `docs/FAQ_DEVELOPER.md` dan `docs/web/SPEC_PORTAL.md` dulu.
> Ikuti scope ketat; jangan merapikan hal di luar scope. Satu sub-tahap = satu PR.
>
> **Status:** DRAFT, ditulis 2026-10-02. Keputusan Efendy ada di bagian 1.

## 1. Keputusan (Efendy, 2026-10-02)

| # | Topik | Keputusan |
|---|---|---|
| 1 | Pembuatan Problem dari Tiket | **Satu endpoint server** (atomik). Jangan meniru 3 langkah browser seperti Client Script Desk |
| 2 | Tombol CR dari Known Error | Tombol tetap selalu tampil. Jika sudah ada CR dengan `related_problem` yang sama, tampilkan **peringatan** (tanpa memblokir), user boleh lanjut |
| 3 | Status Problem setelah Known Error dibuat | **Tetap manual** lewat tombol workflow. Endpoint hanya mengisi `Problem.known_error`, tidak mengubah `status` |
| 4 | SLA "7 hari kerja" | Pilihan A: 1 hari = 1440 menit jam kerja. Tidak ada perubahan kode/data |
| 5 | Impact/Urgency | Tetap 2 level (Tinggi/Rendah). Tidak menambah "Sedang" |

## 2. Aturan Umum (semua sub-tahap)

1. Endpoint di `nexthd/next_helpdesk/api/portal.py`, path `nexthd.next_helpdesk.api.portal.<fungsi>`. Perubahan data hanya POST.
2. Tanpa `ignore_permissions=True`, tanpa SQL langsung untuk data dokumen. Pakai `frappe.get_list` / `frappe.get_doc`.
3. Perubahan status hanya lewat `apply_workflow`. Jangan set field `status` langsung.
4. Pembuatan tautan dilakukan dalam **satu fungsi server** dengan `doc.insert()` / `doc.save()`. Jika ada langkah gagal, seluruh proses batal (tidak boleh ada dokumen yatim).
5. Penyalinan foto (child table `photos`, DocType `NextHD Photo Link`) memakai **satu fungsi helper bersama** di server, dipakai Tiket->Problem dan Problem->Known Error.
6. Setelah tautan jadi, panggil `nexthd.next_helpdesk.utils.activity_log.log_cross_document_link(source_doctype, source_name, target_doctype, target_name)`. **Baca isi fungsi ini dulu** sebelum memakainya; tanda tangan di atas diambil dari Client Script, belum diverifikasi.
7. Output ke HTML di-escape; jangan `innerHTML` dengan data mentah.
8. Known Error: field `symptom`, `related_problem`, `workaround`, `title`. **Tidak ada field `status`.** Tidak ada field asset langsung.
9. Jangan sentuh 4 komponen navigasi terkunci (`FAQ_DEVELOPER.md` Q1).

## 3. Sub-tahap

### 5a - Problem

- Halaman `/nexthd/problem`: daftar (filter status, prioritas) dan detail via `?id=`.
- Detail menampilkan: judul, status, prioritas, kategori, `related_asset`, `root_cause`, `workaround`, `known_error`, `change_request`, daftar `related_tickets`, foto.
- Aksi workflow Problem (tombol sesuai transisi yang diizinkan peran): Mulai Investigasi, Selesaikan Langsung, Selesaikan, Convert to Known Error (hanya muncul jika `known_error` terisi), Tutup.
- Di detail Tiket: tombol **"Buat Problem dari Tiket"** (tampil jika `related_problem` kosong), atau tautan ke Problem jika sudah ada.
- Endpoint `buat_problem_dari_tiket(ticket, title, priority)` dalam satu transaksi:
  1. Buat Problem: `title`, `priority`, `category` (dari tiket), `status=Terbuka`, `related_asset` <- `Ticket.affected_asset`, foto disalin.
  2. Isi `Ticket.related_problem`.
  3. Tambah baris `NextHD Problem Ticket` (`related_tickets`) di Problem.
  4. Log lintas dokumen.
  Tolak jika tiket sudah punya `related_problem`.

### 5b - Known Error

- Halaman `/nexthd/known-error`: daftar dan detail.
- Di detail Problem: tombol **"Buat Known Error dari Problem"** (tampil jika `known_error` kosong).
- Endpoint `buat_known_error_dari_problem(problem)`: buat Known Error (`title`, `related_problem`, `symptom` <- `Problem.root_cause`, foto disalin), isi `Problem.known_error`, log. **Tidak mengubah `Problem.status`** (keputusan 3). Setelah sukses, tombol workflow "Convert to Known Error" muncul sendiri karena `known_error` sudah terisi.
- Catatan: mapping `symptom` <- `root_cause` mengikuti `ARSITEKTUR.md`. Client Script Desk saat ini tidak mengisinya; Devin konfirmasi ke Efendy sebelum menambahkannya jika ragu.

### 5c - Change Request

- Halaman `/nexthd/change-request`: daftar dan detail.
- Aksi workflow CR: Draft -> Diajukan -> Direview -> Disetujui/Ditolak -> Implementasi -> Selesai -> Ditutup (ikuti transisi di `nexthd_change_request_workflow.json`).
- Tiga pintu masuk pembuatan, masing-masing satu endpoint:
  - Dari Problem (tampil jika `Problem.change_request` kosong): `title`, `related_problem`, `related_asset` <- `Problem.related_asset`; isi `Problem.change_request`; log.
  - Dari Known Error: `title`, `related_problem` <- `KnownError.related_problem`; log. **Tombol selalu tampil.** Jika sudah ada CR dengan `related_problem` yang sama, endpoint mengembalikan daftar CR itu dan portal menampilkan peringatan dengan pilihan "Tetap buat" / "Batal" (keputusan 2). Endpoint menerima parameter `konfirmasi_duplikat` (default false).
  - Dari Asset: `title` <- `Asset.asset_name`, `related_asset`; log.

### 5d - Asset

- Halaman `/nexthd/aset`: daftar, detail, buat.
- Pakai struktur yang ada sekarang (field `depends_on` per `asset_type`: PC/Laptop/Server, Network Device, Printer, Lainnya). **Bukan EAV** (EAV masih rencana di `DAFTAR_FITUR.md`).
- Form buat menampilkan field sesuai `asset_type` terpilih.
- Dropdown aset (di Tiket/Problem/CR) memakai pencarian `asset_name, assigned_to, serial_number`.

## 4. Uji Wajib (tiap sub-tahap)

- Tombol tidak muncul jika tautan sudah ada (kecuali CR dari Known Error, lihat keputusan 2).
- Guest dialihkan ke login; peran tanpa hak ditolak di backend (bukan hanya disembunyikan di UI).
- XSS pada judul/deskripsi tidak tereksekusi.
- Foto ikut tersalin ke Problem dan Known Error.
- Simulasi kegagalan di tengah proses (mis. paksa error pada langkah tautan): tidak ada Problem/KE/CR yatim.
- `Problem.status` tidak berubah setelah Known Error dibuat.
- SLA dan notifikasi Telegram tetap terpicu seperti sebelumnya.

## 5. Dokumen yang Diperbarui Devin di PR yang Sama

`docs/web/FITUR_WEB.md`, `docs/web/LOG_WEB.md`, `docs/web/BUG_WEB.md` (bila ada bug).
