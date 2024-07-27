from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from app.utils.qr_code import create_qr_code
from io import BytesIO

def create_labels(dataframe, output):
    # Avery Zweckform 3474 Etiketten auf A4 Blatt (8 Etiketten pro Seite)
    label_width = 99.1 * mm
    label_height = 38.1 * mm
    margin_left = 4.2 * mm
    margin_top = 12.7 * mm
    h_space = 2.5 * mm
    v_space = 0 * mm

    # PDF-Dokument erstellen
    c = canvas.Canvas(output, pagesize=A4)
    width, height = A4

    # Position der Etiketten auf der Seite berechnen
    for index, row in dataframe.iterrows():
        col = index % 2
        row_num = (index // 2) % 4
        x = margin_left + col * (label_width + h_space)
        y = height - margin_top - (row_num + 1) * label_height - row_num * v_space
        
        # Zeichnen der Etiketten
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        c.rect(x, y, label_width, label_height)

        c.drawString(x + 5 * mm, y + label_height - 10 * mm, f"Auftragsnummer: {row['Auftragsnummer']}")
        c.drawString(x + 5 * mm, y + label_height - 20 * mm, f"Annahmedatum: {row['Annahmedatum_Uhrzeit1']}")
        c.drawString(x + 5 * mm, y + label_height - 30 * mm, f"Notizen: {row['Notizen_Serviceberater']}")
        c.drawString(x + 5 * mm, y + label_height - 40 * mm, f"Kundenname: {row['Kundenname']}")
        c.drawString(x + 5 * mm, y + label_height - 50 * mm, f"Kennzeichen: {row['Kennzeichen']}")

        # QR-Code hinzufügen
        qr_data = f"{row['Auftragsnummer']}, {row['Annahmedatum_Uhrzeit1']}, {row['Notizen_Serviceberater']}, {row['Kundenname']}, {row['Kennzeichen']}"
        qr_img = create_qr_code(qr_data)
        qr_io = BytesIO()
        qr_img.save(qr_io, format='PNG')
        qr_io.seek(0)
        c.drawImage(qr_io, x + label_width - 25 * mm, y + 5 * mm, width=20 * mm, height=20 * mm)

        # Neue Seite hinzufügen, wenn notwendig
        if (index + 1) % 8 == 0:
            c.showPage()

    c.save()