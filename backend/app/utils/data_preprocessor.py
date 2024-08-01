import sqlite3
import re
import logging

logger = logging.getLogger(__name__)

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
                        WHEN Notizen_Serviceberater LIKE '%Assyst%' THEN 'WD '
                        WHEN Notizen_Serviceberater LIKE '%Wartung%' THEN 'WD '
                        WHEN Notizen_Serviceberater LIKE '%Service%' THEN 'WD '
                        ELSE ''
                    END
                """)

                # Setze Notizen_Serviceberater als Reparaturumfang, wenn Reparaturumfang vollständig in Großbuchstaben und durch Kommas getrennt ist
                cursor.execute("""
                    UPDATE etiketten
                    SET Reparaturumfang = Notizen_Serviceberater
                    WHERE Reparaturumfang = UPPER(Reparaturumfang)
                """)

                # Selektiere alle Zeilen, um die Änderungen vorzunehmen
                cursor.execute("SELECT id, Reparaturumfang FROM etiketten")
                rows = cursor.fetchall()

                for row in rows:
                    id = row[0]
                    reparaturumfang = row[1]

                    # Füge Leerzeichen nach Kommas hinzu
                    updated_reparaturumfang = re.sub(r'(?<=[A-Z]),(?=[A-Z])', ', ', reparaturumfang)
                    
                    # Aktualisiere die Zeile nur, wenn sich der Wert geändert hat
                    if updated_reparaturumfang != reparaturumfang:
                        cursor.execute("""
                            UPDATE etiketten
                            SET Reparaturumfang = ?
                            WHERE id = ?
                        """, (updated_reparaturumfang, id))

                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Fehler bei der Datenvorverarbeitung: {e}")
            raise