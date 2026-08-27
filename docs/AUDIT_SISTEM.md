# NextHD — Audit Sistem (Script Pemeriksaan Lengkap)

> Script audit menyeluruh untuk verifikasi kesehatan instalasi NextHD — schema drift,
> Workspace, Workflow master data, SLA, fixtures, dan lainnya. Dipakai kapan saja perlu
> memastikan server produksi konsisten dengan kode di repo, atau sebelum merencanakan
> instalasi ke server baru.
>
> **Dibuat:** 2026-08-22 19:30 WIB
> **Alasan dibuat:** Efendy tanya soal cara instalasi NextHD ke server Frappe lain — ternyata
> Frappe tidak pakai Alembic/migration script manual (beda dari SQLAlchemy), melainkan skema
> deklaratif dari file DocType JSON. Risiko utamanya adalah **schema drift**: field yang
> pernah ditambah manual via SQL langsung ke server produksi (pola debug cepat yang dipakai
> di project ini, lihat `POLA_KERJA_DAN_BUG.md`) bisa saja tidak tersinkron balik ke file
> JSON di repo — kalau itu terjadi, field tersebut akan **hilang tanpa error apapun** saat
> install ke server baru. Script ini mendeteksi drift semacam itu, plus cek 13 area lain
> yang riwayatnya pernah bermasalah di project ini.

---

## Cara Pakai

1. SSH ke server (`ssh it@10.1.0.16` atau IP server produksi terkini)
2. Paste seluruh blok command di bawah (heredoc + sed + jalankan + simpan hasil ke file)
3. **WAJIB cek output `cat -A | head -5` dulu** sebelum lanjut — pastikan baris 2-5 diawali
   `^I` (tab). Kalau tidak, JANGAN lanjut ke `bench console`, laporkan ke Claude dulu.
4. Hasil lengkap tersimpan di `/home/it/audit_result.txt` — bisa dibuka lagi kapan saja,
   tidak hilang walau sesi SSH terputus
5. Kirim isi `audit_result.txt` ke Claude untuk diinterpretasi dan disusun rencana
   perbaikan `install.py`/patch berdasarkan temuan aktual

---

## Script Lengkap

