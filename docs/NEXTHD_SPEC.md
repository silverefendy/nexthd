# NextHD — Spesifikasi Teknis Lengkap
### Custom ITSM/ITIL App di atas Frappe Framework
*Dibuat untuk: Efendy (CML) | Repo: silverefendy/nexthd | Tanggal: 2026-08-07*

---

## 1. RINGKASAN PROJECT

| Item | Detail |
|---|---|
| **Nama App** | NextHD |
| **Tujuan** | Sistem ITSM internal (Incident, Problem, Change, Asset, Known Error, Service Catalog) untuk tim IT CML |
| **Basis** | Frappe Framework murni (BUKAN ERPNext — bisa ditambah ERPNext kapan saja nanti tanpa migrasi) |
| **User** | Karyawan internal saja (belum ada customer eksternal) |
| **Autentikasi** | Username-based login, TANPA email asli (email dummy internal sebagai placeholder wajib Frappe) |
| **Notifikasi** | Telegram Bot (utama) + In-app notification (bawaan Frappe, sebagai pelengkap) — TIDAK pakai email sama sekali |
| **Bahasa UI** | Bahasa Indonesia (default, istilah familiar untuk orang lapangan) + opsi English (via Frappe Translation) |
| **Cakupan ITIL** | Incident, Problem, Change, Known Error, Asset/CMDB, Service Catalog — skip Release/Capacity/Financial Management |
| **Server** | VM/server baru, Ubuntu Server (spesifikasi setara cml-helpdesk), disk 40GB (sementara) |
| **Repo Git** | `silverefendy/nexthd`, branch `main` |
| **Alur Development** | Claude (kerangka & spesifikasi) → Devin (implementasi) → Claude (finishing, bugfix, review) |

---

## 2. ARSITEKTUR INFRASTRUKTUR

```
Internet → VPS/Server Baru (nginx + SSL)
              ↓
        Frappe Framework (bench)
              ↓
        Site: nexthd.ciptamebel.co.id (usulan, sesuaikan)
              ↓
        App: nexthd (custom, dari repo silverefendy/nexthd)
              ↓
        Database: MariaDB
              ↓
   Notifikasi keluar → Telegram Bot API (api.telegram.org)
```

### Kebutuhan Server (mengikuti pola cml-helpdesk)
- Ubuntu Server 24.04 LTS
- RAM: minimal 4GB + swap 4GB (sesuaikan kalau load tinggi nanti)
- Disk: 40GB (sementara, sesuai keputusan)
- Python 3.11+ (via deadsnakes PPA jika perlu versi spesifik)
- Node.js 18/20 (via NVM)
- MariaDB 10.11+
- Supervisor untuk process management
- Nginx + Certbot untuk SSL
- **Firewall: pastikan outbound HTTPS ke `api.telegram.org` tidak diblok** (kebutuhan notifikasi)

### Catatan Instalasi
- Install **Frappe Framework + bench** dulu (`bench init`)
- **JANGAN** install app `erpnext` — cukup `frappe` sebagai base
- Buat site baru, lalu `bench get-app` untuk app `nexthd` dari repo GitHub
- Struktur ini memungkinkan `bench get-app erpnext` ditambahkan kapan saja di masa depan tanpa migrasi data

---

## 3. STRUKTUR DOCTYPE

### 3.1 Modul Inti (Core Transactional)

#### **NextHD Ticket** (pengganti konsep HD Ticket, mencakup Incident + Service Request)
| Field | Tipe | Keterangan |
|---|---|---|
| `ticket_type` | Select | Insiden / Permintaan Layanan |
| `subject` | Data | Judul singkat |
| `description` | Text Editor | Detail masalah/permintaan |
| `status` | Select | Baru → Sedang Dikerjakan → Menunggu User → Selesai → Ditutup |
| `priority` | Select | Kritis / Tinggi / Sedang / Rendah |
| `category` | Link → NextHD Category | Kategori masalah (Hardware, Software, Network, dst) |
| `requested_by` | Link → User | Pelapor |
| `assigned_to` | Link → User | Agent yang menangani |
| `team` | Link → NextHD Team | Tim penanggung jawab |
| `sla_response_by` | Datetime | Auto-calculated dari SLA Policy |
| `sla_resolution_by` | Datetime | Auto-calculated dari SLA Policy |
| `resolved_on` | Datetime | Diisi otomatis saat status jadi Selesai |
| `closed_on` | Datetime | Diisi otomatis saat status jadi Ditutup |
| `related_problem` | Link → NextHD Problem | Opsional, jika terkait Problem yang sudah ada |
| `attachments` | Attach | Lampiran (foto, dokumen) |
| Numbering | Auto | `TKT-2026-####` |

