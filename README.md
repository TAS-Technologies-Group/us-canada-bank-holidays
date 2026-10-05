# US & Canada Holidays

A list of United States and Canadian holidays that flags which ones are **bank holidays**, plus a small Python script that builds the list for any year.

- `us_canada_holidays_2026.csv`, `us_canada_holidays_2027.csv`, `us_canada_holidays_2028.csv` — ready-to-use data, one file per year
- `build_holidays.py` — generates the same CSV for any year or range of years

When a US holiday on a Saturday is observed on the Friday before, and that Friday falls in the previous year, the observed row appears in the previous year's file. For example, New Year's Day 2028 is observed on December 31, 2027, so that row is in the 2027 file.

## Data format

| Column | Description |
| --- | --- |
| `Country` | ISO 3166-1 alpha-2 code: `US` or `CA` |
| `Date` | ISO 8601 date (`YYYY-MM-DD`) |
| `Holiday` | Holiday name. Weekend holidays observed on another day appear twice: once on the actual date and once as `(observed)` |
| `Bank Holiday` | `Yes`, `No`, or `Regional` (see below) |
| `Notes` | Context such as provinces affected or why a date is not a bank holiday |

Rows are sorted by date, then country.

### What "Bank Holiday" means

**United States (`US`)** follows the [Federal Reserve Banks holiday schedule (K.8)](https://www.federalreserve.gov/aboutthefed/k8.htm).

- `Yes`: Federal Reserve Banks are closed.
- `No`: Federal Reserve Banks are open. This covers Good Friday, which is not a federal holiday although stock markets close.
- Weekend rule: when a holiday falls on a **Saturday**, Fed Banks stay **open** the Friday before, even though federal offices close (`No`). When it falls on a **Sunday**, Fed Banks close the following **Monday** (`Yes`).

**Canada (`CA`)** follows the Payments Canada clearing systems (Lynx and ACSS).

- `Yes`: national payment systems are closed. When a holiday falls on a weekend, it moves to the next free weekday.
- `Regional`: national payment systems run, but banks in some provinces or territories may be closed. This covers Family Day, the Quebec-only holidays, and Yukon's Discovery Day.
- `No`: banks are generally open. This covers Easter Monday, a federal government holiday.

## Generating data

The script needs Python 3.8 or newer and uses only the standard library.

```bash
# One year
python build_holidays.py 2028

# A range of years (inclusive)
python build_holidays.py 2026 2030

# Choose the output file
python build_holidays.py 2028 -o holidays_2028.csv
```

By default the output is named `us_canada_holidays_<start>[_<end>].csv`.

## Holidays included

**United States:** New Year's Day, Martin Luther King Jr. Day, Presidents' Day, Good Friday (not a bank holiday), Memorial Day, Juneteenth (2021 onward), Independence Day, Labor Day, Columbus Day / Indigenous Peoples' Day, Veterans Day, Thanksgiving Day, Christmas Day.

**Canada:** New Year's Day, Day after New Year's Day (Quebec), Family Day, Good Friday, Easter Monday, Victoria Day, Saint-Jean-Baptiste Day (Quebec), Canada Day, Civic Holiday, Discovery Day (Yukon), Labour Day, National Day for Truth and Reconciliation (2021 onward), Thanksgiving Day, Remembrance Day, Christmas Day, Boxing Day.

State-level US holidays and most provincial holidays outside banking are not included.

## Limitations and maintenance

The script calculates dates from fixed rules, so it cannot discover new holidays or policy changes on its own.

- **New holidays** must be added by hand, as Juneteenth and the National Day for Truth and Reconciliation were in 2021.
- **Some Canadian weekend shifts are assumed, not verified.** The script moves Remembrance Day, the National Day for Truth and Reconciliation and the Quebec holidays to the next weekday when they fall on a weekend, following common practice.
- **Bank branch hours vary.** Some branches open on Remembrance Day in Ontario and Quebec, for example. This list reflects payment-system status, not individual branch hours.

Before relying on a new year's output, compare it with:

- [Federal Reserve: Holidays Observed (K.8)](https://www.federalreserve.gov/aboutthefed/k8.htm)
- [Payments Canada](https://www.payments.ca) or your bank's Canadian holiday processing calendar
- [Canada Revenue Agency: Public holidays](https://www.canada.ca/en/revenue-agency/services/tax/public-holidays.html)

The script's US output for 2026–2030 has been checked against the Federal Reserve's published K.8 schedule.

## Disclaimer

This data is provided for planning purposes only. It is not legal or financial advice. Confirm critical dates, such as payment or settlement deadlines, with your financial institution.

## Contributing

Corrections are welcome. If a date is wrong or a rule has changed, please open an issue or pull request and include a link to the official source.

## License

Released under the [MIT License](LICENSE). Copyright (c) 2026 TAS Technologies Group.
