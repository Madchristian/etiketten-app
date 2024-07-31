import sqlite3
import os
import logging

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_DIR = '/app'
DB_PATH = os.path.join(DB_DIR, 'etiketten.db')

# Verzeichnis erstellen, falls es nicht existiert
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

class DatabaseInitializer:
    """
    Diese Klasse ist für die Initialisierung der Datenbank zuständig.
    """

    @staticmethod
    def initialize(db_path):
        """
        Initialisiert die Datenbank, indem erforderliche Tabellen erstellt werden.

        :param db_path: Pfad zur Datenbankdatei
        """
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''CREATE TABLE IF NOT EXISTS etiketten_count (
                                  id INTEGER PRIMARY KEY,
                                  count INTEGER NOT NULL DEFAULT 0
                                )''')
                cursor.execute('''CREATE TABLE IF NOT EXISTS processed_labels (
                                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                                  timestamp TEXT,
                                  label_count INTEGER
                                )''')
                cursor.execute('SELECT count FROM etiketten_count WHERE id = 1')
                row = cursor.fetchone()
                if row is None:
                    cursor.execute('INSERT INTO etiketten_count (id, count) VALUES (1, 0)')
                conn.commit()
                logger.info("Datenbank erfolgreich initialisiert.")
        except sqlite3.Error as e:
            logger.error("Fehler beim Initialisieren der Datenbank: %s", e)
            raise

    @staticmethod
    def get_count(db_path):
        """
        Gibt die Anzahl der Datensätze in der Tabelle 'etiketten_count' zurück.

        :param db_path: Pfad zur Datenbankdatei
        :return: Anzahl der Datensätze oder None, wenn kein Datensatz gefunden wurde
        """
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT count FROM etiketten_count WHERE id = 1')
                row = cursor.fetchone()
                if row is not None:
                    return row[0]
                else:
                    logger.info("Keine Datensätze in der Tabelle 'etiketten_count' gefunden.")
                    return None
        except sqlite3.Error as e:
            logger.error("Fehler beim Abrufen der Anzahl der Datensätze: %s", e)
            raise
    
    @staticmethod
    def list_tables(db_path):
        """
        Listet alle Tabellen in der Datenbank auf.

        :param db_path: Pfad zur Datenbankdatei
        :return: Liste der Tabellennamen
        """
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                return [table[0] for table in tables]
        except sqlite3.Error as e:
            logger.error("Fehler beim Auflisten der Tabellen: %s", e)
            raise

# Verbindung und Cursor erstellen
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Hauptinitialisierung der Datenbank
if __name__ == "__main__":
    DatabaseInitializer.initialize(DB_PATH)
    count = DatabaseInitializer.get_count(DB_PATH)
    if count is not None:
        logger.info("Anzahl der Datensätze in der Tabelle 'etiketten_count': %d", count)
    tables = DatabaseInitializer.list_tables(DB_PATH)
    logger.info("Tabellen in der Datenbank: %s", tables)