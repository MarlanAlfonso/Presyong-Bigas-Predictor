"""
Cleans the PSA retail rice prices (long-format from presyong_bigas.db or load_psa output) and writes data/processed/ncr_rice_prices_clean.csv.

Steps
1. Load all 288 rows from presyong_bigas.db (PSA, NCR only)
2. Ensure a complete monthly date spine per commodity (Jan 2018 – Dec 2025)
3. Forward-fill any gaps in price_per_kg
4. Detect outliers per commodity using IQR (1.5x fence)
5. Flag outliers with is_outlier column (rows are kept, not removed)
6. Drop exact duplicates (guard; none expected given UNIQUE constraint)
7. Write data/processed/ncr_rice_prices_clean.csv

Design decisions
- Missing months  → forward-fill (LOCF)
- Outlier detection → IQR (1.5× fence, per commodity)
- Outlier handling → flag only (is_outlier = True, row kept)
"""

import argparse
import sqlite3
from pathlib import Path

import pandas as pd


# Paths 
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB   = PROJECT_ROOT / "db"  / "presyong_bigas.db"
DEFAULT_OUT  = PROJECT_ROOT / "data" / "processed" / "ncr_rice_prices_clean.csv"

COMMODITIES  = ["well_milled", "regular_milled", "special"]
DATE_START   = "2018-01-01"
DATE_END     = "2025-12-01"


# Core functions (importable for unit tests) 
def load_from_db(db_path: Path) -> pd.DataFrame:
    #Load PSA NCR rows from rice_prices table.
    con = sqlite3.connect(db_path)
    df = pd.read_sql_query(
        """
        SELECT date, price_per_kg, commodity, region, source, price_type
        FROM rice_prices
        WHERE source = 'PSA' AND region = 'NCR'
        ORDER BY commodity, date
        """,
        con,
        parse_dates=["date"],
    )
    con.close()
    return df

def ensure_date_spine(df: pd.DataFrame) -> pd.DataFrame:
    # For each commodity, ensure every month from DATE_START to DATE_END exists.
    # Missing months are inserted with NaN price, then forward-filled.
    full_index = pd.date_range(start=DATE_START, end=DATE_END, freq="MS")
    frames = []

    for commodity in COMMODITIES:
        subset = df[df["commodity"] == commodity].copy()
        subset = subset.set_index("date")

        # Reindex to full monthly spine
        subset = subset.reindex(full_index)

        # Fill non-price metadata
        subset["commodity"]  = commodity
        subset["region"]     = subset["region"].fillna("NCR")
        subset["source"]     = subset["source"].fillna("PSA")
        subset["price_type"] = subset["price_type"].fillna("retail")

        # Forward-fill price gaps (LOCF)
        filled_before = subset["price_per_kg"].isna().sum()
        subset["price_per_kg"] = subset["price_per_kg"].ffill()
        filled_after  = subset["price_per_kg"].isna().sum()

        subset["gap_filled"] = False
        # Mark rows that were filled (original price was NaN, now has value)
        if filled_before > filled_after:
            # Identify which indices were filled by comparing to original index
            original_dates = df.loc[df["commodity"] == commodity, "date"].values
            subset.loc[
                ~subset.index.isin(original_dates) & subset["price_per_kg"].notna(),
                "gap_filled"
            ] = True

        subset.index.name = "date"
        frames.append(subset.reset_index())

    return pd.concat(frames, ignore_index=True)

def flag_outliers(df: pd.DataFrame, iqr_factor: float = 1.5) -> pd.DataFrame:
    #Flag outliers per commodity using IQR fence.
    # Adds boolean column is_outlier. Rows are NOT removed.
    df = df.copy()
    df["is_outlier"] = False

    for commodity in COMMODITIES:
        mask = df["commodity"] == commodity
        prices = df.loc[mask, "price_per_kg"]

        q1 = prices.quantile(0.25)
        q3 = prices.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - iqr_factor * iqr
        upper = q3 + iqr_factor * iqr

        outlier_mask = mask & ((df["price_per_kg"] < lower) | (df["price_per_kg"] > upper))
        df.loc[outlier_mask, "is_outlier"] = True

    return df

def drop_duplicates(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    # Drop exact duplicate rows on (date, commodity, region, source).
    before = len(df)
    df = df.drop_duplicates(subset=["date", "commodity", "region", "source"])
    return df, before - len(df)

def clean(db_path: Path, out_path: Path) -> dict:
    # Full cleaning pipeline. Returns a summary dict
    # 1. Load
    df = load_from_db(db_path)
    print(f"Loaded from DB       : {len(df)} rows")

    # 2. Complete date spine + forward-fill
    df = ensure_date_spine(df)
    gaps_filled = int(df["gap_filled"].sum())
    print(f"Gaps forward-filled  : {gaps_filled}")

    # 3. Detect and flag outliers
    df = flag_outliers(df)
    n_outliers = int(df["is_outlier"].sum())
    print(f"Outliers flagged     : {n_outliers}")

    # 4. Drop duplicates
    df, n_dupes = drop_duplicates(df)
    print(f"Duplicates dropped   : {n_dupes}")

    # 5. Sort and write
    df = df.sort_values(["commodity", "date"]).reset_index(drop=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False, date_format="%Y-%m-%d")
    print(f"Written to           : {out_path}")
    print(f"Final row count      : {len(df)}")

    return {
        "loaded": len(df),
        "gaps_filled": gaps_filled,
        "outliers_flagged": n_outliers,
        "duplicates_dropped": n_dupes,
        "output_rows": len(df),
    }


# CLI
def main() -> None:
    parser = argparse.ArgumentParser(description="Clean PSA rice price data")
    parser.add_argument("--db",  type=Path, default=DEFAULT_DB)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    if not args.db.exists():
        raise FileNotFoundError(f"DB not found: {args.db}. Run init_db.py first.")

    print(f"DB   : {args.db}")
    print(f"Out  : {args.out}")
    print("─" * 45)
    clean(args.db, args.out)
    print("Done.")

if __name__ == "__main__":
    main()