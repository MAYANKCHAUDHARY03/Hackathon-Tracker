import sqlite3
conn = sqlite3.connect('c:/Hackathon tracker/hackathon-tracker/backend/hackathon.db')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = c.fetchall()
print('Tables in DB:', [t[0] for t in tables])
