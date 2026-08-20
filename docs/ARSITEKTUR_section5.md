## 5. Sistem User Tanpa Email

### Alasan
Sistem hanya untuk karyawan internal. Frappe mewajibkan field email, tapi email nyata tidak dipakai — hosting hanya menyediakan kuota terbatas untuk email asli, tidak cukup untuk semua karyawan.

### Pendekatan Teknis

```
1. Saat buat User baru:
   - Field "email" diisi otomatis via hook:
     format: {username}@ciptamebel.co.id   ← DIUBAH 2026-08-20, sebelumnya @noemail.internal
     contoh: efendy@ciptamebel.co.id
   - Domain ini SAMA dengan domain kantor asli, TAPI mailbox-nya tidak eksis/tidak bisa
     terima mail sungguhan — dipilih supaya alamat terlihat resmi/seragam, bukan supaya
     berfungsi sebagai email beneran
   - Set "Send Welcome Email" = False

2. Login:
   - User login pakai Username (bukan email)
   - Frappe native support ini via field "username" di User doctype

3. Reset Password:
   - TIDAK bisa via "forgot password" email (karena mailbox dummy tidak menerima mail)
   - Solusi: Admin reset manual dari backend:
     bench --site desk.ciptamebel.co.id set-password <username>
   - Alternatif lanjutan: OTP reset via Telegram bot
```

**File:** `nexthd/next_helpdesk/utils/email_helper.py` (update format domain diperlukan, cek isi file saat implementasi berikutnya)
**Hook:** `before_insert` pada Doctype **User**

---
