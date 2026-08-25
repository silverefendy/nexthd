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
| §3 Workspace/Sidebar | `Workspace Sidebar Item` ini adalah tabel **turunan/auto-generate**, bukan sumber asli — lihat "Update 25 Agustus 2026 (Lanjutan)" di bawah. Sumber asli yang harus dicek/diedit adalah `Workspace.links` |
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
`rch04rcult`, `rch0slb247`, dst). Server sudah `git pull`, dikonfirmasi `Total: 21`, `name`
pertama `rch04rcult` — cocok dengan DB. **Belum diuji lewat `bench migrate` sungguhan
setelah perbaikan kedua ini.**

### Script Verifikasi Baru — Workflow Transition (Deteksi Dini)

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

**Hasil verifikasi 25 Agustus (setelah perbaikan pertama):** Ticket 7/7, Problem 6/6, Change
Request 8/8 — semua unik, DB bersih. Lihat catatan lanjutan di atas soal insiden `name`
mismatch dan perbaikan kedua (`322827f`) — jalankan script ini lagi setelah `bench migrate`
berikutnya untuk konfirmasi final.

### Script Verifikasi Baru — Business Hours vs SOP

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
> sebelum dibandingkan.

---

## Update 25 Agustus 2026 (Lanjutan) — Koreksi Total: `Workspace.links` adalah Sumber Asli Sidebar, Bukan `Workspace Sidebar Item`

> **Status keseluruhan pada akhir sesi ini: 6 link report berhasil dimasukkan ke
> `Workspace.links` (sumber asli), diverifikasi via `bench console` — 19 item total. `bench
> migrate` untuk mengonfirmasi hasil ini belum dijalankan.**

### Kronologi Insiden

Sesi ini awalnya (keliru, lanjutan dari sesi 24 Agustus) mengedit `Workspace Sidebar Item`
langsung dan membuat file `nexthd/next_helpdesk/workspace_sidebar/nexthd.json` untuk
"mempermanenkan" 6 link report + section. Saat `bench migrate` dicoba sebagai uji coba:

- Sidebar turun dari 22 item jadi 14 item — item "NextHD Photo" dan 6 report **hilang**,
  log menunjukkan `Removing orphan Workspace Sidebars`
- Workflow Transition ikut melonjak dari 7/6/8 jadi 35/30/40 (lihat insiden `name` mismatch
  di bagian sebelumnya)

**Tindakan yang diambil:** restore database dari backup pra-migrate
(`20260825_150120-desk_ciptamebel_co_id-database.sql.gz`) — berhasil, semua kembali ke
kondisi sebelum migrate (sidebar 22 item, workflow 7/6/8).

### Root Cause Sebenarnya (Terkonfirmasi dari Dokumentasi Resmi Frappe)

Dokumentasi migrasi resmi Frappe v16 (GitHub wiki, halaman "Migrating to version 16")
menyatakan sidebar baru ini "powered by Workspace Sidebar doctype" dan **"autogenerated for
the most part"**.

Artinya: `Workspace Sidebar Item` **bukan sumber data asli** — itu hasil **auto-generate**
dari `Workspace.links` (child table field `links` di doctype stock `Workspace`, yang sudah
ada sejak dulu). Setiap `bench migrate`, Frappe meregenerasi ulang `Workspace Sidebar Item`
berdasarkan `Workspace.links`, lalu menghapus apa pun di `Workspace Sidebar Item` yang tidak
berasal dari `Workspace.links` — itu persis penyebab `Removing orphan Workspace Sidebars`.

**Kesimpulan:** seluruh pendekatan edit `Workspace Sidebar Item` + file
`workspace_sidebar/nexthd.json` (dipakai sejak sesi 24 Agustus) **salah alamat**. Sumber
kebenaran yang benar adalah **`Workspace.links`**. File
`nexthd/next_helpdesk/workspace_sidebar/nexthd.json` **masih ada di repo tapi kemungkinan
besar tidak relevan/tidak berguna** — belum diputuskan apakah dihapus, tidak berbahaya
dibiarkan tapi berpotensi membingungkan sesi berikutnya.