```bash
cat > /home/it/audit_nexthd.py << 'EOF'
def main_check():
    print("=====================================================")
    print("NEXTHD FULL AUDIT - " + str(frappe.utils.now()))
    print("=====================================================")
    doctypes_to_check = [
        "NextHD Ticket", "NextHD Problem", "NextHD Change Request",
        "NextHD Asset", "NextHD Known Error", "NextHD SLA Policy",
        "NextHD Business Hours", "NextHD Holiday", "NextHD Ticket Waiting Log",
        "NextHD Team", "NextHD Category", "NextHD Settings", "NextHD User Profile"
    ]
    print("")
    print("=== 1. SCHEMA DRIFT: DocField (JSON) vs Kolom Fisik Database ===")
    for dt in doctypes_to_check:
        if not frappe.db.exists("DocType", dt):
            print("[MISSING DOCTYPE] " + dt + " tidak ada sama sekali")
            continue
        table_name = "tab" + dt
        try:
            db_cols = frappe.db.sql("SHOW COLUMNS FROM `" + table_name + "`", as_dict=True)
            db_col_names = set([c.Field for c in db_cols])
        except Exception as e:
            print("[ERROR] gagal DESCRIBE " + table_name + ": " + str(e))
            continue
        meta = frappe.get_meta(dt)
        json_field_names = set([f.fieldname for f in meta.fields])
        standard_cols = set(["name", "owner", "creation", "modified", "modified_by", "docstatus", "idx", "_user_tags", "_comments", "_assign", "_liked_by"])
        orphan_in_db = db_col_names - json_field_names - standard_cols
        missing_in_db = json_field_names - db_col_names
        status = "OK"
        if orphan_in_db or missing_in_db:
            status = "DRIFT DITEMUKAN"
        print("[" + status + "] " + dt)
        if orphan_in_db:
            print("    Kolom ADA di DB tapi TIDAK ADA di JSON (siluman, tidak akan tercopy ke install baru): " + str(sorted(orphan_in_db)))
        if missing_in_db:
            print("    Field ADA di JSON tapi TIDAK ADA di DB (akan otomatis dibuat saat migrate, cuma perlu migrate dulu): " + str(sorted(missing_in_db)))
    print("")
    print("=== 2. WORKFLOW: Master Data & Jumlah Transisi ===")
    wf_state_count = frappe.db.count("Workflow State")
    wf_action_count = frappe.db.count("Workflow Action Master")
    print("Workflow State (master global): " + str(wf_state_count) + " record")
    print("Workflow Action Master (master global): " + str(wf_action_count) + " record")
    print("CATATAN: kedua master ini TIDAK ada di fixtures (sengaja), harus dibuat manual di install baru")
    for wf_name in ["NextHD Ticket", "NextHD Problem", "NextHD Change Request"]:
        if not frappe.db.exists("Workflow", wf_name):
            print("[MISSING] Workflow " + wf_name + " tidak ada")
            continue
        is_active = frappe.db.get_value("Workflow", wf_name, "is_active")
        trans_count = frappe.db.count("Workflow Transition", {"parent": wf_name})
        dup_idx0 = frappe.db.count("Workflow Transition", {"parent": wf_name, "idx": 0})
        print("Workflow '" + wf_name + "': is_active=" + str(is_active) + ", transitions=" + str(trans_count) + ", idx=0 (indikasi duplikat)=" + str(dup_idx0))
    print("")
    print("=== 3. WORKSPACE & SIDEBAR ===")
    ws_exists = frappe.db.exists("Workspace", "NextHD")
    print("Workspace 'NextHD' ada: " + str(bool(ws_exists)))
    sidebar_items = frappe.db.sql("SELECT wsi.label, wsi.link_to FROM `tabWorkspace Sidebar Item` wsi WHERE wsi.parent = 'NextHD'", as_dict=True)
    print("Jumlah item sidebar: " + str(len(sidebar_items)))
    for item in sidebar_items:
        print("    - " + str(item.label) + " -> " + str(item.link_to))
    holiday_in_sidebar = any("Holiday" in (i.label or "") or "Holiday" in (i.link_to or "") for i in sidebar_items)
    print("Holiday ada di sidebar: " + str(holiday_in_sidebar))
    print("")
    print("=== 4. DESKTOP ICON ===")
    icon = frappe.db.get_value("Desktop Icon", {"app": "nexthd"}, ["name", "link_type", "link_to", "standard"], as_dict=True)
    print("Desktop Icon nexthd: " + str(icon))
    print("")
    print("=== 5. NAVIGASI TERKUNCI (HANDOFF.md - jangan sampai berubah tanpa sengaja) ===")
    default_app_system = frappe.db.get_single_value("System Settings", "default_app")
    print("System Settings default_app: " + str(default_app_system) + " (harus: nexthd)")
    support_user_app = frappe.db.get_value("User", "support@ciptamebel.co.id", "default_app")
    print("User support@ciptamebel.co.id default_app: " + str(support_user_app) + " (harus: nexthd)")
    print("")
    print("=== 6. SLA POLICY - Bandingkan dengan SOP Final (19 Agustus 2026) ===")
    expected_sla = {
        "Kritis": {"response_time_minutes": 15, "resolution_time_minutes": 60, "is_24x7": 1},
        "Tinggi": {"response_time_minutes": 30, "resolution_time_minutes": 240, "is_24x7": 0},
        "Sedang": {"response_time_minutes": 60, "resolution_time_minutes": 2880, "is_24x7": 0},
        "Rendah": {"response_time_minutes": 120, "resolution_time_minutes": 10080, "is_24x7": 0}
    }
    for priority, expected in expected_sla.items():
        actual = frappe.db.get_value("NextHD SLA Policy", priority, ["response_time_minutes", "resolution_time_minutes", "is_24x7"], as_dict=True)
        if not actual:
            print("[MISSING] NextHD SLA Policy '" + priority + "' tidak ada")
            continue
        match = (actual.response_time_minutes == expected["response_time_minutes"] and actual.resolution_time_minutes == expected["resolution_time_minutes"] and actual.is_24x7 == expected["is_24x7"])
        status = "OK" if match else "TIDAK COCOK SOP"
        print("[" + status + "] " + priority + ": aktual=" + str(actual) + " | seharusnya=" + str(expected))
    print("")
    print("=== 7. BUSINESS HOURS ===")
    bh_count = frappe.db.count("NextHD Business Hours")
    print("Jumlah record Business Hours: " + str(bh_count) + " (harus 7, satu per hari)")
    bh_all = frappe.db.get_list("NextHD Business Hours", fields=["day", "start_time", "end_time", "is_working_day"])
    for row in bh_all:
        print("    " + str(row.day) + ": " + str(row.start_time) + "-" + str(row.end_time) + " working=" + str(row.is_working_day))
    print("")
    print("=== 8. DATA MASTER LAIN (tidak ter-fixture, cek manual perlu diisi di install baru) ===")
    print("NextHD Team: " + str(frappe.db.count("NextHD Team")) + " record")
    print("NextHD Category: " + str(frappe.db.count("NextHD Category")) + " record")
    print("NextHD Holiday: " + str(frappe.db.count("NextHD Holiday")) + " record")
    print("")
    print("=== 9. ROLES ===")
    required_roles = ["Requester", "Agent", "Agent Manager", "IT Manager", "IT Auditor"]
    for role in required_roles:
        exists = frappe.db.exists("Role", role)
        print("Role '" + role + "': " + ("ADA" if exists else "TIDAK ADA"))
    print("")
    print("=== 10. NEXTHD SETTINGS ===")
    settings_name = frappe.db.get_value("NextHD Settings", {}, "name")
    if settings_name:
        token_set = bool(frappe.db.get_value("NextHD Settings", settings_name, "telegram_bot_token"))
        enabled = frappe.db.get_value("NextHD Settings", settings_name, "enable_telegram_notification")
        print("Record: " + str(settings_name) + ", token terisi=" + str(token_set) + ", enabled=" + str(enabled))
    else:
        print("[MISSING] NextHD Settings record tidak ada")
    print("")
    print("=== 11. CLIENT SCRIPTS (harus ada di fixtures) ===")
    required_scripts = ["a258744559", "cs_known_error_from_problem", "cs_change_request_from_problem", "cs_change_request_from_known_error", "cs_change_request_from_asset"]
    for script_name in required_scripts:
        exists = frappe.db.exists("Client Script", script_name)
        print("Client Script '" + script_name + "': " + ("ADA" if exists else "TIDAK ADA"))
    print("")
    print("=== 12. WEB FORM ===")
    wf_form = frappe.db.get_value("Web Form", "Tiket Saya", ["route", "published"], as_dict=True)
    print("Web Form 'Tiket Saya': " + str(wf_form))
    print("")
    print("=== 13. NAMING SERIES - Cek Format YY.MM di Setiap DocType ===")
    naming_dts = ["NextHD Ticket", "NextHD Problem", "NextHD Change Request", "NextHD Asset", "NextHD Known Error"]
    for dt in naming_dts:
        opts = frappe.db.get_value("DocField", {"parent": dt, "fieldname": "naming_series"}, "options")
        print(dt + " naming_series options: " + str(opts))
    print("")
    print("=== 14. FITUR FOTO (item W, cek apakah sudah di-push Devin) ===")
    photo_dt_exists = frappe.db.exists("DocType", "NextHD Photo")
    photo_link_dt_exists = frappe.db.exists("DocType", "NextHD Photo Link")
    print("DocType NextHD Photo ada: " + str(bool(photo_dt_exists)))
    print("DocType NextHD Photo Link ada: " + str(bool(photo_link_dt_exists)))
    print("")
    print("=====================================================")
    print("AUDIT SELESAI")
    print("=====================================================")

main_check()
EOF
sed -i 's/\r$//' /home/it/audit_nexthd.py && \
sed -i 's/^    /\t/' /home/it/audit_nexthd.py && \
cat -A /home/it/audit_nexthd.py | head -5 && \
bench --site desk.ciptamebel.co.id console < /home/it/audit_nexthd.py > /home/it/audit_result.txt 2>&1 && \
cat /home/it/audit_result.txt
```

---

## Panduan Interpretasi Hasil

