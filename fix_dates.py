#!/usr/bin/env python3
"""
Script to fix malformed date strings in the conference_sessions.db.
In some records the day and time run together (e.g. "Jun 510:00 AM").
This script adds a missing space between the day and the time.
"""
import os
import re
import sqlite3

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "conference_sessions.db")

def main():
    # Pattern: prefix up through month and space, then day digits, then time with no leading space
    pattern = re.compile(r'^(.*?, [A-Za-z]{3} )([0-9]{1,2})([0-9]{1,2}:[0-9]{2}.*)$')
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT rowid, date FROM sessions")
    updates = []
    for row in cursor.fetchall():
        original = row["date"]
        m = pattern.match(original)
        if m:
            fixed = f"{m.group(1)}{m.group(2)} {m.group(3)}"
            if fixed != original:
                updates.append((fixed, row["rowid"]))
    if not updates:
        print("No malformed dates found.")
    else:
        for new_date, rowid in updates:
            cursor.execute(
                "UPDATE sessions SET date = ? WHERE rowid = ?",
                (new_date, rowid)
            )
        conn.commit()
        print(f"Fixed {len(updates)} date entries in the DB.")
    conn.close()

if __name__ == "__main__":
    main()