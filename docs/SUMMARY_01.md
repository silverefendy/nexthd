# Rangkuman Sesi — Status/Priority/Ticket Type Berwarna di NextHD

> Dibuat sebagai catatan kelanjutan (continuity) kalau sesi chat terputus/token habis.
> Copy-paste isi file ini ke sesi baru sebagai konteks awal.
>
> **Catatan penomoran:** file ini `SUMMARY_01.md` — bagian dari seri rangkuman sesi kerja
> (bukan pengganti `docs/SUMMARY.md` utama). Kalau sudah menumpuk beberapa file `SUMMARY_NN.md`,
> akan di-compress/digabung jadi satu lagi di sesi mendatang.

---

## 1. Masalah Awal

Efendy ingin kolom **Status** di NextHD Ticket (dan berpotensi Priority, Ticket Type, serta
doctype lain) tampil **berwarna**, bukan abu-abu semua.

---

## 2. Investigasi & Temuan Penting

### 2.1 Ada 2 Mekanisme Berbeda yang Sempat Membingungkan

| Mekanisme | Fungsi | Status di NextHD |
|---|---|---|
| **A. `Workflow State.style`** (master global, doctype `Workflow State`) | Mewarnai badge/indicator status berdasarkan **state Workflow** — dipakai Frappe untuk kolom Status di List View kalau doctype pakai Workflow | ✅ **Ini yang akhirnya jadi solusi** — kosong semua di awal, sudah diisi |
| **B. `get_indicator` di `<doctype>_list.js`** (`frappe.listview_settings`) | Fungsi custom JS untuk render titik indicator + warna di List View | Sudah ada duluan sejak 8 September (file: `public/js/nexthd_ticket_list.js`, terdaftar di `hooks.py` via `doctype_list_js`) — **tidak terdokumentasi sebelumnya** |

**Kesalahan awal:** sempat mencoba cek/set field `style` di **`Workflow Document State`**
(child table per-Workflow) — ini **SALAH TABEL**, field `style` tidak ada di situ
(`AttributeError: 'WorkflowDocumentState' object has no attribute 'style'`).

**Field yang benar:** `style` ada di master **`Workflow State`** (global, dipakai lintas semua
Workflow di seluruh site) — tabel `tabWorkflow State`, cukup di-`UPDATE`/`set_value` langsung.

### 2.2 Kenapa Warna Tidak Muncul Padahal `get_indicator` Sudah Benar

- `get_indicator` custom (Opsi B) **sudah ter-load dengan benar** di browser — dikonfirmasi via
  console: `frappe.listview_settings['NextHD Ticket']` mengembalikan object berisi fungsi
  `get_indicator`, dan `cur_list.settings.get_indicator(cur_list.data[0])` mengembalikan array
  yang benar, mis. `["Sedang Dikerjakan", "blue", "status,=,Sedang Dikerjakan"]`.
- **Tapi** tampilan List View Efendy pakai **kolom kustom eksplisit** (Status, Priority,
  Requested By, dst ditambahkan manual via "+ Add/Remove Fields") — bukan tampilan kartu
  default Frappe. Dalam mode ini, Frappe merender kolom "Status" sebagai **field biasa**
  (pakai warna dari **`Workflow State.style`**, bukan dari `get_indicator` JS).
- **Ditemukan juga:** field "Status" ke-duplikat 3× di List View Settings (bug konfigurasi
  terpisah, bukan penyebab utama, tapi perlu dibereskan — lihat §5 Item Belum Selesai).

### 2.3 Root Cause & Solusi Final

**Root cause:** `Workflow State.style` (master global) kosong untuk kelima state Ticket
(Baru, Sedang Dikerjakan, Menunggu User, Selesai, Ditutup).

**Fix yang berhasil (sudah dieksekusi & dikonfirmasi tampil berwarna oleh Efendy):**

```bash
cat > /home/it/set_master_workflow_state_style.py << 'EOF'
def main_check():
    mapping = {
        "Baru": "Warning",
        "Sedang Dikerjakan": "Primary",
        "Menunggu User": "Inverse",
        "Selesai": "Success",
        "Ditutup": "Danger"
    }
    for state, style in mapping.items():
        if frappe.db.exists("Workflow State", state):
            frappe.db.set_value("Workflow State", state, "style", style)
            print(state + " -> di-set ke " + style)
        else:
            print(state + " -> [TIDAK DITEMUKAN, skip]")
    frappe.db.commit()

main_check()
EOF
sed -i 's/\r$//' /home/it/set_master_workflow_state_style.py && \
sed -i 's/^    /\t/' /home/it/set_master_workflow_state_style.py && \
bench --site desk.ciptamebel.co.id console < /home/it/set_master_workflow_state_style.py
```