| Bagian | Kalau Ditemukan Masalah, Artinya |
|---|---|
| §1 Schema Drift | `[DRIFT DITEMUKAN]` + "Kolom ADA di DB tapi TIDAK ADA di JSON" = field siluman, akan **hilang** di install baru. Paling kritis untuk difix duluan |
| §1 "Field ADA di JSON tapi TIDAK ADA di DB" | Tidak berbahaya — tinggal `bench migrate` di server ini, Frappe akan otomatis bikin kolomnya |
| §2 Workflow | `is_active=0` atau jumlah transisi tidak sesuai (Ticket 7, Problem 6, CR 8) = ada yang belum di-migrate/rusak. `idx=0` count > 0 = ada duplikat belum dibersihkan. **Lihat catatan penting di "Update 25 Agustus 2026" di bawah — dedup di DB saja TIDAK CUKUP kalau fixture di repo juga masih kotor** |
| §3 Workspace/Sidebar | `Workspace Sidebar Item` ini adalah tabel **turunan/auto-generate**, bukan sumber asli — lihat "Update 25 Agustus 2026 (Lanjutan)" di bawah. Sumber asli yang harus dicek/diedit adalah `Workspace.links`. **PENTING (26 Agustus):** jangan pernah kosongkan `Workspace.links` tanpa langsung mengisi ulang di transaksi yang sama — pernah menyebabkan seluruh sidebar hilang total, lihat "Update 26 Agustus 2026 (Lanjutan)". **PENTING (27 Agustus):** kalau kasusnya adalah workspace LAIN (bukan NextHD sendiri) yang perlu 1 link sidebar mengarah ke sana, jalur yang benar bukan `Workspace.links` — lihat "Update 27 Agustus 2026" di bawah soal `Workspace Sidebar` + `export_sidebar()` dan jebakan lokasi file |
| §5 Navigasi Terkunci | Kalau bukan `nexthd`, ini pelanggaran aturan kunci di `HANDOFF.md` — perlu dikoreksi manual |
| §6 SLA Policy | `[TIDAK COCOK SOP]` = nilai di database beda dari SOP final 19 Agustus — kemungkinan besar karena instalasi baru pakai `install.py` yang belum diperbaiki (lihat catatan bug di bawah) |
| §14 Fitur Foto | Kalau `False` untuk kedua DocType, berarti pekerjaan Devin soal fitur foto (item W) memang belum ter-push — konsisten dengan temuan sebelumnya |

---

## Status Bug `install.py` — SUDAH DIPERBAIKI (24 Agustus 2026)

~~`nexthd/install.py` fungsi `create_default_sla_policies()` masih pakai nilai SLA versi LAMA~~

**Update:** Sudah diperbaiki dan di-push ke `main` (commit `b3a24b2`, merged ke `2d795b9`) pada 24 Agustus 2026. Nilai sekarang: Kritis 15/60 `is_24x7=1`, Tinggi 30/240, Sedang 60/2880, Rendah 120/10080 — sesuai SOP final 19 Agustus. Instalasi baru dari kode `main` saat ini sudah akan dapat SLA yang benar sejak awal, tidak perlu patch manual lagi.

---

## Update 24 Agustus 2026 — Verifikasi Ringan Pasca-Perbaikan Sesi Ini

> **Waktu:** 24 Agustus 2026 (jam tidak tercatat di log sesi — kalau perlu presisi menit,
> cek timestamp asli di riwayat chat Claude)
> **Konteks:** Script ini dipakai untuk verifikasi cepat setelah rangkaian perbaikan sesi
> 24 Agustus: fix sidebar "NextHD Photo" yang gagal muncul (root cause: `import_file_by_path`
> tidak sync child table `links`, harus di-append manual via `doc.save()`), dedup Workflow
> Transition yang terduplikasi 4× di ketiga workflow (Ticket 28→7, Problem 24→6, Change
> Request 32→8 — root cause diduga saat itu: `Workflow Action Master` "Convert to Known Error"
> hilang, bikin `wf.save()` gagal validasi sampai master dibuat ulang), penambahan 8 Cuti
> Bersama 2026, dan patch `install.py` di atas.
>
> **⚠️ Koreksi 25 Agustus:** dugaan root cause di atas (Workflow Action Master hilang) ternyata
> BUKAN akar masalah sebenarnya — lihat "Update 25 Agustus 2026" di bawah untuk root cause yang
> terkonfirmasi dan perbaikan permanen.
>
> Lebih ringan dari script Full Audit di atas — cuma verifikasi 9 titik spesifik yang
> disentuh sesi ini, bukan schema drift menyeluruh. Cocok dipakai sebagai smoke test cepat
> setelah perubahan serupa, bukan pengganti Full Audit.

```bash
cat > /home/it/final_check_all_v2.py << 'EOF'
exec("""
print("========================================")
print("1. WORKFLOW TRANSITIONS (harus 7/6/8, no dup)")
print("========================================")
for wf_name, expected in [("NextHD Ticket", 7), ("NextHD Problem", 6), ("NextHD Change Request", 8)]:
    rows = frappe.db.sql("SELECT state, action, next_state FROM `tabWorkflow Transition` WHERE parent=%s", (wf_name,), as_dict=True)
    total = len(rows)
    unique_keys = set((r.state, r.action, r.next_state) for r in rows)
    status = "OK" if total == expected and total == len(unique_keys) else "MASIH ADA MASALAH"
    print(wf_name + ": total=" + str(total) + " unique=" + str(len(unique_keys)) + " expected=" + str(expected) + " -> " + status)

print("")
print("========================================")
print("2. WORKFLOW ACTION MASTER (semua action harus ada master-nya)")
print("========================================")
all_actions = set()
for wf_name in ["NextHD Ticket", "NextHD Problem", "NextHD Change Request"]:
    rows = frappe.db.sql("SELECT DISTINCT action FROM `tabWorkflow Transition` WHERE parent=%s", (wf_name,), as_dict=True)
    for r in rows:
        all_actions.add(r.action)
missing = [a for a in all_actions if not frappe.db.exists("Workflow Action Master", a)]
print("Total action unik: " + str(len(all_actions)))
print("Yang masih bolong: " + (str(missing) if missing else "TIDAK ADA (aman)"))

print("")
print("========================================")
print("3. SIDEBAR WORKSPACE NextHD")
print("========================================")
ws = frappe.get_doc("Workspace", "NextHD")
labels = [l.label for l in ws.links]
print("Total sidebar item: " + str(len(labels)))
print("Ada NextHD Photo: " + str("NextHD Photo" in labels))
print("List: " + str(labels))

print("")
print("========================================")
print("4. NUMBER CARDS DI WORKSPACE")
print("========================================")
nc = frappe.db.sql("SELECT number_card_name FROM `tabWorkspace Number Card` WHERE parent='NextHD'", as_dict=True)
print("Total: " + str(len(nc)) + " -> " + str([n.number_card_name for n in nc]))
print("Ada Total Foto Terupload: " + str(any(n.number_card_name == "Total Foto Terupload" for n in nc)))

print("")
print("========================================")
print("5. SLA POLICY")
print("========================================")
sla_rows = frappe.get_all("NextHD SLA Policy", fields=["priority", "response_time_minutes", "resolution_time_minutes", "is_24x7"], order_by="priority")
for s in sla_rows:
    print("    " + str(s.priority) + ": response=" + str(s.response_time_minutes) + " resolution=" + str(s.resolution_time_minutes) + " is_24x7=" + str(s.is_24x7))
kritis = [s for s in sla_rows if s.priority == "Kritis"]
if kritis and kritis[0].is_24x7 == 1:
    print("Kritis is_24x7=1 -> OK")
else:
    print("Kritis is_24x7 BUKAN 1 -> PERLU DICEK")

print("")
print("========================================")
print("6. BUSINESS HOURS")
print("========================================")
bh = frappe.get_all("NextHD Business Hours", fields=["day", "is_working_day"], order_by="creation")
print("Total record: " + str(len(bh)))
days_seen = [b.day for b in bh]
dup_days = set([d for d in days_seen if days_seen.count(d) > 1])
print("Hari duplikat: " + (str(dup_days) if dup_days else "TIDAK ADA"))
for b in bh:
    print("    " + str(b.day) + " working=" + str(b.is_working_day))

print("")
print("========================================")
print("7. NEXTHD HOLIDAY")
print("========================================")
total_holiday = frappe.db.count("NextHD Holiday")
cuti_count = frappe.db.count("NextHD Holiday", {"description": ["like", "Cuti Bersama%"]})
print("Total: " + str(total_holiday) + " (cuti bersama: " + str(cuti_count) + ")")

print("")
print("========================================")
print("8. ROLES NEXTHD")
print("========================================")
roles = ["Requester", "Agent", "Agent Manager", "IT Manager", "IT Auditor"]
for r in roles:
    exists = frappe.db.exists("Role", r)
    print("    " + r + ": " + ("ADA" if exists else "TIDAK ADA -- MASALAH"))

print("")
print("========================================")
print("9. NextHD Photo DocType")
print("========================================")
print("DocType NextHD Photo ada: " + str(frappe.db.exists("DocType", "NextHD Photo") is not None))
print("Jumlah record NextHD Photo: " + str(frappe.db.count("NextHD Photo")))

print("")
print("========================================")
print("SELESAI - REVIEW HASIL DI ATAS")
print("========================================")
""")
EOF
bench --site desk.ciptamebel.co.id console < /home/it/final_check_all_v2.py > /home/it/final_check_all_v2_result.txt 2>&1 && cat /home/it/final_check_all_v2_result.txt
```

