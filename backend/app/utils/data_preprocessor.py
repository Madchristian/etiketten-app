import sqlite3

class DataPreprocessor:
    """
    This class is responsible for preprocessing data in a SQLite database.
    """
    @staticmethod
    def preprocess_data(db_path):
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Setze Standardwert für Fertigstellungstermin, wenn leer
                cursor.execute("UPDATE etiketten SET Fertigstellungstermin = '-' WHERE Fertigstellungstermin IS NULL OR Fertigstellungstermin = ''")

                # Übertragen der Schlüsselwörter in die neue Spalte
                cursor.execute("""
                    UPDATE etiketten
                    SET Schluesselwort = CASE
                        WHEN Reparaturumfang LIKE '%Assyst%' THEN 'WD '
                        WHEN Reparaturumfang LIKE '%Wartung%' THEN 'WD '
                        WHEN Reparaturumfang LIKE '%Service%' THEN 'WD '
                        WHEN Reparaturumfang LIKE '%Inspektion%' THEN 'WD '
                        ELSE ''
                    END
                """)
                conn.commit()
        except sqlite3.Error as e:
            print(f"Fehler bei der Datenvorverarbeitung: {e}")
            raise