# NextHD Web — Riwayat Bug Portal

> Khusus bug portal web (`www/nexthd`, `public/*/nexthd*`, `api/portal.py`).
> Bug Desk/DocType/workflow ada di `docs/BUG_HISTORY.md` dan file terkait.
>
> **Last updated:** 2026-09-30

Belum ada bug tercatat.

## Format Entri

```
### YYYY-MM-DD — judul singkat
- Gejala:
- Root cause:
- Fix:
- Pelajaran:
```

## Titik Rawan yang Perlu Diuji Tiap Tahap

| Area | Cek |
|---|---|
| Izin | Requester tidak bisa membaca tiket orang lain; Guest dialihkan ke login |
| Workflow | Perubahan status lewat `apply_workflow`, bukan set field |
| Side-effect | SLA dan notifikasi Telegram terpicu dari tiket buatan portal |
| Cache | Setelah ubah CSS/JS: `bench build --app nexthd`, naikkan `?v=`, hard refresh |
| Aset | Cek `curl -I /assets/nexthd/css/...` harus 200 bila halaman tampil polos |
