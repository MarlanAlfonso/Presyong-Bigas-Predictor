# Initializes the SQLite database
"""
What it does:
    1. Creates db/presyong_bigas.db if it does not exist
    2. Executes db/schema.sql (CREATE TABLE, indexes, view)
    3. Confirms the table and view exist
    4. Prints a summary
"""

import sqlite3
from pathlib import Path

# Paths 
PROJECT_ROOT = Path(__file__).resolve().parents[2]  # src/etl/ → project root
DB_PATH      = PROJECT_ROOT / "db" / "presyong_bigas.db"
SCHEMA_PATH  = PROJECT_ROOT / "db" / "schema.sql"


def init_db() -> None:
    # Check that schema.sql exists
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema file not found: {SCHEMA_PATH}")

    # Create db/ directory if missing
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    db_existed = DB_PATH.exists()

    # Connect (creates the file on first run)
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    #  Execute schema
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    cur.executescript(schema_sql)
    con.commit()

    # Verify table exists
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='rice_prices';")
    table = cur.fetchone()

    # Verify view exists
    cur.execute("SELECT name FROM sqlite_master WHERE type='view' AND name='well_milled_ncr';")
    view = cur.fetchone()

    # Verify indexes
    cur.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='rice_prices';")
    indexes = [row[0] for row in cur.fetchall()]

    con.close()

    # Report
    status = "already existed" if db_existed else "created"
    print(f"Database : {DB_PATH}  [{status}]")
    print(f"Table    : {'rice_prices ✓' if table else 'rice_prices ✗ NOT FOUND'}")
    print(f"View     : {'well_milled_ncr ✓' if view else 'well_milled_ncr ✗ NOT FOUND'}")
    print(f"Indexes  : {indexes if indexes else 'none found'}")
    print("Done.")


if __name__ == "__main__":
    init_db()