# NextHD Web - Tugas Tahap 5 (Problem, Known Error, Change Request, Asset)

> Untuk Devin. Baca `docs/FAQ_DEVELOPER.md` dan `docs/web/SPEC_PORTAL.md` dulu.
> Ikuti scope ketat; jangan merapikan hal di luar scope. Satu sub-tahap = satu PR.
>
> **Status:** diperbarui 2026-10-06. Keputusan Efendy ada di bagian 1. Bagian 6 (B1) dikerjakan lebih dulu.

## 1. Keputusan (Efendy)

| # | Topik | Keputusan |
|---|---|---|
| 1 | Pembuatan Problem dari Tiket | **Satu endpoint server** (atomik). Jangan meniru 3 langkah browser seperti Client Script Desk |
| 2 | Tombol CR dari Known Error | Tombol tetap selalu tampil. Jika sudah ada CR dengan `related_problem` yang sama, tampilkan **peringatan** (tanpa memblokir), user boleh lanjut |
| 3 | Status Problem setelah Known Error dibuat | **Tetap manual** lewat tombol workflow. Endpoint hanya mengisi `Problem.known_error`, tidak mengubah `status` |
| 4 | SLA "7 hari kerja" | Pilihan A: 1 hari = 1440 menit jam kerja. Tidak ada perubahan kode/data |
| 5 | Impact/Urgency | Tetap 2 level (Tinggi/Rendah). Tidak menambah "Sedang" |
| 6 | "Baru" untuk semua jenis (2026-10-06) | **Opsional**: Problem, Known Error, Change Request, dan Aset masing-masing bisa dibuat **mandiri** (formulir "Baru") **maupun** dari objek asalnya (tombol "Buat ... dari ..."). Tidak wajib dari tiket |
| 7 | Menu navigasi (2026-10-06) | Dikerjakan **Claude** di `ui.js` (menu dropdown per kelompok: Daftar + Baru). **Devin tidak mengubah `ui.js` / `renderNav`.** Sebutkan halaman baru di deskripsi PR agar Claude menambahkannya ke menu |
| 8 | Problem dari Tiket berstatus Selesai | Saat ini **boleh** (hanya status Ditutup yang ditolak). Menunggu keputusan Efendy apakah Selesai juga ditolak. Jangan diubah sebelum ada keputusan |

## 2. Aturan Umum (semua sub-tahap)

1. Endpoint di `nexthd/next_helpdesk/api/portal.py`, path `nexthd.next_helpdesk.api.portal.<fungsi>`. Perubahan data hanya POST.
2. Tanpa `ignore_permissions=True`, tanpa SQL langsung untuk data dokumen. Pakai `frappe.get_list` / `frappe.get_doc`.
3. Perubahan status hanya lewat `apply_workflow`. Jangan set field `status` langsung.
4. Pembuatan tautan dilakukan dalam **satu fungsi server** dengan `doc.insert()` / `doc.save()`. Jika ada langkah gagal, seluruh proses batal (tidak boleh ada dokumen yatim).
5. Penyalinan foto (child table `photos`, DocType `NextHD Photo Link`) memakai **satu fungsi helper bersama** di server (`_copy_photos` sudah ada), dipakai Tiket->Problem dan Problem->Known Error.
6. Setelah tautan jadi, panggil `nexthd.next_helpdesk.utils.activity_log.log_cross_document_link(source_doctype, source_name, target_doctype, target_name)` (4 parameter, sudah diverifikasi). Pembuatan mandiri tidak punya sumber, jadi tidak memanggil log ini.
7. Output ke HTML di-escape; jangan `innerHTML` dengan data mentah.
8. Known Error: field `symptom`, `related_problem`, `workaround`, `title`. **Tidak ada field `status`.** Tidak ada field asset langsung.
9. Jangan sentuh 4 komponen navigasi terkunci (`FAQ_DEVELOPER.md` Q1) dan jangan ubah `ui.js` (keputusan 7).
10. **Tes:** jangan menulis tes yang hanya berisi `pass` atau tanpa assert; tes semacam itu ditolak di review. Devin tidak punya site uji, jadi tulis tes hanya untuk logika murni yang benar-benar berjalan tanpa database. Pembuktian fungsi dilakukan Claude lewat skrip uji di server.
11. **Dokumentasi:** Devin **tidak mengedit** `docs/`. Ringkasan perubahan, daftar file, dan hal yang tidak teruji ditulis di deskripsi PR. Claude yang memperbarui `FITUR_WEB.md`, `LOG_WEB.md`, `BUG_WEB.md` setelah review (menghindari konflik dokumen).
12. **Git (wajib, agar tidak macet):** selalu `git --no-pager ...`; commit dengan `git commit -m "..."` (jangan membuka editor); tanpa rebase interaktif; jangan `git rebase` atau `git push --force`. Jika branch tertinggal dari `main`, jangan di-rebase: buat commit baru atau minta bantuan.
13. **Laporan akhir** wajib menyertakan output mentah `git --no-pager log --stat -3` dan `git --no-pager diff --stat main`, serta daftar eksplisit apa yang **tidak** diuji. Klaim "selesai" tanpa ini tidak diterima.
14. Pembagian PR: tiap jenis dipecah **dua PR kecil**: (-1) daftar + detail + aksi + tombol "Buat dari ..."; (-2) formulir "Baru" mandiri.

