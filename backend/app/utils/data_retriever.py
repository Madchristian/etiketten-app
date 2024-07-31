"""
This class is responsible for retrieving data from a SQLite database.
"""

import sqlite3
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class DataRetriever:
    """
    This class is responsible for retrieving data from a SQLite database."""
    def __init__(self, db_path):
        self.db_path = db_path

    def get_sorted_data(self, upload_id):
        """
        Retrieves sorted data from the database by upload_id."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = '''
                    SELECT * FROM etiketten
                    WHERE upload_id = ?
                    ORDER BY Annahmedatum_Uhrzeit1 ASC, id ASC
                '''
                df = pd.read_sql_query(query, conn, params=(upload_id,))
        except Exception as e:
            logger.error("Fehler beim Abrufen der sortierten Daten: %s", e)
            raise
        return df

    def get_all_data(self):
        """
        Retrieves all data from the database.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = '''
                    SELECT * FROM etiketten
                    ORDER BY Annahmedatum_Uhrzeit1 ASC, id ASC
                '''
                df = pd.read_sql_query(query, conn)
        except Exception as e:
            logger.error("Fehler beim Abrufen aller Daten: %s", e)
            raise
        return df
