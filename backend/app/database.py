import sqlite3
import os
import pandas as pd
import uuid

db_dir = '/app'
db_path = os.path.join(db_dir, 'etiketten.db')

# Verzeichnis erstellen, falls nicht existiert
if not os.path.exists(db_dir):
    os.makedirs(db_dir)

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

def load_data_to_db(file_path, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Tabelle erstellen
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS etiketten (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            upload_id TEXT,
            Kundenname TEXT,
            Annahmedatum_Uhrzeit1 TEXT,
            Fertigstellungstermin TEXT,
            Amtl_Kennzeichen TEXT,
            Terminart TEXT,
            Notizen_Serviceberater TEXT,
            Auftragsnummer TEXT
        )
    ''')

    # UUID generieren
    upload_id = str(uuid.uuid4())

    # Daten aus der Datei einfügen und Spalten umbenennen
    columns = {
        'Auftragsnummer': 'Auftragsnummer',
        'Annahmedatum_Uhrzeit1': 'Annahmedatum_Uhrzeit1',
        'Notizen_Serviceberater': 'Notizen_Serviceberater',
        'Kundenname': 'Kundenname',
        'Fertigstellungstermin': 'Fertigstellungstermin',
        'Terminart': 'Terminart',
        'Amtl. Kennzeichen': 'Amtl_Kennzeichen'
    }
    df = pd.read_csv(file_path, sep='\t', usecols=columns.keys())
    df.rename(columns=columns, inplace=True)
    df['upload_id'] = upload_id  # UUID zur DataFrame hinzufügen

    # Debugging-Ausgabe der Spalten und ersten Zeilen der DataFrame
    print("DataFrame Spalten nach dem Laden:")
    print(df.columns)
    print("Erste Zeilen der DataFrame:")
    print(df.head())

    # Daten in die Datenbank einfügen
    df.to_sql('etiketten', conn, if_exists='append', index=False)

    # Debugging-Ausgabe der Tabellenstruktur
    cursor.execute('PRAGMA table_info(etiketten)')
    table_info = cursor.fetchall()
    print("Struktur der Tabelle 'etiketten':")
    print(table_info)

    conn.close()

    return upload_id

def get_sorted_data(db_path, upload_id):
    conn = sqlite3.connect(db_path)
    query = '''
        SELECT * FROM etiketten
        WHERE upload_id = ?
        ORDER BY Annahmedatum_Uhrzeit1 ASC, id ASC
    '''
    df = pd.read_sql_query(query, conn, params=(upload_id,))
    conn.close()
    return df

def delete_data_by_upload_id(db_path, upload_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM etiketten WHERE upload_id = ?', (upload_id,))
    conn.commit()
    conn.close()