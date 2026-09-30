# TASK Devin - Portal Web NextHD, Tahap 1 dan 2

> Dokumen tugas untuk Devin. Ikuti persis. Bila ada yang tidak jelas, atau bertentangan dengan
> file lain, JANGAN menebak: tulis di bagian 'Pertanyaan' pada deskripsi PR, dan kerjakan hanya
> bagian yang jelas.
>
> Dibuat: 2026-09-30 oleh Claude. Pemilik keputusan: Efendy.

## 0. Ringkasan

Bangun portal web kerja untuk tim IT di dalam Frappe v16 (halaman `www/`, tanpa framework
frontend). Dua PR berurutan:

- **PR 1 (Tahap 1):** fondasi. CSS/JS bersama, `api.js`, `ui.js`, endpoint `get_session_info`,
  halaman `/nexthd/kerja` (placeholder), penjaga akses berdasarkan peran, unit test.
- **PR 2 (Tahap 2):** antrian tiket, detail tiket (baca saja), form buat tiket.

Kerjakan PR 1 sampai PR dibuka, lalu **BERHENTI**. Jangan mulai PR 2 sebelum Efendy menyatakan
PR 1 sudah di-merge. Satu branch dan satu PR per tahap: `feat/web-tahap-1`, `feat/web-tahap-2`.

Tidak ada perubahan DocType, field, fixture, atau patch. Tidak perlu `bench migrate`.

## 1. Baca dulu (wajib, sesuai urutan)

1. `docs/FAQ_DEVELOPER.md` (seluruhnya, terutama Q1, Q2, Q7)
2. `docs/web/README.md` dan `docs/web/SPEC_PORTAL.md`
3. `docs/POLA_KERJA.md` (terutama tabel Aturan Wajib di bagian 3)
4. `docs/WORKFLOW.md` bagian 2 dan 4 (workflow Ticket, jebakan workflow)
5. `docs/ARSITEKTUR.md` bagian 3 (field NextHD Ticket, Worklog). PERINGATAN: bagian Asset di sana
   sudah usang (sebelum EAV). Untuk field apa pun, sumber kebenaran adalah file JSON DocType.
6. `docs/BUG_HISTORY.md` (bagian 'Pelajaran Teknis') dan `docs/BUG_WORKSPACE_SIDEBAR.md` (sekilas)
7. Kode: `nexthd/next_helpdesk/doctype/nexthd_ticket/nexthd_ticket.json` dan `.py`,
   `nexthd_ticket_worklog.json`, `nexthd_ticket_waiting_log.json`, `nexthd/hooks.py`,
   `nexthd/next_helpdesk/api/telegram_webhook.py` (contoh gaya endpoint),
   dan landing page: `nexthd/www/nexthd/index.py`, `index.html`,
   `nexthd/public/css/nexthd_landing.css`, `nexthd/public/js/nexthd_landing.js`
8. Contoh gaya test: `nexthd/next_helpdesk/doctype/nexthd_ticket/test_nexthd_ticket.py`
   (catatan: `test_nexthd_asset.py` sedang rusak dan BUKAN tugasmu)

## 2. Aturan dokumentasi (penting)

- Semua file `docs/*.md` di LUAR `docs/web/` adalah **sumber kebenaran, HANYA-BACA**. Jangan edit.
- Kamu hanya boleh membuat/mengubah file di `docs/web/`:
  - `FITUR_WEB.md`: ubah status tahap yang kamu kerjakan (dari rencana ke selesai/dikerjakan)
  - `LOG_WEB.md`: tambah satu baris ringkas per PR (tanggal, apa yang dibuat)
  - `BUG_WEB.md`: catat bug/keanehan yang kamu temukan dan cara mengatasinya
  - `TEMUAN_DOKUMEN_LAIN.md`: jika kamu menemukan isi dokumen lain yang salah, usang, atau
    bertentangan dengan kode (contoh: nama field beda dengan JSON DocType), CATAT DI SINI
    (file mana, bagian mana, apa selisihnya, bukti dari kode). Jangan memperbaiki dokumen aslinya.
    Claude/Efendy yang akan memperbaikinya nanti.
