import sqlite3
import pandas as pd
import uuid
import logging

logger = logging.getLogger(__name__)

class DataLoader:
    """
    This class is responsible for loading data from a file into a SQLite database.
    """
    def __init__(self, db_path):
        self.db_path = db_path

    def load_data(self, file_path):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                self._migrate_table(cursor)
                upload_id = self._generate_upload_id()
                df = self._read_and_prepare_data(file_path, upload_id)
                
                # Log der Rohdaten vor dem Filtern
                logger.info("Rohdaten vor dem Filtern:")
                logger.info(df.head())

                # Überprüfen der einzigartigen Werte von `Terminstatus`
                unique_status = df['Terminstatus'].unique()
                logger.info(f"Einzigartige Werte von `Terminstatus`: {unique_status}")

                # Filtern der Daten
                df = df[df['Terminstatus'].astype(str) == '2']
                logger.info("Daten nach dem Filtern:")
                logger.info(df.head())

                df.to_sql('etiketten', conn, if_exists='append', index=False)
                self._log_table_structure(cursor)
        except Exception as e:
            logger.error(f"Fehler beim Laden der Daten in die Datenbank: {e}")
            raise
        return upload_id

    def _migrate_table(self, cursor):
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS etiketten (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                upload_id TEXT,
                Kundenname TEXT,
                Annahmedatum_Uhrzeit1 TEXT,
                Fertigstellungstermin TEXT,
                Amtl_Kennzeichen TEXT,
                Terminart TEXT,
                Reparaturumfang TEXT,
                Notizen_Serviceberater TEXT,
                Auftragsnummer TEXT,
                Direktannahme TEXT,
                Terminstatus TEXT,
                Modell TEXT,
                Schluesselwort TEXT DEFAULT ''
            )
        ''')
        
        # Check if the column 'Schluesselwort' exists, if not, add it
        cursor.execute("PRAGMA table_info(etiketten)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'Schluesselwort' not in columns:
            cursor.execute("ALTER TABLE etiketten ADD COLUMN Schluesselwort TEXT DEFAULT ''")

    def _generate_upload_id(self):
        return str(uuid.uuid4())

    def _read_and_prepare_data(self, file_path, upload_id):
        columns = {
            'Auftragsnummer': 'Auftragsnummer',
            'Annahmedatum_Uhrzeit1': 'Annahmedatum_Uhrzeit1',
            'Notizen_Serviceberater': 'Notizen_Serviceberater',
            'Reparaturumfang': 'Reparaturumfang',
            'Kundenname': 'Kundenname',
            'Fertigstellungstermin': 'Fertigstellungstermin',
            'Terminart': 'Terminart',
            'Amtl. Kennzeichen': 'Amtl_Kennzeichen',
            'Direktannahme am Fzg.': 'Direktannahme',
            'Terminstatus': 'Terminstatus',
            'Modell': 'Modell'
        }
        df = pd.read_csv(file_path, sep='\t', usecols=columns.keys())
        df.rename(columns=columns, inplace=True)
        df['upload_id'] = upload_id
        logger.info("DataFrame Spalten nach dem Laden:")
        logger.info(df.columns)
        logger.info("Erste Zeilen der DataFrame:")
        logger.info(df.head())
        return df

    def _log_table_structure(self, cursor):
        cursor.execute('PRAGMA table_info(etiketten)')
        table_info = cursor.fetchall()
        logger.info("Struktur der Tabelle 'etiketten':")
        logger.info(table_info)