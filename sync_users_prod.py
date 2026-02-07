"""Sync user data from SQLite to MySQL (update existing rows)."""
import sqlite3
import pymysql

SQLITE_PATH = "/home/shareloc/ieeetadeo/tickets.db"
MYSQL_CONFIG = {
    "host": "localhost",
    "user": "ieeetadeo",
    "password": "IEEE_Tadeo_2025!",
    "database": "ieeetadeo",
    "charset": "utf8mb4",
}

sq = sqlite3.connect(SQLITE_PATH)
sq.row_factory = sqlite3.Row

my = pymysql.connect(**MYSQL_CONFIG, autocommit=False)
mycur = my.cursor()

# Get MySQL columns
mycur.execute("DESCRIBE users")
mysql_cols = {r[0] for r in mycur.fetchall()}

# Get all SQLite users
rows = sq.cursor().execute("SELECT * FROM users").fetchall()
sqlite_cols = rows[0].keys() if rows else []

# Columns to update (intersection, excluding id)
update_cols = [c for c in sqlite_cols if c in mysql_cols and c != "id"]

print(f"Updating {len(rows)} users, {len(update_cols)} columns each")

updated = 0
for row in rows:
    sets = ", ".join("`" + c + "`=%s" for c in update_cols)
    vals = [row[c] for c in update_cols] + [row["id"]]
    mycur.execute("UPDATE users SET " + sets + " WHERE id=%s", vals)
    if mycur.rowcount > 0:
        updated += 1

my.commit()
print(f"Updated {updated} users")

# Verify
mycur.execute("SELECT count(*) FROM users WHERE login_count > 0")
print(f"Portal users now: {mycur.fetchone()[0]}")

my.close()
sq.close()