**Komunikasi/Reply:** pakai **Frappe Comment/Timeline native** (bukan email) — setiap reply Agent atau User muncul di timeline dokumen, trigger notifikasi Telegram otomatis via hook.

#### **NextHD Problem**
Struktur sama seperti `IT Problem` versi sebelumnya, disesuaikan:
| Field | Tipe |
|---|---|
| `title` | Data |
| `status` | Select: Terbuka → Investigasi → Known Error → Selesai → Ditutup |
| `root_cause` | Text Editor |
| `related_tickets` | Table → NextHD Problem Ticket (child table, link ke NextHD Ticket) |
| Numbering | `PRB-2026-####` |

#### **NextHD Change Request**
| Field | Tipe |
|---|---|
| `title` | Data |
| `status` | Select: Draft → Diajukan → Direview → Disetujui/Ditolak → Implementasi → Selesai → Ditutup |
| `change_type` | Select: Standard / Normal / Emergency |
| `risk_level` | Select: Rendah / Sedang / Tinggi |
| `related_problem` | Link → NextHD Problem |
| `implementation_plan` | Text Editor |
| `rollback_plan` | Text Editor |
| Numbering | `CHG-2026-####` |

#### **NextHD Known Error**
| Field | Tipe |
|---|---|
| `title` | Data |
| `symptom` | Text Editor |
| `workaround` | Text Editor |
| `related_problem` | Link → NextHD Problem |
| Numbering | `KE-2026-####` |

#### **NextHD Asset** (CMDB sederhana)
| Field | Tipe |
|---|---|
| `asset_name` | Data |
| `asset_type` | Select: Laptop / PC / Server / Network Device / Printer / dst |
| `location` | Data |
| `assigned_to` | Link → User |
| `status` | Select: Aktif / Rusak / Diperbaiki / Dihapus |
| `purchase_date`, `warranty_until` | Date |
| Numbering | `AST-2026-####` |

#### **NextHD Service Catalog**
| Field | Tipe |
|---|---|
| `service_name` | Data |
| `description` | Text Editor |
| `category` | Select |
| `default_sla` | Link → NextHD SLA Policy |
| Numbering | `SVC-2026-####` |

---

### 3.2 Modul Pendukung (Supporting)

#### **NextHD User Profile** (extend informasi User bawaan Frappe)
| Field | Tipe | Keterangan |
|---|---|---|
| `user` | Link → User | 1-1 dengan User Frappe |
| `telegram_chat_id` | Data | Diisi otomatis saat user link akun via bot `/start` |
| `telegram_username` | Data | Opsional, untuk referensi |
| `preferred_language` | Select: ID / EN | Default ID |
| `department` | Data | |
| `phone_internal` | Data | |

#### **NextHD Team**
| Field | Tipe |
|---|---|
| `team_name` | Data |
| `members` | Table (link ke User) |

#### **NextHD Category**
Simple lookup: `category_name`, `parent_category` (opsional untuk sub-kategori)

#### **NextHD SLA Policy**
| Field | Tipe |
|---|---|
| `priority` | Select |
| `response_time_minutes` | Int |
| `resolution_time_minutes` | Int |
| `business_hours` | Link → NextHD Business Hours |

#### **NextHD Business Hours**
Hari, jam mulai, jam selesai (mengikuti pola jam kerja CML: Senin-Sabtu)

#### **NextHD Settings** (Doctype Single)
| Field | Tipe | Keterangan |
|---|---|---|
| `telegram_bot_token` | Password | Token dari @BotFather |
| `telegram_bot_username` | Data | |
| `default_language` | Select | |
| `enable_telegram_notification` | Check | |

---

## 4. SISTEM USER TANPA EMAIL

