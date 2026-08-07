# NextHD API

Folder untuk whitelisted API methods (@frappe.whitelist()).

## Endpoint yang Tersedia

### Telegram Webhook
- File: `telegram_webhook.py` 
- Endpoint: `POST /api/method/nexthd.next_helpdesk.api.telegram_webhook.telegram_webhook` 
- Akses: `allow_guest=True` (dipanggil oleh Telegram Bot API)
- Fungsi: Menerima update dari Telegram (pesan, command /start, /help, /link)
  dan memproses linking akun serta command bot.

## Catatan
Daftarkan URL webhook ini ke Telegram Bot API menggunakan:
`https://api.telegram.org/bot<TOKEN>/setWebhook?url=<SITE_URL>/api/method/nexthd.next_helpdesk.api.telegram_webhook.telegram_webhook`
