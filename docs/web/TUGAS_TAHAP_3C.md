# Tugas Tahap 3c — Polesan Portal (untuk Devin)

> Dibuat 2 Okt 2026. Lingkup kecil, hanya portal. Baca dulu `FAQ_DEVELOPER.md`, `LOG_WEB.md` (bagian "Aturan yang dipelajari"), dan `BUG_WEB.md`.

## Aturan

1. Hanya boleh mengubah: `nexthd/public/js/nexthd/api.js`, `nexthd/public/js/nexthd/pages/tiket.js`, `nexthd/next_helpdesk/api/test_portal.py` (hanya bila perlu), dan `docs/web/*`.
2. Dilarang: `ignore_permissions`, `allow_guest`, SQL langsung, mengubah DocType, mengubah `nexthd_ticket.py`.
3. Indentasi TAB, tanpa BOM, tanpa CRLF.
4. Klaim selesai hanya diterima bersama output mentah `git status`, `git log -3 --oneline`, `git diff --stat`, dan nomor baris kode per butir. Commit dan push dulu sebelum melapor. Jangan merge sendiri.

## Butir

### C-1. Pesan galat bersih dari tag HTML
- Gejala: toast menampilkan `Error: <strong>NextHD Ticket Worklog</strong> Row #1: Value missing for: Aktivitas`.
- Cari tempat `api.js` membentuk `err.message` dari respons server. Bersihkan tag memakai `new DOMParser().parseFromString(pesan, "text/html").body.textContent` (jangan memakai `innerHTML` untuk menampilkan).
- Penerimaan: pesan di toast dan di form tidak memuat tanda `<` atau `>` dari tag.

### C-2. Tombol "Ambil untuk saya"
- Gejala: tombol tetap muncul walau tiket sudah ditugaskan ke diri sendiri.
- Simpan hasil `get_session_info` di `tiket.js` (sekarang hanya dipakai untuk navigasi).
- Tampilkan tombol hanya jika `actions.can_assign_self` dan (`!ticket.assigned_to` atau (`ticket.assigned_to !== session.user` dan `actions.can_assign_other`)).
- Penerimaan: tiket milik sendiri tidak menampilkan tombol; tiket tanpa penugasan menampilkannya; manajer melihatnya pada tiket orang lain.

## Tidak dikerjakan di 3c

- Kunci penugasan setelah Selesai/Ditutup: menunggu keputusan Efendy.
- Perilaku Buka Kembali dan SLA: ada di `nexthd_ticket.py`, lihat `docs/TEMUAN_SLA_2026-10-02.md`.
- Tes terhadap site: belum ada site uji; jangan menjalankan `run-tests` di produksi.

## Pengujian oleh Efendy

Buat satu tiket uji, ambil untuk saya (tombol hilang), tugaskan ke user lain (tombol muncul bagi manajer), kirim catatan berisi hanya `<img src=x>` (pesan tanpa tag).