Catatan: `Workspace.links` sendiri sudah pernah terbukti aman disentuh — item "NextHD Photo"
berhasil ditambahkan ke situ pada sesi 24 Agustus lewat `doc.save()` dan bertahan lewat
migrate berkali-kali.

### Perbaikan yang Dilakukan (Pendekatan Baru, via `Workspace.links`)

1. Cek skema `tabWorkspace Link` (child table dari `Workspace.links`) — dikonfirmasi punya
   kolom `report_ref_doctype` (yang sebelumnya bikin error di `Workspace Sidebar Item`),
   sehingga link report bisa dibuat lebih lengkap dan benar di tabel ini.
2. Item ke-14 "NextHD Report" (generic, `link_type: DocType`, `link_to: Report`) dihapus dari
   `Workspace Link`, diganti 6 link report langsung (`link_type: Report`, dengan
   `report_ref_doctype` terisi): Tiket per Bulan, Tiket per Agent, Tiket per Prioritas, Tiket
   per Kategori, SLA Compliance Bulanan (semua ref `NextHD Ticket`), dan Aset Bermasalah (ref
   `NextHD Asset`).
3. **Sengaja dibuat flat (bukan submenu/section collapsible)** — dukungan `type: Section
   Break` di `Workspace Link` belum terverifikasi (beda dari `Workspace Sidebar Item` yang
   sudah terbukti support), jadi pendekatan yang lebih aman dipilih dulu.
4. Hasil dikonfirmasi via `bench console`: total 19 item di `Workspace.links` (13 lama + 6
   report baru di idx 14-19), urutan dan `link_to` sesuai rencana.

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
    print("")
    print("=== CONTOH LEWAT frappe.get_doc (format ORM, kalau mau doc.save()) ===")
    doc = frappe.get_doc("Workspace", "NextHD")
    for l in doc.links:
        print(l.as_dict())

check()
EOF
sed -i 's/\r$//' /home/it/check_workspace_link_schema.py && \
sed -i 's/^    /\t/' /home/it/check_workspace_link_schema.py && \
cat -A /home/it/check_workspace_link_schema.py | head -5 && \
bench --site desk.ciptamebel.co.id console < /home/it/check_workspace_link_schema.py > /home/it/check_workspace_link_schema_result.txt 2>&1 && \
cat /home/it/check_workspace_link_schema_result.txt
```

### Script — Ganti "NextHD Report" dengan 6 Link Report di `Workspace.links` (Sudah Dijalankan, Hasil OK)

```bash
cat > /home/it/replace_workspace_link_report.py << 'EOF'
def replace():
    print("=== GANTI NextHD Report DI Workspace.links ===")
    target = frappe.db.sql("SELECT name, idx FROM `tabWorkspace Link` WHERE parent='NextHD' AND label='NextHD Report'", as_dict=True)
    if len(target) == 0:
        print("TIDAK KETEMU item NextHD Report. Cek manual, tidak lanjut.")
        return
    old_idx = target[0].idx
    old_name = target[0].name
    print("Ketemu item lama idx " + str(old_idx) + " name " + old_name)
    frappe.db.sql("DELETE FROM `tabWorkspace Link` WHERE name=%s", (old_name,))
    from frappe.utils import now, generate_hash
    now_ts = now()
    user = frappe.session.user
    new_rows = []
    new_rows.append(("Link", "Tiket per Bulan", "Report", "Tiket per Bulan", "NextHD Ticket"))
    new_rows.append(("Link", "Tiket per Agent", "Report", "Tiket per Agent", "NextHD Ticket"))
    new_rows.append(("Link", "Tiket per Prioritas", "Report", "Tiket per Prioritas", "NextHD Ticket"))
    new_rows.append(("Link", "Tiket per Kategori", "Report", "Tiket per Kategori", "NextHD Ticket"))
    new_rows.append(("Link", "SLA Compliance Bulanan", "Report", "SLA Compliance Bulanan", "NextHD Ticket"))
    new_rows.append(("Link", "Aset Bermasalah", "Report", "Aset Bermasalah", "NextHD Asset"))
    i = 0
    for row in new_rows:
        row_type, label, link_type, link_to, ref_dt = row
        row_name = generate_hash(length=10)
        row_idx = old_idx + i
        frappe.db.sql("INSERT INTO `tabWorkspace Link` (name, parent, parenttype, parentfield, idx, type, label, link_type, link_to, report_ref_doctype, hidden, onboard, is_query_report, link_count, docstatus, creation, modified, modified_by, owner) VALUES (%s, 'NextHD', 'Workspace', 'links', %s, %s, %s, %s, %s, %s, 0, 0, 0, 0, 0, %s, %s, %s, %s)", (row_name, row_idx, row_type, label, link_type, link_to, ref_dt, now_ts, now_ts, user, user))
        i = i + 1
    frappe.db.commit()
    print("Selesai. 6 link report disisipkan di idx " + str(old_idx) + " sampai " + str(old_idx + 5))
    print("")
    print("=== VERIFIKASI ===")
    rows = frappe.db.sql("SELECT idx, label, link_to FROM `tabWorkspace Link` WHERE parent='NextHD' ORDER BY idx", as_dict=True)
    print("Total item sekarang: " + str(len(rows)))
    for r in rows:
        print(str(r.idx) + " | " + r.label + " -> " + str(r.link_to))

