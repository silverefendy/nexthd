# Tugas Devin: Tahap 3 (Aksi Workflow, Worklog, Penugasan) + Perbaikan 2b

> Dibuat: 1 Okt 2026. Satu PR, branch `feat/web-tahap-3` dari `main` terbaru.
> Baca dulu: `SPEC_PORTAL.md`, `PRASYARAT_PR2.md`, `REVIEW_PR14.md`, dan `docs/FAQ_DEVELOPER.md`.

## 0. Aturan tidak bisa ditawar

1. Hanya boleh mengubah: `nexthd/next_helpdesk/api/portal.py`, `test_portal.py`, `nexthd/public/js/nexthd/*`, `nexthd/public/css/nexthd/*`, `nexthd/www/nexthd/*`, dan `docs/web/*`. Jangan menyentuh DocType, workflow, hooks, fixture.
2. Tanpa `ignore_permissions`, tanpa SQL langsung (kecuali butir 3.3), tanpa `allow_guest`.
3. Indentasi **tab** untuk Python dan JS. **Tanpa BOM** (EF BB BF). Tanpa framework/CDN.
4. Semua endpoint penulis memakai POST. Parameter dari klien divalidasi di server.
5. Frappe v16: fungsi SQL di `fields` ditolak (bug `count(name)` di PR 2). Jangan tulis `fields=["count(...)"]`.
6. **Bukti wajib saat lapor selesai** (tempel output mentah, bukan ringkasan):
   - `git log origin/feat/web-tahap-3 --oneline -5` dan `git diff --stat origin/main`
   - untuk setiap file `.py`: `git show origin/feat/web-tahap-3:<file> | head -c3 | xxd -p` (bukan `efbbbf`) dan `ast.parse` OK
   - untuk setiap file `.js`: `node --check` OK
   - hasil menjalankan **setiap endpoint baru terhadap site nyata** (lihat §5). Tes yang hanya `pass` tidak dihitung.

## 1. Fakta dari server (jangan ditebak ulang)

Child table di `NextHD Ticket`:

| Field | DocType | Kolom penting |
|---|---|---|
| `worklog` | `NextHD Ticket Worklog` | `waktu` (Datetime), `teknisi` (User), `aktivitas` (Small Text, **wajib**), `hasil` (Select: `Berhasil`, `Belum Berhasil`, `Perlu Eskalasi`, `Menunggu Sparepart`), `durasi_menit` (Int) |
| `waiting_log` | `NextHD Ticket Waiting Log` | `asked_on`, `asked_by`, `question` (Small Text, **wajib**), `replied_on`, `reply` |

Ticket **tidak** punya field `additional_assignees` dsb. Penugasan memakai `assigned_to` (satu User).

Workflow `NextHD Ticket` (status): `Baru`, `Sedang Dikerjakan`, `Menunggu User`, `Selesai`, `Ditutup`. Aksi: Mulai Kerjakan, Tunggu User, Lanjut Kerjakan, Selesaikan, Konfirmasi Selesai, Buka Kembali. Peran aksi ada di fixture workflow; portal **tidak boleh menyalin aturan itu**, cukup bertanya ke Frappe.

Di `nexthd_ticket.py`, `on_update` -> `handle_workflow_sla_transitions()` sudah:
- `Baru -> Sedang Dikerjakan`: hitung ulang `sla_resolution_by`, isi `responded_on`.
- `Sedang Dikerjakan -> Menunggu User`: **menyisipkan sendiri satu baris `waiting_log`** lewat `frappe.db.sql` dengan `question = "Menunggu respons dari user"`.
- `Menunggu User -> Sedang Dikerjakan`: menutup baris terbuka dan memperpanjang SLA.

## 2. Endpoint baru (semua di `portal.py`, path `nexthd.next_helpdesk.api.portal.<fungsi>`)

