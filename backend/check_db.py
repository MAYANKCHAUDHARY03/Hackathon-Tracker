import sqlite3
import traceback

conn = sqlite3.connect("app.db")
try:
    cursor = conn.cursor()
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='projects'")
    schema = cursor.fetchone()[0]
    print("SCHEMA:")
    print(schema)
    
    # Try fetching a project
    try:
        cursor.execute("SELECT * FROM projects LIMIT 1")
        print("Successfully queried projects")
    except sqlite3.OperationalError as e:
        print("Query failed:", e)

except Exception as e:
    traceback.print_exc()
finally:
    conn.close()