### Hasil Terakhir Sesi 24 Agustus 2026

Semua 9 titik pemeriksaan **OK**, kecuali satu anomali yang saat itu belum diputuskan.

- Workflow Transition: Ticket 7/7, Problem 6/6, Change Request 8/8 — semua unik, tidak ada duplikat (saat itu)
- Workflow Action Master: 17 action unik, tidak ada yang bolong
- Sidebar: "NextHD Photo" muncul
- Number Card: "Total Foto Terupload" muncul (total 9 card)
- SLA Policy: sesuai SOP final 19 Agustus, Kritis `is_24x7=1`
- Holiday: 25 record (17 nasional + 8 cuti bersama 2026)
- Roles: 5/5 ada
- NextHD Photo DocType: aktif, 0 record (belum ada foto diupload, wajar karena fitur baru live)

**✅ Update 25 Agustus — anomali Sabtu sudah diputuskan (bukan lagi open item):** Business
Hours Sabtu `is_working_day=1` **memang benar dan disengaja** — Sabtu adalah hari kerja CML,
08:00–15:00. Ini sudah dikonfirmasi ulang Efendy 25 Agustus dan konsisten dengan
`docs/SUMMARY.md` (item Y, diputuskan 24 Agustus). Tidak perlu tindakan apa pun terhadap
Business Hours — data sudah benar.

---

## Update 25 Agustus 2026 — Root Cause Duplikasi Workflow Transition (Ditemukan & Diperbaiki Permanen)

> **Konteks:** Audit ulang 25 Agustus menemukan Workflow Transition **kembali** ke kondisi
> rusak (Ticket 28, Problem 24, Change Request 32 — persis pola sebelum dedup 24 Agustus),
> padahal sudah dua kali dibersihkan sebelumnya. Ini memicu investigasi lebih dalam, bukan
> langsung dedup ulang untuk ketiga kalinya.

### Root Cause Sebenarnya (Terkonfirmasi)

Dugaan sebelumnya (24 Agustus) — bahwa `Workflow Action Master` yang hilang menyebabkan
duplikasi — **bukan akar masalah utama**. Akar masalah sebenarnya:

`Workflow Transition` terdaftar di `hooks.py` sebagai **fixture aktif**. File sumbernya,
`nexthd/fixtures/workflow_transition.json`, ternyata **menumpuk 4 generasi export**
(timestamp `2026-08-20`, `2026-08-21`, dan `2026-08-24` — bahkan batch `2026-08-24 21:48:32`
sendiri berisi **2 salinan penuh di dalamnya**), karena setiap kali dedup dilakukan, itu
**hanya dijalankan di database via SQL/`bench console`**, tidak pernah diikuti dengan
membersihkan file fixture di repo. Akibatnya, **setiap `bench migrate`** (untuk alasan apa
pun) meng-import ulang seluruh isi file itu, termasuk duplikatnya — membuat dedup di
database selalu kembali rusak.

**Pelajaran penting:** untuk doctype apa pun yang aktif di `fixtures` hook, perbaikan data
**HARUS** diikuti dengan membersihkan file JSON fixture-nya juga di repo — dedup di database
saja tidak permanen dan akan selalu kembali rusak saat `bench migrate` berikutnya.

### Perbaikan yang Dilakukan (25 Agustus)

1. Dedup database (pola sama seperti sebelumnya) — Ticket 28→7, Problem 24→6, CR 32→8
2. **Fixture file `nexthd/fixtures/workflow_transition.json` ditulis ulang total** — dari
   1500+ baris (berisi duplikat) menjadi 21 entri unik bersih (7 Ticket + 6 Problem + 8 CR),
   commit `9cf994f`
3. Divalidasi otomatis sebelum push: total 21 entri, breakdown per parent benar, tidak ada
   duplikat internal (kombinasi `parent`+`state`+`action`+`next_state` semua unik)

**⚠️ Update 25 Agustus (lanjutan):** commit `9cf994f` sempat push fixture dengan `name` yang
TIDAK cocok dengan `name` aktual di database (memakai `name` dari batch lama). Ini
menyebabkan `bench migrate` **menambahkan** 21 baris baru alih-alih meng-update (fixture sync
Frappe itu upsert-by-`name`), sehingga angka sempat melonjak lagi jadi 35/30/40 saat migrate
dicoba (lihat detail insiden di bagian "Update 25 Agustus 2026 (Lanjutan)" di bawah).
**Sudah diperbaiki lagi** di commit `322827f` — fixture ditulis ulang dengan `name` yang
cocok persis dengan `name` aktual di database saat ini setelah restore backup (mis.
`rch04rcult`, `rch0slb247`, dst).

**✅ Update 26 Agustus — dikonfirmasi PERMANEN.** Sudah diuji lewat 2× `bench migrate`
sungguhan (26 Agustus pagi dan siang) — hasil tetap **7/6/8, tidak ada duplikat** di
kedua percobaan. Fixture dan database sudah benar-benar selaras, tidak perlu dikhawatirkan
lagi kecuali ada perubahan manual baru ke Workflow Transition di masa depan.