- Perubahan dokumen ikut di PR yang sama dengan kodenya.

## 3. Larangan (jangan sentuh)

Jangan mengubah, menghapus, atau menambahkan apa pun pada:

- `nexthd/hooks.py` (tidak diperlukan; halaman `www/` dan aset `public/` otomatis dilayani Frappe)
- `nexthd/fixtures/*`, `nexthd/patches.txt`, `nexthd/patches/*`
- File JSON DocType, Workflow, Workspace, Desktop Icon, Client Script, Property Setter, Web Form
- File controller DocType (`*.py` di folder `doctype/`), `telegram.py`, `tasks.py`, `business_hours.py`
- File yang sudah ada di `nexthd/public/js/` dan `nexthd/public/css/` (kecuali file baru milikmu
  di subfolder `nexthd/`), dan `nexthd/api.py` di root app
- 4 komponen navigasi terkunci (`FAQ_DEVELOPER.md` Q1)
- Web Form `Tiket Saya` (`/tiket-saya`): tetap hidup, jangan dihapus atau diubah
- Jangan menambah dependensi Python/npm, font eksternal, CDN, atau library JS/CSS apa pun
- Jangan merapikan kode di luar scope (`FAQ_DEVELOPER.md` Q7)

Yang BOLEH diubah di luar file baru milikmu: hanya `nexthd/www/nexthd/index.py` dan `index.html`
(landing) dengan perubahan sekecil mungkin sesuai bagian 7.7.

## 4. Fakta teknis yang harus dipegang

| Hal | Nilai |
|---|---|
| Frappe | v16, site `desk.ciptamebel.co.id`, akses lokal `http://10.1.0.16:8001` |
| Nama app / paket Python | `nexthd` (root repo `nexthd/`, paket `nexthd/nexthd/`) |
| Module | `Next Helpdesk` (folder `next_helpdesk`) |
| DocType utama | `NextHD Ticket`. Child: `worklog` (NextHD Ticket Worklog), `waiting_log` (NextHD Ticket Waiting Log) |
| Workflow | `NextHD Ticket`, state: Baru, Sedang Dikerjakan, Menunggu User, Selesai, Ditutup |
| Role IT | `Agent`, `Agent Manager`, `IT Manager`, `IT Auditor`, plus `System Manager` |
| Role lain | `Requester` (BELUM dilayani portal; tahap 7) |
| Lokasi endpoint | `nexthd/next_helpdesk/api/portal.py`. Path panggil: `nexthd.next_helpdesk.api.portal.<fungsi>` |
| DILARANG | membuat folder `nexthd/nexthd/api/`: bentrok dengan `nexthd/nexthd/api.py` yang sudah ada |
| Halaman | `nexthd/nexthd/www/nexthd/<nama>.html` + `<nama>.py` (route `/nexthd/<nama>`) |
| CSS | `nexthd/nexthd/public/css/nexthd/*.css` (URL `/assets/nexthd/css/nexthd/*.css`) |
| JS | `nexthd/nexthd/public/js/nexthd/*.js` (URL `/assets/nexthd/js/nexthd/*.js`) |
| Jangan | menamai file JS/CSS berakhiran `.bundle.js` / `.bundle.css` (memicu bundler Frappe) |

Frappe punya beberapa detail API yang kamu harus VERIFIKASI ke source Frappe v16 di GitHub
(`frappe/frappe`, branch `develop`/`version-16`) sebelum dipakai, dan tuliskan hasilnya di deskripsi
PR: (a) `@frappe.whitelist(methods=[...])`, (b) `frappe.sessions.get_csrf_token()`,
(c) `frappe.utils.html_utils.sanitize_html`, (d) `frappe.model.workflow` (tidak dipakai di
tahap ini), (e) endpoint `/api/method/logout`. Jika salah satu tidak ada atau berbeda, pakai
padanan yang benar-benar ada di v16 dan jelaskan.

