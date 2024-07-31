import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from datetime import datetime

def map_terminart(terminart, direktannahme):
    if direktannahme == "Ja":
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

def create_labels(dataframe, output):
    label_width = 50 * mm
    label_height = 27 * mm
    margin_left = 5 * mm
    margin_top = 14 * mm
    h_space = 0 * mm
    v_space = 0 * mm

    dataframe = dataframe.fillna('').astype(str)
    dataframe['Auftragsnummer'] = dataframe['Auftragsnummer'].astype(str).str.split('.').str[0]

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
        c.drawString(text_x, text_y, kundenname)

        c.setFont("Helvetica", 8)
        text_y -= 4 * mm
        formatted_date, formatted_time = format_datetime(row['Annahmedatum_Uhrzeit1'])
        c.drawString(text_x, text_y, formatted_date)
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(colors.red)
        c.drawString(text_x + c.stringWidth(formatted_date, "Helvetica", 8) + 2 * mm, text_y, formatted_time)
        c.setFillColor(colors.black)
        text_y -= 4 * mm
        formatted_fertigstellung, _ = format_datetime(row['Fertigstellungstermin'])
        c.drawString(text_x, text_y, f"bis {formatted_fertigstellung}")

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
        text_y -= 8 * mm
        highlighted_notiz = highlight_words(row['Notizen_Serviceberater'], ['Wartung', 'Assyst', 'Service'])
        words = highlighted_notiz.split()
        for word in words:
            if word in ['Wartung', 'Assyst', 'Service']:
                c.setFillColor(colors.yellow)
                c.setFont("Helvetica-Bold", 7)
            else:
                c.setFillColor(colors.black)
                c.setFont("Helvetica", 7)
            c.drawString(text_x, text_y, word)
            text_x += c.stringWidth(word + " ", "Helvetica", 7)

    c.save()