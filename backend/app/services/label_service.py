import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from datetime import datetime

def map_terminart(terminart):
    mapping = {
        'K': 'KW',
        'H': 'H&B',
        'R': ''
    }
    return mapping.get(terminart, '')

def wrap_text(c, text, x, y, max_width, line_height, max_lines):
    words = text.split(' ')
    lines = []
    line = []
    for word in words:
        if c.stringWidth(' '.join(line + [word]), "Helvetica", 7) < max_width:
            line.append(word)
        else:
            lines.append(' '.join(line))
            line = [word]
        if len(lines) >= max_lines:
            break
    if len(lines) < max_lines:
        lines.append(' '.join(line))
    for line in lines:
        c.drawString(x, y, line)
        y -= line_height
    return y

def format_datetime(datetime_str):
    """ Hilfsfunktion zum Formatieren von Datum und Uhrzeit """
    try:
        dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        formatted_date = dt.strftime('%d.%m')
        formatted_time = dt.strftime('%H:%M')
        return f"{formatted_date} {formatted_time}"
    except ValueError:
        return datetime_str

def create_labels(dataframe, output):
    label_width = 48.5 * mm
    label_height = 25.4 * mm
    margin_left = 8 * mm
    margin_top = 21.5 * mm
    h_space = 0 * mm
    v_space = 0 * mm

    dataframe = dataframe.fillna('').astype(str)
    dataframe['Auftragsnummer'] = dataframe['Auftragsnummer'].astype(str).str.split('.').str[0]


    # Sortieren nach Annahmedatum_Uhrzeit1
    dataframe['Annahmedatum_Uhrzeit1'] = pd.to_datetime(dataframe['Annahmedatum_Uhrzeit1'], format='%Y-%m-%d %H:%M:%S')
    dataframe.sort_values(by='Annahmedatum_Uhrzeit1', inplace=True)

    # PDF-Dokument erstellen

    c = canvas.Canvas(output, pagesize=A4)
    width, height = A4

    current_datetime = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    total_labels = len(dataframe)
    labels_per_page = 40
    total_pages = (total_labels + labels_per_page - 1) // labels_per_page

    def draw_header(c, page_number, total_pages):
        c.setFont("Helvetica", 10)
        c.drawString(margin_left, height - 10 * mm, f"Erstellt am: {current_datetime}")
        c.drawRightString(width - margin_left, height - 10 * mm, f"Seite {page_number} von {total_pages}")

    page_number = 1
    draw_header(c, page_number, total_pages)

    for index, row in dataframe.iterrows():
        if index > 0 and index % labels_per_page == 0:
            c.showPage()
            page_number += 1
            draw_header(c, page_number, total_pages)

        col = index % 4
        row_num = (index // 4) % 10
        x = margin_left + col * (label_width + h_space)
        y = height - margin_top - (row_num + 1) * label_height - row_num * v_space

        # Debugging-Ausgabe für jede Position des Labels
        print(f"Index: {index}, Seite: {page_number}, Spalte: {col}, Zeile: {row_num}")

        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        c.rect(x, y, label_width, label_height)

        text_x = x + 2 * mm
        text_y = y + label_height - 4 * mm

        terminart_abkuerzung = map_terminart(row['Terminart'])

        max_name_length = 21
        kundenname = row['Kundenname']
        if len(kundenname) > max_name_length:
            kundenname = kundenname[:max_name_length] + '...'

        if terminart_abkuerzung:
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(colors.red)
            c.drawString(x + label_width - 10 * mm, y + label_height - 4 * mm, terminart_abkuerzung)
            c.setFillColor(colors.black)

        c.setFont("Helvetica-Bold", 8)
        c.drawString(text_x, text_y, kundenname)

        c.setFont("Helvetica", 8)

        text_y -= 3.5 * mm
        formatted_annahme = format_datetime(row['Annahmedatum_Uhrzeit1'])
        formatted_fertigstellung = format_datetime(row['Fertigstellungstermin'])
        c.drawString(text_x, text_y, f"{formatted_annahme} bis {formatted_fertigstellung}")


        text_y -= 4 * mm
        formatted_annahme = format_datetime(row['Annahmedatum_Uhrzeit1'].strftime('%Y-%m-%d %H:%M:%S'))
        formatted_fertigstellung = format_datetime(row['Fertigstellungstermin'])
        c.drawString(text_x, text_y, f"{formatted_annahme} bis {formatted_fertigstellung}")

        # rechtsbündige Auftragsnummer

        c.setFont("Helvetica-Bold", 10)
        kennzeichen = row['Amtl_Kennzeichen']
        auftragsnummer = f"AU{row['Auftragsnummer']}"
        kennzeichen_width = c.stringWidth(kennzeichen, "Helvetica-Bold", 10)
        auftragsnummer_width = c.stringWidth(auftragsnummer, "Helvetica-Bold", 10)
        space_between = label_width - (kennzeichen_width + auftragsnummer_width + 4 * mm)

        c.drawString(text_x, text_y - 4 * mm, kennzeichen)
        c.drawRightString(x + label_width - 2 * mm, text_y - 4 * mm, auftragsnummer)

        c.setLineWidth(0.5)
        c.line(text_x, text_y - 5 * mm, x + label_width - 2 * mm, text_y - 5 * mm)
        c.setFont("Helvetica", 7)
        text_y -= 7 * mm
        notiz = row['Notizen_Serviceberater'][:180]
        text_y = wrap_text(c, notiz, text_x, text_y, label_width - 3 * mm, line_height=7, max_lines=5)

    c.save()