## 5. Aturan keamanan (WAJIB, akan diperiksa Claude saat review)

1. Setiap endpoint dan setiap halaman menolak `frappe.session.user == 'Guest'`.
2. Setiap endpoint memeriksa peran IT lewat fungsi penjaga tunggal `require_it_role()`.
3. **DILARANG** `ignore_permissions=True` di mana pun dalam kode portal.
4. **DILARANG** `frappe.db.sql`, `frappe.db.get_value`, `frappe.db.count`, `frappe.db.set_value`
   untuk data tiket. Gunakan `frappe.get_list` (menghormati izin) dan `frappe.get_doc` + `doc.check_permission('read')`.
5. Tulis data hanya lewat `doc.insert()` (bukan `db_insert`, bukan SQL) agar validate, SLA,
   priority matrix, dan hook Telegram (`after_insert`) berjalan.
6. **Jangan pernah** mengisi field `status`, `priority`, `priority_manually_set`, `sla_*`,
   `responded_on`, `resolved_on`, `closed_on`, `naming_series`, `owner`, `docstatus` dari input
   pengguna. Biarkan default dan logika DocType yang mengisinya.
7. Endpoint yang mengubah data: `methods=['POST']`. Endpoint baca: `methods=['GET']`.
8. Semua parameter dari klien divalidasi: tipe, panjang maksimum, dan whitelist nilai/kunci.
   Kunci filter/order_by hanya dari whitelist eksplisit (lihat PR 2). Jangan pernah menyusun
   string SQL atau nama field dari input klien.
9. HTML bebas (field `description`) disanitasi di server sebelum dikirim, dan hanya boleh masuk
   halaman lewat satu wadah khusus. Semua data lain ditampilkan lewat `textContent`.
10. Pesan error ke klien tidak boleh membocorkan traceback atau detail internal.

## 6. Aturan teknis front-end

- HTML/CSS/JS biasa. Skrip klasik dibungkus IIFE, dimuat dengan `defer`, satu namespace global `window.NX`.
  Tanpa `import`/`export`, tanpa `eval`, tanpa `innerHTML` dengan data dinamis (kecuali wadah
  deskripsi ter-sanitasi, bagian 8.6).
- Tema: pakai ulang token warna di `nexthd_landing.css` (`:root`, termasuk blok dark mode).
  Nilai identik, jangan membuat palet baru. Gaya retro: kertas krem, garis tebal, huruf monospace
  untuk label. Font hanya stack sistem (Georgia, ui-monospace, Courier New).
- Responsif (lebar 360px ke atas), hormati `prefers-reduced-motion`, fokus keyboard terlihat,
  kontras memadai, tombol/field punya label.
- Semua teks antarmuka Bahasa Indonesia. Nama variabel/fungsi bahasa Inggris. Komentar singkat
  boleh Indonesia.
- CSRF: halaman `www/` standalone tidak memuat objek `frappe`. Server menaruh token di
  `<meta name='csrf-token' content='{{ csrf_token }}'>`; `NX.api.post` mengirim header
  `X-Frappe-CSRF-Token`. Halaman dengan `no_cache = 1`.
- Tanggal/jam dari server berupa string `YYYY-MM-DD HH:MM:SS` tanpa zona waktu. JANGAN
  diparse dengan `new Date(...)` (menggeser zona waktu). Format dengan memecah string
  (contoh tampil: `30 Sep 2026 14:05`). Untuk penanda lewat-SLA, bandingkan string dengan
  `server_now` yang dikirim server (format sama, perbandingan string valid).
- Cache aset: tautan aset di HTML memakai `?v=1`; naikkan angkanya saat file berubah.
- Gaya kode Python: ikuti persis file yang sudah ada di repo (indentasi, kutip, urutan import).
  Cek `ruff`/`pyproject` di repo bila ada dan patuhi.

## 7. PR 1 - Tahap 1: Fondasi

