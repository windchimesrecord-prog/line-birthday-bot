import sqlite3

conn = sqlite3.connect("members.db")
cursor = conn.cursor()

rows = cursor.execute("SELECT * FROM members").fetchall()

for row in rows:
    print(row)

conn.close()
