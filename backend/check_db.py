import sqlite3
conn = sqlite3.connect('test_db.sqlite')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='platform_events'")
print('EXISTS' if c.fetchone() else 'MISSING')
