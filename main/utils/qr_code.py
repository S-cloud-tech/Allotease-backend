import qrcode
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.core.files.base import ContentFile
from django.conf import settings
from datetime import datetime


# QR code generation 
def generate_qr_code(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    buffer = BytesIO()
    img.save(buffer)
    return ContentFile(buffer.getvalue())

# Receipt generation
def generate_receipt(order):
    """Generate a receipt PDF with a QR code"""
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle(f"Receipt_{order.id}")

    # Add receipt details
    pdf.drawString(100, 750, "Purchase Receipt")
    pdf.drawString(100, 730, f"Order ID: {order.id}")
    pdf.drawString(100, 710, f"Customer: {order.user.username}")
    pdf.drawString(100, 690, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    pdf.drawString(100, 650, "Items Purchased:")
    y = 630
    for item in order.items.all():
        pdf.drawString(120, y, f"{item.product.name} - ${item.price} x {item.quantity}")
        y -= 20  

    pdf.drawString(100, y - 30, f"Total: ${order.total_price}")

    # Add QR code
    qr_code = generate_qr_code(order)
    pdf.drawInlineImage(qr_code, 400, 700, 100, 100)  # Position QR at the top right
    
    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    return buffer

def save_receipt(order):
    """Generate and save the receipt PDF in the database"""
    pdf_buffer = generate_receipt(order)
    order.delete_old_receipt()  # Delete old receipt if exists
    order.receipt.save(f"receipt_{order.id}.pdf", ContentFile(pdf_buffer.getvalue()))
    order.save()