### 7.1 File baru

```
nexthd/nexthd/public/css/nexthd/base.css
nexthd/nexthd/public/css/nexthd/layout.css
nexthd/nexthd/public/css/nexthd/components.css
nexthd/nexthd/public/js/nexthd/api.js
nexthd/nexthd/public/js/nexthd/ui.js
nexthd/nexthd/public/js/nexthd/pages/kerja.js
nexthd/nexthd/next_helpdesk/api/portal.py
nexthd/nexthd/next_helpdesk/api/test_portal.py
nexthd/nexthd/www/nexthd/kerja.html
nexthd/nexthd/www/nexthd/kerja.py
```

(Pastikan `nexthd/nexthd/next_helpdesk/api/__init__.py` sudah ada; jangan diubah.)

### 7.2 CSS

- `base.css`: token `:root` (salin nilai dari landing, termasuk dark mode), reset ringan,
  tipografi dasar, `.nx-mono`.
- `layout.css`: `.nx-nav` (bilah atas, menu bisa membungkus di layar sempit), `.nx-wrap`
  (lebar maks 1100px), `.nx-page-head`, `.nx-grid`.
- `components.css`: `.nx-btn` (+ varian `.nx-btn--alt`, `:disabled`), `.nx-card`, `.nx-badge`
  (varian warna: `--red --orange --yellow --grey --blue --green`), `.nx-table` (dibungkus
  `.nx-table-wrap` dengan `overflow-x:auto`), `.nx-field` (label + input/select/textarea),
  `.nx-toast`, `.nx-empty`, `.nx-loading`, `.nx-pager`.
- Semua kelas berawalan `nx-` supaya tidak bentrok dengan CSS Frappe atau landing.

### 7.3 `api.js`

`NX.api.get(method, params)` dan `NX.api.post(method, data)` mengembalikan Promise berisi
isi `message` dari respons Frappe.

- URL: `/api/method/` + method penuh. GET: params jadi query string (nilai objek di-JSON-kan).
  POST: body JSON, header `Content-Type: application/json`, `X-Frappe-CSRF-Token` dari meta.
- `credentials: 'same-origin'`.
- Status 401/403 (atau `exc_type` PermissionError): arahkan ke
  `/login?redirect-to=` + path saat ini (di-encode), kecuali sudah di halaman login.
- Error lain: lempar `Error` dengan pesan ramah. Ambil pesan dari `_server_messages`
  (string JSON berisi array string JSON; parse dua lapis dalam try/catch) atau `exception`;
  bila gagal parse, pakai pesan umum 'Terjadi kesalahan. Coba lagi.'.
- Jaringan mati: pesan 'Tidak dapat terhubung ke server.'.

### 7.4 `ui.js`

Fungsi dalam `NX.ui`: `esc(text)` (escape HTML), `el(tag, attrs, children)` (buat elemen tanpa
innerHTML, atribut aman), `toast(msg, type)`, `fmtDateTime(str)`, `badge(text, color)`,
`renderNav(session)` (mengisi `#nx-nav`), `setLoading(node, bool)`, `empty(node, text)`.

Menu `renderNav` (untuk peran IT): Beranda (`/nexthd`), Kerja (`/nexthd/kerja`),
Tiket Baru (`/nexthd/tiket-baru`, hanya jika `session.can_create`), Desk (`/desk/nexthd`),
Keluar (POST `/api/method/logout`, lalu ke `/login`). Tautan Tiket Baru sudah boleh tampil di
PR 1; halamannya baru ada di PR 2, jadi di PR 1 sembunyikan tautan itu dengan flag konstanta
`NX.ui.FEATURES.newTicket = false` yang diubah jadi true di PR 2.

### 7.5 `portal.py`

Konstanta dan fungsi (nama persis):