### Pendekatan Teknis
```
1. Saat buat User baru:
   - Field wajib "email" diisi otomatis via hook:
     format: {username}@noemail.internal
     contoh: efendy@noemail.internal
   - Field "Username" (terpisah dari email) diisi manual dengan nama login yang diinginkan
   - Set "Send Welcome Email" = False (karena email tidak nyata)

2. Login:
   - User login pakai Username (bukan format email)
   - Frappe native support ini via field "username" di User doctype

3. Reset Password:
   - TIDAK bisa via "forgot password" email (karena email dummy)
   - Solusi: Admin/Agent Manager reset manual dari backend
   - Alternatif lanjutan (opsional, fase berikutnya): OTP reset via Telegram bot
```

### Hook yang Perlu Dibuat (untuk Devin)
- `before_insert` pada Doctype **User**: auto-generate email dummy jika field email kosong dan user dibuat dari form NextHD (bukan dari Administrator biasa)
- Custom halaman "Buat User Baru" yang menyederhanakan proses ini (supaya Agent Manager tidak perlu mikir soal field email dummy — otomatis di-generate di belakang layar)

---

## 5. SISTEM NOTIFIKASI TELEGRAM

### Alur Setup Bot
```
1. Buat bot via @BotFather di Telegram → dapat Bot Token
2. Simpan token di NextHD Settings
3. User baru harus "link" akun:
   - User klik link t.me/NamaBotAnda dari NextHD (ditampilkan di halaman profile)
   - User kirim /start ke bot
   - Bot minta user masukkan Username NextHD mereka untuk verifikasi
   - chat_id disimpan ke NextHD User Profile
4. Setelah linked, semua notifikasi otomatis terkirim ke Telegram user tsb
```

### Trigger Notifikasi (via Frappe hooks — `doc_events`)
| Event | Notifikasi ke | Isi Pesan |
|---|---|---|
| Ticket baru dibuat | Agent/Team terkait | "Tiket baru: [subject] - Prioritas: [priority]" |
| Ticket di-assign | Agent yang di-assign | "Anda ditugaskan tiket TKT-2026-XXXX" |
| Ada reply/comment baru | Pihak lain (requester/agent) | "Ada balasan baru di tiket TKT-2026-XXXX" |
| Status berubah jadi Selesai | Requester | "Tiket Anda telah diselesaikan, mohon konfirmasi" |
| SLA mendekati breach (H-30 menit) | Agent + Manager | "⚠️ SLA tiket TKT-2026-XXXX akan terlampaui" |
| Change Request perlu approval | Approver terkait | "Ada Change Request menunggu persetujuan" |

### Implementasi Teknis (untuk Devin)
- Python module `nexthd/utils/telegram.py` — fungsi `send_telegram_message(chat_id, message)` pakai library `requests` ke endpoint `https://api.telegram.org/bot{TOKEN}/sendMessage`
- Daftarkan di `hooks.py` pada `doc_events` untuk trigger otomatis
- Gunakan **Background Jobs** (Frappe `enqueue`) untuk kirim notifikasi async — supaya tidak memperlambat proses simpan tiket

---

## 6. WORKFLOW (Status Transition)

### Workflow 1: NextHD Ticket
```
Baru → Sedang Dikerjakan → [Menunggu User ⇄ Sedang Dikerjakan] → Selesai → Ditutup
                                                                        ↓
                                                              (User bisa Buka Kembali)
```
| Role yang bisa ubah status | Aksi |
|---|---|
| Agent | Baru → Sedang Dikerjakan, → Menunggu User, → Selesai |
| Requester (User) | Selesai → Ditutup (konfirmasi) ATAU Selesai → Baru (buka kembali) |
| Agent Manager | Bisa override semua transisi |

### Workflow 2: NextHD Problem
```
Terbuka → Investigasi → Known Error → Selesai → Ditutup
                ↓
            Selesai (langsung, jika root cause ditemukan tanpa perlu status Known Error)
```

### Workflow 3: NextHD Change Request
```
Draft → Diajukan → Direview → [Disetujui/Ditolak] → Implementasi → Selesai → Ditutup
```

---

## 7. ROLE & PERMISSION MATRIX

| Role | Ticket | Problem | Change | Asset | Known Error | Service Catalog |
|---|---|---|---|---|---|---|
| **Karyawan (Requester)** | Buat, Baca (punya sendiri), Comment | Baca (jika terkait) | - | - | Baca | Baca |
| **Agent** | Baca/Tulis semua, Assign | Baca/Tulis | Baca/Tulis (draft) | Baca/Tulis | Baca/Tulis | Baca |
| **Agent Manager** | Full akses | Full akses | Full akses + Approve | Full akses | Full akses | Full akses |
| **IT Manager** | Full akses | Full akses | Full akses + Approve | Full akses | Full akses | Full akses |
| **IT Auditor** | Baca semua | Baca semua | Baca semua | Baca semua | Baca semua | Baca semua |

