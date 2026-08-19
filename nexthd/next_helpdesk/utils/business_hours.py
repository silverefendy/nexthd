import frappe
from frappe.utils import get_datetime, add_to_date, getdate

WEEKDAY_MAP = {
    0: "Senin", 1: "Selasa", 2: "Rabu", 3: "Kamis",
    4: "Jumat", 5: "Sabtu", 6: "Minggu"
}


def is_holiday(date):
    return bool(frappe.db.exists("NextHD Holiday", {"holiday_date": getdate(date)}))


def get_business_hours(weekday_name):
    row = frappe.db.get_value(
        "NextHD Business Hours",
        {"day": weekday_name},
        ["is_working_day", "start_time", "end_time"],
        as_dict=True,
    )
    if not row or not row.is_working_day:
        return None
    return row


def next_working_start(dt):
    """Cari waktu mulai kerja berikutnya dari dt. Kalau dt sudah di dalam jam kerja, return dt apa adanya."""
    dt = get_datetime(dt)
    for _ in range(30):
        weekday_name = WEEKDAY_MAP[dt.weekday()]
        bh = get_business_hours(weekday_name)
        if bh and not is_holiday(dt.date()):
            start_dt = get_datetime(f"{dt.date()} {bh.start_time}")
            end_dt = get_datetime(f"{dt.date()} {bh.end_time}")
            if dt <= start_dt:
                return start_dt
            if dt < end_dt:
                return dt
        dt = get_datetime(f"{dt.date()} 00:00:00")
        dt = add_to_date(dt, days=1)
    frappe.log_error("Business Hours: 30-day lookahead exceeded", "NextHD SLA")
    return dt


def add_working_time(start_dt, duration_minutes, is_24x7=0):
    """
    Tambahkan durasi (menit) ke start_dt, hanya menghitung jam kerja.
    Loop per hari kerja, kurangi sisa menit yang kepakai tiap hari,
    lompat ke hari kerja berikutnya kalau durasi belum habis.
    """
    if is_24x7:
        return add_to_date(get_datetime(start_dt), minutes=duration_minutes, as_datetime=True)

    remaining = duration_minutes
    current = next_working_start(start_dt)

    for _ in range(400):  # safety cap ~ lebih dari 1 tahun kerja, cukup buat SLA terpanjang (1 minggu)
        weekday_name = WEEKDAY_MAP[current.weekday()]
        bh = get_business_hours(weekday_name)

        if not bh or is_holiday(current.date()):
            current = next_working_start(add_to_date(get_datetime(f"{current.date()} 00:00:00"), days=1))
            continue

        window_end = get_datetime(f"{current.date()} {bh.end_time}")
        available_minutes = (window_end - current).total_seconds() / 60

        if available_minutes <= 0:
            current = next_working_start(add_to_date(get_datetime(f"{current.date()} 00:00:00"), days=1))
            continue

        if remaining <= available_minutes:
            return add_to_date(current, minutes=remaining, as_datetime=True)

        remaining -= available_minutes
        current = next_working_start(add_to_date(get_datetime(f"{current.date()} 00:00:00"), days=1))

    frappe.log_error("add_working_time: 400-iteration cap exceeded", "NextHD SLA")
    return current