```python
IT_ROLES = ('Agent', 'Agent Manager', 'IT Manager', 'IT Auditor', 'System Manager')

def _user_roles(): ...            # frappe.get_roles(), dikembalikan sebagai set
def require_it_role(): ...        # tolak Guest dan non-IT dengan frappe.PermissionError
def resolve_home(roles): ...      # '/nexthd/kerja' jika ada irisan dengan IT_ROLES, selain itu None
def page_guard(context): ...      # dipakai file www/*.py, lihat di bawah

@frappe.whitelist(methods=['GET'])
def get_session_info(): ...
```

`get_session_info()` memanggil `require_it_role()` lalu mengembalikan dict:

```
{
  'user': frappe.session.user,
  'full_name': <nama lengkap dari frappe.utils.get_fullname(user)>,
  'roles': [peran milik user yang termasuk IT_ROLES, terurut],
  'home': '/nexthd/kerja',
  'can_create': bool(frappe.has_permission('NextHD Ticket', 'create')),
  'server_now': frappe.utils.now(),
}
```

`page_guard(context)` (fungsi biasa, TIDAK di-whitelist):

1. Guest -> `frappe.local.flags.redirect_location = '/login?redirect-to=' + <path saat ini>`
   lalu `raise frappe.Redirect` (pola sama dengan `index.py` landing).
2. Login tetapi bukan peran IT -> `raise frappe.PermissionError`.
3. Set `context.no_cache = 1` dan `context.csrf_token = frappe.sessions.get_csrf_token()`.

### 7.6 Halaman `kerja`

- `kerja.py`: `def get_context(context): page_guard(context); context.title = 'Ruang Kerja'`.
- `kerja.html`: kerangka HTML lengkap (doctype, meta viewport, meta csrf-token, tautan tiga CSS
  dan skrip `api.js`, `ui.js`, `pages/kerja.js` dengan `defer`), `<div id='nx-nav'></div>`,
  `<main id='nx-main'>`.
- `pages/kerja.js`: panggil `NX.api.get('nexthd.next_helpdesk.api.portal.get_session_info')`,
  `NX.ui.renderNav(session)`, lalu tampilkan kartu sapaan: nama, peran, dan pesan
  'Antrian tiket menyusul di tahap berikutnya.' Tangani state loading dan error.
- Jangan memakai Jinja `{% extends %}` atau `{% include %}` untuk layout bersama di tahap ini
  (resolusi path template belum diverifikasi). Nav diisi oleh JS.

### 7.7 Perubahan kecil landing (`index.py`, `index.html`)

- `index.py`: setelah pemeriksaan Guest yang sudah ada, tambahkan
  `context.home_url = resolve_home(set(frappe.get_roles()))` (import dari `portal.py`).
  Jangan ubah logika lain, `PRIVATE_MODE` tetap.
- `index.html`: jika `home_url` ada, tampilkan tombol tambahan 'Ruang Kerja' menuju `home_url`
  di area hero, di samping tombol yang sudah ada. Jangan mengubah bagian lain.

### 7.8 Test (`test_portal.py`)

Gaya sama dengan test yang sudah ada di repo. Minimal:

- `resolve_home`: peran Agent -> '/nexthd/kerja'; Requester saja -> None; set kosong -> None.
- `require_it_role`: user Guest ditolak; user dengan peran Agent lolos; user hanya Requester ditolak.
- `get_session_info`: struktur kunci lengkap; `roles` hanya berisi peran IT.

Catatan: kamu tidak punya server Frappe. Tulis test dengan benar, sebutkan di PR bahwa test
belum dijalankan, dan Efendy akan menjalankannya (`bench --site ... run-tests --module ...`).

### 7.9 Kriteria selesai PR 1

- Daftar file di 7.1 lengkap; tidak ada file lain yang berubah selain 7.7 dan `docs/web/*`.
- Self-check bagian 10 lulus.
- `docs/web/FITUR_WEB.md` (tahap 1 -> dikerjakan/selesai menunggu uji), `LOG_WEB.md` diperbarui.

## 8. PR 2 - Tahap 2: Antrian, Detail, Buat Tiket (mulai HANYA setelah PR 1 di-merge)