---

## 8. RENCANA IMPLEMENTASI (untuk Devin)

### Tahap 1 — Fondasi
- [ ] Setup app skeleton `nexthd` (bench new-app)
- [ ] Setup hooks.py dasar (app_name, doc_events kosong dulu)
- [ ] Buat semua Doctype di atas (tanpa workflow dulu)
- [ ] Setup Role & Permission dasar

### Tahap 2 — User Tanpa Email
- [ ] Hook auto-generate email dummy
- [ ] Custom form/halaman buat user baru yang simple
- [ ] Testing login via username

### Tahap 3 — Telegram Integration
- [ ] Setup bot, module `telegram.py`
- [ ] Halaman "Link Telegram Account" untuk user
- [ ] Hook notifikasi untuk semua event di tabel Section 5

### Tahap 4 — Workflow
- [ ] Implementasi 3 workflow (Ticket, Problem, Change) sesuai Section 6

### Tahap 5 — UI Kustomisasi
- [ ] Workspace utama (dashboard ringkas)
- [ ] List View & Kanban View untuk Ticket
- [ ] Terjemahan label ke Bahasa Indonesia (Section 9)

### Tahap 6 — SLA & Business Hours
- [ ] Setup SLA Policy per prioritas
- [ ] Auto-calculate SLA response/resolution time
- [ ] Job scheduler untuk cek SLA breach warning

### Tahap 7 — Testing End-to-End
- [ ] Alur: User buat tiket → Agent kerjakan → Notifikasi tiap tahap → Selesai
- [ ] Alur: Ticket → eskalasi ke Problem → Change → Selesai

---

## 9. BAHASA INDONESIA — LABEL REFERENSI

| Istilah Inggris (internal/dev) | Label Indonesia (tampil ke user) |
|---|---|
| Ticket | Tiket |
| Priority | Prioritas |
| Status | Status |
| Open | Baru |
| In Progress | Sedang Dikerjakan |
| Pending User | Menunggu User |
| Resolved | Selesai |
| Closed | Ditutup |
| Assigned To | Ditugaskan Ke |
| Requested By | Dilaporkan Oleh |
| Category | Kategori |
| Problem | Masalah |
| Root Cause | Akar Masalah |
| Known Error | Kesalahan yang Diketahui |
| Change Request | Permintaan Perubahan |
| Asset | Aset |
| Critical / High / Medium / Low | Kritis / Tinggi / Sedang / Rendah |

> Catatan untuk Devin: gunakan Frappe Translation system (`bench --site [site] build-message-files` + file `.csv` translasi) supaya label ini bisa di-maintain terpisah dari kode, dan gampang diubah ke Bahasa Inggris untuk user yang prefer itu (via field `preferred_language` di User Profile).

---

## 10. CATATAN & RISIKO

> ⚠️ **Reset password tanpa email** — perlu SOP manual: Agent Manager reset password dari backend (`bench --site [site] set-password [username]`) atau buat halaman admin khusus untuk ini.

> ⚠️ **Backup rutin** — karena ini sistem baru dari nol, pastikan setup backup database (`bench backup`) terjadwal via cron sejak awal, jangan tunggu sampai ada insiden kehilangan data (belajar dari kasus folder AD yang hilang sebelumnya).

> ⚠️ **Telegram sebagai satu-satunya kanal notifikasi** — pastikan ada fallback in-app notification (bell icon bawaan Frappe) untuk jaga-jaga kalau Telegram API down atau user belum link akun.

> 💡 **Untuk Devin:** dokumen ini adalah kerangka arsitektur, bukan kode final. Devin punya keleluasaan menyesuaikan detail implementasi teknis (nama variabel, struktur folder internal) selama mengikuti struktur Doctype, workflow, dan alur bisnis yang didefinisikan di sini. Setelah Devin selesai, akan direview dan disempurnakan lagi.

---

*Dokumen ini dibuat oleh Claude untuk keperluan development app NextHD. Untuk pertanyaan lebih lanjut terkait spesifikasi ini, kembali ke sesi Claude dengan referensi dokumen ini.*