### 2.1 `get_ticket_actions(name)` (GET)
- Muat dokumen, cek `frappe.has_permission("NextHD Ticket", "read", doc)`.
- Panggil `frappe.model.workflow.get_transitions(doc)` (verifikasi signature di source Frappe v16 yang terpasang: `/home/it/frappe/apps/frappe/frappe/model/workflow.py`).
- Kembalikan: `{"actions": [{"action": ..., "next_state": ...}], "can_assign_self": bool, "can_assign_other": bool, "can_worklog": bool}`.
- Server yang memutuskan tombol; JS hanya menampilkan.

### 2.2 `do_ticket_action(name, action, question=None)` (POST)
- Tolak jika pengguna bukan penulis (lihat §3).
- Pastikan `action` ada di hasil `get_transitions` saat ini, kalau tidak: `frappe.throw`.
- Jalankan `frappe.model.workflow.apply_workflow(doc, action)`.
- Khusus aksi `Tunggu User`: `question` wajib (tidak kosong, maks 500 karakter, sanitasi teks). **Jangan menyisipkan baris `waiting_log` baru**, karena hook di atas sudah melakukannya. Setelah `apply_workflow` selesai, cari baris `waiting_log` milik tiket itu dengan `replied_on` kosong dan `idx` terbesar, lalu perbarui hanya kolom `question`-nya dengan `frappe.db.set_value` (ini pengecualian SQL langsung yang diizinkan, dan hanya setelah aksi workflow lolos izin). Jika baris tidak ditemukan, kembalikan galat jelas, jangan membuat baris baru.
- Aksi lain: `question` diabaikan.
- Kembalikan status baru dan `get_ticket` ringkas.

### 2.3 `add_worklog(name, aktivitas, hasil=None, durasi_menit=None)` (POST)
- Tolak jika bukan penulis. `aktivitas` wajib, maks 1000 karakter. `hasil` harus salah satu dari 4 opsi (whitelist). `durasi_menit` bilangan bulat 0 sampai 1440.
- `doc.append("worklog", {"waktu": now_datetime(), "teknisi": frappe.session.user, ...})` lalu `doc.save()` (izin dicek Frappe). Teknisi tidak boleh dikirim dari klien.
- Tidak boleh pada tiket berstatus `Ditutup`.

### 2.4 `assign_ticket(name, user=None)` (POST)
- Tanpa `user`: "Ambil untuk saya", set `assigned_to = frappe.session.user`. Hanya jika tiket belum ditugaskan atau pengguna Agent Manager/IT Manager.
- Dengan `user`: hanya Agent Manager atau IT Manager atau System Manager. Validasi `user` ada dan memiliki salah satu peran IT (`IT_ROLES`).
- Gunakan `doc.assigned_to = ...; doc.save()`.

## 3. Aturan peran (hati-hati, ini jebakan)

3.1 "IT Auditor hanya baca" **tidak boleh** diimplementasikan sebagai "tolak jika punya peran IT Auditor". Akun Efendy memegang semua peran termasuk IT Auditor. Aturan yang benar: pengguna disebut **penulis** jika punya minimal satu dari `Agent`, `Agent Manager`, `IT Manager`, `System Manager`. Bukan penulis -> semua endpoint penulis menolak (`frappe.PermissionError`) dan `get_ticket_actions` mengembalikan daftar kosong.

3.2 Daftar peran penulis dan manajer diletakkan sebagai konstanta di `portal.py` (`WRITER_ROLES`, `MANAGER_ROLES`), bukan diulang di tiap fungsi.

3.3 Satu-satunya SQL langsung yang diizinkan: `frappe.db.set_value` pada baris `waiting_log` (butir 2.2).

## 4. Frontend

Halaman detail `/nexthd/tiket?id=...` (`tiket.js`):
- Panel "Aksi": tombol dari `get_ticket_actions`. Klik -> `confirm` ringan, lalu `do_ticket_action`. Untuk "Tunggu User" tampilkan kotak isian pertanyaan (wajib). Setelah sukses muat ulang detail dan tampilkan toast.
- Tombol "Ambil untuk saya" jika `can_assign_self`. Pilihan penerima (dropdown pengguna IT) jika `can_assign_other`; daftar penerima diambil dari endpoint kecil `list_it_users()` (GET, hanya untuk manajer; mengembalikan `name` dan `full_name`).
- Form "Tambah catatan" (aktivitas, hasil, durasi) jika `can_worklog`.
- Semua teks dari server dirender dengan `textContent`. `innerHTML` hanya untuk deskripsi yang sudah disanitasi server (sudah ada, jangan diperluas).
- Tombol dinonaktifkan selama permintaan berjalan (cegah klik ganda).
- Pengguna bukan penulis: panel aksi tidak tampil sama sekali.

