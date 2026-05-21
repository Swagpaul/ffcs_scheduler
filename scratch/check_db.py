import sqlite3
import os

db_path = os.path.join("instance", "ffcs_scheduler.db")
print("Checking DB at:", db_path)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())
conn.close()