### Script Verifikasi — Workflow Transition (Deteksi Dini)

Jalankan kapan saja curiga duplikasi balik lagi. Kalau hasilnya "MASIH ADA DUPLIKAT" padahal
baru saja di-dedup, curigai fixture file di repo, bukan cuma database — minta Claude cek
`nexthd/fixtures/workflow_transition.json` langsung dari GitHub.

```bash
cat > /home/it/check_workflow_transition_clean.py << 'EOF'
def check():
    print("=== CEK WORKFLOW TRANSITION - DB BERSIH? ===")
    all_ok = True
    for wf_name, expected in [("NextHD Ticket", 7), ("NextHD Problem", 6), ("NextHD Change Request", 8)]:
        rows = frappe.db.sql("SELECT state, action, next_state FROM `tabWorkflow Transition` WHERE parent=%s", (wf_name,), as_dict=True)
        total = len(rows)
        unique_keys = set((r.state, r.action, r.next_state) for r in rows)
        status = "OK" if total == expected and total == len(unique_keys) else "MASIH ADA DUPLIKAT"
        if status != "OK":
            all_ok = False
        print(wf_name + ": total=" + str(total) + " unique=" + str(len(unique_keys)) + " expected=" + str(expected) + " -> " + status)
    print("")
    if all_ok:
        print("HASIL: DB BERSIH")
    else:
        print("HASIL: DB MASIH KOTOR - kemungkinan fixture di repo juga masih menumpuk duplikat, minta Claude cek nexthd/fixtures/workflow_transition.json")

check()
EOF
sed -i 's/\r$//' /home/it/check_workflow_transition_clean.py && \
sed -i 's/^    /\t/' /home/it/check_workflow_transition_clean.py && \
bench --site desk.ciptamebel.co.id console < /home/it/check_workflow_transition_clean.py
```

### Script — Business Hours vs SOP

```bash
cat > /home/it/check_business_hours.py << 'EOF'
def check():
    print("=====================================================")
    print("CEK BUSINESS HOURS vs SOP - " + str(frappe.utils.now()))
    print("=====================================================")
    expected = {
        "Senin": {"start_time": "08:00:00", "end_time": "17:00:00", "is_working_day": 1},
        "Selasa": {"start_time": "08:00:00", "end_time": "17:00:00", "is_working_day": 1},
        "Rabu": {"start_time": "08:00:00", "end_time": "17:00:00", "is_working_day": 1},
        "Kamis": {"start_time": "08:00:00", "end_time": "17:00:00", "is_working_day": 1},
        "Jumat": {"start_time": "08:00:00", "end_time": "17:30:00", "is_working_day": 1},
        "Sabtu": {"start_time": "08:00:00", "end_time": "15:00:00", "is_working_day": 1},
        "Minggu": {"start_time": "08:00:00", "end_time": "08:00:00", "is_working_day": 0}
    }
    all_ok = True
    for day, exp in expected.items():
        actual = frappe.db.get_value("NextHD Business Hours", day, ["start_time", "end_time", "is_working_day"], as_dict=True)
        if not actual:
            print("[MISSING] " + day + " tidak ada record")
            all_ok = False
            continue
        actual_start_str = str(actual.start_time)
        actual_end_str = str(actual.end_time)
        actual_start_norm = actual_start_str if len(actual_start_str) == 8 else "0" + actual_start_str
        actual_end_norm = actual_end_str if len(actual_end_str) == 8 else "0" + actual_end_str
        actual_working = actual.is_working_day
        match = (actual_start_norm == exp["start_time"] and actual_end_norm == exp["end_time"] and actual_working == exp["is_working_day"])
        status = "OK" if match else "TIDAK COCOK"
        if not match:
            all_ok = False
        print("[" + status + "] " + day + ": aktual(" + actual_start_str + "-" + actual_end_str + ", working=" + str(actual_working) + ") | seharusnya(" + exp["start_time"] + "-" + exp["end_time"] + ", working=" + str(exp["is_working_day"]) + ")")
    total_record = frappe.db.count("NextHD Business Hours")
    print("Total record: " + str(total_record) + " (harus 7)")
    if total_record != 7:
        all_ok = False
    print("")
    if all_ok:
        print("HASIL AKHIR: SEMUA SESUAI SOP")
    else:
        print("HASIL AKHIR: ADA YANG TIDAK COCOK, PERLU DIKOREKSI")
    print("=====================================================")

check()
EOF
sed -i 's/\r$//' /home/it/check_business_hours.py && \
sed -i 's/^    /\t/' /home/it/check_business_hours.py && \
bench --site desk.ciptamebel.co.id console < /home/it/check_business_hours.py
```

> **Catatan:** versi pertama script ini (dipakai 25 Agustus pagi) salah membandingkan format
> waktu (`8:00:00` vs `08:00:00` dianggap beda padahal sama), sehingga sempat melaporkan
> "TIDAK COCOK" di semua hari padahal datanya benar. Versi di atas sudah menormalkan format
> sebelum dibandingkan. **Sabtu `is_working_day=1` (08:00-15:00) adalah data yang BENAR dan
> disengaja** — jangan diubah tanpa konfirmasi eksplisit dari Efendy.

---

## Update 25 Agustus 2026 (Lanjutan) — Koreksi Total: `Workspace.links` adalah Sumber Asli Sidebar, Bukan `Workspace Sidebar Item`

### Kronologi Insiden

Sesi ini awalnya (keliru, lanjutan dari sesi 24 Agustus) mengedit `Workspace Sidebar Item`
langsung dan membuat file `nexthd/next_helpdesk/workspace_sidebar/nexthd.json` untuk
"mempermanenkan" 6 link report + section. Saat `bench migrate` dicoba sebagai uji coba:

- Sidebar turun dari 22 item jadi 14 item — item "NextHD Photo" dan 6 report **hilang**,
  log menunjukkan `Removing orphan Workspace Sidebars`
- Workflow Transition ikut melonjak dari 7/6/8 jadi 35/30/40 (insiden `name` mismatch,
  lihat bagian sebelumnya)

**Tindakan yang diambil:** restore database dari backup pra-migrate — berhasil, semua
kembali ke kondisi sebelum migrate.

### Root Cause Sebenarnya (Terkonfirmasi dari Dokumentasi Resmi Frappe)

