# NextHD — Roadmap Fitur (Visi Jangka Menengah-Panjang)

> Berbeda dari `docs/SUMMARY.md §2` (open items operasional harian), file ini berisi
> **rencana fitur besar** yang belum masuk task konkret — visi ke mana NextHD akan
> dikembangkan setelah backlog inti (SLA/priority/foto) selesai.
>
> Prinsip yang dipegang: **"Best No 2", bukan sempurna.** Fokus ke fitur yang paling
> murah dikerjakan tapi paling kentara dampaknya, baru naik ke fitur struktural yang
> butuh desain lebih matang.
>
> **Dibuat:** 2026-08-23 17:15 WIB

---

## Kerangka Berpikir

ITSM yang "matang" (bukan cuma sistem tiket) biasanya dibedakan oleh 3 hal:

1. **Self-service yang benar-benar mengurangi beban Agent** — bukan cuma bikin tiket lebih
   gampang, tapi MENCEGAH tiket dengan kasih solusi mandiri
2. **Data yang bisa dipakai ambil keputusan** — bukan cuma nyimpan tiket, tapi kasih tahu
   "kenapa tiket kita banyak", tren apa yang naik
3. **Proses closed-loop** — tiket ditutup bukan cuma status berubah, ada verifikasi
   kepuasan & pembelajaran (Known Error/Knowledge Article) dari tiap insiden

---

## 🥇 Tier 1 — Quick Win, Prioritas Berikutnya

### 1. Knowledge Base Publik (`NextHD Knowledge Article`) — DocType BARU

> **Keputusan desain (23 Agustus 2026):** dibuat DocType terpisah dari `NextHD Known Error`,
> BUKAN reuse. Alasan: Known Error ditulis teknis untuk Agent (boleh sebut detail infra,
> config server), sedangkan Knowledge Article ditulis untuk orang awam (requester) —
> campur keduanya berisiko bocorkan detail sensitif ke publik atau bikin solusi awam jadi
> terlalu teknis untuk dipahami.

**Struktur field yang direncanakan:**

| Fieldname | Fieldtype | Keterangan |
|---|---|---|
| `title` | Data | Judul singkat, bahasa awam (misal "Cara Reset Password Email") |
| `category` | Link (NextHD Category) | Reuse kategori yang sudah ada |
| `content` | Text Editor | Isi langkah-langkah, boleh gambar/screenshot |
| `visibility` | Select: Publik / Internal | **Ini yang jawab kebutuhan "ada yang credential, ada yang publik"** — Publik = siapapun bisa baca tanpa login (via Web Form/portal), Internal = cuma role tertentu (Agent/Requester login) |
| `tags` | (pakai sistem tag bawaan Frappe, bukan field custom) | Untuk pencarian silang dengan tiket |
| `related_known_error` | Link (NextHD Known Error), opsional | Kalau artikel ini lahir dari insiden nyata |
| `related_problem` | Link (NextHD Problem), opsional | Sama, opsional |
| `status` | Select: Draft / Published / Perlu Ditinjau Ulang | Approval sederhana sebelum tampil publik |
| `view_count` | Int, read-only | Opsional — tracking artikel mana yang paling sering dibaca (bantu tahu solusi mandiri mana yang efektif) |
| `author` | Link (User), read-only | Auto-fill |
| `last_reviewed_on` | Date | Supaya artikel lama bisa ditandai "perlu dicek ulang masih relevan atau tidak" |

**Alur pemakaian:**
- Requester buka Web Form publik (tanpa login) → cari artikel berdasarkan kata kunci/kategori → coba solusi sendiri
- Kalau tidak berhasil → requester lanjut bikin tiket seperti biasa (tombol "Solusi tidak membantu, buat tiket" di halaman artikel)
- **Auto-suggest saat bikin tiket baru** (lihat Tier 1 poin 3) — search artikel Publik yang cocok dengan `subject` tiket yang sedang diketik, tampilkan sebagai saran sebelum submit

**Catatan permission:** artikel `visibility=Publik` perlu di-render lewat Frappe Web Page/Website
Route (bukan Desk form biasa) supaya bisa diakses tanpa login sama sekali — perlu dicek detail
teknisnya saat implementasi (kemungkinan pakai pola serupa `Web Form` yang sudah ada untuk
`/tiket-saya`, tapi untuk baca bukan submit).

---

### 2. Tag di Tiket

> **Keputusan desain:** pakai sistem tag bawaan Frappe (`Tag` DocType + `_user_tags`),
> BUKAN field custom baru. Frappe sudah sediakan UI autocomplete + filter-by-tag secara
> gratis kalau diaktifkan di DocType — jauh lebih murah daripada develop dari nol.

Implementasi: cukup pastikan `NextHD Ticket` punya `track_changes`/tag support aktif di
DocType settings (`is_tree`, dst — detail teknis dicek saat eksekusi). Tidak butuh DocType
atau field tambahan.