### 8.1 File baru / diubah

```
nexthd/nexthd/next_helpdesk/api/portal.py            (tambah fungsi, jangan ubah fungsi PR 1)
nexthd/nexthd/next_helpdesk/api/test_portal.py       (tambah test)
nexthd/nexthd/www/nexthd/kerja.html                  (jadi halaman antrian)
nexthd/nexthd/www/nexthd/tiket.html + tiket.py       (detail, route /nexthd/tiket?id=TKT-...)
nexthd/nexthd/www/nexthd/tiket-baru.html + tiket-baru.py
nexthd/nexthd/public/js/nexthd/pages/kerja.js        (diganti isinya)
nexthd/nexthd/public/js/nexthd/pages/tiket.js
nexthd/nexthd/public/js/nexthd/pages/tiket-baru.js
nexthd/nexthd/public/js/nexthd/ui.js                 (FEATURES.newTicket = true, helper tabel/pager)
nexthd/nexthd/public/css/nexthd/components.css       (tambah gaya seperlunya)
```

Semua `.py` halaman memakai `page_guard(context)`.

### 8.2 Endpoint

**`get_ticket_options()`** GET. Mengembalikan opsi dinamis, TIDAK di-hardcode di klien:

```
{
  'status': [...], 'priority': [...], 'ticket_type': [...], 'impact': [...], 'urgency': [...],
  'categories': [nama kategori dari frappe.get_list('NextHD Category', pluck='name')],
  'required': [fieldname wajib dari meta yang termasuk field form buat tiket],
}
```

Opsi Select diambil dari `frappe.get_meta('NextHD Ticket').get_field(<f>).options` (dipecah per
baris, buang string kosong).

**`list_tickets(view='all', status=None, priority=None, ticket_type=None, category=None, search=None, order_by='modified desc', page=1, page_size=20)`** GET.

- `view` whitelist: `all`, `mine` (assigned_to = user), `unassigned` (assigned_to kosong),
  `overdue` (`sla_resolution_by` < sekarang DAN status bukan Selesai/Ditutup).
- Filter lain hanya diterapkan bila nilainya string non-kosong dan ada di daftar opsi meta.
- `search`: string maks 100 karakter, dipakai sebagai `or_filters` LIKE pada `name` dan `subject`.
- `order_by` whitelist persis: `modified desc`, `creation desc`, `sla_resolution_by asc`.
  Selain itu tolak dengan error validasi.
- `page` >= 1; `page_size` 1..50 (lebih dari 50 dipotong ke 50).
- Pakai `frappe.get_list('NextHD Ticket', fields=[...], filters=..., or_filters=..., order_by=..., limit_start=..., limit_page_length=...)`.
  Field: `name, subject, status, priority, ticket_type, category, requested_by, assigned_to, team, sla_response_by, sla_resolution_by, creation, modified`.
- Total baris: `frappe.get_list` dengan filter yang sama dan `fields=['count(name) as total']`.
- Respons: `{'rows': [...], 'total': int, 'page': int, 'page_size': int, 'server_now': frappe.utils.now()}`.

**`get_ticket(name)`** GET. `name` string maks 140.

- `doc = frappe.get_doc('NextHD Ticket', name)`; `doc.check_permission('read')`.
- Kembalikan HANYA: `name, subject, ticket_type, status, priority, category, impact, urgency,
  requested_by, assigned_to, team, affected_asset, related_problem, sla_response_by,
  sla_resolution_by, responded_on, resolved_on, closed_on, creation, modified`,
  `description` (sudah disanitasi, bagian 8.6), `worklog` (baris: `waktu, teknisi, aktivitas,
  hasil, durasi_menit`), `waiting_log` (hanya field yang benar-benar ada di JSON child
  `nexthd_ticket_waiting_log.json`), dan `server_now`.

**`create_ticket(data)`** POST. `data` berupa JSON string atau dict (`frappe.parse_json`).