Dokumentasi migrasi resmi Frappe v16 menyatakan sidebar baru ini "powered by Workspace
Sidebar doctype" dan **"autogenerated for the most part"**. Artinya: `Workspace Sidebar Item`
**bukan sumber data asli** — itu hasil **auto-generate** dari `Workspace.links` (child table
field `links` di doctype stock `Workspace`). Setiap `bench migrate`, Frappe meregenerasi ulang
`Workspace Sidebar Item` berdasarkan `Workspace.links`, lalu menghapus apa pun di `Workspace
Sidebar Item` yang tidak berasal dari `Workspace.links`.

**Kesimpulan:** seluruh pendekatan edit `Workspace Sidebar Item` + file
`workspace_sidebar/nexthd.json` (dipakai sejak sesi 24 Agustus) **salah alamat**. Sumber
kebenaran yang benar adalah **`Workspace.links`**.

> **Catatan (27 Agustus):** kesimpulan ini valid **khusus untuk menambah link BARU ke
> sidebar workspace NextHD sendiri**, yang di-regenerate otomatis tiap migrate. Kalau
> kasusnya adalah menambah 1 entri sidebar yang mengarah ke **workspace lain** (bukan
> menambah entri di dalam NextHD), jalurnya berbeda lagi — lihat "Update 27 Agustus 2026"
> di bawah.

### Perbaikan yang Dilakukan (via `Workspace.links`)

Item "NextHD Report" generic dihapus dari `tabWorkspace Link`, diganti 6 link report langsung
(`link_type: Report`, dengan `report_ref_doctype` terisi): Tiket per Bulan, Tiket per Agent,
Tiket per Prioritas, Tiket per Kategori, SLA Compliance Bulanan (ref `NextHD Ticket`), dan
Aset Bermasalah (ref `NextHD Asset`). Total `Workspace.links` jadi 19 item (13 lama + 6
report baru).

### Script — Cek Skema `Workspace Link` (Read-Only)

```bash
cat > /home/it/check_workspace_link_schema.py << 'EOF'
def check():
    print("=== KOLOM TABEL tabWorkspace Link ===")
    cols = frappe.db.sql("DESCRIBE `tabWorkspace Link`", as_dict=True)
    for c in cols:
        print(c.Field + " | " + c.Type)
    print("")
    print("=== ISI Workspace.links SAAT INI (parent NextHD) ===")
    rows = frappe.db.sql("SELECT * FROM `tabWorkspace Link` WHERE parent='NextHD' ORDER BY idx", as_dict=True)
    print("Total: " + str(len(rows)))
    for r in rows:
        print("---")
        for k, v in r.items():
            if v not in (None, "", 0):
                print("    " + str(k) + ": " + str(v))

check()
EOF
sed -i 's/\r$//' /home/it/check_workspace_link_schema.py && \
sed -i 's/^    /\t/' /home/it/check_workspace_link_schema.py && \
bench --site desk.ciptamebel.co.id console < /home/it/check_workspace_link_schema.py
```

---

## Update 26 Agustus 2026 — Dashboard Shortcut "NextHD Photo" & 6 Report (`Workspace Shortcut`, `report_ref_doctype`)

> **Konteks:** Berbeda dari sidebar kiri (`Workspace.links`), sesi ini menambahkan **kartu
> shortcut di badan dashboard** `/desk/nexthd` — tabel `tabWorkspace Shortcut` (`parentfield =
> 'shortcuts'`). Root cause & fix lengkap ada di `docs/POLA_KERJA_DAN_BUG.md` §1.B, §1.C.
> Ringkasan: 6 shortcut Report tidak render karena `report_ref_doctype` kosong (fix: isi
> field itu), shortcut "NextHD Photo" tidak render karena cache Redis setelah update
> `Workspace.content` via SQL langsung (fix: `bench clear-cache` + `clear-website-cache`).

### Script Gabungan — Cek SEMUA Isu Workspace/Sidebar/Dashboard Sekaligus

```bash
cat > /home/it/audit_workspace_all.py << 'EOF'
def main_check():
    import json
    print("=====================================================")
    print("AUDIT WORKSPACE/SIDEBAR/DASHBOARD LENGKAP - " + str(frappe.utils.now()))
    print("=====================================================")
    print("")
    print("=== 1. Workspace.content - Jumlah & Tipe Blok ===")
    content_raw = frappe.db.get_value("Workspace", "NextHD", "content")
    content = json.loads(content_raw) if content_raw else []
    print("Total blok: " + str(len(content)))
    type_count = {}
    for block in content:
        t = block.get("type", "unknown")
        type_count[t] = type_count.get(t, 0) + 1
    print("Breakdown per tipe: " + str(type_count))
    shortcut_names_in_content = set()
    for block in content:
        if block.get("type") == "shortcut":
            shortcut_names_in_content.add(block.get("data", {}).get("shortcut_name"))
    print("")
    print("=== 2. tabWorkspace Shortcut (kartu dashboard) vs Workspace.content ===")
    shortcut_rows = frappe.db.sql("SELECT label, type, report_ref_doctype FROM `tabWorkspace Shortcut` WHERE parent='NextHD'", as_dict=True)
    print("Total baris di tabel: " + str(len(shortcut_rows)))
    for r in shortcut_rows:
        in_content = r.label in shortcut_names_in_content
        problem = ""
        if not in_content:
            problem = problem + " [TIDAK ADA DI content JSON]"
        if r.type == "Report" and not r.report_ref_doctype:
            problem = problem + " [report_ref_doctype KOSONG]"
        status = "OK" if not problem else "BERMASALAH:" + problem
        print("    " + str(r.label) + " (" + str(r.type) + ") -> " + status)
    orphan_content_refs = shortcut_names_in_content - set([r.label for r in shortcut_rows])
    if orphan_content_refs:
        print("[PERINGATAN] content JSON mereferensikan shortcut_name yang TIDAK ADA di tabWorkspace Shortcut: " + str(orphan_content_refs))
    print("")
    print("=== 3. Workspace.links (sumber asli SIDEBAR KIRI) ===")
    ws_doc = frappe.get_doc("Workspace", "NextHD")
    link_labels = [l.label for l in ws_doc.links]
    print("Total item: " + str(len(link_labels)))
    print("List: " + str(link_labels))
    report_labels_expected = ["Tiket per Bulan", "Tiket per Agent", "Tiket per Prioritas", "Tiket per Kategori", "SLA Compliance Bulanan", "Aset Bermasalah"]
    missing_report_links = [r for r in report_labels_expected if r not in link_labels]
    if missing_report_links:
        print("[BELUM ADA di Workspace.links] " + str(missing_report_links))
    else:
        print("Semua 6 link report sudah ada di Workspace.links")
    print("")
    print("=== 4. tabWorkspace Sidebar Item (turunan/auto-generate dari Workspace.links) ===")
    sidebar_item_rows = frappe.db.sql("SELECT label, link_to FROM `tabWorkspace Sidebar Item` WHERE parent='NextHD'", as_dict=True)
    sidebar_item_labels = [r.label for r in sidebar_item_rows]
    print("Total item: " + str(len(sidebar_item_labels)))
    print("List: " + str(sidebar_item_labels))
    if len(sidebar_item_labels) != len(link_labels):
        print("[INFO] Jumlah Workspace Sidebar Item (" + str(len(sidebar_item_labels)) + ") BEDA dari Workspace.links (" + str(len(link_labels)) + ") - CATATAN 26 Agustus: ini TERNYATA NORMAL untuk link bertipe Report, Frappe v16 tampaknya tidak menyertakan link Report ke auto-generate sidebar (cuma DocType/Workspace). Selisih persis jumlah link Report di Workspace.links = bukan bug, jangan coba 'perbaiki' lagi tanpa bukti baru.")
    else:
        print("Jumlah sinkron dengan Workspace.links")
    print("")
    print("=== 5. Number Card di Workspace ===")
    nc_rows = frappe.db.sql("SELECT number_card_name FROM `tabWorkspace Number Card` WHERE parent='NextHD'", as_dict=True)
    nc_names = [r.number_card_name for r in nc_rows]
    print("Total: " + str(len(nc_names)) + " -> " + str(nc_names))
    print("")
    print("=== 6. Desktop Icon nexthd ===")
    icon = frappe.db.get_value("Desktop Icon", {"app": "nexthd"}, ["name", "link_type", "link_to", "standard"], as_dict=True)
    print(str(icon))
    print("")
    print("=== 7. SEMUA WORKSPACE (public/hidden) - ditambahkan 26 Agustus ===")
    all_ws = frappe.db.sql("SELECT name, public, is_hidden, module FROM `tabWorkspace` ORDER BY module, name", as_dict=True)
    print("Total workspace di database: " + str(len(all_ws)))
    for w in all_ws:
        flag = ""
        if w.module == "Next Helpdesk" and w.name != "NextHD" and w.public == 1 and w.is_hidden == 0:
            flag = "  <-- WARNING: workspace NextHD lain yang TAMPIL PUBLIK, kemungkinan perlu disembunyikan spt Ticket Center dkk"
        print("    " + str(w.name) + " | public=" + str(w.public) + " | hidden=" + str(w.is_hidden) + " | module=" + str(w.module) + flag)
    print("")
    print("=====================================================")
    print("AUDIT WORKSPACE/SIDEBAR/DASHBOARD SELESAI")
    print("Cara baca cepat: cari baris [PERINGATAN], [BERMASALAH], [BELUM ADA], atau WARNING di atas")
    print("=====================================================")

main_check()
EOF
sed -i 's/\r$//' /home/it/audit_workspace_all.py && \
sed -i 's/^    /\t/' /home/it/audit_workspace_all.py && \
cat -A /home/it/audit_workspace_all.py | head -5 && \
bench --site desk.ciptamebel.co.id console < /home/it/audit_workspace_all.py > /home/it/audit_workspace_all_result.txt 2>&1 && \
cat /home/it/audit_workspace_all_result.txt
```

