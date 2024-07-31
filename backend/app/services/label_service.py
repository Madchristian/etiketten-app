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
    """
    Wrap text to fit in a given width and height.
    """
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
        return f"{formatted_date} {formatted_time}", formatted_time
    except ValueError:
        return datetime_str, ""


def highlight_words(text, highlight_list):
    for word in highlight_list:
        if word in text:
            text = text.replace(word, f"<yellow>{word}</yellow>")
    return text


def draw_highlighted_text(c, text, x, y, max_width, line_height, max_lines):
    parts = text.split('<yellow>')
    for part in parts:
        if '</yellow>' in part:
            normal_text, highlighted_text = part.split('</yellow>')
            y = wrap_text(c, normal_text, x, y, max_width, line_height, max_lines)
            c.setFillColor(colors.yellow)
            y = wrap_text(c, highlighted_text, x, y, max_width, line_height, max_lines)
            c.setFillColor(colors.black)
        else:
            y = wrap_text(c, part, x, y, max_width, line_height, max_lines)
    return y


def draw_datetime_with_colored_time(c, datetime_str, x, y):
    formatted_datetime, time_part = format_datetime(datetime_str)
    date_part = formatted_datetime.replace(time_part, "").strip()

    c.setFont("Helvetica", 8)
    c.setFillColor(colors.black)
    c.drawString(x, y, date_part)

    time_x = x + c.stringWidth(date_part + " ", "Helvetica", 8)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(colors.red)
    c.drawString(time_x, y, time_part)

    return y


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
        text_y = draw_datetime_with_colored_time(c, row['Annahmedatum_Uhrzeit1'], text_x, text_y)
        formatted_fertigstellung = format_datetime(row['Fertigstellungstermin'])[0]
        c.setFillColor(colors.black)
        c.drawString(text_x, text_y - 4 * mm, f" bis {formatted_fertigstellung}")

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
        highlighted_notiz = highlight_words(row['Notizen_Serviceberater'], ['Wartung', 'Assyst'])
        text_y = draw_highlighted_text(c, highlighted_notiz, text_x, text_y, label_width - 3 * mm, line_height=7, max_lines=5)

    c.save()