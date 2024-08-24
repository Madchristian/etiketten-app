import sqlite3
import os
import logging

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_DIR = '/app/db'
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
                
                # Tabelle 'etiketten_count' erstellen
                cursor.execute('''CREATE TABLE IF NOT EXISTS etiketten_count (
                                  id INTEGER PRIMARY KEY,
                                  count INTEGER NOT NULL DEFAULT 0
                                )''')
                logger.info("'etiketten_count' Tabelle erstellt oder bereits vorhanden.")

                # Tabelle 'processed_labels' erstellen
                cursor.execute('''CREATE TABLE IF NOT EXISTS processed_labels (
                                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                                  timestamp TEXT,
                                  label_count INTEGER
                                )''')
                logger.info("'processed_labels' Tabelle erstellt oder bereits vorhanden.")

                # Tabelle 'etiketten_config' erstellen
                cursor.execute('''CREATE TABLE IF NOT EXISTS etiketten_config (
                                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                                  name TEXT NOT NULL,
                                  label_width REAL NOT NULL,
                                  label_height REAL NOT NULL,
                                  margin_left REAL NOT NULL,
                                  margin_top REAL NOT NULL,
                                  h_space REAL NOT NULL,
                                  v_space REAL NOT NULL,
                                  rows INTEGER NOT NULL,
                                  columns INTEGER NOT NULL,
                                  max_name_length INTEGER NOT NULL
                                )''')
                logger.info("'etiketten_config' Tabelle erstellt oder bereits vorhanden.")

                # Initialeintrag für eine Standardkonfiguration
                cursor.execute('SELECT count(*) FROM etiketten_config')
                if cursor.fetchone()[0] == 0:
                    cursor.execute('''INSERT INTO etiketten_config 
                                      (name, label_width, label_height, margin_left, margin_top, 
                                       h_space, v_space, rows, columns, max_name_length) 
                                      VALUES 
                                      ('Standardetikett Avery 3657', 48.5, 25.4, 7, 21, 0, 0, 10, 4, 21)''')
                    logger.info("Standardkonfiguration in 'etiketten_config' Tabelle hinzugefügt.")
                else:
                    logger.info("Standardkonfiguration in 'etiketten_config' Tabelle bereits vorhanden.")
                
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