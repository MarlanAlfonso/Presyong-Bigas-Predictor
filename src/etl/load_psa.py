# Parses the PSA wide-format CSV and INSERTs rows into the rice_prices table.

import argparse
import sqlite3
from pathlib import Path

import pandas as pd

# Defaults
PROJECT_ROOT = Path(__file__).resolve().parents[2]   # src/etl/ → project root
DEFAULT_CSV  = PROJECT_ROOT / "data" / "raw" / "psa_retail_rice_prices_ncr_2018_2025.csv"
DEFAULT_DB   = PROJECT_ROOT / "db"  / "presyong_bigas.db"

# Maps raw PSA commodity strings - DB commodity codes
COMMODITY_MAP: dict[str, str] = {
    "RICE, WELL-MILLED, 1 KG":    "well_milled",
    "RICE, REGULAR-MILLED, 1 KG": "regular_milled",
    "RICE, SPECIAL, 1 KG":        "special",
}

# Maps month name - zero-padded month number
MONTH_MAP: dict[str, str] = {
    "January": "01", "February": "02", "March":    "03",
    "April":   "04", "May":      "05", "June":     "06",
    "July":    "07", "August":   "08", "September":"09",
    "October": "10", "November": "11", "December": "12",
}

# Core functions (importable for unit tests)
def load_csv(csv_path: Path) -> pd.DataFrame:
    """
    Reads the PSA wide CSV and returns a clean long-format DataFrame.

    Columns returned: date (str YYYY-MM-DD), price_per_kg (float),
                      commodity (str), region (str), source (str), price_type (str)
    """
    # Row 1 = title, row 2 = blank → skip first 2 rows; row 3 becomes header
    df_wide = pd.read_csv(csv_path, skiprows=2, dtype=str)

    # Normalise column names (strip whitespace)
    df_wide.columns = [c.strip() for c in df_wide.columns]

    # Year columns are everything after Geolocation / Commodity / Period
    year_cols = [c for c in df_wide.columns if c.isdigit()]

    rows = []
    for _, row in df_wide.iterrows():
        raw_commodity = str(row["Commodity"]).strip()
        period        = str(row["Period"]).strip()

        commodity = COMMODITY_MAP.get(raw_commodity)
        month_num = MONTH_MAP.get(period)

        # Skip rows we don't recognise
        if commodity is None or month_num is None:
            continue

        for year in year_cols:
            raw_price = str(row[year]).strip()
            if raw_price in ("", "nan", "-", ".."):
                continue  # missing value — skip rather than insert NULL

            rows.append({
                "date":         f"{year}-{month_num}-01",
                "price_per_kg": float(raw_price),
                "commodity":    commodity,
                "region":       "NCR",
                "source":       "PSA",
                "price_type":   "retail",
            })

    return pd.DataFrame(rows)


def insert_rows(df: pd.DataFrame, db_path: Path) -> dict[str, int]:
    """
    INSERTs rows into rice_prices, skipping duplicates (INSERT OR IGNORE).

    Returns a summary dict with keys: attempted, inserted, skipped.
    """
    if df.empty:
        return {"attempted": 0, "inserted": 0, "skipped": 0}

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    sql = """
        INSERT OR IGNORE INTO rice_prices
            (date, price_per_kg, commodity, region, source, price_type)
        VALUES
            (:date, :price_per_kg, :commodity, :region, :source, :price_type)
    """

    before = _row_count(cur)
    cur.executemany(sql, df.to_dict(orient="records"))
    con.commit()
    after = _row_count(cur)
    con.close()

    inserted = after - before
    attempted = len(df)
    return {"attempted": attempted, "inserted": inserted, "skipped": attempted - inserted}


def _row_count(cur: sqlite3.Cursor) -> int:
    cur.execute("SELECT COUNT(*) FROM rice_prices;")
    return cur.fetchone()[0]

# CLI entry point
def main() -> None:
    parser = argparse.ArgumentParser(description="Load PSA retail rice prices into presyong_bigas.db")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV,
                        help="Path to PSA CSV file")
    parser.add_argument("--db",  type=Path, default=DEFAULT_DB,
                        help="Path to SQLite database file")
    args = parser.parse_args()

    if not args.csv.exists():
        raise FileNotFoundError(f"CSV not found: {args.csv}")
    if not args.db.exists():
        raise FileNotFoundError(
            f"Database not found: {args.db}\n"
            "Run `python src/etl/init_db.py` first."
        )

    print(f"CSV  : {args.csv}")
    print(f"DB   : {args.db}")

    df = load_csv(args.csv)
    print(f"Rows parsed from CSV : {len(df)}")

    summary = insert_rows(df, args.db)
    print(f"Attempted : {summary['attempted']}")
    print(f"Inserted  : {summary['inserted']}")
    print(f"Skipped   : {summary['skipped']}  (duplicates / already loaded)")
    print("Done.")


if __name__ == "__main__":
    main()