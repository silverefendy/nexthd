# NextHD User Profile

Extend informasi User bawaan Frappe — kunci untuk integrasi Telegram & user tanpa email.

## Field
| Field | Fieldtype | Keterangan |
|---|---|---|
| user | Link -> User | Relasi 1-1 |
| telegram_chat_id | Data | Diisi via bot /start command |
| telegram_username | Data | Opsional |
| preferred_language | Select | ID / EN, default ID |
| department | Data | |
| phone_internal | Data | |

## Catatan Implementasi PENTING
- Ini doctype kunci untuk fitur "user tanpa email" — lihat NEXTHD_SPEC.md bagian 4
- Hook before_insert pada Doctype User (BUKAN di sini) untuk auto-generate email dummy
  format: {username}@noemail.internal
- Halaman "Link Telegram Account" perlu dibuat di sini (custom page atau client script)
