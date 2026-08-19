import frappe
from frappe.utils import get_datetime, add_to_date, getdate

WEEKDAY_MAP = {
    0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday",
    4: "Friday", 5: "Saturday", 6: "Sunday"
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
        dt = add_to_date(get_datetime(f"{dt.date()} 00:00:00"), days=1)
    frappe.log_error("Business Hours: 30-day lookahead exceeded", "NextHD SLA")
    return dt


def add_working_time(start_dt, duration_minutes, is_24x7=0):
    start_dt = get_datetime(start_dt)

    if is_24x7:
        return add_to_date(start_dt, minutes=duration_minutes, as_datetime=True)

    weekday_name = WEEKDAY_MAP[start_dt.weekday()]
    bh = get_business_hours(weekday_name)
    today_is_working = bh and not is_holiday(start_dt.date())

    if today_is_working:
        window_start = get_datetime(f"{start_dt.date()} {bh.start_time}")
        window_end = get_datetime(f"{start_dt.date()} {bh.end_time}")
        effective_start = window_start if start_dt < window_start else start_dt

        if window_start <= effective_start < window_end:
            candidate = add_to_date(effective_start, minutes=duration_minutes, as_datetime=True)
            if candidate <= window_end:
                return candidate
            next_start = next_working_start(add_to_date(get_datetime(f"{start_dt.date()} 00:00:00"), days=1))
            return add_to_date(next_start, minutes=duration_minutes, as_datetime=True)

    next_start = next_working_start(start_dt)
    return add_to_date(next_start, minutes=duration_minutes, as_datetime=True)
