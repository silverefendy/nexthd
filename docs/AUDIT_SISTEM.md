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
| §2 Workflow | `is_active=0` atau jumlah transisi tidak sesuai (Ticket 7, Problem 6, CR 8) = ada yang belum di-migrate/rusak. `idx=0` count > 0 = ada duplikat belum dibersihkan |
| §3 Workspace/Sidebar | Item pertama HARUS "Dashboard" (link ke Workspace) — kalau bukan, navigasi terkunci sudah bergeser dari HANDOFF.md, cek segera |
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
> Request 32→8 — root cause: `Workflow Action Master` "Convert to Known Error" hilang,
> bikin `wf.save()` gagal validasi sampai master dibuat ulang), penambahan 8 Cuti Bersama
> 2026, dan patch `install.py` di atas.
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

### Hasil Terakhir (24 Agustus 2026)

Semua 9 titik pemeriksaan **OK**, kecuali satu anomali yang perlu keputusan manusia:

- Workflow Transition: Ticket 7/7, Problem 6/6, Change Request 8/8 — semua unik, tidak ada duplikat
- Workflow Action Master: 17 action unik, tidak ada yang bolong
- Sidebar: "NextHD Photo" muncul
- Number Card: "Total Foto Terupload" muncul (total 9 card)
- SLA Policy: sesuai SOP final 19 Agustus, Kritis `is_24x7=1`
- Holiday: 25 record (17 nasional + 8 cuti bersama 2026)
- Roles: 5/5 ada
- NextHD Photo DocType: aktif, 0 record (belum ada foto diupload, wajar karena fitur baru live)

**⚠️ Anomali ditemukan — belum diputuskan:** Business Hours **Sabtu tercatat `is_working_day=1`** (hari kerja), padahal `install.py` (setelah patch 24 Agustus) men-set default Sabtu `is_working_day=0` (bukan hari kerja). Perlu diklarifikasi: apakah Sabtu memang sengaja dijadikan hari kerja di production (kalau ya, `install.py` perlu disesuaikan lagi supaya konsisten), atau ini data lama yang salah dan perlu dikoreksi ke `0`. **Belum ada tindakan diambil terhadap ini — menunggu keputusan.**

---

*Dokumen ini dikelola oleh Claude. Dipakai on-demand (bukan tiap sesi), jalankan lagi kapan saja meragukan konsistensi server vs repo.*