## 3. Sub-tahap

### 5a - Problem

**5a-1 (sudah di `main`)**: halaman `/nexthd/problem` (daftar + detail via `?id=`), aksi workflow Problem, tombol "Buat Problem dari Tiket", endpoint `buat_problem_dari_tiket`. Jangan diubah kecuali diminta.

**5a-2 (belum)**: formulir **Problem Baru** mandiri.
- Halaman `/nexthd/problem-baru` (ikuti pola `tiket-baru`).
- Field form: `title` (wajib), `priority`, `category`, `related_asset` (pencarian aset memakai `search_assets` yang sudah ada), `root_cause` (opsional), `workaround` (opsional).
- Endpoint `buat_problem(data)`: whitelist kunci, `status=Terbuka`, validasi panjang, sanitasi `root_cause`/`workaround` dengan `sanitize_html`, `doc.insert()` tanpa `ignore_permissions`. Peran penulis saja (`_is_writer`).
- Kembalikan `{"problem_name": ...}` lalu arahkan ke detail Problem.

### 5b - Known Error

**5b-1**
- Halaman `/nexthd/known-error`: daftar dan detail.
- Di detail Problem: tombol **"Buat Known Error dari Problem"** (tampil jika `known_error` kosong).
- Endpoint `buat_known_error_dari_problem(problem)`: buat Known Error (`title`, `related_problem`, `symptom` <- `Problem.root_cause`, foto disalin), isi `Problem.known_error`, log. **Tidak mengubah `Problem.status`** (keputusan 3). Setelah sukses, tombol workflow "Convert to Known Error" muncul sendiri karena `known_error` sudah terisi.
- Catatan: mapping `symptom` <- `root_cause` mengikuti `ARSITEKTUR.md`. Client Script Desk saat ini tidak mengisinya; Devin konfirmasi ke Efendy sebelum menambahkannya jika ragu.

**5b-2**: formulir **Known Error Baru** mandiri (`/nexthd/known-error-baru`): `title` (wajib), `symptom`, `workaround`, `related_problem` (opsional; cek `reqd` di meta DocType, jika wajib maka jadikan wajib di form).

### 5c - Change Request

**5c-1**
- Halaman `/nexthd/change-request`: daftar dan detail.
- Aksi workflow CR: Draft -> Diajukan -> Direview -> Disetujui/Ditolak -> Implementasi -> Selesai -> Ditutup (ikuti transisi di `nexthd_change_request_workflow.json`).
- Tiga pintu masuk "dari ...", masing-masing satu endpoint:
  - Dari Problem (tampil jika `Problem.change_request` kosong): `title`, `related_problem`, `related_asset` <- `Problem.related_asset`; isi `Problem.change_request`; log.
  - Dari Known Error: `title`, `related_problem` <- `KnownError.related_problem`; log. **Tombol selalu tampil.** Jika sudah ada CR dengan `related_problem` yang sama, endpoint mengembalikan daftar CR itu dan portal menampilkan peringatan dengan pilihan "Tetap buat" / "Batal" (keputusan 2). Endpoint menerima parameter `konfirmasi_duplikat` (default false).
  - Dari Asset: `title` <- `Asset.asset_name`, `related_asset`; log.

**5c-2**: formulir **Change Request Baru** mandiri (`/nexthd/change-request-baru`): `title` (wajib), `change_type`, `risk_level`, `related_problem` (opsional), `related_asset` (opsional), `implementation_plan`, `rollback_plan`. Opsi Select diambil dari meta DocType, jangan di-hardcode.

### 5d - Asset

**5d-1 dan 5d-2** (daftar, detail, buat; aset sudah punya "Baru" bawaan karena inti halamannya memang formulir)
- Halaman `/nexthd/aset`: daftar, detail, buat (`/nexthd/aset-baru`).
- Pakai struktur yang ada sekarang (field `depends_on` per `asset_type`: PC/Laptop/Server, Network Device, Printer, Lainnya). **Bukan EAV** (EAV masih rencana di `DAFTAR_FITUR.md`).
- Form buat menampilkan field sesuai `asset_type` terpilih.
- Dropdown aset (di Tiket/Problem/CR) memakai pencarian `asset_name, assigned_to, serial_number`.
- Tombol "Buat Change Request dari Aset" di detail aset (mengikuti 5c-1).

## 4. Uji Wajib (tiap sub-tahap)

