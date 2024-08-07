import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from datetime import datetime
import pytz
import logging

logger = logging.getLogger(__name__)

def map_terminart(terminart, direktannahme):
    if direktannahme == "1":
        return "DIA", colors.red
    mapping = {
        'K': ('KW', colors.red),
        'H': ('H&B', colors.blue),
        'R': ('', colors.black)
    }
    return mapping.get(terminart, ('', colors.black))

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
    try:
        dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        formatted_date = dt.strftime('%d.%m')
        formatted_time = dt.strftime('%H:%M')
        return formatted_date, formatted_time
    except ValueError:
        return datetime_str, ''

def highlight_words(text, highlight_list):
    for word in highlight_list:
        if word in text:
            text = text.replace(word, f'<highlight>{word}</highlight>')
            text = f'{word} ' + text.replace(f'<highlight>{word}</highlight>', '').strip()
    return text

def limit_text(text, max_length=180):
    if len(text) > max_length:
        text = text[:max_length] + '...'
    return text

def split_text_into_lines(text, max_chars_per_line=30, max_lines=5):
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        if len(current_line) + len(word) + 1 <= max_chars_per_line:
            current_line += (word + " ")
        else:
            lines.append(current_line.strip())
            current_line = word + " "
            if len(lines) == max_lines - 1:
                break
    lines.append(current_line.strip())
    return lines[:max_lines]

def draw_text_with_highlight(c, text, x, y, max_width, line_height, margin_left, schluesselwort):
    lines = split_text_into_lines(text)
    for line in lines:
        words = line.split()
        current_x = x
        for word in words:
            if word.startswith('<highlight>') and word.endswith('</highlight>'):
                word = word.replace('<highlight>', '')
                c.setFillColor(colors.yellow)
                c.setFont("Helvetica-Bold", 7)
            else:
                if schluesselwort:
                    c.setFillColor(colors.darkgoldenrod)
                else:
                    c.setFillColor(colors.black)
                c.setFont("Helvetica", 7)
            c.drawString(current_x, y, word + " ")
            current_x += c.stringWidth(word + " ", "Helvetica", 7)
        y -= line_height
    return y

def draw_vertical_text(c, text, x, y):
    for char in text:
        c.drawString(x, y, char)
        y -= 10  # Adjust this value as needed to control the spacing between characters

def create_labels(dataframe, output):
    """
    Create labels for each row in the dataframe and save them to a PDF file."""
    label_width = 48.5 * mm
    label_height = 25.5 * mm
    margin_left = 7 * mm
    margin_top = 21 * mm
    h_space = 0 * mm
    v_space = 0 * mm

    dataframe = dataframe.fillna('').astype(str)
    dataframe['Auftragsnummer'] = dataframe['Auftragsnummer'].astype(str).str.split('.').str[0]

    # Daten filtern
    dataframe = dataframe[dataframe['Terminstatus'] == '2']
    logger.info(f"Gefilterte Daten: {dataframe.head()}")

    c = canvas.Canvas(output, pagesize=A4)
    width, height = A4

    # Lokale Zeitzone verwenden
    local_tz = pytz.timezone('Europe/Berlin')
    current_datetime = datetime.now(local_tz).strftime("%d.%m.%Y %H:%M:%S")
    
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

        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        c.rect(x, y, label_width, label_height)

        text_x = x + 2 * mm
        text_y = y + label_height - 4 * mm

        terminart_abkuerzung, color = map_terminart(row['Terminart'], row['Direktannahme'])

        max_name_length = 21
        kundenname = row['Kundenname']
        if len(kundenname) > max_name_length:
            kundenname = kundenname[:max_name_length] + '...'

        if terminart_abkuerzung:
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(color)
            c.drawString(x + label_width - 10 * mm, y + label_height - 4 * mm, terminart_abkuerzung)
            c.setFillColor(colors.black)

        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(colors.black)
        c.drawString(text_x, text_y, kundenname)

        c.setFont("Helvetica", 8)
        text_y -= 3 * mm
        formatted_date, formatted_time = format_datetime(row['Annahmedatum_Uhrzeit1'])
        c.drawString(text_x, text_y, formatted_date)
        date_time_width = c.stringWidth(formatted_date, "Helvetica", 8)
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(colors.red)
        c.drawString(text_x + date_time_width + 2 * mm, text_y, formatted_time)
        c.setFillColor(colors.black)

        formatted_fertigstellung, fertigstellung_time = format_datetime(row['Fertigstellungstermin'])
        c.setFont("Helvetica", 8)
        fertigstellung_width = c.stringWidth(f"bis {formatted_fertigstellung}", "Helvetica", 8)
        c.drawString(text_x + date_time_width + c.stringWidth(formatted_time, "Helvetica-Bold", 8) + 4 * mm, text_y, f"bis {formatted_fertigstellung}")
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(colors.red)
        c.drawString(text_x + date_time_width + c.stringWidth(formatted_time, "Helvetica-Bold", 8) + 4 * mm + fertigstellung_width + 2 * mm, text_y, fertigstellung_time)
        c.setFillColor(colors.black)

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

        c.setFont("Helvetica", 8)
        text_y -= 8 * mm

        schluesselwort = row['Schluesselwort']
        if schluesselwort:
            c.setFillColor(colors.darkgoldenrod)
            c.setFont("Helvetica", 8)

        limited_text = limit_text(row['Reparaturumfang'])
        text_y = draw_text_with_highlight(c, limited_text, text_x, text_y, label_width - 4 * mm, 7, margin_left, schluesselwort)

    c.save()