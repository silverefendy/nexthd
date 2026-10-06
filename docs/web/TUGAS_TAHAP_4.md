# NextHD Web - Tugas Tahap 4 (Dashboard Beranda)

> Untuk Devin. Baca `docs/FAQ_DEVELOPER.md`, `docs/web/SPEC_PORTAL.md`, dan `docs/web/TUGAS_TAHAP_5.md` (bagian 2 "Aturan Umum") dulu.
> Ikuti scope ketat; jangan merapikan hal di luar scope. Satu PR.
>
> **Status:** ditulis 2026-10-06. Prasyarat B1 (filter dari URL, PR #19) sudah di `main` dan teruji.

## 1. Tujuan

Beranda `/nexthd` untuk tim IT menjadi **dashboard**: kartu angka yang bisa diklik, masing-masing membuka daftar yang sudah terfilter (memakai filter dari URL hasil B1). Beranda memakai **menu bersama** (`ui.js`, `renderNav`) seperti halaman lain, bukan menu landing lama.

## 2. Keputusan

| # | Topik | Keputusan |
|---|---|---|
| 1 | Menu Beranda | **Opsi A (Efendy, 2026-10-06):** Beranda memakai menu yang sama dengan halaman dalam |
| 2 | Konten landing lama (hero, fitur, alur, teknologi) | Turunan dari keputusan 1: dipindah **utuh** ke `/nexthd/tentang` (halaman baru, tanpa perubahan tampilan). Dashboard punya tautan kecil "Tentang NextHD" di bagian bawah |
| 3 | User login tetapi bukan peran IT | Dialihkan ke `/nexthd/tentang` (landing lama, tombol "Buat Tiket" ke `/tiket-saya` tetap ada). Guest tetap dialihkan ke `/login?redirect-to=/nexthd` |
| 4 | Angka di kartu | **Harus sama persis** dengan total di halaman tujuan klik. Angka dihitung dengan filter yang sama dengan `list_tickets` (lihat bagian 4) |
| 5 | Kartu "Belum ditugaskan" | Menghitung hanya tiket aktif (status bukan Selesai/Ditutup). **Saran Claude, konfirmasi Efendy sebelum prompt dikirim** (lihat bagian 8) |
| 6 | Yang tidak dibangun di tahap ini | Daftar tiket di dashboard, grafik, kartu "Ditugaskan ke saya", kartu Prioritas Kritis (filter `list_tickets` belum bisa mengecualikan tiket Selesai/Ditutup saat dikombinasi prioritas), dashboard khusus manajer `/nexthd/manajer` |

## 3. File yang boleh diubah/dibuat

| File | Aksi |
|---|---|
| `nexthd/next_helpdesk/api/portal.py` | Tambah helper `_view_filters` dan endpoint `get_dashboard_counts`; ubah `list_tickets` **hanya** agar memakai helper (perilaku identik, kecuali keputusan 5) |
| `nexthd/www/nexthd/tentang.html`, `tentang.py` | Baru: salinan `index.html` dan `index.py` yang sekarang, tanpa perubahan isi |
| `nexthd/www/nexthd/index.html`, `index.py` | Tulis ulang menjadi dashboard |
| `nexthd/public/js/nexthd/pages/beranda.js` | Baru |
| `nexthd/public/css/nexthd/dashboard.css` | Baru (gaya kartu; jangan ubah `components.css`/`layout.css`/`base.css`) |

**Dilarang:** `ui.js`, `nexthd_landing.css`, `nexthd_landing.js`, `hooks.py`, `docs/`, halaman lain di `www/nexthd/`, file tes.

## 4. Backend

### 4a. Helper `_view_filters(view)`

Pindahkan logika filter per `view` dari `list_tickets` ke satu helper yang mengembalikan dict `filters`:

- `all`: `{}`
- `mine`: `assigned_to = user sekarang` (tidak berubah)
- `unassigned`: `assigned_to is not set` **ditambah** `status not in [Selesai, Ditutup]` (keputusan 5)
- `overdue`: `sla_resolution_by < now()` dan `status not in [Selesai, Ditutup]` (tidak berubah)

`list_tickets` memanggil helper itu. Selain perubahan `unassigned`, hasil `list_tickets` harus identik dengan sebelumnya. Jangan merapikan bagian lain fungsi itu.

### 4b. Endpoint `get_dashboard_counts`

- `@frappe.whitelist(methods=["GET"])`, `require_it_role()` di awal.
- Tanpa `ignore_permissions`, tanpa SQL langsung. Hitung dengan `len(frappe.get_list(doctype, pluck="name", filters=..., limit_page_length=0))` (aturan Frappe v16, `count(name)` ditolak).
- Jika user tidak punya izin baca sebuah DocType, nilai untuk DocType itu `null` (UI menampilkan "-"), bukan error.
- Bentuk respons:

```
{
  "tiket": {
    "baru": n, "sedang_dikerjakan": n, "menunggu_user": n,
    "lewat_sla": n, "belum_ditugaskan": n, "total": n
  },
  "problem": { "terbuka": n, "investigasi": n, "known_error": n, "total": n },
  "known_error_total": n,
  "aset_total": n,
  "server_now": "..."
}
```

- `baru`, `sedang_dikerjakan`, `menunggu_user` = tiket dengan `status` tersebut. `lewat_sla` dan `belum_ditugaskan` memakai `_view_filters`. Status Problem memakai nilai `Terbuka`, `Investigasi`, `Known Error`.

## 5. Halaman

### 5a. `index.py` (dashboard)

- Guest: redirect ke `/login?redirect-to=/nexthd` (seperti sekarang).
- Login tetapi tanpa peran IT (`IT_ROLES` di `portal.py`): redirect ke `/nexthd/tentang`.
- Peran IT: `context.no_cache = 1`, `context.csrf_token = frappe.sessions.get_csrf_token()`, `context.title = "Beranda"`.
- Hapus `PRIVATE_MODE` dan hitung statistik lama dari `index.py` (sekarang dilayani endpoint).

### 5b. `index.html`

Ikuti pola `kerja.html` (nav `#nx-nav`, `#nx-main`, `#nx-content`). Versi aset **harus**: `base.css?v=3`, `layout.css?v=3`, `components.css?v=3`, `dashboard.css?v=1`, `api.js?v=4`, `ui.js?v=4`, `pages/beranda.js?v=1`. Tambahkan meta `csrf-token` seperti `kerja.html`. Di bawah konten: tautan kecil "Tentang NextHD" ke `/nexthd/tentang`.

### 5c. `tentang.py` / `tentang.html`

Salin isi `index.py` dan `index.html` yang ada sekarang tanpa mengubah tampilan. Guest tetap dialihkan ke login (`redirect-to=/nexthd/tentang`). Tombol "Ruang Kerja" dan "Buat Tiket" tetap.

### 5d. `beranda.js`

Alur: `get_session_info` -> `NX.ui.renderNav(session)` -> `get_dashboard_counts` -> render. Tampilkan status "Memuat" lebih dulu dan tombol "Coba lagi" jika gagal (ikuti pola `kerja.js`).

Kartu (angka besar, label, seluruh kartu adalah tautan):

| Kelompok | Kartu | Tautan |
|---|---|---|
| Tiket | Baru | `/nexthd/kerja?status=Baru` |
| Tiket | Sedang Dikerjakan | `/nexthd/kerja?status=Sedang%20Dikerjakan` |
| Tiket | Menunggu User | `/nexthd/kerja?status=Menunggu%20User` |
| Tiket | Lewat SLA | `/nexthd/kerja?view=overdue` (aksen merah jika > 0) |
| Tiket | Belum ditugaskan | `/nexthd/kerja?view=unassigned` |
| Problem | Terbuka | `/nexthd/problem?status=Terbuka` |
| Problem | Investigasi | `/nexthd/problem?status=Investigasi` |
| Problem | Known Error | `/nexthd/problem?status=Known%20Error` |
| Ringkasan (bukan tautan) | Total Tiket, Problem, Known Error, Aset | - (halaman Known Error dan Aset belum ada) |

Aturan: nilai dari server hanya lewat `textContent`; `href` berupa konstanta di kode, bukan dari data server. Tampilan harus responsif (grid kartu turun ke satu kolom di layar sempit) dan mengikuti token warna yang ada (`--a`, `--b`, dark mode otomatis).

## 6. Uji Wajib

- Guest ke `/nexthd` dialihkan ke login.
- Akun non-IT login: `/nexthd` mengarah ke `/nexthd/tentang` dan halaman itu tampil seperti landing lama.
- Akun IT: menu bersama tampil (Beranda, Tiket ▾, Problem, Desk, nama user, Keluar), kartu terisi.
- Setiap kartu: angka sama dengan "dari ... " total di halaman tujuan (Claude memeriksa dengan skrip server: bandingkan `get_dashboard_counts` dengan `list_tickets(...).total` dan `list_problems(...).total`).
- Klik tiap kartu membuka daftar dengan filter/tab yang benar (memakai B1).
- Akun Auditor (hanya baca) tetap bisa melihat dashboard.
- Tampilan HP: kartu satu kolom, menu dropdown tetap berfungsi.
- `list_tickets` tanpa parameter dan dengan `view=mine/overdue/all` memberi hasil sama seperti sebelum PR.

## 7. Laporan PR

Sesuai `TUGAS_TAHAP_5.md` bagian 2 butir 11-13: output mentah `git --no-pager log --stat -3` dan `git --no-pager diff --stat main`, daftar file, dan daftar eksplisit hal yang **tidak** diuji. Jangan mengedit `docs/`.

**Prompt/branch:** `feat/web-tahap-4`, nama PR "Tahap 4 - Dashboard Beranda".

## 8. Keputusan menunggu Efendy

| # | Pertanyaan | Saran Claude |
|---|---|---|
| 9 | Kartu "Belum ditugaskan": hitung hanya tiket aktif? Saat ini `view=unassigned` di `list_tickets` ikut menghitung tiket Selesai/Ditutup yang tidak punya penanggung jawab, sehingga angka dan daftar menyesatkan | Ya, hanya tiket aktif (perubahan kecil di `_view_filters`, ikut memperbaiki tab "Belum ditugaskan" di antrian) |
