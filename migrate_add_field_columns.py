"""
Migration: Add field_name, field_location, session_id to weekly_assessments
Run this ONCE before starting the Flask app after updating model.py

Usage:
    python migrate_add_field_columns.py

It is safe to run multiple times — it checks if columns already exist first.
"""

import sqlite3
import os
import sys

# ── Find the database file ────────────────────────────────────────────────────
# Try common locations used by Flask-SQLAlchemy
POSSIBLE_PATHS = [
    'agripal.db',
    'instance/agripal.db',
    'database.db',
    'instance/database.db',
    'app.db',
    'instance/app.db',
]

DB_PATH = None
for p in POSSIBLE_PATHS:
    if os.path.exists(p):
        DB_PATH = p
        break

if DB_PATH is None:
    # Let the user specify
    if len(sys.argv) > 1:
        DB_PATH = sys.argv[1]
    else:
        print("❌ Could not find database file automatically.")
        print("   Please run:  python migrate_add_field_columns.py <path_to_your.db>")
        print("   Example:     python migrate_add_field_columns.py instance/agripal.db")
        sys.exit(1)

print(f"🗄️  Using database: {DB_PATH}")

# ── Connect and migrate ───────────────────────────────────────────────────────
conn = sqlite3.connect(DB_PATH)
cur  = conn.cursor()

# Get existing columns in weekly_assessments
cur.execute("PRAGMA table_info(weekly_assessments)")
existing_cols = {row[1] for row in cur.fetchall()}
print(f"   Existing columns: {len(existing_cols)} found")

# Columns to add: (column_name, SQL_definition)
NEW_COLUMNS = [
    ('field_name',     "VARCHAR(100) DEFAULT 'Field 1'"),
    ('field_location', "VARCHAR(200) DEFAULT ''"),
    ('session_id',     "VARCHAR(64)  DEFAULT ''"),
]

added = []
for col_name, col_def in NEW_COLUMNS:
    if col_name in existing_cols:
        print(f"   ✅ Column '{col_name}' already exists — skipping")
    else:
        sql = f"ALTER TABLE weekly_assessments ADD COLUMN {col_name} {col_def}"
        cur.execute(sql)
        added.append(col_name)
        print(f"   ➕ Added column '{col_name}'")

conn.commit()
conn.close()

if added:
    print(f"\n✅ Migration complete! Added: {', '.join(added)}")
    print("   You can now restart your Flask app.")
else:
    print("\n✅ No changes needed — all columns already exist.")