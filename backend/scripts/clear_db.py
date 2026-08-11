import sqlite3

def clear_db():
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    for table in tables:
        table_name = table[0]
        if table_name != 'sqlite_sequence':
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    conn.commit()
    conn.close()
    print("Database cleared.")

if __name__ == '__main__':
    clear_db()
