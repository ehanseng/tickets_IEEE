"""
Script de migración: SQLite -> MySQL (producción)
Lee datos faltantes de tickets.db (SQLite) e inserta en MySQL.
Ejecutar en el servidor de producción.
"""
import sqlite3
import pymysql
import json
from datetime import datetime

SQLITE_PATH = "/home/shareloc/ieeetadeo/tickets.db"
MYSQL_CONFIG = {
    "host": "localhost",
    "user": "ieeetadeo",
    "password": "IEEE_Tadeo_2025!",
    "database": "ieeetadeo",
    "charset": "utf8mb4",
}

def get_sqlite_conn():
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_mysql_conn():
    return pymysql.connect(**MYSQL_CONFIG, autocommit=False)

def get_existing_ids(mysql_cur, table, id_col="id"):
    mysql_cur.execute(f"SELECT {id_col} FROM {table}")
    return {row[0] for row in mysql_cur.fetchall()}

def migrate_table(sqlite_conn, mysql_conn, table, columns, id_col="id"):
    """Migrate missing rows from SQLite to MySQL for a given table."""
    sqlite_cur = sqlite_conn.cursor()
    mysql_cur = mysql_conn.cursor()

    sqlite_cur.execute(f"SELECT * FROM {table}")
    rows = sqlite_cur.fetchall()
    col_names = [desc[0] for desc in sqlite_cur.description]

    # Check if id_col exists; if not, use INSERT IGNORE for all rows
    has_id = id_col in col_names
    existing_ids = set()
    if has_id:
        existing_ids = get_existing_ids(mysql_cur, table, id_col)

    id_idx = col_names.index(id_col) if has_id else None
    inserted = 0
    skipped = 0

    for row in rows:
        if has_id:
            row_id = row[id_idx]
            if row_id in existing_ids:
                skipped += 1
                continue

        values = {}
        for i, col in enumerate(col_names):
            if col in columns:
                values[col] = row[i]

        if not values:
            continue

        cols_str = ", ".join(f"`{c}`" for c in values.keys())
        placeholders = ", ".join(["%s"] * len(values))
        sql = f"INSERT IGNORE INTO `{table}` ({cols_str}) VALUES ({placeholders})"

        try:
            mysql_cur.execute(sql, list(values.values()))
            if mysql_cur.rowcount > 0:
                inserted += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"  ERROR inserting {table}: {e}")

    mysql_conn.commit()
    print(f"  {table}: {inserted} inserted, {skipped} skipped (already exist)")

def get_mysql_columns(mysql_cur, table):
    mysql_cur.execute(f"DESCRIBE `{table}`")
    return {row[0] for row in mysql_cur.fetchall()}

def main():
    print("=== Migración SQLite -> MySQL ===")
    sqlite_conn = get_sqlite_conn()
    mysql_conn = get_mysql_conn()
    mysql_cur = mysql_conn.cursor()

    # Tables to migrate in order (respecting foreign keys)
    tables_order = [
        "admin_users",
        "users",
        "universities",
        "tags",
        "events",
        "projects",
        "tickets",
        "campaigns",
        "messages",
        "event_attendance",
        "event_photos",
        "user_tags",
        "user_studies",
        "project_members",
    ]

    for table in tables_order:
        # Check if table exists in both databases
        try:
            sqlite_conn.cursor().execute(f"SELECT count(*) FROM {table}")
        except sqlite3.OperationalError:
            print(f"  {table}: does not exist in SQLite, skipping")
            continue

        try:
            mysql_cur.execute(f"SELECT count(*) FROM `{table}`")
        except Exception:
            print(f"  {table}: does not exist in MySQL, skipping")
            continue

        mysql_cols = get_mysql_columns(mysql_cur, table)
        print(f"Migrating {table}...")
        migrate_table(sqlite_conn, mysql_conn, table, mysql_cols)

    # Summary
    print("\n=== Verificación final ===")
    for table in tables_order:
        try:
            sc = sqlite_conn.cursor()
            sc.execute(f"SELECT count(*) FROM {table}")
            sqlite_count = sc.fetchone()[0]
        except:
            sqlite_count = "N/A"
        try:
            mysql_cur.execute(f"SELECT count(*) FROM `{table}`")
            mysql_count = mysql_cur.fetchone()[0]
        except:
            mysql_count = "N/A"
        print(f"  {table}: SQLite={sqlite_count}, MySQL={mysql_count}")

    sqlite_conn.close()
    mysql_conn.close()
    print("\nMigración completada!")

if __name__ == "__main__":
    main()
