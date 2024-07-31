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
                
                # Neue Spalte für Schlüsselwörter hinzufügen, wenn sie nicht existiert
                cursor.execute("ALTER TABLE etiketten ADD COLUMN IF NOT EXISTS Schluesselwort TEXT DEFAULT ''")

                # Setze Standardwert für Fertigstellungstermin, wenn leer
                cursor.execute("UPDATE etiketten SET Fertigstellungstermin = '-' WHERE Fertigstellungstermin IS NULL OR Fertigstellungstermin = ''")
                
                # Übertragen der Schlüsselwörter in die neue Spalte
                cursor.execute("""
                    UPDATE etiketten
                    SET Schluesselwort = CASE
                        WHEN Notizen_Serviceberater LIKE '%Assyst%' THEN 'W'
                        WHEN Notizen_Serviceberater LIKE '%Wartung%' THEN 'W'
                        WHEN Notizen_Serviceberater LIKE '%Service%' THEN 'W'
                        ELSE ''
                    END
                """)
                
                conn.commit()
        except sqlite3.Error as e:
            print(f"Fehler bei der Datenvorverarbeitung: {e}")
            raise