**Cara pakai hasilnya:** kalau ada baris `[PERINGATAN]`, `[BERMASALAH]`, `[BELUM ADA]`, atau
`WARNING`, itu kandidat kuat kenapa sesuatu tidak muncul di UI (atau muncul padahal
seharusnya tidak). Kombinasikan dengan `bench clear-cache` + `bench clear-website-cache` +
hard refresh browser sebelum menyimpulkan ada bug data — banyak kasus di project ini yang
ternyata murni cache, bukan data salah. **§4 sekarang TIDAK lagi otomatis dianggap masalah**
kalau selisihnya persis jumlah link Report — itu confirmed normal (lihat Update 26 Agustus
Lanjutan di bawah).

---

## Update 26 Agustus 2026 (Lanjutan) — Ditemukan 5 Workspace "Center" Tersembunyi + Insiden Sidebar Hilang Total + Konfirmasi Limitasi Frappe v16

### Temuan: Workspace "Center" yang Sebelumnya Tidak Terdeteksi

Ditemukan 5 workspace tambahan yang **sebelumnya tidak pernah muncul di audit manapun**
sepanjang sesi-sesi ini, semua `module: Next Helpdesk` (jadi bagian dari project NextHD,
kemungkinan dibuat Devin/Codex atau sesi AI lain di luar riwayat chat ini, tidak pernah
terdokumentasi sampai sekarang):

- `Ticket Center`
- `Asset Center`
- `Service Management`
- `Configuration Center`
- `Reports Center`

Kelimanya (plus `Next Helpdesk`, workspace legacy) sempat tampil (`public=1, hidden=0`) di
sidebar, membuat sidebar utama jadi sangat ramai/berantakan (di luar 15 item DocType NextHD
yang biasa). **Sekarang statusnya sudah `public=0, hidden=1` (disembunyikan, TIDAK
dihapus)** — data, Report, Number Card, dsb di dalamnya masih utuh, cuma tidak tampil di
sidebar utama.

### ⚠️ Insiden: Mengosongkan `Workspace.links` Tanpa Isi Ulang Langsung = Sidebar Hilang Total

Percobaan pertama untuk merapikan sidebar (dari sumber eksternal/AI lain) sempat menjalankan
`DELETE FROM tabWorkspace Link WHERE parent='NextHD'` **tanpa langsung insert ulang isi
barunya** (rencananya navigasi dipindah seluruhnya ke dashboard shortcut). Begitu cache
dibersihkan, **seluruh sidebar NextHD hilang total** — karena `Workspace Sidebar Item`
(tampilan sidebar) di-regenerate dari `Workspace.links` saat cache/migrate, jadi
`Workspace.links` kosong = sidebar kosong.

**PELAJARAN KRITIS:** jangan pernah `DELETE` isi `Workspace.links` tanpa `INSERT` pengganti
di **transaksi/script yang sama**. Kalau mau ganti isi sidebar, selalu hapus-dan-isi-ulang
sekaligus dalam satu script, jangan dua langkah terpisah.

**Perbaikan:** dijalankan script restore yang mengisi ulang 19 `Workspace Link` (13 DocType +
6 Report) sekaligus menyembunyikan 5 workspace "Center" + legacy "Next Helpdesk" — semua
lewat `frappe.db.sql()`/`frappe.db.set_value()` langsung (bukan `.save()`, karena `.save()`
pada Workspace lama sempat memicu `MandatoryError`/`DocType View cannot be "Form"`). Hasil
setelah restore + `clear-cache` + `clear-website-cache`: sidebar NextHD kembali bersih (15
item inti), 5 workspace "Center" tidak lagi tampil, `Workflow Transition` tetap 7/6/8 (tidak
terpengaruh insiden ini).

