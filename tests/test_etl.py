# Unit tests for the PSA ETL pipeline.
# Uses an in-memory SQLite database — never touches the real sinaing.db.

import io
import sqlite3
import textwrap
from pathlib import Path

import pandas as pd
import pytest

# Import the functions under test
from src.etl.load_psa import (
    COMMODITY_MAP,
    MONTH_MAP,
    load_csv,
    insert_rows,
)

# Helpers
SCHEMA_PATH = Path(__file__).resolve().parents[1] / "db" / "schema.sql"

# Minimal PSA-format CSV (matches real file structure):
# Row 0 = title, Row 1 = blank, Row 2 = header, Row 3+ = data
SAMPLE_CSV_CONTENT = textwrap.dedent("""\
    "Cereals: Retail Prices of Agricultural Commodities by Geolocation, Commodity, Year and Period"

    "Geolocation","Commodity","Period","2018","2019"
    "..National Capital Region (NCR)","RICE, WELL-MILLED, 1 KG","January",43.80,42.88
    "..National Capital Region (NCR)","RICE, WELL-MILLED, 1 KG","February",43.94,42.69
    "..National Capital Region (NCR)","RICE, REGULAR-MILLED, 1 KG","January",37.26,39.15
    "..National Capital Region (NCR)","RICE, SPECIAL, 1 KG","January",54.62,56.64
""")


def make_sample_csv(tmp_path: Path) -> Path:
    """Write SAMPLE_CSV_CONTENT to a temp file and return its path."""
    csv_file = tmp_path / "sample_psa.csv"
    csv_file.write_text(SAMPLE_CSV_CONTENT, encoding="utf-8")
    return csv_file


def make_in_memory_db() -> sqlite3.Connection:
    """Create an in-memory SQLite DB with the full schema applied."""
    con = sqlite3.connect(":memory:")
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    con.executescript(schema_sql)
    con.commit()
    return con

# Tests: load_csv
class TestLoadCsv:

    def test_returns_dataframe(self, tmp_path):
        csv_path = make_sample_csv(tmp_path)
        df = load_csv(csv_path)
        assert isinstance(df, pd.DataFrame)

    def test_expected_row_count(self, tmp_path):
        """Sample CSV has 3 commodities × 2 years but only some months → 7 data points."""
        csv_path = make_sample_csv(tmp_path)
        df = load_csv(csv_path)
        # well_milled: Jan+Feb × 2 years = 4 rows
        # regular_milled: Jan × 2 years = 2 rows
        # special: Jan × 2 years = 2 rows
        assert len(df) == 8

    def test_required_columns_present(self, tmp_path):
        csv_path = make_sample_csv(tmp_path)
        df = load_csv(csv_path)
        for col in ["date", "price_per_kg", "commodity", "region", "source", "price_type"]:
            assert col in df.columns, f"Missing column: {col}"

    def test_date_format(self, tmp_path):
        csv_path = make_sample_csv(tmp_path)
        df = load_csv(csv_path)
        # All dates should be YYYY-MM-01
        assert df["date"].str.match(r"^\d{4}-\d{2}-01$").all()

    def test_commodity_values_are_normalised(self, tmp_path):
        csv_path = make_sample_csv(tmp_path)
        df = load_csv(csv_path)
        valid = {"well_milled", "regular_milled", "special"}
        assert set(df["commodity"].unique()).issubset(valid)

    def test_price_is_float(self, tmp_path):
        csv_path = make_sample_csv(tmp_path)
        df = load_csv(csv_path)
        assert df["price_per_kg"].dtype == float

    def test_region_is_ncr(self, tmp_path):
        csv_path = make_sample_csv(tmp_path)
        df = load_csv(csv_path)
        assert (df["region"] == "NCR").all()

    def test_source_is_psa(self, tmp_path):
        csv_path = make_sample_csv(tmp_path)
        df = load_csv(csv_path)
        assert (df["source"] == "PSA").all()

    def test_price_type_is_retail(self, tmp_path):
        csv_path = make_sample_csv(tmp_path)
        df = load_csv(csv_path)
        assert (df["price_type"] == "retail").all()

    def test_specific_price_value(self, tmp_path):
        """Jan 2018 well-milled should be 43.80."""
        csv_path = make_sample_csv(tmp_path)
        df = load_csv(csv_path)
        row = df[(df["date"] == "2018-01-01") & (df["commodity"] == "well_milled")]
        assert len(row) == 1
        assert row.iloc[0]["price_per_kg"] == pytest.approx(43.80)

    def test_unknown_commodity_skipped(self, tmp_path):
        """Rows with unrecognised commodity strings should be dropped."""
        bad_csv = textwrap.dedent("""\
            Title

            "Geolocation","Commodity","Period","2018"
            "..National Capital Region (NCR)","RICE, WELL-MILLED, 1 KG","January",43.80
            "..National Capital Region (NCR)","RICE, UNKNOWN TYPE, 1 KG","January",99.99
        """)
        csv_file = tmp_path / "bad.csv"
        csv_file.write_text(bad_csv, encoding="utf-8")
        df = load_csv(csv_file)
        assert len(df) == 1
        assert "unknown" not in df["commodity"].values

    def test_missing_price_skipped(self, tmp_path):
        """Cells with '..' or blank should not produce a row."""
        bad_csv = textwrap.dedent("""\
            Title

            "Geolocation","Commodity","Period","2018","2019"
            "..National Capital Region (NCR)","RICE, WELL-MILLED, 1 KG","January",43.80,..
        """)
        csv_file = tmp_path / "missing.csv"
        csv_file.write_text(bad_csv, encoding="utf-8")
        df = load_csv(csv_file)
        # Only 2018 Jan should load; 2019 Jan (".." price) should be skipped
        assert len(df) == 1
        assert df.iloc[0]["date"] == "2018-01-01"

