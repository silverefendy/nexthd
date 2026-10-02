# Temuan SLA — Investigasi 2 Oktober 2026

> Hasil membaca kode `business_hours.py`, `nexthd_sla_policy.py`, `nexthd_ticket.py` (branch `main`, `14de747`) dan mencocokkan dengan angka di layar. **Belum ada kode yang diubah.** Bagian "Keputusan" menunggu Efendy.

## 1. "Hari" dihitung sebagai 1440 menit JAM KERJA (terbukti)

- `nexthd_sla_policy.py`: `UNIT_TO_MINUTES = {Menit: 1, Jam: 60, Hari: 1440}`. "7 Hari" menjadi 10080 menit.
- `add_working_time()` menghabiskan menit itu hanya di jam kerja. Jadi 10080 menit = **168 jam kerja**, bukan 7 hari kerja.
- Kapasitas jam kerja: Senin-Kamis 09:00 (08-17), Jumat 09:30 (08:00-17:30), Sabtu 07:00 (08-15) = 52,5 jam/minggu. 168 jam = sekitar 3,2 minggu kerja.
- Bukti: tiket `TKT-2610-0001` dimulai Jumat 2 Okt 17:10:47, SLA Resolusi tampil 26 Okt 11:12:47. Hitungan manual: sisa Jumat 19,2 menit + 3 minggu Senin-Sabtu penuh + sisa -> 26 Okt 11:10:47, ditambah 2 menit perpanjangan jeda "Menunggu User" (17:12:42 sampai 17:14:13 = 91 detik, dibulatkan 2 menit) = **11:12:47, persis**. Tidak ada hari libur Oktober dalam rentang itu.
- Dampak: Sedang "2 hari" = 48 jam kerja (bukan 2 hari kerja); Rendah "7 hari" = 168 jam kerja (bukan 7 hari kerja). Tinggi dan Kritis memakai menit/jam, tidak terdampak.

## 2. Pilihan perbaikan (dihitung dari Jumat 2 Okt 17:10:47)

| Pilihan | Rendah | Sedang | Perlu kode? |
|---|---|---|---|
| A. Dibiarkan (sekarang) | Sen 26 Okt 11:10 | Jum 9 Okt 12:40 | Tidak |
| B. Ubah data policy ke Jam: Rendah 63 Jam, Sedang 18 Jam (anggap 1 hari kerja = 9 jam) | Sen 12 Okt 11:10 | Sel 6 Okt 09:40 | Tidak (isi di Desk), tetapi `install.py` default dan dokumen perlu diselaraskan |
| C. Ubah konversi "Hari" di kode menjadi hari kalender kerja | bergantung definisi | bergantung definisi | Ya |

Catatan: panjang "hari" kerja tidak seragam (9 / 9,5 / 7 jam), jadi "7 hari kerja" literal ambigu; pilihan B memakai 9 jam sebagai pendekatan.

## 3. Dokumen vs kode: "all-or-nothing" tidak diterapkan

- Dokumen (SUMMARY, POLA_KERJA, HANDOFF) menyebut aturan SLA luar jam kerja "all-or-nothing" (durasi penuh diulang dari jam kerja berikutnya bila tidak muat).
- Kode `add_working_time()` melakukan **carry-over**: sisa menit hari itu dipakai, sisanya dilanjutkan di hari kerja berikutnya.
- Bukti: SLA Respon `TKT-2610-0001` = Sabtu 3 Okt 09:02:17. Di bawah all-or-nothing hasilnya hanya bisa hari yang sama (jika muat) atau tepat 10:00:00 Sabtu; 09:02:17 hanya mungkin dengan carry-over.
- Uji 20 Agustus "lulus" karena tiketnya dimulai tepat jam buka, di mana kedua aturan memberi hasil sama.
- Dampak praktis kecil (selisih menit pada SLA pendek), tetapi dokumen dan kode harus disatukan. Keputusan: pertahankan carry-over dan koreksi dokumen, atau ubah kode ke all-or-nothing.

## 4. Perpanjangan jeda "Menunggu User" memakai waktu kalender

- `_close_waiting_log_and_extend_sla()` menambah `sla_resolution_by` dengan menit jeda kalender (penambahan lurus, disengaja di PR #8).
- Jeda yang melewati malam atau akhir pekan menambah tenggat jauh lebih banyak daripada jam kerja yang benar-benar terlewat (contoh: jeda Jumat 17:00 sampai Senin 08:00 = 63 jam kalender, padahal 0 menit jam kerja terlewat).
- Belum diuji; ini dari pembacaan kode. Pilihan: perpanjang hanya sebesar menit jam kerja di dalam rentang jeda.

## 5. Buka Kembali: cap waktu tidak dibersihkan

- Terlihat di layar: status Baru, tetapi "Selesai Pada" 17:14:43 dan "Direspon Pada" masih terisi.
- Dari kode: `update_timestamps()` hanya mengisi `resolved_on`/`closed_on` jika kosong, jadi Selesai kedua tidak memperbarui; `_recalculate_sla_resolution_on_start()` menghitung ulang SLA dari durasi penuh dan menimpa `responded_on` setiap transisi Baru -> Sedang Dikerjakan (termasuk setelah Buka Kembali). Bagian terakhir ini belum diuji.
- Keputusan: apakah saat Buka Kembali `resolved_on`/`closed_on` dikosongkan, dan apakah `responded_on` hanya diisi sekali.

## Keputusan yang dibutuhkan

1. Arti "7 hari kerja" (bagian 2): A, B (63/18 Jam), atau C.
2. All-or-nothing vs carry-over (bagian 3).
3. Perpanjangan jeda: kalender atau jam kerja (bagian 4).
4. Perilaku Buka Kembali (bagian 5).

Perubahan kode (3, 4, 5) ada di `nexthd_ticket.py` / `business_hours.py` (area Desk, bukan portal), jadi lewat PR terpisah atau skrip yang dijalankan Efendy.
