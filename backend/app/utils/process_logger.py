"""
This module contains the ProcessLogger class, 
which is responsible for logging processed labels to a SQLite database.
"""
import sqlite3
from datetime import datetime
import logging
import pandas as pd

logger = logging.getLogger(__name__)

class ProcessLogger:
    """
    This class is responsible for logging processed labels to a SQLite database.
    """
    def __init__(self, db_path):
        self.db_path = db_path

    def log_processed_labels(self, label_count):
        """
        Logs the number of processed labels to the database.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute('INSERT INTO processed_labels (timestamp, label_count) VALUES (?, ?)', (timestamp, label_count))
                conn.commit()
        except Exception as e:
            logger.error("Fehler beim Protokollieren der verarbeiteten Labels: %s", e)
            raise
    
    def get_processed_labels(self):
        """
        Retrieves the processed labels from the database.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = '''
                    SELECT * FROM processed_labels
                    ORDER BY timestamp DESC
                '''
                df = pd.read_sql_query(query, conn)
        except Exception as e:
            logger.error("Fehler beim Abrufen der verarbeiteten Labels: %s", e)
            raise
        return df