- Kunci diizinkan (whitelist): `ticket_type, subject, description, category, impact, urgency,
  requested_by, affected_asset, team, assigned_to`. Kunci lain DIABAIKAN (bukan error) dan tidak
  pernah diteruskan ke dokumen.
- Wajib: `subject`, `ticket_type`, `requested_by` (default ke user saat ini jika kosong), plus
  semua field `reqd` menurut meta. Panjang `subject` maks 140; `description` maks 20000.
- `doc = frappe.get_doc({'doctype': 'NextHD Ticket', **data_terfilter}); doc.insert()`.
  Tanpa `ignore_permissions`. Tanpa mengisi field terlarang (bagian 5 poin 6).
- Respons: `{'name': doc.name}`.

Pencarian user untuk field requested_by/assigned_to di form: pakai endpoint standar Frappe
`frappe.desk.search.search_link` (doctype `User`) lewat `NX.api.get`; jangan membuat endpoint sendiri.
Pencarian aset dan tim: sama, doctype `NextHD Asset` dan `NextHD Team`.

### 8.3 Halaman antrian (`/nexthd/kerja`)

- Tab tampilan: Semua, Ditugaskan ke saya, Belum ditugaskan, Lewat SLA (sesuai `view`).
- Kotak cari (debounce 300 ms), filter Status/Prioritas/Tipe/Kategori (opsi dari `get_ticket_options`),
  pilihan urutan (tiga nilai whitelist), pager (sebelumnya/berikutnya + 'x-y dari total').
- Tabel kolom: ID (tautan ke `/nexthd/tiket?id=...`), Subjek, Status, Prioritas, Kategori,
  Ditugaskan ke, SLA resolusi, Diubah. Di layar sempit tabel bisa digulir horizontal.
- Badge: prioritas Kritis=red, Tinggi=orange, Sedang=yellow, Rendah=grey; tipe Insiden=red,
  Permintaan Layanan=blue; status Baru=blue, Sedang Dikerjakan=orange, Menunggu User=yellow,
  Selesai=green, Ditutup=grey (keputusan tampilan, bukan dari Workflow State).
- Penanda 'Lewat SLA' bila `sla_resolution_by` < `server_now` dan status bukan Selesai/Ditutup.
- State: loading, kosong ('Tidak ada tiket'), error (pesan + tombol coba lagi).
- Tombol 'Tiket Baru' tampil hanya bila `session.can_create`.

### 8.4 Halaman detail (`/nexthd/tiket?id=...`)

- `id` dibaca dari query string; validasi tidak kosong, maks 140, lalu `NX.api.get('...get_ticket', {name: id})`.
- Tampilkan: judul (subjek), ID, badge status/prioritas/tipe, blok informasi (pelapor, ditugaskan
  ke, tim, kategori, impact, urgency, aset terkait, problem terkait), blok SLA (respon, resolusi,
  waktu respons, selesai, ditutup), deskripsi, tabel Worklog, tabel Waiting Log.
- **Read-only.** Jangan menampilkan tombol aksi workflow (itu Tahap 3).
- Tombol kembali ke antrian. Error 403/404: pesan ramah, bukan halaman kosong.

### 8.5 Halaman buat tiket (`/nexthd/tiket-baru`)

- Field: Tipe Tiket, Subjek, Deskripsi (textarea polos, bukan editor HTML), Kategori, Impact,
  Urgency, Pelapor (default user saat ini), Aset terkait (opsional), Tim (opsional), Ditugaskan ke
  (opsional). Tanda wajib sesuai `required` dari `get_ticket_options`.
- **Tidak ada** field Prioritas atau Status. Tampilkan catatan: 'Prioritas dihitung otomatis dari
  Impact dan Urgency.'
- Validasi sisi klien untuk field wajib; tetap andalkan validasi server. Cegah kirim ganda
  (tombol nonaktif saat mengirim). Sukses: toast lalu arahkan ke `/nexthd/tiket?id=<name>`.
  Gagal: tampilkan pesan server di atas form tanpa menghapus isian.
