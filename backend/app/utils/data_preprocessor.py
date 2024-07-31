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
                
                # Manipuliere Notizen, um wichtige Wörter nach vorne zu setzen
                cursor.execute("""
                    UPDATE etiketten
                    SET Notizen_Serviceberater = CASE
                        WHEN Notizen_Serviceberater LIKE '%Wartung%' THEN 'Wartung ' || Notizen_Serviceberater
                        WHEN Notizen_Serviceberater LIKE '%Assyst%' THEN 'Assyst ' || Notizen_Serviceberater
                        WHEN Notizen_Serviceberater LIKE '%Service%' THEN 'Service ' || Notizen_Serviceberater
                        ELSE Notizen_Serviceberater
                    END
                """)
                conn.commit()
        except sqlite3.Error as e:
            print(f"Fehler bei der Datenvorverarbeitung: {e}")
            raise