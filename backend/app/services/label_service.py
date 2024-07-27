from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from datetime import datetime
import pandas as pd

def map_terminart(terminart):
    mapping = {
        'R': 'KW',  # Wartet
        'H': 'H&B',  # Hol&Bring
        'K': ''      # Normal
        # Füge hier weitere Zuordnungen hinzu, falls nötig
    }
    return mapping.get(terminart, '')

def wrap_text(c, text, x, y, max_width, line_height, max_lines):
    """ Hilfsfunktion zum Umbruch von Text, um innerhalb eines bestimmten Breitenlimits zu bleiben und max. Anzahl von Zeilen zu begrenzen """
    words = text.split(' ')
    lines = []
    line = []
    for word in words:
        if c.stringWidth(' '.join(line + [word]), "Helvetica", 7) < max_width:
            line.append(word)
        else:
            lines.append(' '.join(line))
            line = [word]
        if len(lines) >= max_lines:  # Stoppe, wenn max. Anzahl von Zeilen erreicht ist
            break
    if len(lines) < max_lines:
        lines.append(' '.join(line))  # Letzte Zeile hinzufügen, wenn noch Platz ist
    for line in lines:
        c.drawString(x, y, line)
        y -= line_height  # Abstand zwischen den Zeilen
    return y

def create_labels(dataframe, output):
    # Avery Zweckform Etiketten auf A4 Blatt (40 Etiketten pro Seite, 4 x 10)
    label_width = 48.5 * mm
    label_height = 25.4 * mm
    margin_left = 8 * mm
    margin_top = 21.5 * mm
    h_space = 0 * mm
    v_space = 0 * mm

    # NaN-Werte durch leere Strings ersetzen und alle Werte in Strings konvertieren
    dataframe = dataframe.fillna('').astype(str)

    # PDF-Dokument erstellen
    c = canvas.Canvas(output, pagesize=A4)
    width, height = A4

    # Aktuelles Datum und Uhrzeit
    current_datetime = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    total_labels = len(dataframe)
    labels_per_page = 40
    total_pages = (total_labels + labels_per_page - 1) // labels_per_page  # Aufrunden

    # Position der Etiketten auf der Seite berechnen
    for index, row in dataframe.iterrows():
        col = index % 4
        row_num = (index // 4) % 10
        x = margin_left + col * (label_width + h_space)
        y = height - margin_top - (row_num + 1) * label_height - row_num * v_space

        if index % labels_per_page == 0:
            # Kopfzeile mit Datum, Uhrzeit und Seitennummerierung
            c.setFont("Helvetica", 10)
            c.drawString(margin_left, height - 10 * mm, f"Erstellt am: {current_datetime}")
            c.drawRightString(width - margin_left, height - 10 * mm, f"Seite {(index // labels_per_page) + 1} von {total_pages}")

        # Zeichnen der Etiketten
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        c.rect(x, y, label_width, label_height)

        # Text innerhalb der Grenzen platzieren
        text_x = x + 2 * mm
        text_y = y + label_height - 4 * mm

        terminart_abkuerzung = map_terminart(row['Terminart'])

        # Begrenze den Namen auf eine bestimmte Länge, um Überschreibungen zu vermeiden
        max_name_length = 21
        kundenname = row['Kundenname']
        if len(kundenname) > max_name_length:
            kundenname = kundenname[:max_name_length] + '...'

        # Terminart oben rechts in Rot
        if terminart_abkuerzung:
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(colors.red)
            c.drawString(x + label_width - 10 * mm, y + label_height - 4 * mm, terminart_abkuerzung)
            c.setFillColor(colors.black)  # Zurücksetzen auf Schwarz für den Rest des Textes

        c.setFont("Helvetica-Bold", 8)
        c.drawString(text_x, text_y, kundenname)

        c.setFont("Helvetica", 8)
        text_y -= 3 * mm
        c.drawString(text_x, text_y, f"{row['Annahmedatum_Uhrzeit1']} - {row['Fertigstellungstermin']}")

        c.setFont("Helvetica-Bold", 10)
        text_y -= 4 * mm  # Text näher an das vorherige Element rücken
        c.drawString(text_x, text_y, row['Amtl. Kennzeichen'])

        # Linie unter dem Kennzeichen zeichnen
        c.setLineWidth(0.5)
        c.line(text_x, text_y - 1 * mm, x + label_width - 2 * mm, text_y - 1 * mm)  # Linie näher an das Kennzeichen rücken

        # Notiztext umbrochen und auf 200 Zeichen begrenzt
        c.setFont("Helvetica", 7)
        text_y -= 4 * mm  # Text näher an die Linie rücken
        notiz = row['Notizen_Serviceberater'][:200]  # Begrenze auf 200 Zeichen
        text_y = wrap_text(c, notiz, text_x, text_y, label_width - 4 * mm, line_height=7, max_lines=5)

        # Neue Seite hinzufügen, wenn 40 Etiketten erreicht sind
        if (index + 1) % 40 == 0:
            c.showPage()

    c.save()