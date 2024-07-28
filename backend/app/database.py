import sqlite3

db_path = '/app/etiketten.db'
conn = sqlite3.connect(db_path, check_same_thread=False)
cursor = conn.cursor()

# Tabelle erstellen, falls nicht vorhanden
cursor.execute('''CREATE TABLE IF NOT EXISTS etiketten_count (
                  id INTEGER PRIMARY KEY,
                  count INTEGER NOT NULL DEFAULT 0
                )''')
conn.commit()

# Initialisiere den Zähler, falls nicht vorhanden
cursor.execute('SELECT count FROM etiketten_count WHERE id = 1')
row = cursor.fetchone()
if row is None:
    cursor.execute('INSERT INTO etiketten_count (id, count) VALUES (1, 0)')
    conn.commit()