Lalu `bench clear-cache` + hard refresh browser → **warna langsung muncul, dikonfirmasi
Efendy**.

---

## 3. Persistensi — Apakah Aman dari `bench migrate`/`bench build`?

| Operasi | Aman? | Alasan |
|---|---|---|
| `bench build` | ✅ Aman | Cuma compile asset JS/CSS, tidak sentuh database sama sekali |
| `bench migrate` | ✅ Aman | `Workflow State` **sengaja tidak terdaftar di fixtures** `hooks.py` (dikonfirmasi berkali-kali di dokumentasi project — field ini tidak punya kolom `workflow` sehingga tidak bisa difilter fixture, sifatnya global). Karena bukan fixture, migrate tidak reimport/menimpa data `style` |
| Install ulang app dari nol (`bench reinstall`) di server BARU | ⚠️ Berisiko | Kalau `install.py` bikin ulang master `Workflow State` untuk server baru, `style` akan balik kosong — perlu ditambahkan ke checklist instalasi server baru |
| Restore database dari backup lama | ⚠️ Ya, hilang | Berlaku untuk semua perubahan data apapun, bukan spesifik ini |

**Kesimpulan: aman untuk operasional harian (migrate/build rutin di server produksi
`desk.ciptamebel.co.id`).**

---

## 4. Pertanyaan Terbuka Efendy (Belum Dijawab Detail) — Priority, Ticket Type, Doctype Lain

### 4.1 Bisakah Priority & Ticket Type Juga Diwarnai?

**Bisa, tapi mekanismenya BEDA dari Status** — ini penting dipahami:

- **Status** = field terikat Workflow → otomatis pakai warna dari `Workflow State.style`
  (mekanisme A) tanpa perlu kode tambahan.
- **Priority** dan **Ticket Type** = field **Select biasa** (bukan Workflow) → `Workflow
  State.style` **tidak berlaku** untuk field ini. Titik `• Sedang` yang terlihat di
  screenshot List View kemungkinan besar cuma bullet dekoratif abu-abu polos (bukan
  berwarna kondisional).
- **Cara mewarnai field Select seperti Priority/Ticket Type:** pakai `formatters` di
  `frappe.listview_settings` (BUKAN `get_indicator` — `get_indicator` cuma untuk SATU
  titik indicator utama per baris, biasanya dipakai untuk status). `formatters` bisa
  custom render HTML per kolom/field apapun.

**Contoh penambahan ke `public/js/nexthd_ticket_list.js` yang sudah ada** (menambah, bukan
mengganti isi yang sudah ada):

```javascript
frappe.listview_settings['NextHD Ticket'] = {
    get_indicator: function(doc) {
        var status_colors = {
            "Baru": "red",
            "Sedang Dikerjakan": "blue",
            "Menunggu User": "yellow",
            "Selesai": "green",
            "Ditutup": "gray"
        };
        var color = status_colors[doc.status] || "gray";
        return [__(doc.status), color, "status,=," + doc.status];
    },
    formatters: {
        priority: function(value) {
            var color_map = {
                "Kritis": "red",
                "Tinggi": "orange",
                "Sedang": "yellow",
                "Rendah": "green"
            };
            var color = color_map[value] || "gray";
            return `<span class="indicator-pill ${color}">${__(value)}</span>`;
        },
        ticket_type: function(value) {
            var color_map = {
                "Insiden": "red",
                "Permintaan Layanan": "blue"
            };
            var color = color_map[value] || "gray";
            return `<span class="indicator-pill ${color}">${__(value)}</span>`;
        }
    }
};
```

**Catatan:**
- Key di `formatters` harus **fieldname** persis (`priority`, `ticket_type` — cek dulu
  fieldname asli via `frappe.get_meta("NextHD Ticket")` kalau ragu, jangan asumsi dari
  label tampilan).
- Class CSS `indicator-pill <color>` adalah class bawaan Frappe — otomatis dapat styling
  pill/badge berwarna tanpa perlu CSS custom.
- File ini **tidak boleh di-push Claude ke GitHub** — Efendy yang commit setelah
  ditest berhasil (aturan project: Claude hanya push `.md`).

### 4.2 Bisakah Doctype Lain (Problem, Change Request, Known Error, Asset) Juga Diwarnai?

**Bisa**, pola sama persis, tapi perlu 2 keputusan per-doctype:

| Doctype | Field Status | Mekanisme yang Berlaku | Field Select Lain yang Bisa Diwarnai |
|---|---|---|---|
| NextHD Problem | `status` (Workflow) | A (`Workflow State.style` — style-nya **SAMA** dengan Ticket karena state "Terbuka" dst kemungkinan reuse master yang sama, perlu dicek) | `priority` |
| NextHD Change Request | `status` (Workflow) | A (idem, cek dulu apakah nama state-nya sama dengan Ticket/Problem atau unik) | `change_type`, `risk_level` |
| NextHD Known Error | ❌ **Tidak ada field `status`** (dikonfirmasi di `ARSITEKTUR.md`) | — | — (tidak relevan) |
| NextHD Asset | `status` (Select biasa, **BUKAN** Workflow — Asset tidak pakai Workflow) | B (`formatters`, bukan `Workflow State.style`) | `asset_category` (Link, agak beda pendekatan) |

**Penting — cek dulu sebelum eksekusi ke Problem/Change Request:**
Karena `Workflow State` adalah **master global** (bukan per-Workflow), state dengan nama
sama (misal kalau ada state "Selesai" dipakai di Ticket DAN Problem/CR) akan **otomatis
ikut ke-set warnanya juga** begitu kita ubah salah satu — ini bisa jadi keuntungan
(konsisten) atau masalah (kalau ternyata state yang namanya sama tapi maksudnya beda).
**Rekomendasi:** jalankan dulu script audit nama-nama state di ketiga Workflow sebelum
menambah/mengubah `style` lagi, supaya tidak menimpa yang sudah benar untuk Ticket.

---

## 5. Item Belum Selesai / Next Steps

| # | Item | Prioritas | Keterangan |
|---|---|---|---|
| 1 | Bereskan duplikat field "Status" ×3 di List View Settings NextHD Ticket | Sedang | Buka List View Settings → hapus 2 dari 3 baris "Status" duplikat → Save. Bug kosmetik terpisah, tidak mempengaruhi warna, tapi bikin tampilan aneh |
| 2 | Audit nama Workflow State di Problem & Change Request sebelum warnai statusnya | Tinggi (kalau lanjut ke doctype lain) | Perlu cek dulu nama-nama state supaya tidak menimpa mapping warna Ticket yang sudah benar (karena `Workflow State` global) |
| 3 | Tambah `formatters` untuk Priority & Ticket Type di `nexthd_ticket_list.js` | Sesuai permintaan Efendy | Kode contoh sudah disiapkan di §4.1 — tinggal ditulis Efendy ke file yang sudah ada, lalu `bench build` + `clear-cache` + restart |
| 4 | Warnai Priority di Problem, Change Request (kalau applicable) | Opsional | Field `priority`/`risk_level` Select biasa, pakai pola `formatters` yang sama |
| 5 | Warnai Status Asset (`formatters`, bukan `Workflow State`, karena Asset tidak pakai Workflow) | Opsional | Perlu file baru `nexthd_asset_list.js` + entri baru di `doctype_list_js` |
| 6 | Update `docs/DAFTAR_FITUR.md` mencatat fitur "Status Berwarna" selesai | Housekeeping | Belum dilakukan — tunggu semua item warna (Ticket status+priority+type, doctype lain kalau jadi dikerjakan) selesai dulu baru dicatat sekaligus, supaya tidak bolak-balik commit `.md` |

---

## 6. File & Lokasi Terkait (untuk Referensi Cepat)

| File/Path | Isi/Fungsi |
|---|---|
| `nexthd/public/js/nexthd_ticket_list.js` | File `get_indicator` untuk NextHD Ticket, sudah ada sejak 8 September, siap ditambah `formatters` |
| `nexthd/hooks.py` (baris ~313) | `doctype_list_js = {"NextHD Ticket": "public/js/nexthd_ticket_list.js"}` — sudah terdaftar |
| Master `Workflow State` (DB, bukan file) | `style` untuk Baru/Sedang Dikerjakan/Menunggu User/Selesai/Ditutup sudah diisi Warning/Primary/Inverse/Success/Danger |
| `docs/ARSITEKTUR.md §3` | Referensi field per-DocType (cek `status` ada/tidak, tipe field Select vs Workflow) |
| `docs/WORKFLOW.md §2` | Daftar state per-Workflow (Ticket/Problem/Change Request) — perlu dicek sebelum ubah `Workflow State` lagi |

---

*Rangkuman ini dibuat 9 September 2026 dalam sesi chat. Bagian dari seri `SUMMARY_NN.md` —
akan digabung/dirapikan lagi ke `docs/SUMMARY.md` utama atau file tematik lain setelah
menumpuk beberapa sesi.*