replace()
EOF
sed -i 's/\r$//' /home/it/replace_workspace_link_report.py && \
sed -i 's/^    /\t/' /home/it/replace_workspace_link_report.py && \
cat -A /home/it/replace_workspace_link_report.py | head -5 && \
bench --site desk.ciptamebel.co.id console < /home/it/replace_workspace_link_report.py
```

**Hasil eksekusi 25 Agustus:** berhasil. Total item `Workspace.links` sekarang **19** — 13
item lama + 6 link report baru di idx 14-19 (Tiket per Bulan, Tiket per Agent, Tiket per
Prioritas, Tiket per Kategori, SLA Compliance Bulanan, Aset Bermasalah), semua `link_to`
sesuai rencana.

### Yang Belum Selesai / Langkah Berikutnya

1. **Buat backup baru** (`bench backup --with-files`) sebelum lanjut — jangan pakai backup
   lama, karena kondisi DB sudah berubah lagi sejak backup itu dibuat (fixture workflow sudah
   diperbaiki kedua kalinya, `Workspace.links` sudah diubah)
2. **Jalankan `bench migrate`** — ini akan jadi uji nyata pertama untuk dua perbaikan
   sekaligus: fixture `workflow_transition.json` (name sudah disamakan, commit `322827f`) dan
   pendekatan baru sidebar via `Workspace.links`
3. **Verifikasi pasca-migrate:** jalankan `check_workflow_transition_clean.py` (harus tetap
   7/6/8), cek jumlah `Workspace Sidebar Item` (harus merefleksikan 6 report baru dari
   `Workspace.links` — idealnya 19-20 item: 13 lama + Photo + 6 report), dan cek manual di
   browser (sidebar kiri harus menampilkan 6 report tersebut)
4. **Kalau migrate sukses dan sidebar benar** → pertimbangkan apakah mau upgrade ke submenu
   collapsible (perlu riset dulu apakah `Workspace Link` support `type: Section Break`, belum
   pernah dicoba)
5. **Kalau migrate gagal/regresi lagi** → restore dari backup baru, jangan ulangi pola
   coba-coba tanpa riset akar masalah dulu
6. **Jangan edit `Workspace Sidebar Item` atau file `workspace_sidebar/nexthd.json` langsung
   lagi** — pendekatan itu sudah terbukti salah dan berisiko menghapus data
7. Pertimbangkan apakah file `nexthd/next_helpdesk/workspace_sidebar/nexthd.json` di repo
   perlu dihapus atau diberi catatan "tidak dipakai" supaya tidak membingungkan sesi
   berikutnya

---

*Dokumen ini dikelola oleh Claude. Update terakhir: 2026-08-25.*
