"""
Dieses Modul bietet Funktionen zum Laden, Abrufen, Löschen und Loggen von 
Etikettendaten in einer SQLite-Datenbank.

Klassen:
- DataLoader: Lädt Daten aus einer Datei in die Datenbank.
- DataRetriever: Ruft sortierte Daten aus der Datenbank ab.
- DataDeleter: Löscht Daten aus der Datenbank.
- ProcessLogger: Loggt verarbeitete Labels.

Abhängigkeiten:
- sqlite3: SQLite-Datenbankmodul
- pandas: Datenverarbeitung und -analyse
- logging: Logging-Modul für Fehler- und Informationsmeldungen

Beispiel:
    # Daten in die Datenbank laden
    data_loader = DataLoader('path/to/database.db')
    upload_id = data_loader.load_data('path/to/file.txt')

    # Sortierte Daten abrufen
    data_retriever = DataRetriever('path/to/database.db')
    sorted_data = data_retriever.get_sorted_data(upload_id)

    # Daten basierend auf der upload_id löschen
    data_deleter = DataDeleter('path/to/database.db')
    data_deleter.delete_data_by_upload_id(upload_id)

    # Verarbeitete Labels loggen
    process_logger = ProcessLogger('path/to/database.db')
    process_logger.log_processed_labels(len(sorted_data))
"""

import sqlite3
import logging

logger = logging.getLogger(__name__)

class DataDeleter:
    """
    This class is responsible for deleting data from a SQLite database.
    """
    def __init__(self, db_path):
        self.db_path = db_path

    def delete_data_by_upload_id(self, upload_id):
        """
        Deletes data from the database by upload_id."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM etiketten WHERE upload_id = ?', (upload_id,))
                conn.commit()
        except Exception as e:
            logger.error("Fehler beim Löschen der Daten mit upload_id=%s: %s", upload_id, e)
            raise

    def delete_all_data(self):
        """
        Deletes all data from the database.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM etiketten')
                conn.commit()
        except Exception as e:
            logger.error("Fehler beim Löschen aller Daten: %s", e)
            raise
