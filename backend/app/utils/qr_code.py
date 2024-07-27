from PIL import Image, ImageDraw
import qrcode

def create_qr_code(data, size=290):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    img = img.resize((size, size), Image.LANCZOS)
    return img