### Konfirmasi Resmi: Sidebar Pendek di Halaman Report/DocType Adalah Limitasi Frappe v16, Bukan Bug Kita

Saat masuk ke halaman report (`/desk/query-report/...`) atau DocType tertentu dari module
"Next Helpdesk", sidebar otomatis berganti jadi versi pendek/generic ("Module Sidebar" —
daftar DocType/Report auto berdasarkan field `module`), BUKAN sidebar lengkap Workspace
NextHD. Ini **dikonfirmasi sebagai known limitation Frappe v16** (GitHub Issue #36317, juga
dibahas di forum resmi Frappe) — sidebar Workspace yang lengkap **memang didesain hanya
tampil di halaman Workspace itu sendiri**, otomatis berganti ke Module Sidebar begitu masuk
DocType/Report. Belum ada fix resmi dari tim Frappe. Percobaan mengubah field
`report_doc.module` breadcrumb/sidebar report tidak berhasil karena `set_breadcrumbs()`
bawaan (di `query_report.js` baris ~1546) dipanggil ulang dan menimpa override custom.

**Yang berhasil sebagai gantinya:** breadcrumb 2-level ("NextHD / <Nama Report>") di setiap
file `.js` report NextHD (`frappe.query_reports["<nama>"].onload`), sehingga user tetap bisa
1 klik balik ke dashboard NextHD dari halaman report mana pun, meski sidebar tetap versi
pendek. **Per akhir sesi 26 Agustus, perbaikan breadcrumb ini masih dalam proses trial —
beberapa percobaan format (`add()` single object, array, override `set_breadcrumbs`) belum
berhasil, root cause pastinya (kapan/di mana breadcrumb bawaan menimpa ulang) belum
sepenuhnya ditemukan.** Jangan hapus/reset 5 workspace "Center" atau `Workspace.links` untuk
mengejar solusi sidebar ini — sudah terbukti berisiko tinggi (insiden di atas).

### Rekomendasi untuk Sesi Berikutnya

1. Kalau ingin lanjut riset breadcrumb, cek dulu apakah `report.set_breadcrumbs` di-reassign
   lagi oleh proses lain setelah `onload` (misal saat data refresh/filter berubah) — belum
   terverifikasi.
2. Jangan coba lagi memaksakan sidebar lengkap tampil di halaman report/DocType — itu
   limitasi platform, bukan config yang bisa diperbaiki tanpa override JS inti Frappe
   (berisiko rusak tiap update Frappe, sebaiknya jadi task terpisah untuk Devin dengan
   testing menyeluruh, bukan quick-fix).
3. 6 link Report di sidebar `Workspace Sidebar Item` (turunan) kemungkinan **tidak akan
   pernah muncul** meski migrate berkali-kali — ini pola konsisten di 2× percobaan migrate
   (26 Agustus). Terima sebagai keterbatasan, akses report tetap tersedia lewat dashboard
   shortcut (`Workspace Shortcut`) yang sudah berfungsi normal.

---

## Update 27 Agustus 2026 — Workspace Terpisah "NextHD Report" + 1 Link Sidebar "NextHD Reporting" (Kasus Berbeda dari `Workspace.links`)

> **Konteks:** Berbeda dari kasus 25-26 Agustus (menambah 6 link *Report* langsung di dalam
> `Workspace.links` milik NextHD), sesi ini menyangkut sebuah **workspace terpisah** bernama
> `NextHD Report` (berisi 11 shortcut ke report), dan kebutuhan menambah **satu entri**
> sidebar ("NextHD Reporting", link_type: `Workspace`) yang mengarah ke workspace itu. Detail
> kronologi 4 lapis akar masalah ada di `docs/POLA_KERJA_DAN_BUG.md` §1.C dan §4 (bug session
> 27 Agustus). Bagian ini hanya mencatat 2 temuan yang relevan untuk audit/instalasi baru.

### Temuan 1 — Workspace Baru via `bench console` Insert Tidak Trigger Export Fixture

Workspace yang dibuat lewat insert langsung ke database (`bench console`, bukan UI Workspace
Editor) **tidak memicu** proses otomatis yang biasanya menulis file fixture JSON-nya. Baru
setelah `developer_mode=1` diaktifkan dan `doc.save()` dipanggil manual, file fixture
`nexthd/<module>/workspace/<nama_scrub>/<nama_scrub>.json` benar-benar tertulis ke disk.

**Implikasi untuk audit/instalasi baru:** kalau ada Workspace yang ada di database tapi
**tidak** punya file fixture JSON yang sesuai, curigai workspace itu pernah dibuat via
insert manual — bukan bug Frappe.

### Temuan 2 — Lokasi File Export `Workspace Sidebar` yang Sebenarnya (Koreksi Path)

Fungsi `export_sidebar()` di controller `workspace_sidebar.py` menulis file ke:

```
<app_root>/<app>/workspace_sidebar/<judul_scrub>.json
```

Contoh nyata di project ini:

```
~/frappe/apps/nexthd/nexthd/workspace_sidebar/nexthd.json   <- BENAR, aktif dipakai
```

**BUKAN** di dalam folder module seperti yang diasumsikan di sesi-sesi sebelumnya (lihat
`HANDOFF.md` bagian lama, `nexthd/next_helpdesk/workspace_sidebar/nexthd.json`) — path itu
adalah **peninggalan lama/usang** yang sudah tidak pernah ditulis ulang oleh Frappe, dan
sudah dihapus dari server. Kalau `sidebar.save()`/`export_sidebar()` tidak error tapi file
tidak berubah, kemungkinan besar penyebabnya adalah mengecek path yang salah ini, bukan
logika save yang gagal.

**Prasyarat lain yang wajib benar sebelum `export_sidebar()` mau menulis file sama sekali:**
field `app` (harus diisi nama app scrub, mis. `nexthd`) dan `standard` (harus `1`) pada
dokumen `Workspace Sidebar` terkait.

### Catatan yang Diperkuat Ulang

- Menambah satu link sidebar yang mengarah ke **workspace lain** (bukan menambah item di
  dalam sidebar NextHD sendiri) dilakukan lewat UI **"⋯" → Edit Sidebar**, bukan lewat
  `Workspace.links` — dua mekanisme yang berbeda untuk dua kebutuhan yang berbeda pula
  (lihat catatan di "Update 25 Agustus 2026 (Lanjutan)" di atas).
- `is_hidden=1`/`public=0` tidak cocok untuk workspace yang aksesnya lewat link sidebar
  biasa — sempat dicoba untuk workspace "NextHD Report" ini dan terbukti membuat link
  hilang total. Sudah di-undo, workspace ini tetap `public=1, is_hidden=0`.

---

*Dokumen ini dikelola oleh Claude. Update terakhir: 2026-08-27.*
