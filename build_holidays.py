#!/usr/bin/env python3
# Copyright (c) 2026 TAS Technologies Group
# SPDX-License-Identifier: MIT
"""
Build a CSV of US and Canadian holidays for one or more years.

Columns: Country, Date, Holiday, Bank Holiday, Notes
  Bank Holiday = Yes | No | Regional
    US     -> Federal Reserve Banks schedule (K.8)
    Canada -> Payments Canada clearing systems (Lynx / ACSS)

Usage:
  python build_holidays.py 2028              # one year
  python build_holidays.py 2026 2030         # range, inclusive
  python build_holidays.py 2028 -o mine.csv  # custom output file

No third-party packages needed (Python 3.8+).

Review the rules below if a holiday is added or a schedule changes. Check:
  https://www.federalreserve.gov/aboutthefed/k8.htm
  https://www.payments.ca
"""
import argparse
import csv
import datetime as dt

YES, NO, REG = "Yes", "No", "Regional"
SAT, SUN = 5, 6


# ---------- date helpers ----------
def easter(y):
    """Gregorian Easter Sunday (anonymous Gregorian algorithm)."""
    a, b, c = y % 19, y // 100, y % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return dt.date(y, month, day)


def nth_weekday(y, month, weekday, n):
    """n-th weekday (Mon=0) of a month; n=-1 means last."""
    if n > 0:
        d = dt.date(y, month, 1)
        d += dt.timedelta((weekday - d.weekday()) % 7)
        return d + dt.timedelta(weeks=n - 1)
    nxt = dt.date(y + (month == 12), month % 12 + 1, 1)
    d = nxt - dt.timedelta(1)
    return d - dt.timedelta((d.weekday() - weekday) % 7)


def next_monday(d):
    return d + dt.timedelta((7 - d.weekday()) % 7 or 7)


def day_name(d):
    return d.strftime("%A")


# ---------- United States (Federal Reserve) ----------
def us_fixed(rows, d, name, note=""):
    """Fed rule: Saturday -> Fed Banks open the Friday before (federal offices
    closed); Sunday -> closed the following Monday."""
    if d.weekday() == SAT:
        rows.append(("US", d, name, NO, "Saturday"))
        rows.append(("US", d - dt.timedelta(1), f"{name} (observed)", NO,
                     f"{d:%B} {d.day} is a Saturday; federal offices closed, Fed Banks open"))
    elif d.weekday() == SUN:
        rows.append(("US", d, name, NO, "Sunday"))
        rows.append(("US", d + dt.timedelta(1), f"{name} (observed)", YES,
                     f"{d:%B} {d.day} is a Sunday"))
    else:
        rows.append(("US", d, name, YES, note))


def us_holidays(y):
    rows = []
    jan1 = dt.date(y, 1, 1)
    if jan1.weekday() == SAT:
        # observed date falls on Dec 31 of the previous year (listed in that year)
        rows.append(("US", jan1, "New Year's Day", NO, "Saturday"))
    else:
        us_fixed(rows, jan1, "New Year's Day")
    rows.append(("US", nth_weekday(y, 1, 0, 3), "Martin Luther King Jr. Day", YES, ""))
    rows.append(("US", nth_weekday(y, 2, 0, 3), "Presidents' Day (Washington's Birthday)", YES, ""))
    rows.append(("US", easter(y) - dt.timedelta(2), "Good Friday", NO,
                 "Not a federal holiday; stock markets closed"))
    rows.append(("US", nth_weekday(y, 5, 0, -1), "Memorial Day", YES, ""))
    if y >= 2021:
        us_fixed(rows, dt.date(y, 6, 19), "Juneteenth")
    us_fixed(rows, dt.date(y, 7, 4), "Independence Day")
    rows.append(("US", nth_weekday(y, 9, 0, 1), "Labor Day", YES, ""))
    rows.append(("US", nth_weekday(y, 10, 0, 2), "Columbus Day / Indigenous Peoples' Day", YES,
                 "Stock markets open"))
    us_fixed(rows, dt.date(y, 11, 11), "Veterans Day", "Stock markets open")
    rows.append(("US", nth_weekday(y, 11, 3, 4), "Thanksgiving Day", YES, ""))
    us_fixed(rows, dt.date(y, 12, 25), "Christmas Day")
    # Next year's New Year's Day on a Saturday is observed on Dec 31 of this year
    if dt.date(y + 1, 1, 1).weekday() == SAT:
        rows.append(("US", dt.date(y, 12, 31), f"New Year's Day {y + 1} (observed)", NO,
                     f"Jan 1, {y + 1} is a Saturday; federal offices closed, Fed Banks open"))
    return rows