- Peran IT Auditor / tanpa izin create: halaman menampilkan pesan 'Anda tidak memiliki izin
  membuat tiket' dan tidak menampilkan form.

### 8.6 Sanitasi deskripsi

- Server: `description` dilewatkan `frappe.utils.html_utils.sanitize_html` (verifikasi nama
  fungsinya, bagian 4) sebelum dikirim.
- Klien: satu-satunya penggunaan `innerHTML` yang diizinkan adalah untuk wadah deskripsi
  (`#nx-description`) yang isinya sudah disanitasi server. Beri komentar di kode kenapa aman.

### 8.7 Test tambahan

- `list_tickets`: `order_by` di luar whitelist ditolak; `page_size` > 50 dipotong; `view`
  tidak dikenal ditolak.
- `create_ticket`: kunci terlarang (`status`, `priority`) tidak masuk ke dokumen; subjek kosong
  ditolak; user tanpa izin create ditolak.
- `get_ticket`: nama tidak ada -> DoesNotExistError; user tanpa izin read ditolak.

### 8.8 Kriteria selesai PR 2

- Semua di bagian 8 terpenuhi, self-check bagian 10 lulus, `docs/web/*` diperbarui.

## 9. Cara uji oleh Efendy (tulis ulang versi rapi di deskripsi tiap PR)

```bash
cd /home/it/frappe/apps/nexthd && git pull origin main
cd /home/it/frappe
bench build --app nexthd
bench --site desk.ciptamebel.co.id clear-cache
bench --site desk.ciptamebel.co.id clear-website-cache
bench restart
```

Skenario minimal yang harus kamu tuliskan beserta hasil yang diharapkan: (1) belum login ->
redirect ke login lalu kembali; (2) user Agent melihat halaman; (3) user tanpa peran IT ->
ditolak (403); (4) panggilan API tanpa login ditolak; (5) PR 2: tiket dibuat dari portal
memunculkan notifikasi Telegram dan SLA terisi, prioritas terhitung otomatis; (6) IT Auditor
tidak bisa membuat tiket.

## 10. Self-check sebelum membuka PR

Jalankan dan lampirkan hasilnya di deskripsi PR (hit yang muncul harus kamu jelaskan satu per satu):

```bash
grep -rn "ignore_permissions\|frappe.db.sql\|frappe.db.get_value\|frappe.db.count\|frappe.db.set_value" nexthd/next_helpdesk/api/portal.py nexthd/www/nexthd/
grep -rn "innerHTML\|eval(\|document.write\|new Date(" nexthd/public/js/nexthd/
grep -rn "http://\|https://\|cdn" nexthd/public/css/nexthd/ nexthd/public/js/nexthd/ nexthd/www/nexthd/kerja.html
python -m py_compile nexthd/next_helpdesk/api/portal.py
for f in nexthd/public/js/nexthd/*.js nexthd/public/js/nexthd/pages/*.js; do node --check "$f"; done
git diff --stat origin/main   # hanya file yang diizinkan boleh muncul
```

## 11. Deskripsi PR (wajib memuat)

1. Ringkasan apa yang dibuat.
2. Daftar file (baru/diubah) dan konfirmasi tidak ada file terlarang yang disentuh.
3. Hasil verifikasi detail API Frappe (bagian 4).
4. Hasil self-check (bagian 10).
5. Cara uji untuk Efendy (bagian 9).
6. Asumsi yang kamu ambil, dan Pertanyaan yang belum terjawab.
7. Bagian `Temuan dokumen lain` yang merujuk isi `docs/web/TEMUAN_DOKUMEN_LAIN.md`.

## 12. Jika ragu

Bertanya lebih baik daripada menebak. Untuk hal di luar scope (misalnya bug yang kamu lihat di
tempat lain), catat di `docs/web/BUG_WEB.md` atau `TEMUAN_DOKUMEN_LAIN.md`, jangan diperbaiki.