- Tombol tidak muncul jika tautan sudah ada (kecuali CR dari Known Error, lihat keputusan 2).
- Guest dialihkan ke login; peran tanpa hak ditolak di backend (bukan hanya disembunyikan di UI).
- XSS pada judul/deskripsi tidak tereksekusi.
- Foto ikut tersalin ke Problem dan Known Error.
- Simulasi kegagalan di tengah proses (mis. paksa error pada langkah tautan): tidak ada Problem/KE/CR yatim.
- `Problem.status` tidak berubah setelah Known Error dibuat.
- SLA dan notifikasi Telegram tetap terpicu seperti sebelumnya.
- Pembuatan mandiri: dokumen terbentuk dengan `status` awal sesuai workflow, tanpa tautan yatim.

Catatan untuk pengujian: pada skrip uji server jangan mengandalkan `frappe.db.rollback()` untuk membersihkan data uji (alur bisnis bisa commit sendiri). Beri judul data uji awalan "ZZ UJI" dan sediakan pembersihan.

## 5. Catatan Pengetahuan Frappe yang Relevan

- State workflow "Ditutup" memakai `doc_status=0` karena DocType NextHD tidak submittable; `doc_status=1` membuat `apply_workflow` memanggil `submit()` dan gagal untuk non-Administrator (diperbaiki 2026-10-06, fixture `workflow.json`). Jangan mengubahnya kembali.
- `frappe.get_list(..., fields=["count(name)"])` tidak diizinkan di Frappe v16; hitung dengan `len(get_list(pluck="name"))`.
- Menu navigasi bersama ada di `ui.js` (`renderNav`); jangan diubah (keputusan 7).

## 6. B1 - Filter dari URL (kerjakan PERTAMA, sebelum 5a-2 dan seterusnya)

Tujuan: dashboard di Beranda nanti memakai tautan seperti `/nexthd/kerja?view=overdue` dan `/nexthd/problem?status=Terbuka`. Halaman harus membaca filter dari query string saat dibuka.

**File yang boleh diubah (hanya dua):** `nexthd/public/js/nexthd/pages/kerja.js` dan `nexthd/public/js/nexthd/pages/problem.js`. Tidak ada perubahan Python, tidak ada perubahan `ui.js`, tidak ada perubahan dokumentasi.

**Halaman Tiket (`kerja.js`)**
- Parameter yang dibaca saat halaman dimuat: `view` (`all`, `mine`, `unassigned`, `overdue`), `status`, `priority`, `ticket_type`, `category`, `search`.
- Nilai harus diperiksa sebelum dipakai: `view` hanya dari empat nilai di atas; `status`/`priority`/`ticket_type`/`category` hanya jika ada di opsi hasil `get_ticket_options` (jika tidak ada, abaikan, jangan error). `search` dipotong maksimal 100 karakter.
- Nilai tersebut mengisi state awal (`currentView`, `currentFilters`, `currentSearch`) **sebelum** pemuatan pertama, sehingga tab dan dropdown filter tampil terpilih sesuai URL.
- Opsi `get_ticket_options` dimuat lebih dulu daripada daftar (sudah begitu di kode sekarang); pembacaan URL dilakukan setelah opsi tersedia.
- Tanpa parameter, perilaku sama persis seperti sekarang.

**Halaman Problem (`problem.js`), hanya mode daftar (tanpa `?id=`)**
- Parameter: `status` (salah satu dari `Terbuka`, `Investigasi`, `Known Error`, `Selesai`, `Ditutup`), `priority` (`Kritis`, `Tinggi`, `Sedang`, `Rendah`), `page` (bilangan bulat >= 1).
- Nilai di luar daftar diabaikan. Mengisi `listState` sebelum pemuatan pertama.
- Mode detail (`?id=`) tidak berubah.

**Keamanan:** jangan memasukkan nilai query string ke `innerHTML`; nilai hanya dipakai sebagai parameter API atau `.value` elemen form.

**Contoh yang harus berfungsi** (Efendy akan menguji manual):
- `/nexthd/kerja?view=overdue` -> tab "Lewat SLA" aktif
- `/nexthd/kerja?view=mine&priority=Kritis` -> tab "Ditugaskan ke saya" aktif dan filter Prioritas = Kritis
- `/nexthd/kerja?status=Baru` -> filter Status = Baru
- `/nexthd/kerja?view=ngawur&status=ngawur` -> diabaikan, tampil seperti tanpa parameter
- `/nexthd/problem?status=Terbuka` -> filter Status = Terbuka
- `/nexthd/problem?status=ngawur&page=abc` -> diabaikan

**Urutan pengerjaan setelah B1:** Tahap 4 (dashboard Beranda; spesifikasinya ditulis Claude di `TUGAS_TAHAP_4.md`), lalu 5a-2, 5b-1, 5b-2, 5c-1, 5c-2, 5d. Satu per satu, tanpa diselingi pekerjaan lain.