# Tests: insert_rows  (uses in-memory DB via a real Path to :memory: workaround)
class TestInsertRows:
    """
    insert_rows() expects a Path to a .db file.
    We write a temp .db from the real schema so tests stay isolated.
    """

    def _make_temp_db(self, tmp_path: Path) -> Path:
        db_path = tmp_path / "test_sinaing.db"
        con = sqlite3.connect(db_path)
        schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
        con.executescript(schema_sql)
        con.commit()
        con.close()
        return db_path

    def _row_count(self, db_path: Path) -> int:
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM rice_prices;")
        count = cur.fetchone()[0]
        con.close()
        return count

    def _make_df(self, n: int = 3) -> pd.DataFrame:
        return pd.DataFrame([
            {
                "date":         f"2018-0{i+1}-01",
                "price_per_kg": 43.0 + i,
                "commodity":    "well_milled",
                "region":       "NCR",
                "source":       "PSA",
                "price_type":   "retail",
            }
            for i in range(n)
        ])

    def test_rows_are_inserted(self, tmp_path):
        db_path = self._make_temp_db(tmp_path)
        df = self._make_df(3)
        summary = insert_rows(df, db_path)
        assert summary["inserted"] == 3
        assert self._row_count(db_path) == 3

    def test_summary_keys_present(self, tmp_path):
        db_path = self._make_temp_db(tmp_path)
        summary = insert_rows(self._make_df(1), db_path)
        assert {"attempted", "inserted", "skipped"} == set(summary.keys())

    def test_duplicate_is_skipped(self, tmp_path):
        """Inserting the same rows twice should not raise and skipped count = 3."""
        db_path = self._make_temp_db(tmp_path)
        df = self._make_df(3)
        insert_rows(df, db_path)
        summary = insert_rows(df, db_path)  # second run
        assert summary["skipped"] == 3
        assert summary["inserted"] == 0
        assert self._row_count(db_path) == 3  # still 3, not 6

    def test_partial_duplicate(self, tmp_path):
        """First batch inserts 2 rows; second batch has 1 overlap + 1 new → 1 inserted."""
        db_path = self._make_temp_db(tmp_path)
        insert_rows(self._make_df(2), db_path)
        insert_rows(self._make_df(3), db_path)  # row 3 is new
        assert self._row_count(db_path) == 3

    def test_empty_dataframe_returns_zero_summary(self, tmp_path):
        db_path = self._make_temp_db(tmp_path)
        summary = insert_rows(pd.DataFrame(), db_path)
        assert summary == {"attempted": 0, "inserted": 0, "skipped": 0}

    def test_attempted_equals_len_df(self, tmp_path):
        db_path = self._make_temp_db(tmp_path)
        df = self._make_df(5)
        summary = insert_rows(df, db_path)
        assert summary["attempted"] == 5

    def test_well_milled_ncr_view_populated(self, tmp_path):
        """The well_milled_ncr view should return rows after insert."""
        db_path = self._make_temp_db(tmp_path)
        insert_rows(self._make_df(3), db_path)
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM well_milled_ncr;")
        count = cur.fetchone()[0]
        con.close()
        assert count == 3


# ---------------------------------------------------------------------------
# Tests: lookup maps (sanity checks)
# ---------------------------------------------------------------------------

class TestMaps:

    def test_all_three_commodities_in_map(self):
        assert "RICE, WELL-MILLED, 1 KG"    in COMMODITY_MAP
        assert "RICE, REGULAR-MILLED, 1 KG" in COMMODITY_MAP
        assert "RICE, SPECIAL, 1 KG"         in COMMODITY_MAP

    def test_all_twelve_months_in_map(self):
        assert len(MONTH_MAP) == 12

    def test_month_values_are_zero_padded(self):
        for v in MONTH_MAP.values():
            assert len(v) == 2