# ---------- Canada (Payments Canada) ----------
def ca_fixed(rows, d, name, taken, note=""):
    """Payments Canada rule: a weekend holiday moves to the next free weekday."""
    if d.weekday() < SAT:
        rows.append(("CA", d, name, YES, note))
        taken.add(d)
        return d
    rows.append(("CA", d, name, NO, day_name(d)))
    obs = d
    while obs.weekday() >= SAT or obs in taken:
        obs += dt.timedelta(1)
    rows.append(("CA", obs, f"{name} (observed)", YES, f"{d:%b} {d.day} is a {day_name(d)}"))
    taken.add(obs)
    return obs


def ca_holidays(y):
    rows, taken = [], set()
    ny_obs = ca_fixed(rows, dt.date(y, 1, 1), "New Year's Day", taken)
    jan2 = dt.date(y, 1, 2)
    if jan2.weekday() < SAT and jan2 != ny_obs:
        rows.append(("CA", jan2, "Day after New Year's Day", REG,
                     "Quebec only; no payments processed in Quebec"))
    rows.append(("CA", nth_weekday(y, 2, 0, 3), "Family Day", REG,
                 "AB, BC, NB, ON, SK; also Louis Riel Day (MB), Islander Day (PE), Heritage Day (NS). "
                 "Payments Canada open; many banks closed in these provinces"))
    e = easter(y)
    rows.append(("CA", e - dt.timedelta(2), "Good Friday", YES, ""))
    rows.append(("CA", e + dt.timedelta(1), "Easter Monday", NO,
                 "Federal government holiday; banks generally open"))
    may24 = dt.date(y, 5, 24)
    rows.append(("CA", may24 - dt.timedelta(may24.weekday()), "Victoria Day", YES,
                 "National Patriots' Day in Quebec"))
    sjb = dt.date(y, 6, 24)
    name = "Saint-Jean-Baptiste Day (Fete nationale)"
    if sjb.weekday() == SUN:  # Quebec moves a Sunday holiday to Monday
        rows.append(("CA", sjb, name, NO, "Sunday"))
        rows.append(("CA", sjb + dt.timedelta(1), f"{name} (observed)", REG, "Quebec only"))
    elif sjb.weekday() == SAT:
        rows.append(("CA", sjb, name, NO, "Saturday"))
    else:
        rows.append(("CA", sjb, name, REG, "Quebec only"))
    ca_fixed(rows, dt.date(y, 7, 1), "Canada Day", taken)
    rows.append(("CA", nth_weekday(y, 8, 0, 1), "Civic Holiday", YES,
                 "Name varies (BC Day, Heritage Day, NB Day, Natal Day); not a holiday in Quebec"))
    rows.append(("CA", nth_weekday(y, 8, 0, 3), "Discovery Day", REG, "Yukon only"))
    rows.append(("CA", nth_weekday(y, 9, 0, 1), "Labour Day", YES, ""))
    if y >= 2021:
        ca_fixed(rows, dt.date(y, 9, 30), "National Day for Truth and Reconciliation", taken,
                 "Payments Canada systems closed")
    rows.append(("CA", nth_weekday(y, 10, 0, 2), "Thanksgiving Day", YES, ""))
    ca_fixed(rows, dt.date(y, 11, 11), "Remembrance Day", taken,
             "Payments Canada closed; some bank branches open in ON and QC")
    ca_fixed(rows, dt.date(y, 12, 25), "Christmas Day", taken)
    ca_fixed(rows, dt.date(y, 12, 26), "Boxing Day", taken)
    return rows


# ---------- output ----------
def build(years):
    rows = []
    for y in years:
        rows += us_holidays(y) + ca_holidays(y)
    rows.sort(key=lambda r: (r[1], r[0]))
    return rows


def main():
    p = argparse.ArgumentParser(description="Build a US/Canada holiday CSV.")
    p.add_argument("start", type=int, help="first year")
    p.add_argument("end", type=int, nargs="?", help="last year (inclusive); defaults to start")
    p.add_argument("-o", "--output", help="output CSV path")
    a = p.parse_args()
    end = a.end or a.start
    if end < a.start:
        p.error("end year must be >= start year")
    years = range(a.start, end + 1)
    out = a.output or (f"us_canada_holidays_{a.start}.csv" if a.start == end
                       else f"us_canada_holidays_{a.start}_{end}.csv")
    rows = build(years)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Country", "Date", "Holiday", "Bank Holiday", "Notes"])
        for c, d, h, b, n in rows:
            w.writerow([c, d.isoformat(), h, b, n])  # ISO 3166-1 alpha-2: US, CA
    print(f"Wrote {len(rows)} rows to {out}")


if __name__ == "__main__":
    main()