**Manfaat:** requester/agent bisa tag tiket bebas (misal "urgent-boss", "vendor-X",
"berulang") di luar struktur `category`/`priority` yang formal — berguna untuk pencarian
ad-hoc yang tidak terprediksi sebelumnya.

---

### 3. CSAT — Survei Kepuasan Pasca-Tiket Selesai

Requester dikirim 1 pertanyaan simpel (1-5 bintang + komentar opsional) via Telegram
begitu tiket masuk status "Selesai" — bagian dari closed-loop, kasih data objektif soal
kualitas layanan IT tanpa perlu nanya manual.

**Struktur:** field baru di `NextHD Ticket` — `csat_rating` (Int 1-5), `csat_comment`
(Small Text), `csat_submitted_on` (Datetime). Trigger kirim survei di hook
`on_update` saat status berubah ke "Selesai" (mirip pola notifikasi Telegram yang sudah ada).

---

### 4. Merge Tiket Duplikat

Kalau beberapa requester lapor masalah yang sama (misal "internet mati") dalam waktu
berdekatan, Agent bisa merge jadi 1 tiket induk — sisanya jadi child/reference, bukan
tiket terpisah yang bikin ribet tracking.

**Kemungkinan pendekatan:** field baru `merged_into` (Link ke NextHD Ticket lain) + status
tambahan "Digabung" — tiket yang digabung otomatis redirect notifikasi ke tiket induk.

---

### 5. Auto-Suggest Knowledge Article Saat Bikin Tiket Baru

Requester lagi isi form tiket baru → sistem search Knowledge Article (`visibility=Publik`)
yang mirip berdasarkan `subject`/`category` yang sedang diketik → tampilkan "mungkin ini
solusinya" sebelum tiket benar-benar dikirim.

**Bergantung pada:** fitur #1 (Knowledge Article) harus ada duluan.

---

### 6. Dashboard Trend Chart

Number Card sekarang cuma snapshot ("15 tiket baru"), belum ada tren. Tambah 1-2 chart
sederhana di Workspace: tren volume tiket per minggu, breakdown kategori mana yang paling
sering — berguna kalau NextHD ini nanti direview manajemen.

---

## 🥈 Tier 2 — Struktural, Butuh Desain Lebih Matang

| Fitur | Ringkasan |
|---|---|
| **Eskalasi otomatis** | Bukan cuma warning H-30 menit — kalau SLA benar-benar breach dan tiket masih belum direspon, otomatis reassign atau notify Agent Manager |
| **Approval matrix Change Request (CAB sederhana)** | 2 level approval: Agent Manager dulu, baru IT Manager kalau risiko tinggi — bukan CAB formal, cukup bertingkat |
| **Bulk actions** | Assign/tutup banyak tiket sekaligus — perlu begitu volume tiket naik |
| **Integrasi PRTG → auto-create tiket** | PRTG deteksi server down → otomatis bikin tiket tanpa nunggu ada yang lapor manual. Relevan karena Efendy sudah pakai PRTG untuk monitoring infra di luar NextHD |
| **Arsip/retensi tiket lama** | Kebijakan: tiket ditutup >1 tahun di-archive (bukan dihapus), jaga performa list-view |

---

## 🥉 Tier 3 — Nice to Have, Belum Prioritas

| Fitur | Kenapa Bisa Nunggu |
|---|---|
| Multi-channel (email-to-ticket, WhatsApp bot) | Telegram sudah cukup untuk internal — baru relevan kalau ada requester eksternal |
| Custom SLA per Team (bukan cuma per Priority) | Baru dibutuhkan kalau tiap tim punya standar yang beda jauh |
| Gamification (leaderboard Agent) | Fun tapi bukan esensial untuk tim kecil |

---

## Urutan Eksekusi yang Disarankan

Setelah fitur foto (item W, sedang dikerjakan Devin) selesai dan terverifikasi:

1. **Knowledge Article + Tag** (fitur #1 + #2) — fondasi dulu, karena fitur #5 (auto-suggest)
   bergantung ke #1
2. **CSAT** (fitur #3) — independen, bisa paralel dengan #1
3. **Dashboard Trend Chart** (fitur #6) — independen, quick win terpisah
4. **Merge Tiket Duplikat** (fitur #4) — bisa nunggu sampai memang ada kejadian nyata yang
   butuh ini (baru kepikiran betapa perlunya biasanya setelah kejadian, bukan sebelumnya)
5. Tier 2 — nunggu sinyal nyata dibutuhkan, jangan dikerjakan preventif dulu

---

*Dokumen ini dikelola oleh Claude. Update kalau ada keputusan desain baru atau fitur di
tier manapun sudah mulai masuk task konkret (pindahkan ke `SUMMARY.md §2` begitu mulai
dikerjakan Devin).*