## 5. Perbaikan 2b (ikut PR ini)

| # | Perbaikan |
|---|---|
| 1 | Label filter di `kerja.js`: Status, Prioritas, Jenis Tiket, Kategori (sekarang `Priority`, `Ticket_type`, `Category`) |
| 2 | Lebarkan kolom Subjek, kolom lain dirampingkan |
| 3 | Format tanggal SLA tanpa mikrodetik: `06 Okt 2026, 10:53` |
| 4 | Sembunyikan SLA resolusi untuk tiket `Selesai` dan `Ditutup` |
| 5 | Kolom Kategori selalu `-`: periksa apakah `category` ada di data dan di respons `list_tickets`; jelaskan penyebabnya di PR |
| 6 | `page_guard`: encode `redirect-to` dengan `urllib.parse.quote` dan sertakan query string (`?id=...`) |
| 7 | Field Link di form buat tiket (Kategori, Aset, Tim, Ditugaskan ke): ganti kotak teks dengan `<select>` untuk Kategori dan Tim (data dari `get_ticket_options`), dan pencarian untuk Aset/pengguna lewat endpoint pencarian kecil dengan batas 20 hasil dan izin baca DocType terkait |
| 8 | Uji XSS: deskripsi `<img src=x onerror=alert(1)>` tidak boleh memicu alert di detail |
| 9 | Hapus file `*.bak_*` jika masuk ke diff |

## 6. Tes (wajib berisi asersi nyata terhadap database)

Gunakan `FrappeTestCase`, buat pengguna uji dengan peran berbeda (`Agent`, `IT Auditor` saja, `Requester`), buat tiket uji, lalu uji:

1. Agent: `get_ticket_actions` pada tiket `Baru` memuat `Mulai Kerjakan`. `do_ticket_action` -> status `Sedang Dikerjakan`.
2. `Tunggu User` tanpa `question` -> ditolak. Dengan `question` -> status `Menunggu User`, **tepat satu** baris `waiting_log` terbuka dan `question` sesuai isian.
3. `Lanjut Kerjakan` menutup baris tersebut (`replied_on` terisi).
4. `add_worklog` menambah tepat satu baris, `teknisi` = pengguna login, `hasil` di luar whitelist ditolak.
5. Pengguna hanya `IT Auditor`: semua endpoint penulis menolak; `get_ticket_actions` kosong.
6. Pengguna `Requester`: ditolak di semua endpoint portal IT.
7. `assign_ticket` tanpa `user` oleh Agent berhasil pada tiket belum ditugaskan; dengan `user` oleh Agent biasa ditolak; oleh Agent Manager berhasil.
8. `list_tickets` dengan setiap `view` berjalan tanpa galat (regresi bug `count`).

Lampirkan output `bench --site desk.ciptamebel.co.id run-tests --app nexthd --module nexthd.next_helpdesk.api.test_portal` (jalankan di site uji atau lampirkan alasan jika tidak bisa). Tes membuat data di database; hapus data uji di `tearDown`.

## 7. Deploy setelah merge (dijalankan Efendy)

```
cd /home/it/frappe/apps/nexthd && git pull origin main
cd /home/it/frappe
bench build --app nexthd
bench --site desk.ciptamebel.co.id clear-cache
bench --site desk.ciptamebel.co.id clear-website-cache
bench restart
```

Tidak perlu `bench migrate` (tidak ada perubahan DocType).

## 8. Di luar cakupan

Dashboard manajer, Problem/Known Error/Change Request/Asset, laporan, lampiran/foto, halaman Requester, field `additional_*`.
